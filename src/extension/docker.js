const execSync = require('child_process').execSync;
const vscode = require('vscode');
const WebSocketClient = require('websocket').client;
let CONFIG = vscode.workspace.getConfiguration("epilinter");
let TOKENIZER_PORT = CONFIG.get('tokenizer_port');
let DOCKER_ADDRESS = `ws://127.0.0.1:${TOKENIZER_PORT}`;
const SERVER_ADDRESS = "ws://54.36.183.139:8081";
const TOKENIZER_IMAGE = "qudes/epitokenizer";
const CONNECTION_TIMEOUT = 10000;

exports.stopTokenizer = async function() {
    try {
        execSync(`docker kill epitokenizer && docker rm epitokenizer`);
    } catch {}
}

let forceDockerStart = async function() {
    exports.stopTokenizer();

    CONFIG = vscode.workspace.getConfiguration("epilinter");
    TOKENIZER_PORT = CONFIG.get('tokenizer_port');
    DOCKER_ADDRESS = `ws://127.0.0.1:${TOKENIZER_PORT}`;
    CONFIG.update('tokenizer_address', DOCKER_ADDRESS);

    let message = await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "Starting the tokenizer..." }, (progress, token) => {
        try {
            execSync(`docker run --restart=always -d -p ${TOKENIZER_PORT}:8081 --name epitokenizer ${TOKENIZER_IMAGE}`);
            let nbTried = 0;
            return new Promise((resolve) => {
                const interval = setInterval(() => {
                    if (nbTried > CONNECTION_TIMEOUT / 250) {
                        clearInterval(interval);
                        resolve("error");
                    }
                    var client = new WebSocketClient();
                    client.on('connect', (connection) => {
                        clearInterval(interval);
                        resolve("good");
                    });
                    client.connect(DOCKER_ADDRESS);
                    nbTried++;
                }, 250);
            });
        } catch {
            return new Promise((resolve) => {resolve("error");});
        }
    });
    return (message == "error") ? false : true;
}

async function startDocker() {
    CONFIG = vscode.workspace.getConfiguration("epilinter");
    try {
        // La command du sheitan
        // If docker is not installed / container is not running / container is not listening on the right port -> throws an error
        let output = execSync("docker ps | grep qudes/epitokenizer | grep epitokenizer | grep -E ':[0-9]{3,5}->8081/tcp' | grep -oE '[0-9]{3,5}->' | head -n 1 | head -c -3 | grep -E '[0-9]{3,5}'");
        let port = parseInt(output.toString());
        // Else, docker is already started.
        // If it is started on the wrong port, restart it
        if (port && port != TOKENIZER_PORT) {
            CONFIG.update('tokenizer_port', port);
            exports.stopTokenizer();
            return await forceDockerStart();
        }
    } catch {
        return await forceDockerStart();
    }
    return true;
}

async function pullDocker() {
    let isPulled = false;

    await vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: "Pulling the tokenizer...", cancellable: false }, (progress, token) => {
        try {
            execSync(`docker pull ${TOKENIZER_IMAGE}:latest`);
        } catch {
            return new Promise((resolve) => {resolve()});
        }
        isPulled = true;
        return new Promise((resolve) => {resolve();});
    })
    return isPulled;
}

function isDockerInstalled() {
    try {
        execSync("docker --version");
    } catch {
        return false;
    }
    return true;
}

function isTokenizerPulled() {
    try {
        execSync(`docker image inspect ${TOKENIZER_IMAGE}`);
    } catch {
        return false;
    }
    return true;
}

/*

If settings change:
    stop tokenizer
    start it with the new settings
    if cannot be started:
        docker address is server address
    else:
        docker address is docker address
*/

exports.startTokenizer = async function() {
    CONFIG = vscode.workspace.getConfiguration("epilinter");
    exports.stopTokenizer();
    CONFIG.update('tokenizer_address', SERVER_ADDRESS);
    if (CONFIG.get('use_docker') === false)
        return;

    // Check if docker is installed
    if (!isDockerInstalled()) {
        vscode.window.showErrorMessage("Docker is not installed. Please install it to use EpiLinter: https://docs.docker.com/get-docker/");
        return;
    }

    // Check if tokenizer exists
    if (!isTokenizerPulled() && !pullDocker()) {
        vscode.window.showErrorMessage("An error occured while EpiLinter configured itself. Possible reason for this error may be:\n- You are not connected to the internet\n- The docker daemon is not running\n- You have not enough rights to run docker\n- You have not enough disk space to pull the image");
        return;
    }

    // Start it
    if (await startDocker() === true)
        CONFIG.update('tokenizer_address', DOCKER_ADDRESS);
    else
        vscode.window.showErrorMessage("An error occured while EpiLinter started.");
}

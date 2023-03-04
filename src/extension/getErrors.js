var WebSocketClient = require('websocket').client;
const vscode = require('vscode');
let {PythonShell} = require('python-shell');
const fs = require('fs');
const { errorCodeToExplanation } = require('./errorCodes');

const CONNECTION_FAILED = "connection failed";
const EXCHANGE_FAILED =  "exchange failed";
const PUBLISHER = "LIL-EpiProjects";
const EXT_NAME = "epilinter";
const EPILINTER_DIR = vscode.extensions.getExtension(PUBLISHER + "." + EXT_NAME).extensionPath;
const TOKENS_TXT = EPILINTER_DIR + "/tokens.txt";
const SCRIPT_SRC = EPILINTER_DIR+"/src/checker/runner.py";


exports.DIAGNOSTIC = vscode.languages.createDiagnosticCollection(
    "EpiLinter"
);

class Token {
    constructor (line, column, width, error_msg) {
        this._line = line;
        this._column = column;
        this._width = width;
        this._error_msg = error_msg;
    }

    get line() {
        return this._line;
    }
    get column() {
        return this._column;
    }
    get width() {
        return this._width;
    }
    get errorMessage() {
        return this._error_msg;
    }
}

class TokenizerClient {
    constructor() {
        let CONFIG = vscode.workspace.getConfiguration("epilinter");

        this.client = new WebSocketClient();
        this.connection = null;
        this.address = CONFIG.get('tokenizer_address');
        this.client.on('connect', (connection) => {
            this.connection = connection;
        });
        try {
            this.client.connect(this.address);
        } catch {
            // Do nothing
        }
    }

    handlePromise(content, resolve, reject) {
        this.connection.on('message', (message) => {
            if (message.type === 'utf8')
                resolve(message.utf8Data);
            reject(EXCHANGE_FAILED + "not an UTF8 message");
        });
        this.connection.on('error', (error) => {
            reject(EXCHANGE_FAILED + error.message);
        });
        this.connection.on('close', async function(error) {
            handleErrorMessage(CONNECTION_FAILED + "Error code: " + error.toString());
            this.connection = null;
            reject("");
        });
        this.connection.sendUTF(content + "\n");
    }

    /**
     * Send a message to the server.
     * @param {Buffer} content - The message to send.
     * @returns {Promise} A promise that will be resolved when the server sends a response, or in case of an error.
     */
    send(content) {
        let CONFIG = vscode.workspace.getConfiguration("epilinter");

        if (this.address != CONFIG.get('tokenizer_address')) {
            vscode.window.showInformationMessage("Tokenizer address changed to " + CONFIG.get('tokenizer_address'));
            this.address = CONFIG.get('tokenizer_address');
            this.connection = null;
        }
        this.client.removeAllListeners();
        return new Promise((resolve, reject) => {
            if (!this.connection) {
                this.client.on('connect', (connection) => {
                    this.connection = connection;
                    this.handlePromise(content, resolve, reject);
                });
                this.client.on('connectFailed', (error) => {
                    reject(CONNECTION_FAILED + error.message);
                });
                this.client.connect(this.address);
            } else {
                this.handlePromise(content, resolve, reject);
            }
        });
    }
}
const CLIENT = new TokenizerClient();

let lastErrorTimestamp = 0;

// Write every found token for this file in {__dirname}/logs/{path.basename(fileName)}.tokens, and return the created file path
function loadTokensForFile(fileName) {
    let content;
    try {
        content = fs.readFileSync(fileName);
    } catch {
        return new Promise((resolve, reject) => {
            reject();
        });
    }
    return CLIENT.send(content);
}

function getLoggedErrorsAsTokens() {
    const log_file = EPILINTER_DIR+"/src/checker/logs.log";
    const content = fs.readFileSync(log_file).toString().split("\n");
    let tokens = []
    for (let line of content) {
        const fields = line.split("__");
        tokens.push(new Token(parseInt(fields[1]), parseInt(fields[2]), parseInt(fields[4]), fields[3]));
    }
    return tokens;
}

function parseScriptOutput(err, fileUri) {
    if (err) {
        vscode.window.showErrorMessage("An error occured while EpiLinter parsed this file.\nMessage:" + err.message);
        return;
    }
    // Open logs.log, read line by line, adding errors to vscode
    const errors = getLoggedErrorsAsTokens();
    const diagnostics = [];
    for (let error of errors) {
        if (!error.errorMessage)
            continue;
        let d = new vscode.Diagnostic(
            new vscode.Range(error.line -1, error.column, error.line - 1, error.column + error.width),
            error.errorMessage + ": " + errorCodeToExplanation[error.errorMessage.slice(-2)],
            vscode.DiagnosticSeverity.Error
        );
        d.source = "EpiLinter";
        diagnostics.push(d);
    }
    exports.DIAGNOSTIC.set(fileUri, diagnostics);
}

function parseServerAnswer(message, fileName, fileUri) {
    fs.writeFileSync(TOKENS_TXT, message);
    PythonShell.run(
        // Script
        SCRIPT_SRC,
        {args: [TOKENS_TXT, fileName]},

        // Function when finished
        (err, results) => {
            parseScriptOutput(err, fileUri);
        }
    );
}

let nbErrors = 0;
function handleErrorMessage(error) {
    //Don't show too many errors
    if (Date.now() - lastErrorTimestamp < 60000 || nbErrors == 0)
        return;
    lastErrorTimestamp = (nbErrors == 0 ? 0 : Date.now());

    nbErrors++;
    if (error.startsWith(EXCHANGE_FAILED)) {
        vscode.window.showErrorMessage("An error occured while communicating with the EpiLinter server. Message: " + error.slice(EXCHANGE_FAILED.length));
    } else if (error.startsWith(CONNECTION_FAILED)) {
        vscode.window.showErrorMessage("Cannot connect to the EpiLinter server. Please check your internet connection, or try again later. Message: " + error.slice(CONNECTION_FAILED.length));
    } else {
        vscode.window.showErrorMessage("Cannot read this file.");
    }
}

exports.parseErrorForFile = (fileName, fileUri) => {
    // Get tokens for this file
    loadTokensForFile(fileName)
        .then((message) => {
            parseServerAnswer(message, fileName, fileUri);
        })
        .catch((error) => {
            handleErrorMessage(error);
        });
}


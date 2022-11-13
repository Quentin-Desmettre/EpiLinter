// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
let path = require("path");
var WebSocketClient = require('websocket').client;
const vscode = require('vscode');
let {PythonShell} = require('python-shell');
const { readFileSync } = require("fs");
const fs = require('fs');

const DIAGNOSTIC = vscode.languages.createDiagnosticCollection(
    "EpiLinter"
);

const PUBLISHER = "LIL-EpiProjects";
const EXT_NAME = "epilinter";

const EPILINTER_DIR = vscode.extensions.getExtension(PUBLISHER + "." + EXT_NAME).extensionPath;

const errorCodeToExplanation = {
    "A3": "Missing line break at end of file.",
    "C1": "Too many conditional branchings.",
    "C3": "Forbidden keyword: goto.",
    "F2": "Function names should be in snake case.",
    "F3": "Lines should not exceed 80 characters.",
    "F4": "Functions should not exceed 20 lines.",
    "F5": "Functions should not have more than 4 arguments.",
    "F6": "Functions taking no arguments should take void as their only argument.",
    "F8": "Functions should not contain any comment.",
    "F9": "Forbidden feature: nested functions.",
    "G1": "Corrupted Epitech header.",
    "G2": "One and only one empty line should be present between functions.",
    "G3": "Badly indented pre-processor directive.",
    "G4": "Global variables should be marked as const.",
    "G5": "include directive must only include C header (.h) files.",
    "G6": "Line endings must be done in UNIX style (with \n).",
    "G7": "No trailing spaces must be present at the end of a line.",
    "G8": "No leading empty lines must be present and no more than 1 trailing empty line must be present.",
    "H1": "Header files must only contain function prototypes, type declarations, global variable/constant declarations, macros and static inline functions.",
    "H2": "Headers must be protected from double inclusion.",
    "L2": "Each indentation level must be done by using 4 spaces, and no tabulations may be used for identation.",
    "L3": "Misplaced space.",
    "L4": "Misplaced curly-bracket.",
    "O1": "The repository must not contain compiled (.o, .gch, .a, .so, ...), temporary or unnecessary files (*~, #*#, .d, toto, ...)",
    "O3": "A source file must match a logical entity, and group all the functions associated with that entity.",
    "O4": "The name of the file must define the logical entity it represents, and thus be clear, precise, explicit and unambiguous.",
    "V1": "All identifier names must be in English, according to the snake_case convention."
};

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

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

let lastErrorTimestamp = 0;

// Write every found token for this file in {__dirname}/logs/{path.basename(fileName)}.tokens, and return the created file path
function loadTokensForFile(fileName) {
    return new Promise((resolve, reject) => {
        var client = new WebSocketClient();

        client.on('connectFailed', function(error) {
            if (Date.now() - lastErrorTimestamp > 60000) {
                vscode.window.showErrorMessage("Cannot connect to the EpiLinter server. Please check your internet connection, or try again later.\nMessage: " + error.message);
                lastErrorTimestamp = Date.now();
            }
        });

        client.on('connect', function(connection) {
            connection.on('error', function(error) {
                if (Date.now() - lastErrorTimestamp > 60000) {
                    vscode.window.showErrorMessage("An error occured while communicating with the EpiLinter server.\nMessage: " + error.message);
                    lastErrorTimestamp = Date.now();
                }
            });
            connection.on('message', function(message) {
                if (message.type === 'utf8') {
                    connection.close();
                    resolve(message.utf8Data);
                }
            });

            function sendNumber() {
                if (connection.connected) {
                    connection.sendUTF(readFileSync(fileName) + "\n");
                }
            }
            sendNumber();
        });

        client.connect('ws://localhost:8081/');
    }
    );
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


/**
 * Return a list of Token, each describing an error (error code, line, column, width)
 */
function getErrorForFile(fileName) {
    // Get tokens for this file
    loadTokensForFile(fileName).then(message => {
        // Call python script for this file, giving as argument the tokens as a raw string
        const tokens_txt = EPILINTER_DIR + "/tokens.txt";
        fs.writeFileSync(tokens_txt, message);
        PythonShell.run(EPILINTER_DIR+"/src/checker/runner.py",
            {args: [
               tokens_txt, fileName,
               "C-A3",
               "C-C1",
               "C-C3",
               "C-F2",
               "C-F3",
               "C-F4",
               "C-F5",
               "C-F6",
               "C-F8",
               "C-F9",
               "C-G1",
               "C-G2",
               "C-G3",
               "C-G4",
               "C-G5",
               "C-G6",
               "C-G7",
               "C-G8",
               "C-H1",
               "C-H2",
               "C-L2",
               "C-L3",
               "C-L4",
               "C-O1",
               "C-O3",
               "C-O4",
               "C-V1"
            ]},
            async function (err, results) {
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
                DIAGNOSTIC.clear();
                DIAGNOSTIC.set((await vscode.workspace.openTextDocument(fileName)).uri, diagnostics);
            }
        );
    });
}

function codingStyleChecker() {
    var currentlyOpenTabfilePath = vscode.window.activeTextEditor.document.fileName;

    getErrorForFile(currentlyOpenTabfilePath);
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    vscode.workspace.onDidChangeConfiguration(codingStyleChecker);
    vscode.workspace.onDidSaveTextDocument(codingStyleChecker);
    codingStyleChecker();
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
    activate,
    deactivate
}

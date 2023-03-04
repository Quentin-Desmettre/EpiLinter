const vscode = require('vscode');
const { isFileToBeLinted, fetchPatternsToIgnore } = require('./toLint');
const { startTokenizer, stopTokenizer } = require('./docker');
const { parseErrorForFile, DIAGNOSTIC } = require('./getErrors');
// let CONFIG = vscode.workspace.getConfiguration('epilinter');

const IGNORE_PATTERNS = fetchPatternsToIgnore();

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

function codingStyleChecker() {
    var currentlyOpenTabfilePath = vscode.window.activeTextEditor.document.fileName;

    if (isFileToBeLinted(currentlyOpenTabfilePath, IGNORE_PATTERNS))
        parseErrorForFile(currentlyOpenTabfilePath, vscode.window.activeTextEditor.document.uri);
    else
        DIAGNOSTIC.set(vscode.window.activeTextEditor.document.uri, []);
}

function listenConfigChange() {
    let CONFIG = vscode.workspace.getConfiguration('epilinter');
    const VARIABLES = {
        "tokenizer_port": CONFIG.get("tokenizer_port"),
        "use_docker": CONFIG.get("use_docker"),
        "tokenizer_address": CONFIG.get("tokenizer_address")
    }

    let interval = null;
    let checker = async () => {
        CONFIG = vscode.workspace.getConfiguration('epilinter');
        for (const VARIABLE in VARIABLES) {
            if (VARIABLES[VARIABLE] !== CONFIG.get(VARIABLE)) {
                clearInterval(interval);
                VARIABLES[VARIABLE] = CONFIG.get(VARIABLE);
                stopTokenizer();
                await startTokenizer();
                interval = setInterval(checker, 1000);
                break;
            }
        }
    }
    interval = setInterval(checker, 1000);
}

/**
 * @param {vscode.ExtensionContext} context
 */
async function activate(context) {
    await startTokenizer();
    listenConfigChange();
    vscode.window.onDidChangeWindowState(codingStyleChecker);
    vscode.window.onDidChangeTextEditorSelection(codingStyleChecker);
    vscode.window.onDidChangeActiveTextEditor(codingStyleChecker);
    vscode.workspace.onDidChangeConfiguration(codingStyleChecker);
    vscode.workspace.onDidSaveTextDocument(codingStyleChecker);
    vscode.workspace.onDidOpenTextDocument(codingStyleChecker);
    vscode.workspace.onDidChangeTextDocument(codingStyleChecker);
    codingStyleChecker();
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
    activate,
    deactivate
}

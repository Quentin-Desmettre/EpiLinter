const vscode = require('vscode');
const { isFileToBeLinted, fetchPatternsToIgnore } = require('./toLint');
const { parseErrorForFile, DIAGNOSTIC } = require('./getErrors');

const IGNORE_PATTERNS = fetchPatternsToIgnore();

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

function codingStyleChecker() {
    if (!vscode.window.activeTextEditor) return;

    let currentlyOpenTabfilePath = vscode.window.activeTextEditor.document.fileName;

    if (isFileToBeLinted(currentlyOpenTabfilePath, IGNORE_PATTERNS))
        parseErrorForFile(currentlyOpenTabfilePath, vscode.window.activeTextEditor.document.uri);
    else
        DIAGNOSTIC.set(vscode.window.activeTextEditor.document.uri, []);
}

/**
 * @param {vscode.ExtensionContext} context
 */
async function activate(context) {
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

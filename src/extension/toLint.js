const minimatch = require('minimatch');
const execSync = require('child_process').execSync;
const path = require('path');
const vscode = require('vscode');
const fs = require('fs');

function isFileTrackedByGit(fileName, current_dir)
{
    let tracked_files = [];
    try {
        tracked_files = execSync(`cd ${current_dir} && git ls-files`).toString().split("\n");
    } catch {
        return false;
    }
    for (let file of tracked_files) {
        if (file === fileName)
            return true;
    }
    return false;
}

function getAllSubPathsForFile(fileName, current_dir)
{
    const basename = path.basename(fileName);
    // Get all directories
    const directories = (fileName.slice(0, -basename.length)).replaceAll("\\", "/").split("/").filter(x => x !== "");

    // Get all paths
    let paths = [basename];
    let current_path = basename;

    for (let i = directories.length - 1; i >= 0; i--) {
        if (directories[i] == path.basename(current_dir)) {
            current_path = "/" + current_path;
            paths.push(current_path);
            break;
        }
        current_path = directories[i] + (directories[i].endsWith("/") ? "" : "/") + current_path;
        paths.push(current_path);
    }
    return paths;
}

/**
 * Return true if the file should be linted, false otherwise.
 * The file should not be linted if:
 *      - it is in the ignore list and is not tracked by git
 *      - If it is in a /bonus/ or a /tests/ folder
 */
exports.isFileToBeLinted = (fileName, ignore_patterns) => {
    const current_dir = vscode.workspace.workspaceFolders[0].uri.fsPath;

    for (let pattern of ignore_patterns) {
        let subPaths = getAllSubPathsForFile(fileName, current_dir);
        for (let subPath of subPaths) {
            if (minimatch.minimatch(subPath, pattern))
                return isFileTrackedByGit(fileName, current_dir);
        }
    }
    return true;
}

exports.fetchPatternsToIgnore = () => {
    let CONFIG = vscode.workspace.getConfiguration("epilinter");
    let patterns = [];
    const current_dir = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const gitignore = current_dir + "/.gitignore";
    const settings = current_dir + "/.vscode/settings.json";

    // Get .gitignore patterns
    if (fs.existsSync(gitignore)) {
        let gitignore_patterns = fs.readFileSync(gitignore).toString().split("\n");
        // Remove comments and empty lines
        gitignore_patterns = gitignore_patterns.filter((line) => !line.startsWith("#"));
        gitignore_patterns = gitignore_patterns.filter((line) => line !== "");
        patterns = patterns.concat(gitignore_patterns);
    }
    // Get linter-ignore patterns
    return patterns.concat(CONFIG.get('ignoreFiles'));
}

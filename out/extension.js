"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require("vscode");
const child_process = require("child_process");
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "codac" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('extension.helloWorld', () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('Hello World!');
        // console.log(__dirname);
        var recognizer = child_process.spawn('python', [`${__dirname}/sample.py`]);
        recognizer.stdout.on('data', function (data) {
            // console.log(`you said: ${data}`);
            vscode.window.showInformationMessage(`${data}`);
            if (vscode.window.activeTextEditor !== undefined) {
                vscode.window.activeTextEditor.edit(editBuilder => {
                    let p = new vscode.Position(0, 0);
                    editBuilder.insert(p, data.toString());
                });
            }
        });
        recognizer.stderr.on('data', function (data) {
            console.log(`error: ${data}`);
        });
    });
    context.subscriptions.push(disposable);
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map
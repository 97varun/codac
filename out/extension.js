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
    let statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
    statusBarItem.text = '💬 Listen';
    statusBarItem.command = 'extension.listen';
    statusBarItem.show();
    let recognizer;
    let sampleTree = new SampleTree();
    vscode.window.createTreeView('suggestions', { treeDataProvider: sampleTree });
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable1 = vscode.commands.registerCommand('extension.listen', () => {
        // The code you place here will be executed every time your command is executed
        statusBarItem.text = '✖️️ Stop';
        statusBarItem.command = 'extension.stop';
        statusBarItem.show();
        let ed = new Editor();
        recognizer = child_process.spawn('python', [`${__dirname}/audio.py`]);
        recognizer.stdout.on('data', function (data) {
            let JSONdata = JSON.parse(data);
            console.log(JSONdata);
            if (JSONdata.hasOwnProperty('status') && JSONdata.status === 'ready') {
                vscode.window.showInformationMessage(`${JSONdata.status}`);
            }
            else if (JSONdata.hasOwnProperty('error')) {
                let tree = [new SampleNode(JSONdata.input, []), new SampleNode(JSONdata.error, [])];
                sampleTree.setTree(tree);
            }
            else {
                let tree = [new SampleNode(JSONdata.input, [])];
                for (let i = 1; i <= JSONdata.output.length; ++i) {
                    tree.push(new SampleNode(`${i}. ${JSONdata.output[i - 1].code} (${JSONdata.output[i - 1].construct})`, []));
                }
                sampleTree.setTree(tree);
                ed.insertText(JSONdata.output[0].code + '\n');
                if (JSONdata.output[0].construct === 'function') {
                    const position = ed.getCursorPosition();
                    console.log(position);
                    let newPosition = position.with(position.line + 1, 0);
                    ed.moveCursor(newPosition);
                }
            }
        });
        recognizer.stderr.on('data', function (data) {
            console.log(`error: ${data}`);
        });
        recognizer.on('close', function (code) {
            console.log('program stopped');
            statusBarItem.text = '💬 Listen';
            statusBarItem.command = 'extension.listen';
            statusBarItem.show();
        });
    });
    let disposable2 = vscode.commands.registerCommand('extension.stop', () => {
        console.log('killing program');
        recognizer.kill();
        statusBarItem.text = '💬 Listen';
        statusBarItem.command = 'extension.listen';
        statusBarItem.show();
    });
    context.subscriptions.push(disposable1);
    context.subscriptions.push(disposable2);
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
class SampleNode extends vscode.TreeItem {
    constructor(label, children) {
        super(label);
        this.children = children;
        this.label = label;
    }
    getChildren() {
        return this.children;
    }
}
class SampleTree {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.tree = [];
    }
    getTreeItem(element) {
        return {
            label: element.label
        };
    }
    getChildren(element) {
        return element ? element.getChildren() : this.tree;
    }
    setTree(tree) {
        this.tree = tree;
        this._onDidChangeTreeData.fire();
    }
}
class Editor {
    constructor() {
    }
    insertText(text) {
        if (vscode.window.activeTextEditor !== undefined) {
            let pos = new vscode.Position(0, 0);
            const editor = vscode.window.activeTextEditor;
            if (editor.selection.isEmpty) {
                pos = editor.selection.active;
            }
            console.log(pos.line, pos.character);
            editor.edit(editBuilder => {
                editBuilder.insert(pos, text);
            });
        }
    }
    moveCursor(position) {
        if (vscode.window.activeTextEditor !== undefined) {
            const editor = vscode.window.activeTextEditor;
            var newSelection = new vscode.Selection(position, position);
            editor.selection = newSelection;
        }
    }
    getCursorPosition() {
        if (vscode.window.activeTextEditor) {
            const editor = vscode.window.activeTextEditor;
            const position = editor.selection.active;
            return position;
        }
        return new vscode.Position(0, 0);
    }
}
//# sourceMappingURL=extension.js.map
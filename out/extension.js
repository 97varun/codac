"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require("vscode");
const child_process = require("child_process");
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
function activate(context) {
    let codac = new Codac();
    let listen = vscode.commands.registerCommand('extension.listen', () => {
        codac.startRecognizer('audio');
    });
    let stop = vscode.commands.registerCommand('extension.stop', () => {
        codac.stopRecognizer();
    });
    let dictation = vscode.commands.registerCommand('extension.dictation', () => {
        codac.dictate();
    });
    context.subscriptions.push(listen);
    context.subscriptions.push(stop);
    context.subscriptions.push(dictation);
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
class Codac {
    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
        this.setStatusBarBtn('💬 Listen', 'extension.listen');
        this.suggestTree = new SampleTree();
        this.dictateTree = new SampleTree();
        this.errorTree = new SampleTree();
        vscode.window.createTreeView('suggestions', { treeDataProvider: this.suggestTree });
        vscode.window.createTreeView('dictation', { treeDataProvider: this.dictateTree });
        vscode.window.createTreeView('errors', { treeDataProvider: this.errorTree });
        this.editor = new Editor();
        this.recognizer = Object();
        this.isDictation = false;
        this.isListening = false;
    }
    setStatusBarBtn(text, command) {
        this.statusBarItem.text = text;
        this.statusBarItem.command = command;
        this.statusBarItem.show();
    }
    handleOutput(tree, data) {
        return __awaiter(this, void 0, void 0, function* () {
            let self = this;
            console.log(data.toString(), data.toString().length);
            let JSONdata = JSON.parse(data.toString());
            if (JSONdata.hasOwnProperty('status') && JSONdata.status === 'ready') {
                vscode.window.showInformationMessage(`${JSONdata.status}`);
            }
            else if (JSONdata.hasOwnProperty('error')) {
                let treeData = [new SampleNode(JSONdata.error, [])];
                tree.setTree(treeData);
            }
            else {
                let treeData = [new SampleNode(JSONdata[0].input, [])];
                for (let i = 1; i < JSONdata.length; ++i) {
                    treeData.push(new SampleNode(`${i}. ${JSONdata[i].output}`, []));
                }
                tree.setTree(treeData);
                yield self.replaceCode(JSONdata[1]['replace'], JSONdata[1]['cursor']);
            }
        });
    }
    replaceCode(statement, cursor) {
        return __awaiter(this, void 0, void 0, function* () {
            let self = this;
            yield vscode.commands.executeCommand('editor.action.selectAll');
            yield vscode.commands.executeCommand('editor.action.deleteLines');
            yield self.editor.insertText(statement);
            yield self.editor.moveCursor(new vscode.Position(cursor - 1, 0));
            yield vscode.commands.executeCommand('cursorEnd');
        });
    }
    startRecognizer(choice) {
        let self = this;
        let options;
        let tree;
        options = {
            'audio': [
                `${__dirname}/audio.py`,
                `${self.editor.getFileName()}`,
                `${self.editor.getCursorPosition().line + 1}`
            ],
            'dictate_audio': [
                'dictate_audio.py'
            ]
        };
        if (choice === 'audio') {
            this.isListening = true;
            tree = this.suggestTree;
        }
        else {
            tree = this.dictateTree;
        }
        self.recognizer = child_process.spawn('python', options[choice]);
        self.recognizer.stdout.on('data', function (data) {
            try {
                self.handleOutput(tree, data);
            }
            catch (e) {
                console.log(e);
            }
        });
        self.recognizer.on('close', function (code, signal) {
            console.log('program stopped', signal);
            if (signal === null) {
                console.log('respawning');
                self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
                self.startRecognizer('audio');
            }
            else {
                self.setStatusBarBtn('💬 Listen', 'extension.listen');
            }
        });
        self.recognizer.stderr.on('data', function (data) {
            console.log(`error: ${data}`);
        });
        self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
    }
    stopRecognizer() {
        this.recognizer.kill('SIGKILL');
        this.setStatusBarBtn('💬 Listen', 'extension.listen');
        this.isDictation = this.isListening = false;
    }
    dictate() {
        this.isDictation = (this.isDictation) ? false : true;
        if (this.isDictation) {
            if (this.isListening) {
                this.stopRecognizer();
            }
            this.startRecognizer('dictate_audio');
            this.setStatusBarBtn('✖️️ Stop Dictation', 'extension.stop');
        }
        else {
            this.stopRecognizer();
        }
    }
}
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
        console.log(tree);
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
            console.log(pos.line, pos.character, text);
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
    getFileName() {
        if (vscode.window.activeTextEditor) {
            const editor = vscode.window.activeTextEditor;
            return editor.document.uri.fsPath;
        }
        return '';
    }
}
//# sourceMappingURL=extension.js.map
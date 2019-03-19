// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as child_process from 'child_process';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	let statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
	statusBarItem.text = '💬 Listen';
	statusBarItem.command = 'extension.listen';
	statusBarItem.show();

	let recognizer: any;

	let sampleTree = new SampleTree();

	vscode.window.createTreeView('suggestions', {treeDataProvider: sampleTree});

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
		
		recognizer.stdout.on('data', function(data: string) {
			let JSONdata = JSON.parse(data);
			console.log(JSONdata);
			if (JSONdata.hasOwnProperty('status') && JSONdata.status === 'ready') {
				vscode.window.showInformationMessage(`${JSONdata.status}`);
			} else if (JSONdata.hasOwnProperty('error')) {
				let tree = [new SampleNode(JSONdata.input, []), new SampleNode(JSONdata.error, [])];
				sampleTree.setTree(tree);
			} else {
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

		recognizer.stderr.on('data', function(data: string) {
			console.log(`error: ${data}`);
		});

		recognizer.on('close', function(code: string) {
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

// this method is called when your extension is deactivated
export function deactivate() {}

class SampleNode extends vscode.TreeItem{
	private children: SampleNode[];
	public label: string;
	constructor(label: string, children: SampleNode[]) {
		super(label);
		this.children = children;
		this.label = label;
	}
	public getChildren() {
		return this.children;
	}
}

class SampleTree implements vscode.TreeDataProvider<vscode.TreeItem> {
	private tree: SampleNode[];
	private _onDidChangeTreeData: vscode.EventEmitter<any> = new vscode.EventEmitter<any>();
	readonly onDidChangeTreeData: vscode.Event<any> = this._onDidChangeTreeData.event;

	constructor() {
		this.tree = [];
	}

	public getTreeItem(element: SampleNode): vscode.TreeItem {
		return {
			label: element.label
		};
	}
	public getChildren(element: SampleNode): SampleNode[] {
		return element ? element.getChildren() : this.tree;
	}

	public setTree(tree: SampleNode[]) {
		this.tree = tree;
		this._onDidChangeTreeData.fire();
	}
}

class Editor {
	constructor() {

	}

	public insertText(text: string) {
		if (vscode.window.activeTextEditor !== undefined) {
			let pos = new vscode.Position(0, 0);
			const editor = vscode.window.activeTextEditor;
			if (editor.selection.isEmpty) {
				pos = editor.selection.active;
			}
			console.log(pos.line, pos.character);
			editor.edit(
				editBuilder => {
					editBuilder.insert(pos, text);
				}
			);
		}
	}

	public moveCursor(position: vscode.Position) {
		if (vscode.window.activeTextEditor !== undefined) {
			const editor = vscode.window.activeTextEditor;

			var newSelection = new vscode.Selection(position, position);
			editor.selection = newSelection;
		}
	}

	public getCursorPosition(): vscode.Position {
		if (vscode.window.activeTextEditor) {
			const editor = vscode.window.activeTextEditor;
			const position = editor.selection.active;

			return position;
		}
		return new vscode.Position(0, 0);
	}
}

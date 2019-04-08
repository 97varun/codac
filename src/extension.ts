// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as child_process from 'child_process';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
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

// this method is called when your extension is deactivated
export function deactivate() {}

class Codac {
	private statusBarItem: vscode.StatusBarItem;
	private suggestTree: SampleTree; 
	private dictateTree: SampleTree;
	private errorTree: SampleTree;
	private editor: Editor;
	private recognizer: child_process.ChildProcess;
	private isDictation: boolean;
	private isListening: boolean;

	constructor() {
		this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 10);
		this.setStatusBarBtn('💬 Listen', 'extension.listen');

		this.suggestTree = new SampleTree();
		this.dictateTree = new SampleTree();
		this.errorTree = new SampleTree();
		vscode.window.createTreeView('suggestions', {treeDataProvider: this.suggestTree});
		vscode.window.createTreeView('dictation', {treeDataProvider: this.dictateTree});
		vscode.window.createTreeView('errors', {treeDataProvider: this.errorTree});

		this.editor = new Editor();
		this.recognizer = Object();

		this.isDictation = false;
		this.isListening = false;
	}

	public setStatusBarBtn(text: string, command: string) {
		this.statusBarItem.text = text;
		this.statusBarItem.command = command;
		this.statusBarItem.show();
	}

	public async handleOutput(tree: SampleTree, data: any) {
		let self = this;
		console.log(data.toString(), data.toString().length);
		let JSONdata = JSON.parse(data.toString());
		if (JSONdata.hasOwnProperty('status') && JSONdata.status === 'ready') {
			vscode.window.showInformationMessage(`${JSONdata.status}`);
		} else if (JSONdata.hasOwnProperty('error')) {
			let treeData = [new SampleNode(JSONdata.error, [])];
			tree.setTree(treeData);
		} else {
			let treeData = [new SampleNode(JSONdata[0].input, [])];
			for (let i = 1; i < JSONdata.length; ++i) {
				treeData.push(new SampleNode(`${i}. ${JSONdata[i].output}`, []));
			}
			tree.setTree(treeData);
			await self.replaceCode(JSONdata[1]['replace'], JSONdata[1]['cursor']);
		}
	}

	public async replaceCode(statement: string, cursor: number) {
		let self = this;		
		await vscode.commands.executeCommand('editor.action.selectAll');
		await vscode.commands.executeCommand('editor.action.deleteLines');
		await self.editor.insertText(statement);
		await self.editor.moveCursor(new vscode.Position(cursor - 1, 0));
		await vscode.commands.executeCommand('cursorEnd');
	}

	public startRecognizer(choice: string) {
		let self = this;
		let options: any;
		let tree: SampleTree;
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
		} else {
			tree = this.dictateTree;
		}

		self.recognizer = child_process.spawn(
			'python',
			options[choice]
		);
	
		self.recognizer.stdout.on('data', function(data: string) {
			try {
				self.handleOutput(tree, data);
			} catch(e) {
				console.log(e);
			}
		});
	
		self.recognizer.on('close', function(code: number, signal: string) {
			console.log('program stopped', signal);
			if (signal === null) {
				console.log('respawning');
				self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
				self.startRecognizer('audio');
			} else {
				self.setStatusBarBtn('💬 Listen', 'extension.listen');
			}
		});
	
		self.recognizer.stderr.on('data', function(data: string) {
			console.log(`error: ${data}`);
		});

		self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
	}

	public stopRecognizer() {
		this.recognizer.kill('SIGKILL');
		this.setStatusBarBtn('💬 Listen', 'extension.listen');
		this.isDictation = this.isListening = false;
	}

	public dictate() {
		this.isDictation = (this.isDictation) ? false : true;
		if (this.isDictation) {
			if (this.isListening) {
				this.stopRecognizer();
			}
			this.startRecognizer('dictate_audio');
			this.setStatusBarBtn('✖️️ Stop Dictation', 'extension.stop');
		} else {
			this.stopRecognizer();			
		}
	}
}

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
		console.log(tree);
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
			console.log(pos.line, pos.character, text);
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

	public getFileName(): string {
		if (vscode.window.activeTextEditor) {
			const editor = vscode.window.activeTextEditor;
			return editor.document.uri.fsPath;
		}
		return '';
	}
}

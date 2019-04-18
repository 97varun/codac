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

	public async navigate(sem: any) {
		let self = this;
		// let cur_cursor = self.editor.getCursorPosition(); //cur_cursor = line,character
		try {
			//move across line[s]
			if (sem.hasOwnProperty('construct') && sem.construct === 'line') {
				if (sem.hasOwnProperty('direction') ) {
					sem.direction = (sem.direction === 'next') ? "down" : sem.direction;
					sem.direction = (sem.direction === 'back') ? "up" : sem.direction;
					sem.direction = (sem.direction === 'start') ? "wrappedLineFirstNonWhitespaceCharacter" : sem.direction;
					sem.direction = (sem.direction === 'end') ? "wrappedLineLastNonWhitespaceCharacter" : sem.direction;
				}
				if (!(sem.hasOwnProperty('value'))) {
					sem.value = 1;
				}
				if (!(sem.hasOwnProperty('direction'))) {
					self.editor.moveCursor(new vscode.Position(sem.value - 1, 0));
					await vscode.commands.executeCommand('cursorEnd');
					return;									
				}
				vscode.commands.executeCommand("cursorMove", {
					to: sem.direction,
					by: "line",
					select: false,
					value: sem.value
				});
			}
			//move character by character
			else if (sem.hasOwnProperty('construct') && sem.construct === 'character') {
				if (sem.hasOwnProperty('direction') ) {
					sem.direction = (sem.direction === 'next') ? "right" : sem.direction;
					sem.direction = (sem.direction === 'back') ? "left" : sem.direction;
				}
				if (!(sem.hasOwnProperty('value'))) {
					sem.value = 1;
				}
				if (!(sem.hasOwnProperty('direction'))) {
					sem.direction = "right";						
				}
				vscode.commands.executeCommand("cursorMove", {
					to: sem.direction,
					by: "character",
					select: false,
					value: sem.value
				});
			}
			//for goto func types - goto visible window's first line in a function.
			else {
				vscode.commands.executeCommand("cursorMove", {
					to: "viewPortTop",
					by: "line",
					select: false,
					value: 1
				});
			}
		} catch (error) {
			let obj2 = {'input': 'NavError', 'Output':'Navigation Error'};
			this.handleError(Object.assign({}, error, obj2));
			}
	}

	// append to errors tree
	public insertError(message: string) {
		let tree = this.errorTree;
		let idx = tree.getLength() + 1;
		let msg = message.split('\n');
		let treeData = [new SampleNode(idx +'. '+ msg[0], [])];
		for (let index = 2; index <= msg.length; index++) {
			idx += 1;
			treeData.push(new SampleNode(idx +'. ' + msg[index], []));	
		}			
        tree.updateTree(treeData);
    }
	
	public async handleError(sem: any) {
		let s_tree = this.suggestTree;
		if (sem.hasOwnProperty('input')) {
			let treeData = [new SampleNode('-> ' + sem.input, [])];
			if (sem.hasOwnProperty('output')) {
				treeData.push(new SampleNode('    1. ' + sem.output.toString(), []));
			}
			s_tree.setTree(treeData);
		}
		if (sem.hasOwnProperty('error')) {
			this.insertError(sem.error);
		}
    }
	
	public async handleOutput(tree: SampleTree, data: any) {
		let self = this;
		console.log("HandleOp func:");
		console.log(data.toString(), data.toString().length);
		let JSONdata = JSON.parse(data.toString());
		if (JSONdata.hasOwnProperty('status') && JSONdata.status === 'ready') {
			vscode.window.showInformationMessage(`${JSONdata.status}`);
		} else if (JSONdata.hasOwnProperty('error')) {
			this.handleError(JSONdata);
		} else if (JSONdata.hasOwnProperty('audio_type') && JSONdata.audio_type === 'dictation') {
			let treeData = [new SampleNode(`${JSONdata.output}`, [])];
			tree.updateTree(treeData);
		} else{
			let treeData = [new SampleNode('-> ' + JSONdata[0].input, [])];
			if (JSONdata[1].hasOwnProperty('error')) {
				this.handleError(Object.assign({}, JSONdata[0], JSONdata[1]));
				return;
			}
			else if (JSONdata[1].hasOwnProperty('request') && JSONdata[1]['request'] === 'navigate'){
				self.navigate(JSONdata[1]);
			}
			else{
				for (let i = 1; i < JSONdata.length; ++i) {
					treeData.push(new SampleNode(`    ${i}. ${JSONdata[i].output}`, []));
				}
				await self.replaceCode(JSONdata[1]['replace'], JSONdata[1]['cursor']);	
			}
			tree.setTree(treeData);
		}
	}

	public print_dictation_op(){
		let childrenLabel = this.dictateTree.getChildren(undefined).map((child) => {
			return child.label;
		});
		let stringToInsert = childrenLabel.slice(1).join(' ');
		this.editor.insertText(stringToInsert);
	}

	public async replaceCode(statement: string, cursor: number) {
		let self = this;
		if (statement) {
			await vscode.commands.executeCommand('editor.action.selectAll');
			await vscode.commands.executeCommand('editor.action.deleteLines');
			await self.editor.insertText(statement);
			await self.editor.moveCursor(new vscode.Position(cursor - 1, 0));
			await vscode.commands.executeCommand('cursorEnd');				
		}
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
				`${__dirname}/dictate_audio.py`
			]
		};
		if (choice === 'audio') {
			this.isListening = true;
			tree = this.suggestTree;
			self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
		} else {
			tree = this.dictateTree;
			let treeData = [new SampleNode('Your String :', [])];
			tree.setTree(treeData);
			self.setStatusBarBtn('✖️️ Stop Dictation', 'extension.dictation');
		}

		self.recognizer = child_process.spawn(
			'python',
			options[choice]
		);
	
		self.recognizer.stdout.on('data', function(data: string) {
			try {
				self.handleOutput(tree, data);
			} catch(e) {
				console.log('Could not handle output.');
				console.log(e);
				self.insertError('Recognizer could not handle output. Data : ' + data);
			}
		});
	
		self.recognizer.on('close', function(code: number, signal: string) {
			console.log('Program stopped. Signal : ', signal);
			if (signal === null) {
				console.log('Respawning');
				self.setStatusBarBtn('✖️️ Stop', 'extension.stop');
				self.startRecognizer('audio');
			} else {
				self.setStatusBarBtn('💬 Listen', 'extension.listen');
			}
		});
	
		self.recognizer.stderr.on('data', function(data: string) {
			console.log(`ERROR: ${data}`);
			console.log(data);
			// console.log(data.toString());
			self.insertError('On Recognizer stderr :' + data.toString());
		});

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
		} else {
			this.print_dictation_op();
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
	public getChildren(element?: SampleNode): SampleNode[] {
		return element ? element.getChildren() : this.tree;
	}

	public setTree(tree: SampleNode[]) {
		this.tree = tree;
		this._onDidChangeTreeData.fire();		
		// console.log(tree);
	}

	public updateTree(tree: SampleNode[]) {
		this.tree.push(...tree);
		this._onDidChangeTreeData.fire();
		// console.log(tree);
	}

	public getLength(): number {
		return this.tree.length;
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
			console.log("InsertText Func : ");
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

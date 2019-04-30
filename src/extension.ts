import * as vscode from 'vscode';
import * as child_process from 'child_process';

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
	let replace = vscode.commands.registerCommand('extension.replace', (replace, cursor) => {
		codac.replaceCode(replace, cursor);
	});

	context.subscriptions.push(listen);
	context.subscriptions.push(stop);
	context.subscriptions.push(dictation);
	context.subscriptions.push(replace);
}

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

	public async edit(sem: any) {
		let curCursorPos: vscode.Position;
		switch (sem['construct']) {
			case 'undo':
				vscode.commands.executeCommand('undo');
				break;
			case 'redo':
				vscode.commands.executeCommand('redo');
				break;
			case 'copy':
				curCursorPos = this.editor.getCursorPosition();
				this.editor.selectLines(sem['value'], sem['direction'], sem['is_range']);
				await vscode.commands.executeCommand('editor.action.clipboardCopyAction');
				this.editor.moveCursor(curCursorPos);
				break;
			case 'paste':
				vscode.commands.executeCommand('editor.action.clipboardPasteAction');
				break;
			case 'delete':
				curCursorPos = this.editor.getCursorPosition();
				this.editor.selectLines(sem['value'], sem['direction'], sem['is_range']);
				await vscode.commands.executeCommand('editor.action.deleteLines');
				this.editor.moveCursor(curCursorPos);
				break;
		}
	}

	public async execute(sem: any) {
		let filename: string = this.editor.getFileName();
		let lastIndex = filename.lastIndexOf('\\');
		if (lastIndex === -1) {
			lastIndex = filename.lastIndexOf('/');
		}
		let options = {cwd: (filename.slice(0, lastIndex))};
		console.log(options);
		let terminal: vscode.Terminal = vscode.window.createTerminal(
			options
		);
		filename = filename.replace(/^.*[\\\/]/, '').slice(0, -2);
		terminal.show(true);
		if (sem['construct'] === '0') {
			terminal.sendText(`gcc ${filename}.c -o ${filename}`, true);
			terminal.sendText(`${filename}.exe`, true);
		} else if (sem['construct'] === '1') {
			terminal.sendText(`gcc ${filename}.c -o ${filename}`, true);
		} else {
			terminal.sendText(`${filename}.exe`, true);
		}
	}

	// append to errors tree
	public insertError(message: string) {
		let tree = this.errorTree;
		let idx = tree.getLength() + 1;
		let treeData = [{'error': (`${idx}. ${message}`), 'children': []}];
        tree.updateTree(treeData);
	}
	
	public async handleError(sem: any) {
		if (sem.hasOwnProperty('input')) {
			let treeData: any = [{'input': `${sem.input}`, 'children': []}];
			if (sem.hasOwnProperty('output')) {
				treeData[0].children = [{'output': `1. ${sem.output}`, 'children': []}];
			}
			this.suggestTree.setTree(treeData);
		}
		if (sem.hasOwnProperty('error')) {
			this.insertError(sem.error);
		}
		child_process.exec(
			`python ${__dirname}/play_sound.py ${__dirname}/../media/${sem.output}.mp3`,
			{},
			function (err) {
				console.log(err);
			}
		);
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
			let treeData = [{output: JSONdata.output, children: []}];
			tree.updateTree(treeData);
		} else{
			// [{"input": "..."}, {"output": "...", "replace": "..."}, ...]
			// [{"input": "..."}, {"error": "..."}]
			let treeData: any = [{...JSONdata[0], children: []}];
			if (JSONdata[1].hasOwnProperty('error')) {
				this.handleError(Object.assign({}, JSONdata[0], JSONdata[1]));
				return;
			} else if (JSONdata[1].hasOwnProperty('request') && JSONdata[1]['request'] === 'navigate') {
				self.navigate(JSONdata[1]);
			} else if (JSONdata[1].request === 'edit') {
				self.edit(JSONdata[1]);
			} else if (JSONdata[1].request === 'systemCommand') {
				self.execute(JSONdata[1]);
			} else {
				treeData[0].children = JSONdata.slice(1).map(
					(elem: any, idx: number) => {
						return {'output': `${idx + 1}. ${elem.output}`,
								'replace': elem.replace,
								'cursor': elem.cursor,
								children: []};
					}
				);
				await self.replaceCode(JSONdata[1]['replace'], JSONdata[1]['cursor']);
			}
			tree.setTree(treeData);
		}
	}

	public printDictationOp() {
		let childrenLabel = this.dictateTree.getChildren(undefined).map(
			(child) => child.label
		);
		let stringToInsert = childrenLabel.slice(1).join(' ');
		this.editor.insertText(stringToInsert);
	}

	public async replaceCode(statement: string, cursor: number) {
		let self = this;
		if (statement) {
			await vscode.commands.executeCommand('editor.action.selectAll');
			// await vscode.commands.executeCommand('editor.action.deleteLines');
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
			let treeData = [{input: 'Your String:', children: []}]
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
			this.printDictationOp();
			this.stopRecognizer();			
		}
	}
}

class SampleTree implements vscode.TreeDataProvider<vscode.TreeItem> {
	private tree: any[];
	private _onDidChangeTreeData: vscode.EventEmitter<any> = new vscode.EventEmitter<any>();
	readonly onDidChangeTreeData: vscode.Event<any> = this._onDidChangeTreeData.event;

	constructor() {
		this.tree = [];
	}

	public getTreeItem(element: any): vscode.TreeItem {
		let treeItem = new vscode.TreeItem('');
		if (element.hasOwnProperty('error')) {
			treeItem.label = element.error;
		} else if (element.hasOwnProperty('output')) {
			treeItem.label = element.output;
			if (element.hasOwnProperty('replace')) {
				treeItem.command = {
					command: 'extension.replace',
					title: '',
					arguments: [element.replace, element.cursor]
				}
			}
		} else if (element.hasOwnProperty('input')) {
			treeItem.label = element.input;
			treeItem.collapsibleState = vscode.TreeItemCollapsibleState.Expanded;
		}
		return treeItem;
	}

	public getChildren(element?: any): any[] {
		return element ? element.children : this.tree;
	}

	public setTree(tree: any[]) {
		this.tree = tree;
		this._onDidChangeTreeData.fire();		
	}

	public updateTree(tree: any[]) {
		this.tree.push(...tree);
		this._onDidChangeTreeData.fire();
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
				console.log('insertText: insert');
				pos = editor.selection.active;
				editor.edit(
					editBuilder => {
						editBuilder.insert(pos, text);
					}
				);
			} else {
				console.log('insertText: replace');
				editor.edit(
					editBuilder => {
						editBuilder.replace(editor.selection, text);
					}
				);
			}
		}
	}

	public moveCursor(position: vscode.Position) {
		if (vscode.window.activeTextEditor !== undefined) {
			const editor = vscode.window.activeTextEditor;
			var newSelection = new vscode.Selection(position, position);
			editor.selection = newSelection;
			editor.selections = [newSelection];
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

	public addSelection(selection: vscode.Selection) {
		if (vscode.window.activeTextEditor) {
			const editor = vscode.window.activeTextEditor;
			if (editor.selection.isEmpty) {
				editor.selection = selection;
			} else {
				console.log(editor.selections);
				let selections = editor.selections;
				selections.push(selection);
				editor.selections = selections;
				console.log(editor.selections);
			}
		}
	}

	public getLineRange(line: number): vscode.Range {
		if (vscode.window.activeTextEditor) {
			const editor = vscode.window.activeTextEditor;
			return editor.document.lineAt(line).range;
		}
		const pos = new vscode.Position(0, 0);
		return new vscode.Range(pos, pos);
	}

	public selectLines(val: number[], direction: string, is_range: boolean) {
		if (is_range) {
			let newVal = [];
			for (var i = val[0]; i <= val[1]; ++i) {
				newVal.push(i);
			}
			val = newVal;
		}
		if (direction) {
			let line = this.getCursorPosition().line + 1;
			switch(direction) {
				case 'current':
					val = [line]
					break;
				case 'next':
					val = [line + 1]
					break;
				case 'previous':
				case 'last':
					val = [line - 1]

			}
		}
		val.forEach((elem: number) => {
			let range = this.getLineRange(elem - 1);
			this.addSelection(
				new vscode.Selection(range.start, range.end)
			);
		});
	}
}

from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox, QTabWidget, QHBoxLayout, QTextEdit, QLineEdit, QLabel, QSplitter
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QTextCursor
from src.ui.code_editor import CodeEditor
from src.core.registry import NodeRegistry
import traceback
import sys
import subprocess
import os

class ScriptingConsole(QDockWidget):
    def __init__(self, main_window):
        super().__init__("Scripting Console", main_window)
        self.main_window = main_window
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        
        self.tabs = QTabWidget()
        self.setWidget(self.tabs)
        
        self._init_script_tab()
        self._init_git_tab()

    def _init_script_tab(self):
        self.script_widget = QWidget()
        layout = QVBoxLayout(self.script_widget)
        
        # Splitter for Editor and Debug Output
        splitter = QSplitter(Qt.Horizontal)
        
        # Editor Side
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0,0,0,0)
        
        self.editor = CodeEditor()
        self.editor.setPlainText("""# Vibrante-Node Scripting API
# Available objects: app, scene, registry
# Methods: 
#   scene.add_node_by_name(node_id, (x, y)) -> NodeWidget
#   scene.find_node_by_name(name) -> NodeWidget
#   scene.connect_nodes(from_node, from_port, to_node, to_port) -> Edge
#   node.set_parameter(name, value) -> Updates UI & logic

print('Hello from Scripting Console!')

# Example: Automate building a simple math workflow
# n1 = scene.add_node_by_name("add_integers", (100, 100))
# n2 = scene.add_node_by_name("console_print", (400, 100))
# if n1 and n2:
#     n1.set_parameter('a', 10)
#     n1.set_parameter('b', 20)
#     scene.connect_nodes(n1, "result", n2, "data")
""")
        # Initialize rich completion
        self.editor.set_completer_list([
            "app", "scene", "registry", "print", 
            "add_node_by_name", "connect_nodes", "find_node_by_name", "set_parameter",
            "NodeWidget", "Edge", "NodeRegistry", "execute"
        ])
        
        editor_layout.addWidget(self.editor)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run Script")
        self.run_btn.setStyleSheet("background-color: #50fa7b; color: black; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_script)
        
        self.debug_btn = QPushButton("Debug Trace")
        self.debug_btn.setToolTip("Run with line-by-line highlighting (slow)")
        self.debug_btn.setStyleSheet("background-color: #ffb86c; color: black;")
        self.debug_btn.clicked.connect(self.debug_script)
        
        self.clear_btn = QPushButton("Clear Output")
        self.clear_btn.clicked.connect(lambda: self.debug_output.clear())
        
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.debug_btn)
        btn_layout.addWidget(self.clear_btn)
        editor_layout.addLayout(btn_layout)
        
        splitter.addWidget(editor_container)
        
        # Debug Output Side
        debug_container = QWidget()
        debug_layout = QVBoxLayout(debug_container)
        debug_layout.setContentsMargins(0,0,0,0)
        debug_layout.addWidget(QLabel("Debug/Variables:"))
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setStyleSheet("background-color: #282a36; color: #f8f8f2; font-family: Consolas;")
        debug_layout.addWidget(self.debug_output)
        splitter.addWidget(debug_container)
        
        # Set splitter ratio
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
        self.tabs.addTab(self.script_widget, "Script Editor")

    def _init_git_tab(self):
        self.git_widget = QWidget()
        layout = QVBoxLayout(self.git_widget)
        
        # Status View
        self.git_status = QTextEdit()
        self.git_status.setReadOnly(True)
        self.git_status.setStyleSheet("background-color: #282a36; color: #f8f8f2; font-family: Consolas;")
        layout.addWidget(QLabel("Git Status:"))
        layout.addWidget(self.git_status)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.refresh_git_btn = QPushButton("Refresh Status")
        self.refresh_git_btn.clicked.connect(self._refresh_git_status)
        ctrl_layout.addWidget(self.refresh_git_btn)
        
        self.stage_all_btn = QPushButton("Stage All")
        self.stage_all_btn.clicked.connect(lambda: self._run_git(["add", "."]))
        ctrl_layout.addWidget(self.stage_all_btn)
        
        layout.addLayout(ctrl_layout)
        
        # Commit
        commit_layout = QHBoxLayout()
        self.commit_msg = QLineEdit()
        self.commit_msg.setPlaceholderText("Commit message...")
        commit_btn = QPushButton("Commit")
        commit_btn.clicked.connect(self._git_commit)
        commit_layout.addWidget(self.commit_msg)
        commit_layout.addWidget(commit_btn)
        layout.addLayout(commit_layout)
        
        # Push/Pull
        sync_layout = QHBoxLayout()
        pull_btn = QPushButton("Pull")
        pull_btn.clicked.connect(lambda: self._run_git(["pull"]))
        push_btn = QPushButton("Push")
        push_btn.clicked.connect(lambda: self._run_git(["push"]))
        sync_layout.addWidget(pull_btn)
        sync_layout.addWidget(push_btn)
        layout.addLayout(sync_layout)
        
        self.tabs.addTab(self.git_widget, "Source Control (Git)")
        
        # Initial status check
        QTimer.singleShot(1000, self._refresh_git_status)

    def run_script(self):
        self._execute(debug=False)

    def debug_script(self):
        self._execute(debug=True)

    def _execute(self, debug=False):
        script = self.editor.toPlainText()
        if not script.strip(): return
        
        self.debug_output.clear()
        
        # Prepare context
        context = {
            "app": self.main_window,
            "scene": self.main_window.get_current_scene(),
            "registry": NodeRegistry,
            "print": self.console_print,
            "git": self._git_wrapper()
        }
        
        try:
            if debug:
                self.console_print("Starting Debug Trace...")
                sys.settrace(self._trace_calls)
                exec(script, context)
                sys.settrace(None)
                self.console_print("Debug Finished.")
                self.editor.highlight_current_line() # Reset highlight
            else:
                exec(script, context)
                self.main_window.log_panel.log("Script executed successfully.", "success")
                
            # Show locals in debug panel
            self.debug_output.append("\n--- Final Variables ---")
            for k, v in context.items():
                if k not in ["app", "scene", "registry", "print", "git", "__builtins__"]:
                    self.debug_output.append(f"{k}: {repr(v)}")
                    
        except Exception as e:
            sys.settrace(None)
            error_msg = traceback.format_exc()
            self.main_window.log_panel.log(f"Script Error:\n{error_msg}", "error")
            self.debug_output.append(f"\nERROR:\n{error_msg}")

    def _trace_calls(self, frame, event, arg):
        if event == 'line':
            lineno = frame.f_lineno
            # Highlight line in editor
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, n=lineno-1)
            self.editor.setTextCursor(cursor)
            self.editor.highlight_current_line()
            
            # Simple delay to visualize stepping (blocking, but okay for this proof of concept)
            # For a real non-blocking debugger, we'd need a separate thread and a message loop
            QTimer.singleShot(0, lambda: None) 
            # In a single threaded exec, we can't easily sleep without freezing UI.
            # So we just highlight. Use print() in script to see steps in debug output.
            
        return self._trace_calls

    def console_print(self, *args):
        msg = " ".join(map(str, args))
        self.main_window.log_panel.log(f"[SCRIPT] {msg}", "info")
        self.debug_output.append(f"> {msg}")

    def _git_wrapper(self):
        class Git:
            def status(self): return subprocess.getoutput("git status")
            def commit(self, msg): return subprocess.getoutput(f'git commit -m "{msg}"')
            def push(self): return subprocess.getoutput("git push")
            def pull(self): return subprocess.getoutput("git pull")
        return Git()

    def _run_git(self, args):
        try:
            result = subprocess.run(["git"] + args, capture_output=True, text=True, cwd=os.getcwd())
            output = result.stdout + result.stderr
            self.git_status.setText(output)
            self.console_print(f"Git {' '.join(args)}: {result.returncode == 0}")
            if "status" not in args:
                self._refresh_git_status()
        except Exception as e:
            self.git_status.setText(f"Error running git: {e}")

    def _refresh_git_status(self):
        self._run_git(["status"])

    def _git_commit(self):
        msg = self.commit_msg.text()
        if not msg:
            QMessageBox.warning(self, "Git", "Please enter a commit message.")
            return
        self._run_git(["commit", "-m", msg])
        self.commit_msg.clear()

import json
import threading
from src.utils.qt_compat import QtWidgets, QtCore, Signal, invoke_method

QWidget = QtWidgets.QWidget
QVBoxLayout = QtWidgets.QVBoxLayout
QTextEdit = QtWidgets.QTextEdit
QLineEdit = QtWidgets.QLineEdit
QPushButton = QtWidgets.QPushButton
QLabel = QtWidgets.QLabel
QMessageBox = QtWidgets.QMessageBox
QHBoxLayout = QtWidgets.QHBoxLayout

Qt = QtCore.Qt
from src.utils.config_manager import config
import google.generativeai as genai

class GeminiChatWidget(QWidget):
    node_generated = Signal(dict) # Signal emitted when Gemini generates a node definition

    def __init__(self, parent=None):
        super().__init__(parent)
        self.get_context_callback = None # Callback to get current node definition
        self._init_ui()
        self._setup_gemini()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Gemini Node Architect:"))
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Describe the node you want to create...")
        self.chat_input.returnPressed.connect(self._send_prompt)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_prompt)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def _setup_gemini(self):
        api_key = config.get_gemini_api_key()
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self.chat = self.model.start_chat(history=[])
            
            # System instructions
            self.system_prompt = """
            You are an expert node developer for the Vibrante-Node framework.
            Your task is to help the user create custom nodes by generating the node definition in JSON format.
            
            The node definition must follow this structure:
            {
                "node_id": "slug_name",
                "name": "Display Name",
                "description": "Short description",
                "category": "Math/Logic/etc",
                "icon_path": "icons/gear.svg",
                "inputs": [
                    {"name": "input1", "type": "int", "widget_type": "int"},
                    {"name": "exec_in", "type": "exec"}
                ],
                "outputs": [
                    {"name": "result", "type": "int"},
                    {"name": "exec_out", "type": "exec"}
                ],
                "python_code": "..."
            }
            
            Rules for python_code:
            1. It must inherit from BaseNode.
            2. It must have an __init__ that calls super().__init__() and adds ports using self.add_input, self.add_output, self.add_exec_input, self.add_exec_output.
            3. It must have an async def execute(self, inputs) method.
            4. It must have a register_node function that returns the node class.
            
            Example python_code:
            ```python
            from src.nodes.base import BaseNode
            class MyNode(BaseNode):
                name = "My Node"
                def __init__(self):
                    super().__init__()
                    self.add_input("a", "int", widget_type="int")
                    self.add_output("res", "int")
                async def execute(self, inputs):
                    return {"res": inputs.get("a", 0) * 2}
            def register_node():
                return MyNode
            ```
            
            When the user describes a node, respond with the JSON definition enclosed in ```json ... ``` blocks.
            If the user provides a "Current Node State", apply their requested changes to that state and return the FULL updated JSON.
            You can also provide explanations outside the block.
            """
            # We'll send this as the first hidden message if possible, or just keep it in mind.
            # For now, let's just prepend it to the first user message if chat is empty.
        else:
            self.chat_display.append("<font color='red'>Gemini API Key not set. Go to Help -> Link to Gemini.</font>")

    def _send_prompt(self):
        api_key = config.get_gemini_api_key()
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", "Please set your Gemini API key in Help -> Link to Gemini.")
            return

        prompt = self.chat_input.text().strip()
        if not prompt:
            return

        # Add context to prompt if available
        context_str = ""
        if self.get_context_callback:
            context = self.get_context_callback()
            if context:
                context_str = f"\n\n[Current Node State]\n```json\n{json.dumps(context, indent=2)}\n```\n"

        self.chat_display.append(f"<b>You:</b> {prompt}")
        self.chat_input.clear()
        self.chat_input.setEnabled(False)
        self.send_btn.setEnabled(False)

        threading.Thread(target=self._get_gemini_response, args=(prompt, context_str), daemon=True).start()

    def _get_gemini_response(self, prompt, context_str=""):
        try:
            full_prompt = prompt + context_str
            if not hasattr(self, 'initialized') or not self.initialized:
                full_prompt = self.system_prompt + "\n\nUser request: " + prompt + context_str
                self.initialized = True
            
            response = self.chat.send_message(full_prompt)
            text = response.text
            
            # Extract JSON if present
            import re
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    node_def = json.loads(json_str)
                    self.node_generated.emit(node_def)
                except Exception as e:
                    print(f"Error parsing Gemini JSON: {e}")

            # Update UI from thread
            self._append_to_chat(text)
        except Exception as e:
            self._append_to_chat(f"<font color='red'>Error: {str(e)}</font>")
        finally:
            self._enable_input()

    def _append_to_chat(self, text):
        invoke_method(self.chat_display, "append", Qt.QueuedConnection, f"<b>Gemini:</b> {text}")

    def _enable_input(self):
        invoke_method(self.chat_input, "setEnabled", Qt.QueuedConnection, True)
        invoke_method(self.send_btn, "setEnabled", Qt.QueuedConnection, True)

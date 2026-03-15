from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QPlainTextEdit, QPushButton, QLabel, QSplitter, QWidget, QMessageBox, QFileDialog, QComboBox
from PyQt5.QtCore import Qt, QTimer
import os
import ast
from src.core.loader import ScriptLoader
from src.utils.highlighter import PythonHighlighter
from src.core.registry import NodeRegistry
from src.core.models import NodeDefinitionJSON, PortModel
from src.ui.code_editor import CodeEditor
from src.ui.gemini_chat import GeminiChatWidget

AVAILABLE_WIDGETS = ["", "text", "text_area", "int", "float", "bool", "dropdown", "slider", "file"]
AVAILABLE_TYPES = ["any", "int", "float", "string", "bool", "list", "dict"]

class NodeBuilderDialog(QDialog):
    def __init__(self, parent=None, editing_node_id=None):
        super().__init__(parent)
        self.editing_node_id = editing_node_id
        self.setWindowTitle("Node Builder")
        self.resize(1000, 800)
        
        self._is_syncing = False
        
        self._init_ui()
        self.highlighter = PythonHighlighter(self.code_edit.document())
        
        # Debounce timer for code parsing
        self.sync_timer = QTimer()
        self.sync_timer.setSingleShot(True)
        self.sync_timer.timeout.connect(self._sync_code_to_ui)
        
        self.code_edit.textChanged.connect(self._on_code_changed)
        self.inputs_table.itemChanged.connect(self._on_table_changed)
        self.outputs_table.itemChanged.connect(self._on_table_changed)
        self.name_edit.textChanged.connect(self._on_metadata_changed)

        if self.editing_node_id:
            self._load_existing_node()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: Configuration
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        config_layout.addWidget(QLabel("Node Name (slug):"))
        self.name_edit = QLineEdit()
        config_layout.addWidget(self.name_edit)
        
        config_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        config_layout.addWidget(self.desc_edit)

        config_layout.addWidget(QLabel("Category:"))
        from src.utils.color_manager import ColorManager
        from PyQt5.QtGui import QPixmap, QIcon
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        
        # Populate with existing categories and their colors
        categories = ColorManager.get_all_categories(NodeRegistry._definitions)
        for cat in categories:
            color = ColorManager.get_category_color(cat)
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            self.category_combo.addItem(QIcon(pixmap), cat)
            
        config_layout.addWidget(self.category_combo)

        config_layout.addWidget(QLabel("Icon Path:"))
        icon_layout = QHBoxLayout()
        self.icon_edit = QLineEdit()
        self.icon_btn = QPushButton("...")
        self.icon_btn.setFixedWidth(30)
        self.icon_btn.clicked.connect(self._select_icon)
        icon_layout.addWidget(self.icon_edit)
        icon_layout.addWidget(self.icon_btn)
        config_layout.addLayout(icon_layout)
        
        # Inputs Table
        config_layout.addWidget(QLabel("Inputs:"))
        self.inputs_table = QTableWidget(0, 4)
        self.inputs_table.setHorizontalHeaderLabels(["Name", "Type", "Widget", "Options (csv)"])
        config_layout.addWidget(self.inputs_table)
        
        in_btn_layout = QHBoxLayout()
        add_in_btn = QPushButton("+ Add Input")
        add_in_btn.clicked.connect(lambda: self._add_row(self.inputs_table))
        remove_in_btn = QPushButton("- Remove Input")
        remove_in_btn.clicked.connect(lambda: self._remove_row(self.inputs_table))
        in_btn_layout.addWidget(add_in_btn)
        in_btn_layout.addWidget(remove_in_btn)
        config_layout.addLayout(in_btn_layout)
        
        # Outputs Table
        config_layout.addWidget(QLabel("Outputs:"))
        self.outputs_table = QTableWidget(0, 4)
        self.outputs_table.setHorizontalHeaderLabels(["Name", "Type", "Widget", "Options (csv)"])
        config_layout.addWidget(self.outputs_table)
        
        out_btn_layout = QHBoxLayout()
        add_out_btn = QPushButton("+ Add Output")
        add_out_btn.clicked.connect(lambda: self._add_row(self.outputs_table))
        remove_out_btn = QPushButton("- Remove Output")
        remove_out_btn.clicked.connect(lambda: self._remove_row(self.outputs_table))
        out_btn_layout.addWidget(add_out_btn)
        out_btn_layout.addWidget(remove_out_btn)
        config_layout.addLayout(out_btn_layout)
        
        # Right Panel: Code Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.addWidget(QLabel("Python Algorithm:"))
        self.code_edit = CodeEditor()
        self.code_edit.setPlainText(self._get_template("MyNode"))
        editor_layout.addWidget(self.code_edit)
        
        # Gemini Panel
        self.gemini_chat = GeminiChatWidget()
        self.gemini_chat.get_context_callback = self.get_node_definition
        self.gemini_chat.node_generated.connect(self._on_gemini_node_generated)
        
        splitter.addWidget(config_widget)
        splitter.addWidget(editor_widget)
        splitter.addWidget(self.gemini_chat)
        layout.addWidget(splitter)
        
        # Bottom Buttons
        button_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test Node")
        self.test_btn.clicked.connect(self.test_node)
        self.save_btn = QPushButton("Save & Register")
        self.save_btn.clicked.connect(self.save_node)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.test_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def _select_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.jpg *.svg)")
        if path:
            self.icon_edit.setText(path)

    def _get_template(self, name):
        return f"""from src.nodes.base import BaseNode

class {name}(BaseNode):
    name = "{name}"
    
    def __init__(self):
        super().__init__()
        self.icon_path = None
        # [AUTO-GENERATED-PORTS-START]
        # [AUTO-GENERATED-PORTS-END]
        
    def on_plug_sync(self, port_name, is_input, other_node, other_port_name):
        # Access the other node's port data using the specific other_port_name
        data = other_node.get_parameter(other_port_name)
        self.log_info(f"Connected to {{other_node.name}} port '{{other_port_name}}'. Data: {{data}}")

    def on_unplug_sync(self, port_name, is_input):
        self.log_info(f"Disconnected {{port_name}}")

    async def on_plug(self, port_name, is_input, other_node, other_port_name):
        pass

    async def on_unplug(self, port_name, is_input):
        pass

    async def execute(self, inputs):
        \"\"\"
        Main execution logic for the node.
        
        :param inputs: A dictionary containing data from connected input ports and widgets.
                       Key: Port Name (string), Value: Port Data (any).
        :return: A dictionary containing data to be sent to output ports.
                 Key: Port Name (string), Value: Port Data (any).
        \"\"\"
        return {{}}

def register_node():
    return {name}
"""

    def _on_code_changed(self):
        if not self._is_syncing:
            self.sync_timer.start(1000) # 1 second debounce

    def _on_table_changed(self):
        if not self._is_syncing:
            self._sync_ui_to_code()

    def _on_metadata_changed(self):
        if not self._is_syncing:
            # Sanitize name: remove any non-alphanumeric/underscore and replace spaces
            raw_name = self.name_edit.text()
            sanitized = "".join(c if c.isalnum() else "_" for c in raw_name)
            
            # Prevent recursive loop
            if sanitized != raw_name:
                pos = self.name_edit.cursorPosition()
                self.name_edit.setText(sanitized)
                self.name_edit.setCursorPosition(pos)
                
            self._sync_ui_to_code()

    def _sync_code_to_ui(self):
        """
        Parses the code using AST and updates the UI tables.
        """
        if self._is_syncing:
            return
            
        self._is_syncing = True
        try:
            code = self.code_edit.toPlainText()
            tree = ast.parse(code)
            
            inputs = {} # name -> type
            outputs = {} # name -> type
            
            class PortVisitor(ast.NodeVisitor):
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Attribute) and node.func.attr in ["add_input", "add_output"]:
                        if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                            port_name = node.args[0].value
                            port_type = "any"
                            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                                port_type = node.args[1].value
                            
                            if node.func.attr == "add_input":
                                inputs[port_name] = port_type
                            else:
                                outputs[port_name] = port_type
                    self.generic_visit(node)

            PortVisitor().visit(tree)
            
            # Convert to list for comparison and update
            input_list = [(k, v) for k, v in inputs.items()]
            output_list = [(k, v) for k, v in outputs.items()]
            
            # Check if actual changes happened before updating table to avoid signal storm
            if self._table_needs_update(self.inputs_table, input_list):
                self._update_table(self.inputs_table, input_list)
            if self._table_needs_update(self.outputs_table, output_list):
                self._update_table(self.outputs_table, output_list)
            
        except Exception as e:
            # Code might be invalid while typing, ignore
            pass
        finally:
            self._is_syncing = False

    def _table_needs_update(self, table, new_ports):
        if table.rowCount() != len(new_ports):
            return True
        for i, (name, p_type) in enumerate(new_ports):
            name_item = table.item(i, 0)
            type_combo = table.cellWidget(i, 1)
            if not name_item or not type_combo: return True
            if name_item.text() != name or type_combo.currentText() != p_type:
                return True
        return False

    def _update_table(self, table, ports):
        table.blockSignals(True)
        table.setRowCount(0)
        for p in ports:
            # p can be (name, type) or PortModel
            name = p.name if hasattr(p, 'name') else p[0]
            p_type = p.type if hasattr(p, 'type') else p[1]
            p_widget = p.widget_type if hasattr(p, 'widget_type') else (p[2] if len(p) > 2 else "")
            p_options = ",".join(p.options) if hasattr(p, 'options') and p.options else ""
            
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(name))
            
            # Use Dropdown for type column
            type_combo = QComboBox()
            type_combo.addItems(AVAILABLE_TYPES)
            type_combo.setCurrentText(p_type or "any")
            type_combo.currentTextChanged.connect(self._sync_ui_to_code)
            table.setCellWidget(row, 1, type_combo)
            
            # Use Dropdown for widget column
            widget_combo = QComboBox()
            widget_combo.addItems(AVAILABLE_WIDGETS)
            widget_combo.setCurrentText(p_widget or "")
            widget_combo.currentTextChanged.connect(self._sync_ui_to_code)
            table.setCellWidget(row, 2, widget_combo)
            
            table.setItem(row, 3, QTableWidgetItem(p_options))
        table.blockSignals(False)

    def _sync_ui_to_code(self):
        """
        Updates the auto-generated ports section in the code.
        """
        if self._is_syncing:
            return
            
        self._is_syncing = True
        try:
            name = self.name_edit.text().strip() or "MyNode"
            code = self.code_edit.toPlainText()
            
            # Prepare injection string
            injection = "        # [AUTO-GENERATED-PORTS-START]\n"
            seen_inputs = set()
            for row in range(self.inputs_table.rowCount()):
                item_name = self.inputs_table.item(row, 0)
                if not item_name: continue
                
                port_name = item_name.text().strip()
                if not port_name or port_name in seen_inputs: continue
                seen_inputs.add(port_name)
                
                type_combo = self.inputs_table.cellWidget(row, 1)
                item_widget_combo = self.inputs_table.cellWidget(row, 2)
                item_options = self.inputs_table.item(row, 3)
                
                type_str = type_combo.currentText() if type_combo else "any"
                w_type = item_widget_combo.currentText() if item_widget_combo else ""
                w_str = f', widget_type="{w_type}"' if w_type else ""
                
                # Options injection if dropdown
                if w_type == "dropdown" and item_options and item_options.text():
                    opts = [o.strip() for o in item_options.text().split(",")]
                    w_str += f', options={opts}'
                injection += f'        self.add_input("{port_name}", "{type_str}"{w_str})\n'
            
            seen_outputs = set()
            for row in range(self.outputs_table.rowCount()):
                item_name = self.outputs_table.item(row, 0)
                if not item_name: continue
                
                port_name = item_name.text().strip()
                if not port_name or port_name in seen_outputs: continue
                seen_outputs.add(port_name)
                
                type_combo = self.outputs_table.cellWidget(row, 1)
                type_str = type_combo.currentText() if type_combo else "any"
                injection += f'        self.add_output("{port_name}", "{type_str}")\n'
                
            injection += "        # [AUTO-GENERATED-PORTS-END]"

            # Replace section using markers
            import re
            pattern = r"(\s*)# \[AUTO-GENERATED-PORTS-START\].*?# \[AUTO-GENERATED-PORTS-END\]"
            if re.search(pattern, code, re.DOTALL):
                code = re.sub(pattern, injection, code, flags=re.DOTALL)
            else:
                # If markers are missing, try to inject after __init__
                init_pattern = r"(def __init__\(self.*?\):.*?super\(\)\.__init__\(.*?\))"
                if re.search(init_pattern, code, re.DOTALL):
                    code = re.sub(init_pattern, r"\1\n" + injection, code, flags=re.DOTALL)
            
            # ALSO UPDATE CLASS NAME AND NAME ATTRIBUTE
            # Sanitize name for class
            safe_name = "".join(x for x in name.title() if not x.isspace())
            if safe_name and not safe_name.endswith("Node"): safe_name += "Node"
            if not safe_name: safe_name = "MyNode"
            
            # Update class definition
            code = re.sub(r"class \w+\(BaseNode\):", f"class {safe_name}(BaseNode):", code)
            # Update name attribute
            code = re.sub(r'name = "[^"]+"', f'name = "{name}"', code)
            # Update register_node return
            code = re.sub(r"return \w+", f"return {safe_name}", code)
            
            if code != self.code_edit.toPlainText():
                self.code_edit.setPlainText(code)
        finally:
            self._is_syncing = False

    def _on_gemini_node_generated(self, node_def):
        self._is_syncing = True
        try:
            self.name_edit.setText(node_def.get("node_id", ""))
            self.desc_edit.setPlainText(node_def.get("description", ""))
            self.category_combo.setCurrentText(node_def.get("category", "General"))
            self.icon_edit.setText(node_def.get("icon_path", ""))
            
            # Map inputs and outputs to PortModel-like objects for _update_table
            inputs = [PortModel(**p) if isinstance(p, dict) else p for p in node_def.get("inputs", [])]
            outputs = [PortModel(**p) if isinstance(p, dict) else p for p in node_def.get("outputs", [])]
            
            self._update_table(self.inputs_table, inputs)
            self._update_table(self.outputs_table, outputs)
            self.code_edit.setPlainText(node_def.get("python_code", ""))
        finally:
            self._is_syncing = False

    def _add_row(self, table):
        table.blockSignals(True)
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(f"port_{row}"))
        
        # Add type combo
        type_combo = QComboBox()
        type_combo.addItems(AVAILABLE_TYPES)
        type_combo.currentTextChanged.connect(self._sync_ui_to_code)
        table.setCellWidget(row, 1, type_combo)
        
        # Add widget combo
        widget_combo = QComboBox()
        widget_combo.addItems(AVAILABLE_WIDGETS)
        widget_combo.currentTextChanged.connect(self._sync_ui_to_code)
        table.setCellWidget(row, 2, widget_combo)
        
        table.setItem(row, 3, QTableWidgetItem("")) # Options column
        table.blockSignals(False)
        self._sync_ui_to_code()

    def _remove_row(self, table):
        row = table.currentRow()
        if row >= 0:
            table.blockSignals(True)
            table.removeRow(row)
            table.blockSignals(False)
            self._sync_ui_to_code()

    def test_node(self):
        code = self.code_edit.toPlainText()
        try:
            ast.parse(code)
            # Future: Sandbox execution test
            QMessageBox.information(self, "Validation", "Code syntax is valid.")
        except Exception as e:
            QMessageBox.critical(self, "Syntax Error", str(e))

    def save_node(self):
        # Force a final sync from UI to code to ensure consistency
        self._sync_ui_to_code()
        
        node_id = self.name_edit.text().strip()
        if not node_id:
            QMessageBox.warning(self, "Error", "Node ID/Name is required.")
            return
            
        inputs = []
        seen_inputs = set()
        for r in range(self.inputs_table.rowCount()):
            name_item = self.inputs_table.item(r, 0)
            if not name_item: continue
            name = name_item.text().strip()
            if not name or name in seen_inputs: continue
            seen_inputs.add(name)
            
            type_combo = self.inputs_table.cellWidget(r, 1)
            p_type = type_combo.currentText() if type_combo else "any"
            
            widget_combo = self.inputs_table.cellWidget(r, 2)
            p_widget = widget_combo.currentText() if widget_combo else None
            
            p_options_str = self.inputs_table.item(r, 3).text() if self.inputs_table.item(r, 3) else ""
            p_options = [o.strip() for o in p_options_str.split(",")] if p_options_str else None
            inputs.append(PortModel(name=name, type=p_type, widget_type=p_widget or None, options=p_options))
            
        outputs = []
        seen_outputs = set()
        for r in range(self.outputs_table.rowCount()):
            name_item = self.outputs_table.item(r, 0)
            if not name_item: continue
            name = name_item.text().strip()
            if not name or name in seen_outputs: continue
            seen_outputs.add(name)
            
            type_combo = self.outputs_table.cellWidget(r, 1)
            p_type = type_combo.currentText() if type_combo else "any"
            outputs.append(PortModel(name=name, type=p_type))

        definition = NodeDefinitionJSON(
            node_id=node_id,
            name=node_id,
            description=self.desc_edit.toPlainText(),
            category=self.category_combo.currentText() or "General",
            icon_path=self.icon_edit.text() or None,
            inputs=inputs,
            outputs=outputs,
            python_code=self.code_edit.toPlainText()
        )
        
        nodes_dir = os.path.abspath(os.path.join(os.getcwd(), 'nodes'))
        os.makedirs(nodes_dir, exist_ok=True)
        
        file_path = os.path.join(nodes_dir, f"{node_id}.json")
        with open(file_path, "w") as f:
            f.write(definition.model_dump_json(indent=4))
            
        if NodeRegistry.register_definition(definition):
            QMessageBox.information(self, "Success", f"Node '{node_id}' saved and registered.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to register node class. Check Python code.")

    def _load_existing_node(self):
        self._is_syncing = True
        try:
            defn = NodeRegistry.get_definition(self.editing_node_id)
            if defn:
                self.name_edit.setText(defn.node_id)
                self.desc_edit.setPlainText(defn.description)
                self.category_combo.setCurrentText(defn.category or "General")
                self.icon_edit.setText(defn.icon_path or "")
                self._update_table(self.inputs_table, defn.inputs)
                self._update_table(self.outputs_table, defn.outputs)
                self.code_edit.setPlainText(defn.python_code)
        finally:
            self._is_syncing = False

    def get_node_definition(self) -> dict:
        inputs = []
        for r in range(self.inputs_table.rowCount()):
            name_item = self.inputs_table.item(r, 0)
            if not name_item: continue
            name = name_item.text().strip()
            if not name: continue
            
            type_combo = self.inputs_table.cellWidget(r, 1)
            p_type = type_combo.currentText() if type_combo else "any"
            
            widget_combo = self.inputs_table.cellWidget(r, 2)
            p_widget = widget_combo.currentText() if widget_combo else None
            
            p_options_str = self.inputs_table.item(r, 3).text() if self.inputs_table.item(r, 3) else ""
            p_options = [o.strip() for o in p_options_str.split(",")] if p_options_str else None
            
            port_data = {"name": name, "type": p_type}
            if p_widget: port_data["widget_type"] = p_widget
            if p_options: port_data["options"] = p_options
            inputs.append(port_data)
            
        outputs = []
        for r in range(self.outputs_table.rowCount()):
            name_item = self.outputs_table.item(r, 0)
            if not name_item: continue
            name = name_item.text().strip()
            if not name: continue
            
            type_combo = self.outputs_table.cellWidget(r, 1)
            p_type = type_combo.currentText() if type_combo else "any"
            outputs.append({"name": name, "type": p_type})

        return {
            "node_id": self.name_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "description": self.desc_edit.toPlainText(),
            "category": self.category_combo.currentText(),
            "icon_path": self.icon_edit.text(),
            "inputs": inputs,
            "outputs": outputs,
            "python_code": self.code_edit.toPlainText()
        }

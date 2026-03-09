from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QPlainTextEdit, QPushButton, QLabel, QSplitter, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer
import os
import ast
from src.core.loader import ScriptLoader
from src.utils.highlighter import PythonHighlighter
from src.core.registry import NodeRegistry
from src.core.models import NodeDefinitionJSON, PortModel

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
        self.code_edit = QPlainTextEdit()
        self.code_edit.setPlainText(self._get_template("MyNode"))
        editor_layout.addWidget(self.code_edit)
        
        splitter.addWidget(config_widget)
        splitter.addWidget(editor_widget)
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

    def _get_template(self, name):
        return f"""from src.nodes.base import BaseNode

class {name}(BaseNode):
    name = "{name}"
    
    def __init__(self):
        super().__init__()
        # [AUTO-GENERATED-PORTS-START]
        # [AUTO-GENERATED-PORTS-END]
        
    async def execute(self, inputs):
        # inputs is a dict: {{port_name: value}}
        # return a dict: {{port_name: value}}
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
            self._sync_ui_to_code()

    def _sync_code_to_ui(self):
        """
        Parses the code using AST and updates the UI tables.
        """
        self._is_syncing = True
        try:
            code = self.code_edit.toPlainText()
            tree = ast.parse(code)
            
            inputs = []
            outputs = []
            
            class PortVisitor(ast.NodeVisitor):
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Attribute) and node.func.attr in ["add_input", "add_output"]:
                        if len(node.args) >= 1 and isinstance(node.args[0], ast.Constant):
                            port_name = node.args[0].value
                            port_type = "any"
                            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                                port_type = node.args[1].value
                            
                            if node.func.attr == "add_input":
                                inputs.append((port_name, port_type))
                            else:
                                outputs.append((port_name, port_type))
                    self.generic_visit(node)

            PortVisitor().visit(tree)
            
            # Update Tables
            self._update_table(self.inputs_table, inputs)
            self._update_table(self.outputs_table, outputs)
            
        except Exception as e:
            # Code might be invalid while typing, ignore
            pass
        finally:
            self._is_syncing = False

    def _update_table(self, table, ports):
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
            table.setItem(row, 1, QTableWidgetItem(p_type))
            table.setItem(row, 2, QTableWidgetItem(p_widget or ""))
            table.setItem(row, 3, QTableWidgetItem(p_options))

    def _sync_ui_to_code(self):
        """
        Updates the auto-generated ports section in the code.
        """
        self._is_syncing = True
        try:
            name = self.name_edit.text().strip() or "MyNode"
            code = self.code_edit.toPlainText()
            
            # Prepare injection string
            injection = "        # [AUTO-GENERATED-PORTS-START]\n"
            for row in range(self.inputs_table.rowCount()):
                item_name = self.inputs_table.item(row, 0)
                item_type = self.inputs_table.item(row, 1)
                item_widget = self.inputs_table.item(row, 2)
                item_options = self.inputs_table.item(row, 3)
                if item_name and item_type:
                    w_str = f', widget_type="{item_widget.text()}"' if item_widget and item_widget.text() else ""
                    # Options injection if dropdown
                    if item_widget and item_widget.text() == "dropdown" and item_options and item_options.text():
                        opts = [o.strip() for o in item_options.text().split(",")]
                        w_str += f', options={opts}'
                    injection += f'        self.add_input("{item_name.text()}", "{item_type.text()}"{w_str})\n'
            
            for row in range(self.outputs_table.rowCount()):
                item_name = self.outputs_table.item(row, 0)
                item_type = self.outputs_table.item(row, 1)
                if item_name and item_type:
                    injection += f'        self.add_output("{item_name.text()}", "{item_type.text()}")\n'
            injection += "        # [AUTO-GENERATED-PORTS-END]"

            # Replace section using markers
            import re
            pattern = r"(\s*)# \[AUTO-GENERATED-PORTS-START\].*?# \[AUTO-GENERATED-PORTS-END\]"
            if re.search(pattern, code, re.DOTALL):
                code = re.sub(pattern, injection, code, flags=re.DOTALL)
            
            self.code_edit.setPlainText(code)
        finally:
            self._is_syncing = False

    def _add_row(self, table):
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(f"port_{row}"))
        table.setItem(row, 1, QTableWidgetItem("any"))
        table.setItem(row, 2, QTableWidgetItem("")) # Widget column
        table.setItem(row, 3, QTableWidgetItem("")) # Options column
        self._sync_ui_to_code()

    def _remove_row(self, table):
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)
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
        node_id = self.name_edit.text().strip()
        if not node_id:
            QMessageBox.warning(self, "Error", "Node ID/Name is required.")
            return
            
        inputs = []
        for r in range(self.inputs_table.rowCount()):
            name = self.inputs_table.item(r, 0).text()
            p_type = self.inputs_table.item(r, 1).text()
            p_widget = self.inputs_table.item(r, 2).text() if self.inputs_table.item(r, 2) else None
            p_options_str = self.inputs_table.item(r, 3).text() if self.inputs_table.item(r, 3) else ""
            p_options = [o.strip() for o in p_options_str.split(",")] if p_options_str else None
            inputs.append(PortModel(name=name, type=p_type, widget_type=p_widget or None, options=p_options))
            
        outputs = []
        for r in range(self.outputs_table.rowCount()):
            name = self.outputs_table.item(r, 0).text()
            p_type = self.outputs_table.item(r, 1).text()
            outputs.append(PortModel(name=name, type=p_type))

        definition = NodeDefinitionJSON(
            node_id=node_id,
            name=node_id,
            description=self.desc_edit.toPlainText(),
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
                self._update_table(self.inputs_table, defn.inputs)
                self._update_table(self.outputs_table, defn.outputs)
                self.code_edit.setPlainText(defn.python_code)
        finally:
            self._is_syncing = False

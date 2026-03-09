from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QLabel, QComboBox, QSlider, QTextEdit, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush, QPixmap
from src.ui.port_widget import PortWidget
from uuid import uuid4

class NodeWidget(QGraphicsItem):
    def __init__(self, node_definition, instance_id=None, parent=None):
        super().__init__(parent)
        self.node_definition = node_definition
        self.instance_id = instance_id or uuid4()
        self.width = 180
        self.height = 120
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.input_widgets = []
        self.output_widgets = []
        self.param_widgets = {} # name -> proxy_widget
        self.status = "idle" # idle, running, success, failed
        
        self._init_ui()

    def _init_ui(self):
        # Header
        self.title_text = QGraphicsTextItem(self.node_definition.name, self)
        self.title_text.setDefaultTextColor(Qt.white)
        self.title_text.setPos(10, 5)

        # Create Ports and parameter widgets
        y_offset = 40
        inputs = self.node_definition.inputs
        
        # Handle both list (from NodeDefinitionJSON) and dict (from BaseNode instance)
        input_list = inputs if isinstance(inputs, list) else inputs.values()
        
        for p_model in input_list:
            # Input Port
            p = PortWidget(p_model, is_input=True, parent=self)
            p.setPos(0, y_offset)
            self.input_widgets.append(p)
            
            # Port Label
            label = QGraphicsTextItem(p_model.name, self)
            label.setDefaultTextColor(Qt.white)
            label.setFont(self._get_port_font())
            label.setPos(12, y_offset - 10)
            
            # Associated Parameter Widget
            if hasattr(p_model, 'widget_type') and p_model.widget_type:
                self._create_param_widget(p_model, y_offset + 15)
                y_offset += 45 # More space for widgets
            else:
                y_offset += 25
        
        # Calculate height based on ports
        self.height = max(120, y_offset + 10)
            
        outputs = self.node_definition.outputs
        y_out = 40
        output_list = outputs if isinstance(outputs, list) else outputs.values()
        
        for p_model in output_list:
            p = PortWidget(p_model, is_input=False, parent=self)
            p.setPos(self.width, y_out)
            self.output_widgets.append(p)
            
            # Port Label
            label = QGraphicsTextItem(p_model.name, self)
            label.setDefaultTextColor(Qt.white)
            label.setFont(self._get_port_font())
            # Right align label
            br = label.boundingRect()
            label.setPos(self.width - br.width() - 12, y_out - 10)
            
            y_out += 25

    def _get_port_font(self):
        from PyQt5.QtGui import QFont
        f = QFont("Arial", 8)
        return f

    def _create_param_widget(self, p_model, y_pos):
        proxy = QGraphicsProxyWidget(self)
        w = None
        
        if p_model.widget_type == 'text':
            w = QLineEdit()
            val = self.node_definition.parameters.get(p_model.name)
            w.setText(str(val) if val is not None else "")
            w.textChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'text_area':
            w = QTextEdit()
            w.setAcceptRichText(False)
            w.setMinimumHeight(60)
            val = self.node_definition.parameters.get(p_model.name)
            w.setPlainText(str(val) if val is not None else "")
            w.textChanged.connect(lambda: self._update_param(p_model.name, w.toPlainText()))
        elif p_model.widget_type == 'int':
            w = QSpinBox()
            w.setRange(-999999, 999999)
            val = self.node_definition.parameters.get(p_model.name)
            w.setValue(int(val) if val is not None else 0)
            w.valueChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'float':
            w = QDoubleSpinBox()
            w.setRange(-999999.0, 999999.0)
            val = self.node_definition.parameters.get(p_model.name)
            w.setValue(float(val) if val is not None else 0.0)
            w.valueChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'bool':
            w = QCheckBox()
            val = self.node_definition.parameters.get(p_model.name)
            w.setChecked(bool(val) if val is not None else False)
            w.stateChanged.connect(lambda val: self._update_param(p_model.name, bool(val)))
        elif p_model.widget_type == 'dropdown':
            w = QComboBox()
            if hasattr(p_model, 'options') and p_model.options:
                w.addItems(p_model.options)
            val = self.node_definition.parameters.get(p_model.name)
            if val is not None:
                w.setCurrentText(str(val))
            w.currentTextChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'slider':
            w = QSlider(Qt.Horizontal)
            w.setRange(0, 100) # Default
            val = self.node_definition.parameters.get(p_model.name)
            w.setValue(int(val) if val is not None else 0)
            w.valueChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'file':
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(2)
            
            path_edit = QLineEdit()
            val = self.node_definition.parameters.get(p_model.name)
            path_edit.setText(str(val) if val is not None else "")
            
            btn = QPushButton("...")
            btn.setFixedWidth(25)
            
            def select_file():
                from PyQt5.QtWidgets import QFileDialog
                # We need to find the parent window for the dialog
                curr = self.scene().views()[0] if self.scene() and self.scene().views() else None
                path, _ = QFileDialog.getOpenFileName(curr, "Select File")
                if path:
                    path_edit.setText(path)
                    self._update_param(p_model.name, path)

            btn.clicked.connect(select_file)
            path_edit.textChanged.connect(lambda val: self._update_param(p_model.name, val))
            
            l.addWidget(path_edit)
            l.addWidget(btn)
            # Override standard width handling for this complex widget
            w.setFixedWidth(self.width - 40)

        if w:
            w.setFixedWidth(self.width - 40)
            w.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
            proxy.setWidget(w)
            proxy.setPos(20, y_pos - 10) # Offset slightly from port
            self.param_widgets[p_model.name] = proxy

    def _update_param(self, name, value):
        self.node_definition.parameters[name] = value

    def set_status(self, status: str):
        self.status = status
        self.update()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.scene():
                for edge in self.scene().edges:
                    if edge.from_port in self.input_widgets or \
                       edge.from_port in self.output_widgets or \
                       edge.to_port in self.input_widgets or \
                       edge.to_port in self.output_widgets:
                        edge.update_path()
        return super().itemChange(change, value)
    def paint(self, painter, option, widget):
        base_color = QColor(40, 40, 40)
        if self.status == "running":
            base_color = QColor(100, 100, 0)
        elif self.status == "success":
            base_color = QColor(0, 80, 0)
        elif self.status == "failed":
            base_color = QColor(100, 0, 0)

        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(base_color))
        painter.drawRoundedRect(self.boundingRect(), 10, 10)
        
        header_color = QColor(60, 60, 60)
        painter.setBrush(QBrush(header_color))
        painter.drawRoundedRect(QRectF(0, 0, self.width, 30), 10, 10)
        painter.drawRect(QRectF(0, 15, self.width, 15))

        # Draw Icon if exists
        if hasattr(self.node_definition, 'icon_path') and self.node_definition.icon_path:
            pixmap = QPixmap(self.node_definition.icon_path)
            if not pixmap.isNull():
                painter.drawPixmap(5, 5, 20, 20, pixmap)
                self.title_text.setPos(30, 5)
            else:
                self.title_text.setPos(10, 5)
        else:
            self.title_text.setPos(10, 5)

        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.boundingRect(), 10, 10)

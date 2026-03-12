from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QLabel, QComboBox, QSlider, QTextEdit, QWidget, QHBoxLayout, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPen, QBrush, QPixmap, QPainterPath
from src.ui.port_widget import PortWidget
from uuid import uuid4

class NodeWidget(QGraphicsItem):
    def __init__(self, node_definition, instance_id=None, parent=None):
        super().__init__(parent)
        self.node_definition = node_definition
        self.instance_id = instance_id or uuid4()
        self.width = 220
        self.height = 140 # Initial minimum
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.input_widgets = []
        self.output_widgets = []
        self.input_labels = []
        self.output_labels = []
        self.param_widgets = {} # name -> proxy_widget
        self.status = "idle" # idle, running, success, failed
        self.is_dark = True
        
        self._init_ui()

    def apply_theme(self, is_dark=True):
        self.is_dark = is_dark
        q_text_color = QColor(Qt.white) if is_dark else QColor(Qt.black)
        
        if hasattr(self, 'title_text') and self.title_text:
            self.title_text.setDefaultTextColor(q_text_color)
            
        for label in self.input_labels + self.output_labels:
            label.setDefaultTextColor(q_text_color)
            
        # Update parameter labels and widgets via stylesheet
        bg_color = "#333" if is_dark else "#eee"
        border_color = "#555" if is_dark else "#ccc"
        label_color = "#aaa" if is_dark else "#555"
        text_color_name = q_text_color.name()
        
        for proxy in self.param_widgets.values():
            container = proxy.widget()
            if not container: continue
            
            param_label = container.findChild(QLabel)
            if param_label:
                param_label.setStyleSheet(f"color: {label_color}; font-size: 9px; font-weight: bold; background: transparent;")
            
            from PyQt5.QtWidgets import QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QSlider, QTextEdit
            for w in container.findChildren((QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QSlider, QTextEdit)):
                w.setStyleSheet(f"background-color: {bg_color}; color: {text_color_name}; border: 1px solid {border_color};")
        
        self.update()

    def _init_ui(self):
        # Header
        self.title_text = QGraphicsTextItem(self.node_definition.name, self)
        self.title_text.setDefaultTextColor(Qt.white)
        self.title_text.setPos(10, 5)
        
        self.rebuild_ports()

    def rebuild_ports(self):
        """Dynamic port reconstruction."""
        # 1. Identify affected edges BEFORE detaching old ports
        affected_edges_out = [] # (edge, port_name)
        affected_edges_in = [] # (edge, port_name)
        
        if self.scene():
            for edge in self.scene().edges:
                if edge.from_port in self.output_widgets:
                    affected_edges_out.append((edge, edge.from_port.port_definition.name))
                if edge.to_port in self.input_widgets:
                    affected_edges_in.append((edge, edge.to_port.port_definition.name))

        # 2. Clear old port widgets and labels
        for w in self.input_widgets + self.output_widgets + self.input_labels + self.output_labels:
            if self.scene() and w.scene(): 
                self.scene().removeItem(w)
            else:
                w.setParentItem(None)
                
        self.input_widgets.clear()
        self.output_widgets.clear()
        self.input_labels.clear()
        self.output_labels.clear()

        # 3. Create Ports (Sorted: exec first)
        y_in = 45
        inputs = self.node_definition.inputs
        input_list = inputs if isinstance(inputs, list) else inputs.values()
        
        # Sort so 'exec' type comes first
        sorted_inputs = sorted(input_list, key=lambda x: 0 if getattr(x, 'type', 'any').lower() == 'exec' or getattr(x, 'data_type', 'any').lower() == 'exec' else 1)
        
        for p_model in sorted_inputs:
            p = PortWidget(p_model, is_input=True, parent=self)
            p.setPos(0, y_in)
            self.input_widgets.append(p)
            
            label_text = p_model.name
            if p.port_type == "exec" and label_text in ["in", "exec_in", "trigger"]:
                label_text = ""
                
            label = QGraphicsTextItem(label_text, self)
            label.setDefaultTextColor(Qt.white if self.is_dark else Qt.black)
            label.setFont(self._get_port_font())
            label.setPos(12, y_in - 10)
            self.input_labels.append(label)
            y_in += 25
            
        y_out = 45
        outputs = self.node_definition.outputs
        output_list = outputs if isinstance(outputs, list) else outputs.values()
        
        # Sort so 'exec' type comes first
        sorted_outputs = sorted(output_list, key=lambda x: 0 if getattr(x, 'type', 'any').lower() == 'exec' or getattr(x, 'data_type', 'any').lower() == 'exec' else 1)

        for p_model in sorted_outputs:
            p = PortWidget(p_model, is_input=False, parent=self)
            p.setPos(self.width, y_out)
            self.output_widgets.append(p)
            
            label_text = p_model.name
            if p.port_type == "exec" and label_text in ["out", "exec_out", "then", "exit"]:
                label_text = ""
                
            label = QGraphicsTextItem(label_text, self)
            label.setDefaultTextColor(Qt.white if self.is_dark else Qt.black)
            label.setFont(self._get_port_font())
            self.output_labels.append(label)
            y_out += 25

        # 4. Parameter Widgets (Only create if not already exists)
        for p_model in input_list:
            if hasattr(p_model, 'widget_type') and p_model.widget_type:
                if p_model.name not in self.param_widgets:
                    self._create_param_widget(p_model)

        # 5. Calculate Dynamic Height
        proxies = list(self.param_widgets.values())
        params_total_height = 0
        for p in proxies:
            params_total_height += p.widget().sizeHint().height() + 10
            
        ports_max_y = max(y_in, y_out)
        self.height = max(140, ports_max_y + params_total_height + 20)
        
        self._auto_size(ports_max_y)
        
        # 6. Reconnect Edges to new PortWidgets
        for edge, name in affected_edges_out:
            new_p = next((p for p in self.output_widgets if p.port_definition.name == name), None)
            if new_p: 
                edge.from_port = new_p
                edge.update_path()
            else:
                # Port gone? Remove edge
                if self.scene() and edge in self.scene().edges:
                    self.scene().removeItem(edge)
                    self.scene().edges.remove(edge)

        for edge, name in affected_edges_in:
            new_p = next((p for p in self.input_widgets if p.port_definition.name == name), None)
            if new_p: 
                edge.to_port = new_p
                edge.update_path()
            else:
                if self.scene() and edge in self.scene().edges:
                    self.scene().removeItem(edge)
                    self.scene().edges.remove(edge)

    def _auto_size(self, ports_bottom_y):
        """Dynamically scales the node width and centers children."""
        self.prepareGeometryChange()
        
        # 1. Width Calculation
        min_width = 220
        content_width = 0
        if hasattr(self, 'title_text') and self.title_text:
            content_width = max(content_width, self.title_text.boundingRect().width() + 40)
        for proxy in self.param_widgets.values():
            w = proxy.widget()
            if w:
                content_width = max(content_width, w.sizeHint().width() + 100)
        for i in range(max(len(self.input_labels), len(self.output_labels))):
            w_row = 80
            if i < len(self.input_labels): w_row += self.input_labels[i].boundingRect().width()
            if i < len(self.output_labels): w_row += self.output_labels[i].boundingRect().width()
            content_width = max(content_width, w_row + 20)
        self.width = max(min_width, content_width)
        
        # 2. Vertical Centering for params
        body_top = ports_bottom_y + 10
        body_bottom = self.height - 10
        proxies = list(self.param_widgets.values())
        if proxies:
            total_h = sum([p.widget().sizeHint().height() for p in proxies])
            spacing = max(5, (body_bottom - body_top - total_h) / (len(proxies) + 1))
            current_y = body_top + spacing
            for proxy in proxies:
                w = proxy.widget()
                if w:
                    w.setFixedWidth(int(self.width - 100)) 
                    proxy.setPos(50, int(current_y))
                    current_y += w.sizeHint().height() + spacing

        # 3. Reposition Outputs
        for i, p in enumerate(self.output_widgets):
            p.setPos(self.width, p.pos().y())
            if i < len(self.output_labels):
                label = self.output_labels[i]
                label.setPos(self.width - label.boundingRect().width() - 12, p.pos().y() - 10)
        
        self._refresh_widget_states()

    def _refresh_widget_states(self):
        """Disables widgets if their input port has a connection."""
        if not self.scene(): return
        for p_name, proxy in self.param_widgets.items():
            port_widget = next((pw for pw in self.input_widgets if pw.port_definition.name == p_name), None)
            if port_widget:
                is_connected = any(e.to_port == port_widget for e in self.scene().edges)
                container = proxy.widget()
                container.setEnabled(not is_connected)
                for child in container.findChildren(QWidget):
                    child.setEnabled(not is_connected)

    def _get_port_font(self):
        from PyQt5.QtGui import QFont
        f = QFont("Arial", 8)
        return f

    def _create_param_widget(self, p_model):
        proxy = QGraphicsProxyWidget(self)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        param_label = QLabel(p_model.name)
        param_label.setStyleSheet("color: #aaa; font-size: 9px; font-weight: bold; background: transparent;")
        layout.addWidget(param_label)
        
        w = None
        if p_model.widget_type == 'text':
            w = QLineEdit()
            val = self.node_definition.parameters.get(p_model.name)
            w.setText(str(val) if val is not None else "")
            w.textChanged.connect(lambda val: self._update_param(p_model.name, val))
        elif p_model.widget_type == 'text_area':
            w = QTextEdit()
            w.setAcceptRichText(False)
            w.setMaximumHeight(60)
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
            w.setRange(0, 100)
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
                curr = self.scene().views()[0] if self.scene() and self.scene().views() else None
                path, _ = QFileDialog.getOpenFileName(curr, "Select File")
                if path:
                    path_edit.setText(path)
                    self._update_param(p_model.name, path)
            btn.clicked.connect(select_file)
            path_edit.textChanged.connect(lambda val: self._update_param(p_model.name, val))
            l.addWidget(path_edit)
            l.addWidget(btn)

        if w:
            w.setStyleSheet("background-color: #333; color: white; border: 1px solid #555;")
            layout.addWidget(w)
            
        container.setStyleSheet("background: transparent;")
        proxy.setWidget(container)
        self.param_widgets[p_model.name] = proxy

    def set_parameter(self, name, value, propagate=True):
        """Programmatically set a parameter and update its UI widget."""
        # Type Conversion attempt based on port definition
        inputs = self.node_definition.inputs
        input_list = inputs if isinstance(inputs, list) else inputs.values()
        outputs = self.node_definition.outputs
        output_list = outputs if isinstance(outputs, list) else outputs.values()
        
        port_def = next((p for p in input_list if p.name == name), None)
        if not port_def:
             port_def = next((p for p in output_list if p.name == name), None)
        
        target_value = value
        if port_def:
            try:
                data_type = getattr(port_def, 'data_type', getattr(port_def, 'type', 'any')).lower()
                if data_type == 'int': target_value = int(value)
                elif data_type in ['float', 'number']: target_value = float(value)
                elif data_type == 'string': target_value = str(value)
                elif data_type == 'bool':
                    if isinstance(value, str): target_value = value.lower() in ['true', '1', 'yes']
                    else: target_value = bool(value)
            except (ValueError, TypeError):
                pass

        if self.node_definition.parameters.get(name) == target_value:
            return # No change
            
        self.node_definition.parameters[name] = target_value
        
        # 1. Update UI
        if name in self.param_widgets:
            proxy = self.param_widgets[name]
            container = proxy.widget()
            from PyQt5.QtWidgets import QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QSlider, QTextEdit
            w = container.findChild(QLineEdit) or container.findChild(QSpinBox) or \
                container.findChild(QDoubleSpinBox) or container.findChild(QCheckBox) or \
                container.findChild(QComboBox) or container.findChild(QSlider) or \
                container.findChild(QTextEdit)

            if w:
                w.blockSignals(True) # Prevent recursion
                if isinstance(w, QLineEdit): w.setText(str(target_value) if target_value is not None else "")
                elif isinstance(w, (QSpinBox, QDoubleSpinBox, QSlider)): 
                    if target_value is not None:
                        try:
                            w.setValue(target_value)
                        except TypeError:
                            pass # Guard against bad types
                elif isinstance(w, QCheckBox): w.setChecked(bool(target_value))
                elif isinstance(w, QComboBox): w.setCurrentText(str(target_value) if target_value is not None else "")
                elif isinstance(w, QTextEdit): w.setPlainText(str(target_value) if target_value is not None else "")
                w.blockSignals(False)

        # 2. Trigger node logic
        self.node_definition.on_parameter_changed(name, target_value)
        
        # 3. Push downstream
        if propagate:
            self._propagate_all_outputs()

    def _update_param(self, name, value):
        """Internal handler for widget value changes."""
        self.node_definition.parameters[name] = value
        self.node_definition.on_parameter_changed(name, value)
        self._propagate_all_outputs()

    def _propagate_all_outputs(self):
        """Pushes all current output port values to connected downstream nodes."""
        if not self.scene(): return
        
        for edge in self.scene().edges:
            if edge.from_port.parentItem() == self:
                out_port_name = edge.from_port.port_definition.name
                current_val = self.node_definition.get_parameter(out_port_name)
                
                target_node = edge.to_port.parentItem()
                target_port_name = edge.to_port.port_definition.name
                
                # Recursive push to destination
                target_node.set_parameter(target_port_name, current_val, propagate=True)

    def set_status(self, status: str):
        self.status = status
        self.update()

    def is_port_connected(self, port_name, is_input):
        """Checks if a port has any active connections in the scene."""
        if not self.scene(): return False
        for edge in self.scene().edges:
            if is_input:
                if edge.to_port and edge.to_port.parentItem() == self and edge.to_port.port_definition.name == port_name:
                    return True
            else:
                if edge.from_port and edge.from_port.parentItem() == self and edge.from_port.port_definition.name == port_name:
                    return True
        return False

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
        from src.utils.color_manager import ColorManager
        base_color = QColor(40, 40, 40) if self.is_dark else QColor(220, 220, 220)
        if self.status == "running": base_color = QColor(100, 100, 0)
        elif self.status == "success": base_color = QColor(0, 80, 0)
        elif self.status == "failed": base_color = QColor(100, 0, 0)

        # 1. DRAW BODY
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(base_color))
        painter.drawRoundedRect(self.boundingRect(), 10, 10)
        
        # 2. DRAW HEADER
        # Use Category Color from ColorManager
        header_color = ColorManager.get_category_color(self.node_definition.category)
        
        painter.setBrush(QBrush(header_color))
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 10, 10)
        painter.save()
        painter.setClipPath(path)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, int(self.width), 35)
        
        # Draw text contrast (black or white)
        if header_color.lightness() > 150:
            self.title_text.setDefaultTextColor(Qt.black)
        else:
            self.title_text.setDefaultTextColor(Qt.white)
            
        painter.restore()
        
        painter.setPen(QPen(QColor(30, 30, 30), 1))
        painter.drawLine(0, 35, int(self.width), 35)

        if hasattr(self.node_definition, 'icon_path') and self.node_definition.icon_path:
            pixmap = QPixmap(self.node_definition.icon_path)
            if not pixmap.isNull():
                painter.drawPixmap(8, 8, 20, 20, pixmap)
                self.title_text.setPos(32, 5)
            else: self.title_text.setPos(10, 5)
        else: self.title_text.setPos(10, 5)

        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.boundingRect(), 10, 10)

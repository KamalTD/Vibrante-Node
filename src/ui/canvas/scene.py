from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QAction
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
from src.core.registry import NodeRegistry
from src.ui.node_widget import NodeWidget
from src.ui.canvas.edge import Edge
from src.ui.port_widget import PortWidget
from src.core.models import WorkflowModel, NodeInstanceModel, ConnectionModel
from uuid import uuid4, UUID

class NodeScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(40, 40, 40)) # Darker background
        self.setSceneRect(-5000, -5000, 10000, 10000)
        
        self.nodes = [] # List of NodeWidget
        self.edges = []
        self.active_edge = None
        self.file_path = None # Track current file

        self.grid_size = 20
        self.grid_pen = QPen(QColor("#555555"), 0.5)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Draw custom grid
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())
        
        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)
        
        painter.setPen(self.grid_pen)
        
        # Draw vertical lines
        for x in range(first_left, right, self.grid_size):
            painter.drawLine(x, top, x, bottom)
            
        # Draw horizontal lines
        for y in range(first_top, bottom, self.grid_size):
            painter.drawLine(left, y, right, y)

    def to_workflow_model(self) -> WorkflowModel:
        model = WorkflowModel()
        for node_widget in self.nodes:
            node_model = NodeInstanceModel(
                instance_id=node_widget.instance_id,
                node_id=getattr(node_widget.node_definition, 'node_id', node_widget.node_definition.name),
                position=(node_widget.pos().x(), node_widget.pos().y()),
                parameters=node_widget.node_definition.parameters
            )
            model.nodes.append(node_model)
        
        for edge in self.edges:
            if edge.from_port and edge.to_port:
                conn_model = ConnectionModel(
                    from_node=edge.from_port.parentItem().instance_id,
                    from_port=edge.from_port.port_definition.name,
                    to_node=edge.to_port.parentItem().instance_id,
                    to_port=edge.to_port.port_definition.name
                )
                model.connections.append(conn_model)
        
        return model

    def from_workflow_model(self, model: WorkflowModel):
        self.clear()
        self.nodes = []
        self.edges = []
        
        id_to_widget = {}
        
        for node_model in model.nodes:
            # Try to get class from registry (both custom and builtin)
            node_class = NodeRegistry.get_class(node_model.node_id)
            if not node_class:
                # Fallback to builtin registry if needed (for nodes like FileLoaderNode)
                from src.nodes.base import NodeRegistry as BaseRegistry
                node_class = BaseRegistry.get_node_class(node_model.node_id)

            if node_class:
                node_def = node_class()
                node_def.parameters = node_model.parameters
                widget = NodeWidget(node_def, instance_id=node_model.instance_id)
                widget.setPos(node_model.position[0], node_model.position[1])
                self.addItem(widget)
                self.nodes.append(widget)
                id_to_widget[node_model.instance_id] = widget
                
        for conn in model.connections:
            from_widget = id_to_widget.get(conn.from_node)
            to_widget = id_to_widget.get(conn.to_node)
            
            if from_widget and to_widget:
                from_port = next((p for p in from_widget.output_widgets if p.port_definition.name == conn.from_port), None)
                to_port = next((p for p in to_widget.input_widgets if p.port_definition.name == conn.to_port), None)
                
                if from_port and to_port:
                    edge = Edge(from_port, to_port)
                    self.addItem(edge)
                    self.edges.append(edge)

    def mousePressEvent(self, event):
        view = self.views()[0] if self.views() else None
        transform = view.transform() if view else None
        item = self.itemAt(event.scenePos(), transform) if transform else self.itemAt(event.scenePos())
        
        if event.button() == Qt.LeftButton:
            if isinstance(item, PortWidget):
                # If it's an input and already has a connection, disconnect it and drag it
                if item.is_input:
                    existing_edge = next((e for e in self.edges if e.to_port == item), None)
                    if existing_edge:
                        self.edges.remove(existing_edge)
                        self.active_edge = existing_edge
                        self.active_edge.to_port = None
                    else:
                        self.active_edge = Edge(item)
                        self.addItem(self.active_edge)
                else:
                    self.active_edge = Edge(item)
                    self.addItem(self.active_edge)
                
                self.active_edge.set_end_pos(event.scenePos())
                event.accept()
                return
            elif isinstance(item, Edge):
                # Prioritize edge selection
                item.setSelected(True)
                super().mousePressEvent(event)
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.active_edge:
            self.active_edge.set_end_pos(event.scenePos())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.active_edge and event.button() == Qt.LeftButton:
            view = self.views()[0] if self.views() else None
            transform = view.transform() if view else None
            item = self.itemAt(event.scenePos(), transform) if transform else self.itemAt(event.scenePos())
            
            if isinstance(item, PortWidget):
                if item != self.active_edge.from_port and \
                   item.parentItem() != self.active_edge.from_port.parentItem() and \
                   item.is_input != self.active_edge.from_port.is_input:
                    
                    target_input = item if item.is_input else self.active_edge.from_port
                    target_output = item if not item.is_input else self.active_edge.from_port
                    
                    # ENFORCE SINGLE WIRE PER INPUT
                    old_edge = next((e for e in self.edges if e.to_port == target_input), None)
                    if old_edge:
                        self.removeItem(old_edge)
                        self.edges.remove(old_edge)

                    self.active_edge.from_port = target_output
                    self.active_edge.to_port = target_input
                    self.active_edge.update_path()
                    
                    if self.active_edge not in self.edges:
                        self.edges.append(self.active_edge)
                    self.active_edge = None
                else:
                    self.removeItem(self.active_edge)
                    self.active_edge = None
            else:
                self.removeItem(self.active_edge)
                self.active_edge = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if isinstance(item, Edge):
                    if item in self.edges:
                        self.edges.remove(item)
                    self.removeItem(item)
                elif isinstance(item, NodeWidget):
                    # Remove node and its connections
                    self._remove_node_widget(item)
        super().keyPressEvent(event)

    def _remove_node_widget(self, node_widget):
        # Remove all connected edges
        edges_to_remove = [e for e in self.edges if e.from_port.parentItem() == node_widget or e.to_port.parentItem() == node_widget]
        for e in edges_to_remove:
            self.edges.remove(e)
            self.removeItem(e)
        
        if node_widget in self.nodes:
            self.nodes.remove(node_widget)
        self.removeItem(node_widget)

    def contextMenuEvent(self, event):
        menu = QMenu()
        pos = event.scenePos()
        for node_id in NodeRegistry.list_node_ids():
            action = QAction(f"Add {node_id}", self.parent())
            # Use default arguments in lambda to capture current values of node_id and pos
            action.triggered.connect(lambda checked, nid=node_id, p=pos: self.add_node_by_name(nid, p))
            menu.addAction(action)

        if not menu.isEmpty():
            menu.exec_(event.screenPos())
        else:
            super().contextMenuEvent(event)

    def add_node_by_name(self, node_id, pos):
        node_class = NodeRegistry.get_class(node_id)
        if node_class:
            node_definition = node_class()
            node_widget = NodeWidget(node_definition)
            node_widget.setPos(pos)
            self.addItem(node_widget)
            self.nodes.append(node_widget)
        else:
            print(f"Warning: Node class for '{node_id}' not found in registry.")

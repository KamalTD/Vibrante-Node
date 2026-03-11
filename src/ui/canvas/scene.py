from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QAction
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen
import asyncio
from src.core.registry import NodeRegistry
from src.ui.node_widget import NodeWidget
from src.ui.canvas.edge import Edge
from src.ui.port_widget import PortWidget
from src.core.models import WorkflowModel, NodeInstanceModel, ConnectionModel, StickyNoteModel, BackdropModel
from src.utils.runtime import AsyncRuntime
from src.ui.canvas.sticky_note import StickyNote
from src.ui.canvas.backdrop import Backdrop
from uuid import uuid4, UUID

class NodeScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(40, 40, 40)) # Darker background
        self.setSceneRect(-5000, -5000, 10000, 10000)
        
        self.nodes = [] # List of NodeWidget
        self.edges = []
        self.sticky_notes = []
        self.backdrops = []
        self.active_edge = None
        self.file_path = None

        self.grid_size = 20
        self.grid_pen = QPen(QColor("#555555"), 0.5)

    def _safe_async_call(self, coro):
        """Helper to call async methods from the UI thread using a background loop."""
        AsyncRuntime.run_coroutine(coro)

    def _trigger_unplug(self, from_port, to_port):
        """Triggers sync and async unplug events."""
        if not from_port or not to_port: return
        fn_widget = from_port.parentItem()
        tn_widget = to_port.parentItem()
        fn = fn_widget.node_definition
        tn = tn_widget.node_definition
        
        try:
            fn.on_unplug_sync(from_port.port_definition.name, False)
        except Exception as e:
            print(f"Error in {fn.name} on_unplug_sync: {e}")
            
        try:
            tn.on_unplug_sync(to_port.port_definition.name, True)
        except Exception as e:
            print(f"Error in {tn.name} on_unplug_sync: {e}")
        
        fn_widget._refresh_widget_states()
        tn_widget._refresh_widget_states()
        
        self._safe_async_call(fn.on_unplug(from_port.port_definition.name, False))
        self._safe_async_call(tn.on_unplug(to_port.port_definition.name, True))

    def _trigger_plug(self, from_port, to_port):
        """Triggers sync and async plug events."""
        if not from_port or not to_port: return
        fn_widget = from_port.parentItem()
        tn_widget = to_port.parentItem()
        fn = fn_widget.node_definition
        tn = tn_widget.node_definition
        
        source_val = fn.get_parameter(from_port.port_definition.name)
        if source_val is not None:
            tn_widget.set_parameter(to_port.port_definition.name, source_val)

        try:
            fn.on_plug_sync(from_port.port_definition.name, False, tn, to_port.port_definition.name)
        except Exception as e:
            print(f"Error in {fn.name} on_plug_sync: {e}")
            
        try:
            tn.on_plug_sync(to_port.port_definition.name, True, fn, from_port.port_definition.name)
        except Exception as e:
            print(f"Error in {tn.name} on_plug_sync: {e}")
        
        fn_widget._refresh_widget_states()
        tn_widget._refresh_widget_states()
        
        self._safe_async_call(fn.on_plug(from_port.port_definition.name, False, tn, to_port.port_definition.name))
        self._safe_async_call(tn.on_plug(to_port.port_definition.name, True, fn, from_port.port_definition.name))

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())
        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)
        painter.setPen(self.grid_pen)
        for x in range(first_left, right, self.grid_size):
            painter.drawLine(x, top, x, bottom)
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
        for note in self.sticky_notes:
            model.sticky_notes.append(StickyNoteModel(
                id=note.instance_id,
                position=(note.pos().x(), note.pos().y()),
                size=(note.rect().width(), note.rect().height()),
                text=note.get_text(),
                color=note.bg_color.name()
            ))
        for box in self.backdrops:
            model.backdrops.append(BackdropModel(
                id=box.instance_id,
                position=(box.pos().x(), box.pos().y()),
                size=(box.rect().width(), box.rect().height()),
                title=box.title_item.toPlainText(),
                color=box.bg_color.name()
            ))
        return model

    def from_workflow_model(self, model: WorkflowModel):
        self.clear()
        self.nodes = []
        self.edges = []
        self.sticky_notes = []
        self.backdrops = []
        id_to_widget = {}
        
        for node_model in model.nodes:
            widget = self.add_node_by_name(node_model.node_id, QPointF(node_model.position[0], node_model.position[1]))
            if widget:
                widget.instance_id = node_model.instance_id
                widget.node_definition.parameters = node_model.parameters
                id_to_widget[node_model.instance_id] = widget
        
        for conn in model.connections:
            from_widget = id_to_widget.get(conn.from_node)
            to_widget = id_to_widget.get(conn.to_node)
            if from_widget and to_widget:
                self.connect_nodes(from_widget, conn.from_port, to_widget, conn.to_port)
                
        for note_model in model.sticky_notes:
            self.add_sticky_note(note_model.text, note_model.position, note_model.size, note_model.color, note_model.id)
            
        for bd_model in model.backdrops:
            self.add_backdrop(bd_model.title, bd_model.position, bd_model.size, bd_model.color, bd_model.id)

    def add_sticky_note(self, text="New Note", pos=(0, 0), size=(200, 150), color="#ffffcc", instance_id=None):
        note = StickyNote(text, pos, size, color, instance_id)
        self.addItem(note)
        self.sticky_notes.append(note)
        return note

    def add_backdrop(self, title="Network Box", pos=(0, 0), size=(400, 300), color="#444444", instance_id=None):
        box = Backdrop(title, pos, size, color, instance_id)
        self.addItem(box)
        self.backdrops.append(box)
        return box

    def mousePressEvent(self, event):
        view = self.views()[0] if self.views() else None
        transform = view.transform() if view else None
        item = self.itemAt(event.scenePos(), transform) if transform else self.itemAt(event.scenePos())
        is_dark = self.backgroundBrush().color().lightness() < 128
        if event.button() == Qt.LeftButton:
            if isinstance(item, PortWidget):
                if item.is_input:
                    existing_edge = next((e for e in self.edges if e.to_port == item), None)
                    if existing_edge:
                        from_p = existing_edge.from_port
                        to_p = existing_edge.to_port
                        self.edges.remove(existing_edge)
                        self.active_edge = existing_edge
                        self.active_edge.to_port = None
                        self._trigger_unplug(from_p, to_p)
                    else:
                        self.active_edge = Edge(item)
                        self.active_edge.apply_theme(is_dark)
                        self.addItem(self.active_edge)
                else:
                    self.active_edge = Edge(item)
                    self.active_edge.apply_theme(is_dark)
                    self.addItem(self.active_edge)
                self.active_edge.set_end_pos(event.scenePos())
                event.accept()
                return
            elif isinstance(item, Edge):
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
                    
                    old_edge = next((e for e in self.edges if e.to_port == target_input), None)
                    if old_edge:
                        from_p = old_edge.from_port
                        to_p = old_edge.to_port
                        self.removeItem(old_edge)
                        self.edges.remove(old_edge)
                        self._trigger_unplug(from_p, to_p)

                    self.active_edge.from_port = target_output
                    self.active_edge.to_port = target_input
                    self.active_edge.update_path()
                    if self.active_edge not in self.edges:
                        self.edges.append(self.active_edge)
                    self._trigger_plug(target_output, target_input)
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
                        from_p = item.from_port
                        to_p = item.to_port
                        self.edges.remove(item)
                        self._trigger_unplug(from_p, to_p)
                    self.removeItem(item)
                elif isinstance(item, NodeWidget):
                    self._remove_node_widget(item)
                elif isinstance(item, StickyNote):
                    if item in self.sticky_notes: self.sticky_notes.remove(item)
                    self.removeItem(item)
                elif isinstance(item, Backdrop):
                    if item in self.backdrops: self.backdrops.remove(item)
                    self.removeItem(item)
        super().keyPressEvent(event)

    def _remove_node_widget(self, node_widget):
        edges_to_remove = [e for e in self.edges if e.from_port.parentItem() == node_widget or e.to_port.parentItem() == node_widget]
        for e in edges_to_remove:
            from_p = e.from_port
            to_p = e.to_port
            self.edges.remove(e)
            self.removeItem(e)
            self._trigger_unplug(from_p, to_p)
        if node_widget in self.nodes:
            self.nodes.remove(node_widget)
        self.removeItem(node_widget)

    def contextMenuEvent(self, event):
        menu = QMenu()
        pos = event.scenePos()
        
        selected_items = self.selectedItems()
        selected_nodes = [i for i in selected_items if isinstance(i, NodeWidget)]
        
        # 1. Option to wrap selection in Backdrop
        if selected_nodes:
            wrap_act = QAction(f"Wrap {len(selected_nodes)} Nodes in Box", self.parent())
            def wrap_selection():
                # Calculate bounding rect of all selected nodes
                rect = selected_nodes[0].sceneBoundingRect()
                for node in selected_nodes[1:]:
                    rect = rect.united(node.sceneBoundingRect())
                
                # Add padding
                padding = 40
                box_pos = (rect.x() - padding, rect.y() - padding - 20) # Extra top for title
                box_size = (rect.width() + padding*2, rect.height() + padding*2 + 20)
                
                self.add_backdrop(title="Grouped Nodes", pos=box_pos, size=box_size)
            
            wrap_act.triggered.connect(wrap_selection)
            menu.addAction(wrap_act)
            menu.addSeparator()

        # Core Items
        add_note_act = QAction("Add Sticky Note", self.parent())
        add_note_act.triggered.connect(lambda: self.add_sticky_note(pos=(pos.x(), pos.y())))
        menu.addAction(add_note_act)
        
        add_bd_act = QAction("Add Network Box (Backdrop)", self.parent())
        add_bd_act.triggered.connect(lambda: self.add_backdrop(pos=(pos.x(), pos.y())))
        menu.addAction(add_bd_act)
        
        menu.addSeparator()
        
        # Nodes Submenu
        node_menu = menu.addMenu("Add Node")
        for node_id in NodeRegistry.list_node_ids():
            action = QAction(f"{node_id}", self.parent())
            action.triggered.connect(lambda checked, nid=node_id, p=pos: self.add_node_by_name(nid, p))
            node_menu.addAction(action)
            
        if not menu.isEmpty(): menu.exec_(event.screenPos())
        else: super().contextMenuEvent(event)

    def add_node_by_name(self, node_id, pos):
        if isinstance(pos, tuple): pos = QPointF(pos[0], pos[1])
        node_class = NodeRegistry.get_class(node_id)
        if not node_class:
            from src.nodes.base import NodeRegistry as BaseRegistry
            node_class = BaseRegistry.get_node_class(node_id)
        if node_class:
            node_definition = node_class()
            if self.parent() and hasattr(self.parent(), 'log_panel'):
                lp = self.parent().log_panel
                node_definition._on_log = lambda msg, level: lp.log(f"[{node_definition.name}] {msg}", level)
            node_widget = NodeWidget(node_definition)
            node_widget.setPos(pos)
            self.addItem(node_widget)
            self.nodes.append(node_widget)
            
            # Inherit theme
            is_dark = self.backgroundBrush().color().lightness() < 128
            node_widget.apply_theme(is_dark)
            
            # Ensure states are initialized correctly (all enabled)
            node_widget._refresh_widget_states()
            return node_widget
        return None

    def find_node_by_name(self, name: str):
        for node in self.nodes:
            if node.node_definition.name == name: return node
        return None

    def connect_nodes(self, from_node, from_port_name, to_node, to_port_name):
        if isinstance(from_node, str): from_node = self.find_node_by_name(from_node)
        if isinstance(to_node, str): to_node = self.find_node_by_name(to_node)
        if not from_node or not to_node: return None
        from_port = next((p for p in from_node.output_widgets if p.port_definition.name == from_port_name), None)
        to_port = next((p for p in to_node.input_widgets if p.port_definition.name == to_port_name), None)
        if from_port and to_port:
            old_edge = next((e for e in self.edges if e.to_port == to_port), None)
            if old_edge:
                from_p = old_edge.from_port
                to_p = old_edge.to_port
                self.removeItem(old_edge)
                self.edges.remove(old_edge)
                self._trigger_unplug(from_p, to_p)
            edge = Edge(from_port, to_port)
            is_dark = self.backgroundBrush().color().lightness() < 128
            edge.apply_theme(is_dark)
            self.addItem(edge)
            self.edges.append(edge)
            edge.update_path()
            self._trigger_plug(from_port, to_port)
            return edge
        return None

    def apply_theme(self, is_dark=True):
        if is_dark:
            self.setBackgroundBrush(QColor(40, 40, 40))
            self.grid_pen = QPen(QColor("#555555"), 0.5)
        else:
            self.setBackgroundBrush(QColor(255, 255, 255))
            self.grid_pen = QPen(QColor("#d0d0d0"), 0.5)
        
        for node in self.nodes:
            node.apply_theme(is_dark)
        for edge in self.edges:
            edge.apply_theme(is_dark)
        self.update()

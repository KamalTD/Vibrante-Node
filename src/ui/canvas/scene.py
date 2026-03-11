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

# Simple global clipboard for cross-tab copy/paste
global_clipboard = {"nodes": None}

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

        self.history = []
        self.redo_stack = []
        self._undoing = False

        self.grid_size = 20
        self.grid_pen = QPen(QColor("#555555"), 0.5)

    def push_history(self):
        if self._undoing: return
        snapshot = self.to_workflow_model().model_dump()
        self.history.append(snapshot)
        self.redo_stack.clear()
        if len(self.history) > 50: # Limit history
            self.history.pop(0)

    def undo(self):
        if not self.history: return
        self._undoing = True
        current = self.to_workflow_model().model_dump()
        self.redo_stack.append(current)
        
        last_state = self.history.pop()
        model = WorkflowModel.model_validate(last_state)
        self.from_workflow_model(model)
        self._undoing = False

    def redo(self):
        if not self.redo_stack: return
        self._undoing = True
        current = self.to_workflow_model().model_dump()
        self.history.append(current)
        
        next_state = self.redo_stack.pop()
        model = WorkflowModel.model_validate(next_state)
        self.from_workflow_model(model)
        self._undoing = False

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

    def copy_selection(self):
        selected_items = self.selectedItems()
        if not selected_items:
            return None
        
        # Serialize only selected nodes, notes, backdrops and internal connections
        model = WorkflowModel()
        node_ids = set()
        
        for item in selected_items:
            if isinstance(item, NodeWidget):
                node_ids.add(item.instance_id)
                node_model = NodeInstanceModel(
                    instance_id=item.instance_id,
                    node_id=getattr(item.node_definition, 'node_id', item.node_definition.name),
                    position=(item.pos().x(), item.pos().y()),
                    parameters=item.node_definition.parameters.copy()
                )
                model.nodes.append(node_model)
            elif isinstance(item, StickyNote):
                model.sticky_notes.append(StickyNoteModel(
                    id=item.instance_id,
                    position=(item.pos().x(), item.pos().y()),
                    size=(item.rect().width(), item.rect().height()),
                    text=item.get_text(),
                    color=item.bg_color.name()
                ))
            elif isinstance(item, Backdrop):
                model.backdrops.append(BackdropModel(
                    id=item.instance_id,
                    position=(item.pos().x(), item.pos().y()),
                    size=(item.rect().width(), item.rect().height()),
                    title=item.title_item.toPlainText(),
                    color=item.bg_color.name()
                ))
            
        for edge in self.edges:
            if edge.from_port and edge.to_port:
                f_id = edge.from_port.parentItem().instance_id
                t_id = edge.to_port.parentItem().instance_id
                if f_id in node_ids and t_id in node_ids:
                    conn_model = ConnectionModel(
                        from_node=f_id,
                        from_port=edge.from_port.port_definition.name,
                        to_node=t_id,
                        to_port=edge.to_port.port_definition.name
                    )
                    model.connections.append(conn_model)
        
        global_clipboard["nodes"] = model.model_dump()
        return global_clipboard["nodes"]

    def paste_selection(self, target_pos: QPointF = None, pos_offset: QPointF = None):
        data = global_clipboard.get("nodes")
        if not data:
            return
            
        model = WorkflowModel.model_validate(data)
        
        # Calculate offset if target_pos is provided
        if target_pos is not None:
            # Find the top-left of the copied group as reference
            all_positions = []
            for n in model.nodes: all_positions.append(n.position)
            for n in model.sticky_notes: all_positions.append(n.position)
            for n in model.backdrops: all_positions.append(n.position)
            
            if all_positions:
                min_x = min(p[0] for p in all_positions)
                min_y = min(p[1] for p in all_positions)
                pos_offset = target_pos - QPointF(min_x, min_y)
        
        # Default offset if neither target_pos nor pos_offset is provided
        if pos_offset is None:
            pos_offset = QPointF(30, 30)

        # Map old IDs to new IDs to maintain connections
        import uuid
        id_map = {}
        new_items = []
        
        self.clearSelection()
        
        # Paste Nodes
        for node_model in model.nodes:
            new_pos = QPointF(node_model.position[0], node_model.position[1]) + pos_offset
            widget = self.add_node_by_name(node_model.node_id, new_pos)
            if widget:
                new_id = str(uuid.uuid4())
                id_map[node_model.instance_id] = new_id
                widget.instance_id = new_id
                for p_name, p_val in node_model.parameters.items():
                    widget.set_parameter(p_name, p_val, propagate=False)
                widget.setSelected(True)
                new_items.append(widget)
                
        # Paste Connections
        for conn in model.connections:
            from_id = id_map.get(conn.from_node)
            to_id = id_map.get(conn.to_node)
            if from_id and to_id:
                from_w = next((n for n in self.nodes if n.instance_id == from_id), None)
                to_w = next((n for n in self.nodes if n.instance_id == to_id), None)
                if from_w and to_w:
                    self.connect_nodes(from_w, conn.from_port, to_w, conn.to_port)

        # Paste Sticky Notes
        for note_model in model.sticky_notes:
            new_pos = QPointF(note_model.position[0], note_model.position[1]) + pos_offset
            note = self.add_sticky_note(note_model.text, (new_pos.x(), new_pos.y()), 
                                      note_model.size, note_model.color)
            note.setSelected(True)
            new_items.append(note)

        # Paste Backdrops
        for bd_model in model.backdrops:
            new_pos = QPointF(bd_model.position[0], bd_model.position[1]) + pos_offset
            box = self.add_backdrop(bd_model.title, (new_pos.x(), new_pos.y()), 
                                   bd_model.size, bd_model.color)
            box.setSelected(True)
            new_items.append(box)
        
        return new_items

    def to_workflow_model(self) -> WorkflowModel:
        model = WorkflowModel()
        for node_widget in self.nodes:
            # SYNC: Ensure the latest parameters from the UI are captured
            # Many parameters might have changed via widgets without triggering a full sync
            
            node_model = NodeInstanceModel(
                instance_id=node_widget.instance_id,
                node_id=getattr(node_widget.node_definition, 'node_id', node_widget.node_definition.name),
                position=(node_widget.pos().x(), node_widget.pos().y()),
                parameters=node_widget.node_definition.parameters.copy()
            )
            model.nodes.append(node_model)
        for edge in self.edges:
            if edge.from_port and edge.to_port:
                conn_model = ConnectionModel(
                    from_node=edge.from_port.parentItem().instance_id,
                    from_port=edge.from_port.port_definition.name,
                    to_node=edge.to_port.parentItem().instance_id,
                    to_port=edge.to_port.port_definition.name,
                    is_exec=edge.from_port.port_type == "exec"
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
                # SYNC: Apply parameters to UI widgets and node definition
                for p_name, p_val in node_model.parameters.items():
                    widget.set_parameter(p_name, p_val, propagate=False)
                
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
        self.push_history()
        note = StickyNote(text, pos, size, color, instance_id)
        self.addItem(note)
        self.sticky_notes.append(note)
        return note

    def add_backdrop(self, title="Network Box", pos=(0, 0), size=(400, 300), color="#444444", instance_id=None):
        self.push_history()
        box = Backdrop(title, pos, size, color, instance_id)
        self.addItem(box)
        self.backdrops.append(box)
        return box

    def mousePressEvent(self, event):
        # Snap history before potential move or connection change
        if event.button() == Qt.LeftButton:
            self.push_history()
            
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
            self.push_history()
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
            copy_act = QAction(f"Copy {len(selected_nodes)} Nodes", self.parent())
            copy_act.triggered.connect(self.copy_selection)
            menu.addAction(copy_act)
            
            wrap_act = QAction(f"Wrap {len(selected_nodes)} Nodes in Box", self.parent())
            def wrap_selection():
                self.push_history()
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

        if global_clipboard.get("nodes"):
            paste_act = QAction("Paste Nodes", self.parent())
            paste_act.triggered.connect(lambda: self.paste_selection(target_pos=pos))
            menu.addAction(paste_act)
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
            def spawn_node(nid=node_id, p=pos):
                self.push_history()
                self.add_node_by_name(nid, p)
            action.triggered.connect(spawn_node)
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
        self.push_history()
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

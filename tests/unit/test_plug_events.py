import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from PyQt5.QtCore import Qt, QPointF
from src.ui.canvas.scene import NodeScene
from src.nodes.base import BaseNode
from src.core.registry import NodeRegistry

class MockNode(BaseNode):
    name = "MockNode"
    def __init__(self):
        super().__init__()
        self.add_input("in")
        self.add_output("out")
        self.on_plug = AsyncMock()
        self.on_unplug = AsyncMock()
    async def execute(self, inputs): return {}

@pytest.fixture
def scene(qtbot):
    # Setup registry
    NodeRegistry._classes["MockNode"] = MockNode
    scene = NodeScene()
    return scene

@pytest.mark.asyncio
async def test_plug_unplug_flow(scene, qtbot):
    # Add two nodes
    n1 = scene.add_node_by_name("MockNode", QPointF(0, 0))
    n2 = scene.add_node_by_name("MockNode", QPointF(200, 0))
    
    # 1. Test Plug
    edge = scene.connect_nodes(n1, "out", n2, "in")
    assert edge is not None
    
    # Give some time for async tasks to run
    await asyncio.sleep(0.1)
    
    n1.node_definition.on_plug.assert_called_once()
    n2.node_definition.on_plug.assert_called_once()
    
    # 2. Test Unplug via edge deletion
    edge.setSelected(True)
    from PyQt5.QtGui import QKeyEvent
    from PyQt5.QtCore import QEvent
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier)
    scene.keyPressEvent(event)
    
    await asyncio.sleep(0.1)
    
    n1.node_definition.on_unplug.assert_called_once()
    n2.node_definition.on_unplug.assert_called_once()

@pytest.mark.asyncio
async def test_unplug_on_node_remove(scene, qtbot):
    n1 = scene.add_node_by_name("MockNode", QPointF(0, 0))
    n2 = scene.add_node_by_name("MockNode", QPointF(200, 0))
    scene.connect_nodes(n1, "out", n2, "in")
    await asyncio.sleep(0.1)
    
    # Remove node 1
    scene._remove_node_widget(n1)
    await asyncio.sleep(0.1)
    
    n1.node_definition.on_unplug.assert_called_once()
    n2.node_definition.on_unplug.assert_called_once()

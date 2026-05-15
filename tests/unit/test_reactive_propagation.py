"""Regression test for reactive parameter propagation threading crash.

Scenario: message_node wired to console_print → user types in message_node
          → _propagate_all_outputs called from background async thread → crash.

Root cause: _propagate_all_outputs accessed Qt objects (scene().edges,
            w.blockSignals(), w.setText()) from the background AsyncRuntime
            thread, violating Qt's thread affinity rules.

Fix: dispatch _propagate_all_outputs to the main thread via
     QtCore.QTimer.singleShot(0, ...) instead of calling it directly.
"""
import threading
import pytest
from src.utils.qt_compat import QtCore
from src.ui.canvas.scene import NodeScene
from src.nodes.base import BaseNode
from src.core.registry import NodeRegistry

QPointF = QtCore.QPointF


# ---------------------------------------------------------------------------
# Minimal test nodes — one with a text output, one that receives it
# ---------------------------------------------------------------------------

class SourceNode(BaseNode):
    name = "PropTestSource"

    def __init__(self):
        super().__init__()
        self.add_input("msg", "string", widget_type="text", default="")
        self.add_output("out", "string")

    async def on_parameter_changed(self, name, value):
        if name == "msg":
            self.parameters["out"] = value

    async def execute(self, inputs):
        return {"out": inputs.get("msg", ""), "exec_out": True}


class SinkNode(BaseNode):
    name = "PropTestSink"
    received_values = []
    received_threads = []

    def __init__(self):
        super().__init__()
        self.add_input("data", "string", widget_type="text", default="")
        self.add_output("out", "string")

    async def on_parameter_changed(self, name, value):
        if name == "data":
            SinkNode.received_values.append(value)
            SinkNode.received_threads.append(threading.current_thread())
            self.parameters["out"] = value

    async def execute(self, inputs):
        return {"out": inputs.get("data", ""), "exec_out": True}


@pytest.fixture(autouse=True)
def _register_test_nodes():
    NodeRegistry._classes["PropTestSource"] = SourceNode
    NodeRegistry._classes["PropTestSink"] = SinkNode
    SinkNode.received_values.clear()
    SinkNode.received_threads.clear()
    yield
    NodeRegistry._classes.pop("PropTestSource", None)
    NodeRegistry._classes.pop("PropTestSink", None)


@pytest.fixture
def scene(qtbot):
    return NodeScene()


# ---------------------------------------------------------------------------
# Test 1: propagation delivers the value without crashing
# ---------------------------------------------------------------------------

def test_reactive_propagation_no_crash(scene, qtbot):
    """Typing in source node must propagate to sink without crashing."""
    src = scene.add_node_by_name("PropTestSource", QPointF(0, 0))
    sink = scene.add_node_by_name("PropTestSink", QPointF(300, 0))
    scene.connect_nodes(src, "out", sink, "data")

    # Simulate user typing in the source node's text input
    src._update_param("msg", "hello")

    # Allow async coroutine + QTimer.singleShot(0) to fire
    qtbot.waitUntil(lambda: sink.node_definition.parameters.get("data") == "hello", timeout=3000)

    assert sink.node_definition.parameters["data"] == "hello"


# ---------------------------------------------------------------------------
# Test 2: _propagate_all_outputs runs on the Qt main thread
# ---------------------------------------------------------------------------

def test_reactive_propagation_runs_on_main_thread(scene, qtbot):
    """_propagate_all_outputs must execute on the Qt main thread, not the
    background AsyncRuntime thread.  The Qt widget calls inside
    set_parameter (blockSignals, setText, setValue) are unsafe from any
    other thread and are the root cause of the typing-crash bug."""
    from src.ui import node_widget as _nw

    src = scene.add_node_by_name("PropTestSource", QPointF(0, 0))
    sink = scene.add_node_by_name("PropTestSink", QPointF(300, 0))
    scene.connect_nodes(src, "out", sink, "data")

    propagate_threads = []
    original = src._propagate_all_outputs

    def _patched():
        propagate_threads.append(threading.current_thread())
        original()

    src._propagate_all_outputs = _patched

    src._update_param("msg", "thread_check")

    qtbot.waitUntil(lambda: len(propagate_threads) > 0, timeout=3000)

    main_thread = threading.main_thread()
    for t in propagate_threads:
        assert t is main_thread, (
            f"_propagate_all_outputs ran on background thread '{t.name}' — "
            f"this causes Qt widget method calls from a non-main thread, "
            f"crashing the app when typing in a node text field."
        )


# ---------------------------------------------------------------------------
# Test 3: rapid typing (multiple updates) does not crash or lose last value
# ---------------------------------------------------------------------------

def test_rapid_typing_does_not_crash(scene, qtbot):
    """Multiple quick _update_param calls must not crash and must deliver
    the final value."""
    src = scene.add_node_by_name("PropTestSource", QPointF(0, 0))
    sink = scene.add_node_by_name("PropTestSink", QPointF(300, 0))
    scene.connect_nodes(src, "out", sink, "data")

    for char in "hello world":
        src._update_param("msg", char)

    qtbot.waitUntil(
        lambda: sink.node_definition.parameters.get("data") == "d", timeout=3000
    )
    # Last char dispatched was 'd'
    assert sink.node_definition.parameters["data"] == "d"

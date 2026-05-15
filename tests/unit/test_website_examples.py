"""TDD tests for website_examples/ node JSON files.

Run with:  pytest tests/unit/test_website_examples.py -v

These tests must FAIL before the JSON files are created (TDD red phase),
then PASS after all 10 JSON files exist (green phase).
"""
import os
import pytest
from src.nodes.base import BaseNode
from src.core.registry import NodeRegistry

EXAMPLES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "website_examples")
)

EXAMPLES = [
    {
        "file": "regex_replace.json",
        "node_id": "regex_replace",
        "category": "String",
        "required_inputs": ["exec_in", "text", "pattern", "replacement", "ignore_case"],
        "required_outputs": ["result", "match_count", "exec_out"],
    },
    {
        "file": "http_request.json",
        "node_id": "http_request",
        "category": "Network",
        "required_inputs": ["exec_in", "url", "method", "headers", "body", "timeout"],
        "required_outputs": ["response_data", "status_code", "response_text", "success", "exec_out"],
    },
    {
        "file": "file_batch_processor.json",
        "node_id": "file_batch_processor",
        "category": "Files",
        "required_inputs": ["exec_in", "folder_path", "pattern", "recursive"],
        "required_outputs": ["file_list", "file_count", "exec_out"],
    },
    {
        "file": "email_notification.json",
        "node_id": "email_notification",
        "category": "Network",
        "required_inputs": [
            "exec_in", "smtp_host", "smtp_port", "username", "password",
            "from_addr", "to_addr", "subject", "body", "use_tls",
        ],
        "required_outputs": ["sent", "error_msg", "exec_out"],
    },
    {
        "file": "database_query.json",
        "node_id": "database_query",
        "category": "Data",
        "required_inputs": ["exec_in", "db_path", "query", "parameters"],
        "required_outputs": ["rows", "row_count", "columns", "exec_out"],
    },
    {
        "file": "image_resizer.json",
        "node_id": "image_resizer",
        "category": "Image",
        "required_inputs": [
            "exec_in", "input_path", "output_path", "width", "height",
            "keep_aspect", "resample",
        ],
        "required_outputs": ["out_path", "out_width", "out_height", "exec_out"],
    },
    {
        "file": "llm_text_generation.json",
        "node_id": "llm_text_generation",
        "category": "AI",
        "required_inputs": [
            "exec_in", "api_key", "model", "prompt", "system",
            "temperature", "max_tokens",
        ],
        "required_outputs": ["generated_text", "token_count", "success", "exec_out"],
    },
    {
        "file": "folder_monitor.json",
        "node_id": "folder_monitor",
        "category": "Files",
        "required_inputs": ["exec_in", "folder_path", "pattern", "watch_seconds"],
        "required_outputs": ["new_files", "exec_out"],
    },
    {
        "file": "hou_sop_chain.json",
        "node_id": "hou_sop_chain",
        "category": "Houdini",
        "required_inputs": ["exec_in", "geo_name", "box_size", "extrude_dist", "extrude_divs"],
        "required_outputs": ["geo_path", "display_sop", "exec_out"],
    },
    {
        "file": "prism_multi_asset_publisher.json",
        "node_id": "prism_multi_asset_publisher",
        "category": "Prism",
        "required_inputs": ["exec_in", "asset_names", "entity_type", "task", "version_comment"],
        "required_outputs": ["published", "failed", "publish_count", "exec_out"],
    },
]

_ALL_IDS = [e["node_id"] for e in EXAMPLES]


@pytest.fixture(autouse=True)
def _clean_registry():
    """Remove example node_ids from registry before and after each test."""
    for node_id in _ALL_IDS:
        NodeRegistry._definitions.pop(node_id, None)
        NodeRegistry._classes.pop(node_id, None)
    yield
    for node_id in _ALL_IDS:
        NodeRegistry._definitions.pop(node_id, None)
        NodeRegistry._classes.pop(node_id, None)


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_json_file_exists(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    assert os.path.isfile(path), f"Missing example file: {path}"


# ---------------------------------------------------------------------------
# Load via NodeRegistry
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_loads_successfully(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    result = NodeRegistry.load_node(path)
    assert result is True, (
        f"load_node failed for {example['file']}:\n{NodeRegistry.last_error}"
    )


@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_class_is_registered(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    NodeRegistry.load_node(path)
    cls = NodeRegistry.get_class(example["node_id"])
    assert cls is not None, f"Class not registered for node_id '{example['node_id']}'"
    assert issubclass(cls, BaseNode)


# ---------------------------------------------------------------------------
# Definition metadata
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_has_correct_category(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    NodeRegistry.load_node(path)
    defn = NodeRegistry.get_definition(example["node_id"])
    assert defn is not None
    assert defn.category == example["category"], (
        f"{example['node_id']}: expected category '{example['category']}', got '{defn.category}'"
    )


# ---------------------------------------------------------------------------
# Port presence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_has_required_inputs(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    NodeRegistry.load_node(path)
    defn = NodeRegistry.get_definition(example["node_id"])
    assert defn is not None
    input_names = {p.name for p in defn.inputs}
    for port in example["required_inputs"]:
        assert port in input_names, (
            f"{example['node_id']}: missing input port '{port}'. Present: {sorted(input_names)}"
        )


@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_has_required_outputs(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    NodeRegistry.load_node(path)
    defn = NodeRegistry.get_definition(example["node_id"])
    assert defn is not None
    output_names = {p.name for p in defn.outputs}
    for port in example["required_outputs"]:
        assert port in output_names, (
            f"{example['node_id']}: missing output port '{port}'. Present: {sorted(output_names)}"
        )


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("example", EXAMPLES, ids=_ALL_IDS)
def test_example_node_instantiates(example):
    path = os.path.join(EXAMPLES_DIR, example["file"])
    NodeRegistry.load_node(path)
    cls = NodeRegistry.get_class(example["node_id"])
    assert cls is not None
    instance = cls()
    assert isinstance(instance, BaseNode)

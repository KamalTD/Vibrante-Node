from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class PortModel(BaseModel):
    name: str
    type: str = "any"
    widget_type: Optional[str] = None # 'text', 'int', 'float', 'bool', 'dropdown', 'slider', 'text_area'
    options: Optional[List[str]] = None # For dropdown

class StickyNoteModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    position: Tuple[float, float]
    size: Tuple[float, float] = (200.0, 150.0)
    text: str = "New Note"
    color: str = "#ffffcc"

class BackdropModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    position: Tuple[float, float]
    size: Tuple[float, float] = (400.0, 300.0)
    title: str = "Network Box"
    color: str = "#444444"

class NodeDefinitionJSON(BaseModel):
    node_id: str
    name: str
    description: str = ""
    category: str = "General"
    icon_path: Optional[str] = None
    inputs: List[PortModel] = Field(default_factory=list)
    outputs: List[PortModel] = Field(default_factory=list)
    python_code: str

class NodeInstanceModel(BaseModel):
    instance_id: UUID = Field(default_factory=uuid4)
    node_id: str  # Reference to NodeDefinitionJSON.node_id
    position: Tuple[float, float]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    state: str = "idle"

class ConnectionModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    from_node: UUID
    from_port: str
    to_node: UUID
    to_port: str
    is_exec: bool = False

class WorkflowModel(BaseModel):
    nodes: List[NodeInstanceModel] = Field(default_factory=list)
    connections: List[ConnectionModel] = Field(default_factory=list)
    sticky_notes: List[StickyNoteModel] = Field(default_factory=list)
    backdrops: List[BackdropModel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

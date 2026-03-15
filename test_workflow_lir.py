import asyncio
import os
from uuid import uuid4
from src.core.graph import GraphManager
from src.core.models import NodeInstanceModel, ConnectionModel, WorkflowModel
from src.core.engine import NetworkExecutor
from src.core.registry import NodeRegistry

async def test_workflow_lir():
    # 1. Register nodes
    NodeRegistry.load_all("nodes")
    
    # 2. Setup Graph mirroring the user's workflow
    gm = GraphManager()
    
    # IDs from the workflow JSON
    lir_id = uuid4() # fe631af6-e485-407a-b233-df4f46452c6d
    cp_id = uuid4()  # 6b2ba5fa-5787-45ec-8fa1-2b08b1e4396c
    
    # Use a real directory for testing
    test_dir = os.path.abspath("test_images_repro")
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "img1.png"), "w") as f: f.write("test")
    
    gm.add_node(NodeInstanceModel(
        instance_id=lir_id,
        node_id="list_images_recursive",
        position=(0, 0),
        parameters={"folder_path": test_dir, "recursive": False}
    ))
    
    gm.add_node(NodeInstanceModel(
        instance_id=cp_id,
        node_id="console_print",
        position=(300, 0),
        parameters={"data": ""}
    ))
    
    # Connections
    # LIR.image_paths -> CP.data
    gm.add_connection(ConnectionModel(
        from_node=lir_id, from_port="image_paths",
        to_node=cp_id, to_port="data",
        is_exec=False
    ))
    # LIR.exec_out -> CP.exec_in
    gm.add_connection(ConnectionModel(
        from_node=lir_id, from_port="exec_out",
        to_node=cp_id, to_port="exec_in",
        is_exec=True
    ))
    
    print("\n--- Running Repro Workflow ---")
    executor = NetworkExecutor(gm)
    
    outputs = []
    executor.node_log.connect(lambda nid, msg, lvl: outputs.append(f"LOG [{nid}]: {msg}"))
    
    await executor.run()
    
    print("\nLogs gathered:")
    for log in outputs:
        print(log)
        
    # Cleanup
    os.remove(os.path.join(test_dir, "img1.png"))
    os.rmdir(test_dir)

if __name__ == "__main__":
    asyncio.run(test_workflow_lir())

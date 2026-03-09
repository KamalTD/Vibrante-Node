import json
import os
from typing import Optional
from src.core.models import WorkflowModel

class PersistenceManager:
    @staticmethod
    def save_workflow(model: WorkflowModel, file_path: str) -> bool:
        try:
            with open(file_path, "w") as f:
                f.write(model.model_dump_json(indent=4))
            return True
        except Exception as e:
            print(f"Error saving workflow to {file_path}: {e}")
            return False

    @staticmethod
    def load_workflow(file_path: str) -> Optional[WorkflowModel]:
        try:
            if not os.path.exists(file_path):
                return None
            with open(file_path, "r") as f:
                data = f.read()
            return WorkflowModel.model_validate_json(data)
        except Exception as e:
            print(f"Error loading workflow from {file_path}: {e}")
            return None

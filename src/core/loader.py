import importlib.util
import os
import sys
from typing import Type, List
from src.nodes.base import BaseNode, NodeRegistry

class ScriptLoader:
    @staticmethod
    def load_node_from_file(file_path: str) -> bool:
        """
        Dynamically loads a node from a Python script and registers it.
        The script must contain a 'register_node' function that returns a BaseNode class.
        """
        if not os.path.exists(file_path) or not file_path.endswith('.py'):
            return False

        module_name = os.path.splitext(os.path.basename(file_path))[0]
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'register_node'):
                node_class = module.register_node()
                if issubclass(node_class, BaseNode):
                    NodeRegistry.register(node_class)
                    return True
            return False
        except Exception as e:
            print(f"Error loading script {file_path}: {e}")
            return False

    @staticmethod
    def scan_directory(directory_path: str) -> int:
        """
        Scans a directory for .py files and tries to load them as nodes.
        Returns the number of successfully loaded nodes.
        """
        if not os.path.isdir(directory_path):
            return 0

        count = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                full_path = os.path.join(directory_path, filename)
                if ScriptLoader.load_node_from_file(full_path):
                    count += 1
        return count

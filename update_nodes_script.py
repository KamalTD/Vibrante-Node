import os
import json
import re

def update_node(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return

    # 1. Normalize JSON Port Definitions
    inputs = data.get('inputs', [])
    for p in inputs:
        if p.get('name') == 'exec_in':
            p['type'] = 'exec'
    
    outputs = data.get('outputs', [])
    for p in outputs:
        if p.get('name') == 'exec_out':
            p['type'] = 'exec'
    
    data['inputs'] = inputs
    data['outputs'] = outputs

    # 2. Update Python Code logic
    code = data.get('python_code', '')
    if not code:
        return

    # Normalize __init__ port types if it's a class-based node
    code = re.sub(r'self\.add_input\("exec_in",\s*["\']any["\']\)', 'self.add_input("exec_in", "exec")', code)
    code = re.sub(r'self\.add_output\("exec_out",\s*["\']any["\']\)', 'self.add_output("exec_out", "exec")', code)

    if 'def execute' in code:
        # Check if exec_out is already being set
        if not re.search(r'self\.set_output\([\'"]exec_out[\'"]', code):
            # Split into lines to find the end of execute
            lines = code.split('\n')
            
            # Find the start of execute to know the context
            exec_start_idx = -1
            for i, line in enumerate(lines):
                if re.match(r'^\s*(async\s+)?def\s+execute\b', line):
                    exec_start_idx = i
                    break
            
            if exec_start_idx != -1:
                # Find the LAST return or last line of the execute function
                # We look for the next function definition or end of file
                # to find the scope of execute.
                
                exec_indent = len(lines[exec_start_idx]) - len(lines[exec_start_idx].lstrip())
                last_return_idx = -1
                
                for i in range(exec_start_idx + 1, len(lines)):
                    line = lines[i]
                    if line.strip() and not line.strip().startswith('#'):
                        current_indent = len(line) - len(line.lstrip())
                        if current_indent <= exec_indent and i > exec_start_idx + 1:
                            # We exited the function scope
                            break
                        if 'return' in line:
                            last_return_idx = i
                
                if last_return_idx != -1:
                    indent = lines[last_return_idx][:lines[last_return_idx].find('return')]
                    lines.insert(last_return_idx, f'{indent}await self.set_output("exec_out", True)')
                    code = '\n'.join(lines)
                else:
                    # No return found, just append to end of function scope (simplistic)
                    # For now, let's just append to the end if it's a simple execute
                    if 'def register_node' not in code:
                         code += '\n    await self.set_output("exec_out", True)'
        else:
            # Ensure existing calls use await and correct syntax
            code = re.sub(r'(?<!await\s)self\.set_output\(([\'"])exec_out\1', r'await self.set_output(\1exec_out\1', code)
            
        data['python_code'] = code
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Updated {os.path.basename(path)}")

for directory in ['nodes', 'node_examples']:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                update_node(os.path.join(directory, filename))

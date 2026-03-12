import os
import json

def update_node(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 1. Normalize Inputs
    inputs = data.get('inputs', [])
    has_exec_in = False
    for p in inputs:
        if p.get('name') == 'exec_in':
            p['type'] = 'exec'
            has_exec_in = True
        elif p.get('type') == 'exec':
            p['type'] = 'any'
            
    if not has_exec_in:
        inputs.insert(0, {'name': 'exec_in', 'type': 'exec'})
    data['inputs'] = inputs
    
    # 2. Normalize Outputs
    outputs = data.get('outputs', [])
    has_exec_out = False
    for p in outputs:
        if p.get('name') == 'exec_out':
            p['type'] = 'exec'
            has_exec_out = True
        elif p.get('type') == 'exec':
            p['type'] = 'any'
            
    if not has_exec_out:
        outputs.insert(0, {'name': 'exec_out', 'type': 'exec'})
    data['outputs'] = outputs
    
    # 3. Update Python Code logic
    code = data.get('python_code', '')
    if 'execute' in code:
        if 'exec_out' not in code:
            if 'return' in code:
                # Add it before the final return in execute
                lines = code.split('\n')
                for i in range(len(lines) - 1, -1, -1):
                    line = lines[i]
                    if 'return' in line and not line.strip().startswith('#'):
                        # Ensure we are in execute function if possible
                        # This is naive but works for the current node structures
                        indent = line[:line.find('return')]
                        lines.insert(i, f'{indent}self.set_output("exec_out", True)')
                        break
                code = '\n'.join(lines)
            else:
                # Append to end
                code += '\n    self.set_output("exec_out", True)'
        data['python_code'] = code
        
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Updated {os.path.basename(path)}")

for directory in ['nodes', 'node_examples']:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                update_node(os.path.join(directory, filename))

import json
import traceback

p = r"e:\AI\Vibrante-Node\source\nodes\create_list.json"
with open(p, 'r', encoding='utf-8') as f:
    data = json.load(f)
code = data.get('python_code')
print('--- Python code repr ---')
print(repr(code))
print('--- End repr ---')
try:
    compile(code, '<string>', 'exec')
    print('Compile OK')
    ns = {}
    exec(code, ns)
    print('Exec OK, namespace keys:', list(ns.keys()))
except Exception as e:
    print('Exception during compile/exec:')
    traceback.print_exc()

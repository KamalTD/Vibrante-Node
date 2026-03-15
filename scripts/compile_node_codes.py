import json
import traceback
from pathlib import Path

node_files = [
    'nodes/list_length.json',
    'nodes/create_dictionary.json',
    'nodes/get_dict_value.json',
    'nodes/set_dict_value.json'
]

base = Path(__file__).resolve().parent.parent
success = True
for nf in node_files:
    p = base / nf
    print('---', nf)
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        code = data.get('python_code', '')
        # show a short preview
        print('preview:', code[:120].replace('\n', '\\n'))
        compile(code, '<string>', 'exec')
        print('compile: OK')
    except Exception:
        success = False
        print('compile: ERROR')
        traceback.print_exc()

print('\nOverall OK' if success else '\nSome files failed to compile')

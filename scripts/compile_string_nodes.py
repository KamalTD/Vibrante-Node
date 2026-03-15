import json
import traceback
from pathlib import Path

base = Path(__file__).resolve().parent.parent
files = [
    'nodes/concat.json',
    'nodes/split.json',
    'nodes/replace.json',
    'nodes/lowercase.json',
    'nodes/uppercase.json',
    'nodes/string_length.json'
]

ok = True
for f in files:
    p = base / f
    print('---', f)
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        code = data.get('python_code', '')
        print('preview:', code[:100].replace('\n','\\n'))
        compile(code, '<string>', 'exec')
        print('compile: OK')
    except Exception:
        ok = False
        print('compile: ERROR')
        traceback.print_exc()

print('\nAll OK' if ok else '\nSome files failed to compile')

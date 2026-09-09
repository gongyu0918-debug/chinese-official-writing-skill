import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PY = 'C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe'

def run(name, command, timeout=600):
    started = time.time()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
    record = dict(command=command, exit_code=result.returncode, seconds=round(time.time()-started,3), stdout=result.stdout, stderr=result.stderr)
    (OUT / (name+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(name=name,exit_code=result.returncode,seconds=record['seconds'],tail=(result.stdout+result.stderr)[-2200:]),ensure_ascii=False))
    return result.returncode

if __name__ == "__main__":
    name, command = sys.argv[1], sys.argv[2:]
    if name.endswith("-publish"):
        attempt = OUT / (name + "-attempt.json")
        assert not attempt.exists(), "Inspect the existing attempt and receipt; do not republish."
        attempt.write_text(json.dumps({"formal_attempt": 1, "command": command}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    sys.exit(run(name, command))

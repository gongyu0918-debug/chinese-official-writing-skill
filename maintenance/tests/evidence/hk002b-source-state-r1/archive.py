"""Keep frozen inputs, every call receipt and response; exclude runtime homes."""
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
TARGET=HERE/"raw"
SOURCES={"prototype":"hk002b-prototype-r1-glm","core-r1":"hk002b-core-r1","core-r2":"hk002b-core-r2"}

def archive():
    TARGET.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for stage,directory in SOURCES.items():
        source=ROOT/"output"/directory
        for path in sorted(source.rglob("*")):
            if not path.is_file(): continue
            rel=path.relative_to(source)
            if any(part in {"home","work","__pycache__"} for part in rel.parts): continue
            if path.suffix in {".pyc",".lock"}: continue
            target=TARGET/stage/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                assert target.read_bytes()==path.read_bytes(), "existing evidence must not be overwritten"
            else:
                shutil.copyfile(path,target)
            manifest.append({"path":target.relative_to(HERE).as_posix(),"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"bytes":target.stat().st_size})
    (HERE/"archive-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"files":len(manifest),"bytes":sum(row["bytes"] for row in manifest)}))

if __name__=="__main__": archive()

from pathlib import Path
import tempfile, subprocess, sys

root=Path(__file__).resolve().parents[1]
tests=[
    [sys.executable,"-m","compileall","-q","src","run.py"],
    [sys.executable,"scripts","validate_all.py"] if False else None,
]
r=subprocess.run([sys.executable,"scripts/validate_all.py"],cwd=root)
if r.returncode: raise SystemExit(r.returncode)
r=subprocess.run([sys.executable,"-m","pytest","-q","tests"],cwd=root)
raise SystemExit(r.returncode)

python -m compileall src run.py
python scripts/validate_all.py
python -m pytest -q tests
python run.py --benchmark benchmarks/benchmark_manifest.yaml
git status
git log --oneline --decorate -10

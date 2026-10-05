from pathlib import Path
from .io_utils import load_yaml, save_json

def generate_fix_declaration(benchmark_report, output):
    failures=[(k,v) for k,v in benchmark_report["gates"].items() if v["status"]=="FAIL"]
    worst=failures[0] if failures else None
    doc={
      "worst_gate": worst[0] if worst else "PENDING",
      "failing_number": worst[1] if worst else None,
      "root_cause":"To be written from benchmark evidence; never invent this.",
      "fix":"To be implemented and committed.",
      "prediction":"Expected metric change after fix.",
      "before_after_command":"python run.py --benchmark benchmarks/benchmark_manifest.yaml"
    }
    save_json(doc,output)
    return doc

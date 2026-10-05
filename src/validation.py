import json
from pathlib import Path

def validate_output(path):
    d=json.loads(Path(path).read_text(encoding="utf-8"))
    required=["schema_version","property_id","rooms","adjacency","measurements","damage","scope"]
    missing=[x for x in required if x not in d]
    return {"valid":not missing,"missing":missing}

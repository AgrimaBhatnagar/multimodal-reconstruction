from pathlib import Path
import json
required=[
"README.md","requirements.txt","run.py","schemas/output_schema.json",
"protocols/capture_protocol.md","configs/default.yaml",
"src/lidar.py","src/geometry.py","src/openings.py","src/damage.py",
"src/stitching.py","src/measurements.py","src/uncertainty.py",
"src/calibration.py","src/benchmark.py","src/fix_loop.py",
"src/photo_video.py","src/rendering.py","src/pipeline.py"
]
missing=[p for p in required if not Path(p).exists()]
print("required_files:",len(required),"missing:",missing)
raise SystemExit(1 if missing else 0)

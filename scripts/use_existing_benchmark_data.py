from pathlib import Path
import argparse, shutil

ap=argparse.ArgumentParser(description="Locate benchmark data from the original spatial-reconstruction repo")
ap.add_argument("--source-root", default=None,
                help="Path to original spatial-reconstruction repository")
ap.add_argument("--capture", default="benchmarks/extracted/single_room/c00a170fe1")
args=ap.parse_args()

here=Path.cwd()
source=Path(args.source_root) if args.source_root else here.parent/"spatial-reconstruction"
candidate=source/args.capture
print("Project:", here)
print("Source repo:", source)
print("Requested capture:", candidate)
if candidate.exists():
    print("FOUND")
    print(candidate.resolve())
    print("\nRun:")
    print(f'python run.py --capture "{candidate.resolve()}" --tier lidar --name single_room_lidar')
else:
    print("NOT FOUND")
    print("\nIf your data is elsewhere, pass --source-root C:\\path\\to\\spatial-reconstruction")

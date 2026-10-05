import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from src.lidar import reconstruct, pcd_numpy
from src.pipeline import geometry_from_points

capture = r"..\spatial-reconstruction\benchmarks\extracted\single_room\c00a170fe1"

results = {}

for mode in [False, True]:
    pcd, metadata = reconstruct(
        capture,
        refine_registration=mode,
    )

    geometry = geometry_from_points(
        pcd_numpy(pcd),
        "lidar",
    )

    key = "refinement_on" if mode else "refinement_off"

    results[key] = {
        "lidar_metadata": metadata,
        "geometry": geometry,
    }

    print("\n" + "=" * 60)
    print(key)
    print("=" * 60)
    print(json.dumps(
        {
            "metadata": metadata,
            "geometry": geometry,
        },
        indent=2,
        default=lambda x: x.tolist()
        if hasattr(x, "tolist")
        else str(x),
    ))

with open(
    r"benchmarks\results\fix_loop_sample.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        results,
        f,
        indent=2,
        default=lambda x: x.tolist()
        if hasattr(x, "tolist")
        else str(x),
    )

print("\nWrote benchmarks\\results\\fix_loop_sample.json")

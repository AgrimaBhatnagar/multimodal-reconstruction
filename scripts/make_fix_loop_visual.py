from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lidar import reconstruct, pcd_numpy


CAPTURE = ROOT / ".." / "spatial-reconstruction" / "benchmarks" / "extracted" / "single_room" / "c00a170fe1"
OUT = ROOT / "benchmarks" / "results"

OUT.mkdir(parents=True, exist_ok=True)


def sample_points(points: np.ndarray, max_points: int = 12000) -> np.ndarray:
    if len(points) <= max_points:
        return points

    rng = np.random.default_rng(42)
    idx = rng.choice(len(points), size=max_points, replace=False)
    return points[idx]


def save_plan(points: np.ndarray, path: Path, title: str) -> None:
    points = sample_points(points)

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.scatter(points[:, 0], points[:, 1], s=1)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title(title)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    pcd_before, meta_before = reconstruct(
        CAPTURE,
        refine_registration=False,
    )

    pcd_after, meta_after = reconstruct(
        CAPTURE,
        refine_registration=True,
    )

    before = pcd_numpy(pcd_before)
    after = pcd_numpy(pcd_after)

    save_plan(
        before,
        OUT / "fix_loop_before.png",
        "LiDAR registration - before correction",
    )

    save_plan(
        after,
        OUT / "fix_loop_after.png",
        "LiDAR registration - after correction",
    )

    print("Created:")
    print(OUT / "fix_loop_before.png")
    print(OUT / "fix_loop_after.png")

    print("\nBefore:")
    print(meta_before["registration_refinement"])

    print("\nAfter:")
    print(meta_after["registration_refinement"])


if __name__ == "__main__":
    main()
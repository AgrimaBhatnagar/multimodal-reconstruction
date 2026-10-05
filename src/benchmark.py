from pathlib import Path
import json
import time

from .pipeline import build_lidar, build_photos, build_video
from .calibration import evaluate
from .io_utils import load_yaml, save_json


REQUIRED_GATES = [
    "opening_width_2cm_85pct",
    "ceiling_height_1_5cm",
    "repeat_capture_spread_1cm",
    "wall_repeatability_1cm_or_0_5pct",
    "photo_whole_property_stitch",
    "photo_wall_accuracy_8pct",
    "video_wall_accuracy_3pct",
    "lidar_calibration",
    "video_calibration",
    "photo_calibration",
    "drift_ablation",
    "head_to_head_consumer_app",
]


def run_capture(entry, output_root):
    tier = entry["tier"]
    capture = entry["capture"]
    name = entry["name"]

    out = Path(output_root) / name
    out.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    if tier == "lidar":
        result = build_lidar(capture, tier, out, name)
    elif tier == "photos":
        result = build_photos(capture, tier, out, name)
    elif tier == "video":
        result = build_video(capture, tier, out, name)
    else:
        raise ValueError(f"Unsupported tier: {tier}")

    elapsed = time.perf_counter() - start

    return {
        "name": name,
        "tier": tier,
        "capture": str(capture),
        "runtime_seconds": round(elapsed, 3),
        "result": result,
    }


def compare_gt(pred, values, tolerance):
    if not pred or not values:
        return {
            "status": "PENDING",
            "reason": "No ground truth",
        }

    metrics = evaluate(pred, values, tolerance)

    return {
        "status": (
            "PASS"
            if metrics["pass_rate"] >= 0.85
            else "FAIL"
        ),
        **metrics,
    }


def summarize_result(result):
    """
    Extract quantitative fields already produced by the reconstruction
    pipeline without inventing ground-truth accuracy.
    """

    summary = {
        "available": True,
    }

    if not isinstance(result, dict):
        summary["available"] = False
        summary["reason"] = "Pipeline did not return a dictionary"
        return summary

    # Common reconstruction metrics
    for key in [
        "point_count",
        "points",
        "original_points",
        "cleaned_points",
        "area_m2",
        "estimated_floor_plan_area_m2",
        "perimeter_m",
        "estimated_floor_plan_perimeter_m",
        "ceiling_height_m",
        "vertical_extent_m",
        "wall_count",
        "opening_count",
    ]:
        if key in result:
            summary[key] = result[key]

    # Preserve nested geometry/measurement information when available.
    for key in [
        "geometry",
        "measurements",
        "calibration",
        "trajectory",
        "confidence",
        "timing",
    ]:
        if key in result:
            summary[key] = result[key]

    return summary


def run_benchmark(manifest):
    cfg = load_yaml(manifest)

    results_root = Path(
        cfg.get("results_dir", "benchmarks/results")
    )
    results_root.mkdir(
        parents=True,
        exist_ok=True
    )

    rows = []

    for entry in (cfg.get("captures") or []):
        capture_result = run_capture(
            entry,
            results_root
        )

        capture_result["summary"] = summarize_result(
            capture_result["result"]
        )

        # Save an individual machine-readable result.
        capture_file = (
            results_root
            / entry["name"]
            / "benchmark_result.json"
        )

        save_json(
            capture_result,
            capture_file
        )

        rows.append(capture_result)

    # Start every gate as PENDING.
    #
    # We deliberately do not manufacture PASS/FAIL values.
    # Gates become evaluable only when the required experimental
    # evidence is supplied.
    gates = {
        gate: {
            "status": "PENDING",
            "reason": (
                "Required physical benchmark evidence "
                "not supplied"
            ),
        }
        for gate in REQUIRED_GATES
    }

    # Ground-truth driven gates.
    ground_truth = cfg.get("ground_truth") or {}

    opening_predicted = (
        ground_truth.get("opening_predicted_m") or []
    )
    opening_measured = (
        ground_truth.get("opening_measured_m") or []
    )

    if opening_predicted and opening_measured:
        gates["opening_width_2cm_85pct"] = compare_gt(
            opening_predicted,
            opening_measured,
            0.02,
        )

    ceiling_predicted = (
        ground_truth.get("ceiling_predicted_m") or []
    )
    ceiling_measured = (
        ground_truth.get("ceiling_measured_m") or []
    )

    if ceiling_predicted and ceiling_measured:
        gates["ceiling_height_1_5cm"] = compare_gt(
            ceiling_predicted,
            ceiling_measured,
            0.015,
        )

    report = {
        "manifest": str(manifest),
        "captures": len(rows),
        "capture_results": rows,
        "gates": gates,
        "pass_count": sum(
            gate["status"] == "PASS"
            for gate in gates.values()
        ),
        "fail_count": sum(
            gate["status"] == "FAIL"
            for gate in gates.values()
        ),
        "pending_count": sum(
            gate["status"] == "PENDING"
            for gate in gates.values()
        ),
    }

    save_json(
        report,
        results_root / "benchmark_report.json"
    )

    return report
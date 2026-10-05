from pathlib import Path
import csv, json, statistics, subprocess, sys, time
from .pipeline import build_lidar, build_photos, build_video
from .calibration import evaluate
from .io_utils import load_yaml, save_json

REQUIRED_GATES=[
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
"head_to_head_consumer_app"
]

def run_capture(entry, output_root):
    tier=entry["tier"]; capture=entry["capture"]; name=entry["name"]
    out=Path(output_root)/name
    if tier=="lidar": return build_lidar(capture,tier,out,name)
    if tier=="photos": return build_photos(capture,tier,out,name)
    if tier=="video": return build_video(capture,tier,out,name)
    raise ValueError(tier)

def compare_gt(pred, values, tolerance):
    if not values: return {"status":"PENDING","reason":"No ground truth"}
    return {"status":"PASS" if evaluate(pred,values,tolerance)["pass_rate"]>=0.85 else "FAIL",
            **evaluate(pred,values,tolerance)}

def run_benchmark(manifest):
    cfg=load_yaml(manifest)
    results_root=Path(cfg.get("results_dir","benchmarks/results"))
    results_root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for e in (cfg.get("captures") or []):
        r=run_capture(e,results_root)
        rows.append(r)
    gates={g:{"status":"PENDING","reason":"Required physical benchmark evidence not supplied"} for g in REQUIRED_GATES}
    # Ground-truth driven gates
    gt=cfg.get("ground_truth",{})
    if gt.get("opening_predicted_m") and gt.get("opening_measured_m"):
        gates["opening_width_2cm_85pct"]=compare_gt(gt["opening_predicted_m"],gt["opening_measured_m"],0.02)
    if gt.get("ceiling_predicted_m") and gt.get("ceiling_measured_m"):
        gates["ceiling_height_1_5cm"]=compare_gt(gt["ceiling_predicted_m"],gt["ceiling_measured_m"],0.015)
    report={"manifest":str(manifest),"captures":len(rows),"gates":gates,
            "pass_count":sum(x["status"]=="PASS" for x in gates.values()),
            "fail_count":sum(x["status"]=="FAIL" for x in gates.values()),
            "pending_count":sum(x["status"]=="PENDING" for x in gates.values())}
    save_json(report,results_root/"benchmark_report.json")
    return report

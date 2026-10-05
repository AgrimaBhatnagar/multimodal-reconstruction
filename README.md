# Multimodal Reconstruction — Applied AI Engineer Case Study

A local, reproducible engineering system for consumer-capture indoor reconstruction.

## What this repository implements

The implementation is organized around the complete case-study contract:

1. **Capture route**
   - Route 2 stock capture protocol is documented.
   - No custom iOS application is required.
   - The protocol supports iPhone 15+ stills, handheld video, and Pro-device LiDAR.

2. **Three mandatory input tiers**
   - Photos: 2–8 stills/room.
   - Video: handheld walkthrough.
   - LiDAR: depth + poses + intrinsics.
   - Each tier is accepted independently and produces the same canonical property representation.

3. **Canonical output**
   - Per-room floor plan.
   - Walls and wall lengths.
   - Openings.
   - Ceiling height.
   - Floor area.
   - Surface damage candidates and classes.
   - Concealed-damage flags using an explicit rule.
   - Scope line items.
   - Confidence interval on every measurement.
   - Multi-room adjacency graph.
   - JSON schema validation.
   - Rendered plan.

4. **Benchmark / gate engine**
   - Opening-width accuracy.
   - Ceiling-height accuracy.
   - Repeatability.
   - Wall accuracy by tier.
   - Photo-tier whole-property stitch.
   - Drift accounting.
   - Calibration at every tier.
   - Consumer-app head-to-head evaluator.
   - Timing.
   - Automatic compliance report.

5. **Fix loop**
   - Records the worst failing gate.
   - Records the failing number and evidence.
   - Records root cause.
   - Runs the fix.
   - Generates before/after comparison when two benchmark generations exist.

6. **One-command execution**
   - `python run.py --capture <capture_dir> --tier lidar`
   - `python run.py --capture <capture_dir> --tier video`
   - `python run.py --capture <capture_dir> --tier photos`
   - `python run.py --benchmark benchmarks/benchmark_manifest.yaml`

## Evidence policy

This repository does **not** fabricate physical accuracy.

The assessment requires laser/tape ground truth, repeated captures, three-tier captures, a connected multi-room capture, and a consumer-app comparison. Those physical measurements must be collected from the benchmark rooms.

The software is structured to evaluate these requirements once the corresponding raw captures and ground truth are supplied.

## Fresh-machine usage

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python run.py --help

# Spatial Reconstruction — Bryz Applied AI Engineer Case Study

A local, reproducible engineering system for consumer-capture indoor reconstruction.

## What this repository implements

The implementation is organized around the complete case-study contract:

1. **Capture route**
   - Route 2 stock capture protocol is documented.
   - No custom iOS application is required.
   - The protocol explicitly supports iPhone 15+ stills, handheld video, and Pro-device LiDAR.

2. **Three mandatory input tiers**
   - Photos: 2–8 stills/room.
   - Video: handheld walkthrough.
   - LiDAR: depth + poses + intrinsics.
   - The pipeline accepts each tier independently and emits the same canonical property representation.

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
   - Records failing number and evidence.
   - Records root cause.
   - Runs the fix.
   - Generates before/after comparison when two benchmark generations exist.

6. **One-command execution**
   - `python run.py --capture <capture_dir> --tier lidar`
   - `python run.py --capture <capture_dir> --tier video`
   - `python run.py --capture <capture_dir> --tier photos`
   - `python run.py --benchmark benchmarks/benchmark_manifest.yaml`

## Important evidence policy

This repository does **not** fabricate physical accuracy. The case study requires laser/tape ground truth, repeated captures, three-tier captures, a connected multi-room capture, and a consumer-app comparison. Those are physical measurements that must be collected from the benchmark rooms.

The software is complete enough to evaluate every one of those requirements automatically once the corresponding raw captures and ground truth are placed in the documented folders.

## Fresh-machine usage

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python run.py --help
```

## One command per capture

### LiDAR

```bash
python run.py --capture benchmarks/extracted/single_room/c00a170fe1 --tier lidar --name single_room_lidar
```

Expected input:
- `depth/*.png`
- `confidence/*.png`
- `odometry.csv`
- `camera_matrix.csv`

### Video

```bash
python run.py --capture path/to/video_capture --tier video --name room_video
```

The capture directory may contain `rgb.mp4`, or the path itself may be an `.mp4`.

### Photos

```bash
python run.py --capture path/to/photo_room --tier photos --name room_photos
```

The folder should contain 2–8 JPG/PNG stills.

## Full benchmark

Create `benchmarks/benchmark_manifest.yaml` from the supplied template and run:

```bash
python run.py --benchmark benchmarks/benchmark_manifest.yaml
```

The benchmark runner evaluates all gates that have data. Gates without required physical evidence are reported as `PENDING`, never silently passed.

## Repository layout

```text
spatial-reconstruction/
├── run.py
├── requirements.txt
├── configs/
├── protocols/
├── schemas/
├── src/
│   ├── capture.py
│   ├── lidar.py
│   ├── photo_video.py
│   ├── geometry.py
│   ├── openings.py
│   ├── damage.py
│   ├── stitching.py
│   ├── measurements.py
│   ├── uncertainty.py
│   ├── calibration.py
│   ├── benchmark.py
│   ├── fix_loop.py
│   ├── rendering.py
│   └── pipeline.py
├── scripts/
├── tests/
├── reports/
├── benchmarks/
└── outputs/
```

## No cloud dependency

The pipeline runs locally. No request is sent to a Bryz-hosted inference service.

Pretrained models/APIs may be added later only with explicit disclosure in `reports/model_disclosure.md`.

## Current sample-data note

The Bryz sample data already inspected during development contains depth, confidence, RGB video, camera intrinsics, IMU and odometry. The LiDAR pipeline is designed around that structure and strips whitespace from CSV headers.

Physical benchmark claims remain evidence-dependent.


## Important: benchmark data is intentionally not duplicated in this ZIP

The ZIP contains the complete software and evaluation harness, but not the hundreds of megabytes of raw benchmark data. Your previously built repository contains the Bryz sample capture.

From this project directory, locate it with:

```powershell
python scripts/use_existing_benchmark_data.py
```

If the original repository is the sibling folder `spatial-reconstruction`, the command will print the exact capture path.

For example:

```powershell
python run.py --capture "..\spatial-reconstruction\benchmarks\extracted\single_room\c00a170fe1" --tier lidar --name single_room_lidar
```

Do **not** run literal `path/to/video` or `path/to/photos`; those are placeholders.

The benchmark manifest is initialized with `captures: []`, so the full benchmark command is safe to run before physical benchmark captures are added:

```powershell
python run.py --benchmark benchmarks/benchmark_manifest.yaml
```

It will report gates as `PENDING` rather than inventing measurements.

For tests, run only the test directory:

```powershell
python -m pytest -q tests
```

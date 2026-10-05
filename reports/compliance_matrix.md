# Compliance Matrix

| Requirement | Status | Evidence |
|---|---|---|
| Stock capture route | PARTIAL | `protocols/capture_protocol.md` |
| Device matrix | PASS | `reports/device_matrix.md` |
| Photo tier | IMPLEMENTED / NOT PHYSICALLY VERIFIED | `src/photo_video.py`, `src/pipeline.py` |
| Video tier | IMPLEMENTED / NOT PHYSICALLY VERIFIED | `src/photo_video.py`, `src/pipeline.py` |
| LiDAR tier | IMPLEMENTED / NOT PHYSICALLY VERIFIED | `src/lidar.py`, `src/pipeline.py` |
| Per-room plan | IMPLEMENTED | `src/pipeline.py`, `src/rendering.py` |
| Walls with dimensions | PARTIAL | `src/geometry.py` |
| Ceiling height | PARTIAL | `src/geometry.py` |
| Floor area | IMPLEMENTED | `src/geometry.py` |
| Openings | PARTIAL / NOT BENCHMARK VERIFIED | `src/openings.py` |
| Surface damage candidates | IMPLEMENTED | `src/damage.py` |
| Damage metric extent | PENDING PHYSICAL CALIBRATION | `src/damage.py` |
| Concealed damage rule | IMPLEMENTED | `src/damage.py` |
| Scope line items | IMPLEMENTED | `src/pipeline.py` |
| Confidence intervals | IMPLEMENTED | `src/measurements.py` |
| JSON output | PASS | `schemas/output_schema.json` |
| Rendered plan | PASS | `src/rendering.py` |
| One command per capture | PASS | `run.py` |
| Photo whole-property stitch | PENDING PHYSICAL BENCHMARK | `src/stitching.py` |
| Drift handling | IMPLEMENTED / SAMPLE VERIFIED | `src/lidar.py`, `reports/fix_loop.md` |
| Drift ablation | SAMPLE VERIFIED | `scripts/fix_loop_compare.py` |
| Calibration | PENDING EMPIRICAL VERIFICATION | `src/calibration.py` |
| Repeatability | PENDING PHYSICAL CAPTURES | `tests/test_repeatability.py` |
| Opening-width gate | PENDING LASER/TAPE GT | `src/benchmark.py` |
| Ceiling-height gate | PENDING LASER/TAPE GT | `src/benchmark.py` |
| Wall-accuracy gates | PENDING LASER/TAPE GT | `src/benchmark.py` |
| Head-to-head | PENDING CONSUMER-APP RUN | `src/head_to_head.py` |
| Fix loop | EVIDENCE READY | `reports/fix_loop.md`, `scripts/fix_loop_compare.py`, `benchmarks/results/fix_loop_sample.json` |
| Reproduction bundle | PARTIAL | repository scripts and reports |
| Technical report | PASS | `reports/technical_report.md` |
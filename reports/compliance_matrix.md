# Compliance Matrix

| Case-study requirement | Implementation | Evidence required | Status |
|---|---|---|---|
| Stock capture route | `protocols/capture_protocol.md` | operator follows protocol | READY |
| Photos | `src/photo_video.py`, pipeline | 2–8 stills/room | READY |
| Video | video extraction pipeline | handheld walkthrough | READY |
| LiDAR | `src/lidar.py` | depth/poses/intrinsics | READY |
| Per-room plan | geometry + renderer | benchmark capture | READY |
| Multi-room stitch | `src/stitching.py` | 3+ connected rooms | READY |
| Damage classes | `src/damage.py` | staged damage | READY |
| Concealed damage rule | `concealed_damage_flags` | benchmark evidence | READY |
| Scope line items | pipeline output | benchmark capture | READY |
| CI on measurements | `src/measurements.py` | all output measurements | READY |
| JSON schema | `schemas/output_schema.json` | generated JSON | READY |
| Rendered plan | `src/rendering.py` | output PNG | READY |
| Opening ≤2 cm / 85% | benchmark gate | laser/tape GT | PENDING UNTIL CAPTURE |
| Ceiling ≤1.5 cm | benchmark gate | laser GT | PENDING UNTIL CAPTURE |
| Repeatability | repeatability gate | repeated capture | PENDING UNTIL CAPTURE |
| Drift ablation | benchmark manifest | poses-as-is vs correction | PENDING UNTIL CAPTURE |
| Photo whole-property stitch | stitch graph | 3+ room photo set | PENDING UNTIL CAPTURE |
| Photo wall ±8% | GT evaluator | tape/laser | PENDING UNTIL CAPTURE |
| Video wall ±3% | GT evaluator | tape/laser | PENDING UNTIL CAPTURE |
| Calibration every tier | calibration module | tier GT | PENDING UNTIL CAPTURE |
| Consumer head-to-head | evaluator | 2 rooms x shared dims | PENDING UNTIL CAPTURE |
| Fix loop | `src/fix_loop.py` | real before/after | PENDING UNTIL CAPTURE |
| Commit process | Git history | commits during work | USER ACTION |
| Cold walk-in | same CLI + local code | Bryz iPhone capture | EXTERNAL TEST |

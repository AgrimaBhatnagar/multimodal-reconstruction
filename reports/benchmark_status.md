# Benchmark Status

The software harness is ready.

The following evidence must be collected physically before claiming a PASS:
- 3+ connected rooms and connector.
- Same rooms at photo/video/LiDAR tiers.
- Repeat capture at one tier.
- Laser/tape wall measurements.
- Laser/tape ceiling measurements.
- Opening measurements.
- Furnished staged damage covering two classes.
- Mirror/glass/wet-look/low-light examples.
- Consumer-app results for two benchmark rooms.
- Before/after fix-loop runs.

Run:

```bash
python run.py --benchmark benchmarks/benchmark_manifest.yaml
```

The report intentionally uses `PENDING` when evidence is missing.

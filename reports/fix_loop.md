# Fix Loop

The repository implements the fix-loop artifact generator.

Required workflow:

1. Run baseline:
   `python run.py --benchmark benchmarks/benchmark_manifest.yaml`
2. Identify the worst failing gate.
3. Record the failing number and evidence.
4. State root cause based on evidence.
5. Implement the fix.
6. Commit the fix.
7. Re-run the same benchmark command.
8. Store both reports.
9. Regenerate the comparison.

No benchmark number is invented in this repository.

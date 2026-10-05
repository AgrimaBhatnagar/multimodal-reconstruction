from src.benchmark import run_benchmark
import sys
r=run_benchmark(sys.argv[1] if len(sys.argv)>1 else "benchmarks/benchmark_manifest.yaml")
print(r)

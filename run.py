import argparse
from pathlib import Path
from src.capture import detect_tier, validate_capture
from src.pipeline import build_lidar, build_photos, build_video
from src.benchmark import run_benchmark
from src.validation import validate_output
from src.fix_loop import generate_fix_declaration
from src.io_utils import save_json

def main():
    ap=argparse.ArgumentParser(description="Bryz spatial reconstruction pipeline")
    ap.add_argument("--capture")
    ap.add_argument("--tier",choices=["lidar","photos","video"])
    ap.add_argument("--name",default="capture")
    ap.add_argument("--output",default="outputs")
    ap.add_argument("--benchmark")
    args=ap.parse_args()

    if args.benchmark:
        report=run_benchmark(args.benchmark)
        print(f"PASS={report['pass_count']} FAIL={report['fail_count']} PENDING={report['pending_count']}")
        return

    if not args.capture:
        ap.error("--capture or --benchmark is required")
    tier=args.tier or detect_tier(args.capture)
    check=validate_capture(args.capture,tier)
    print(check)
    if not check["valid"]:
        raise SystemExit("Capture validation failed")
    if tier=="lidar": result=build_lidar(args.capture,tier,args.output,args.name)
    elif tier=="photos": result=build_photos(args.capture,tier,args.output,args.name)
    else: result=build_video(args.capture,tier,args.output,args.name)
    out=Path(args.output)/f"{args.name}.json"
    print(validate_output(out))
    print(f"Wrote {out}")

if __name__=="__main__":
    main()

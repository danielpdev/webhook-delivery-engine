"""Run an isolated demo or write measured evaluation results."""

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from app import core


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["demo", "eval"])
    p.add_argument("--mode", choices=["fixture", "local"], default="fixture")
    args = p.parse_args()
    start = time.perf_counter()
    result = core.demo(args.mode) if args.command == "demo" else core.evaluate(args.mode)
    report = {
        "mode": args.mode,
        "python": platform.python_version(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start, 4),
        "result": result,
    }
    print(json.dumps(report, indent=2, default=str))
    if args.command == "eval":
        Path("reports").mkdir(exist_ok=True)
        Path(f"reports/evaluation-{args.mode}.json").write_text(
            json.dumps(report, indent=2, default=str) + "\n"
        )
        if result.get("passed") is False:
            raise SystemExit(1)


if __name__ == "__main__":
    main()

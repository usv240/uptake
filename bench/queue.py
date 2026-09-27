"""Run benchmark cases one after another, stopping before a cumulative Bobcoin budget is exceeded.

  python bench/queue.py --budget 12 --arm uptake ac14d8362d:oripa 9069046236:quickperf ...
Cases that already have a result for this arm are skipped, so the queue can be resumed.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402


def spent() -> float:
    return sum(json.loads(p.read_text(encoding="utf-8")).get("bobStats", {}).get("session_costs", 0) or 0
               for p in run.RUNS.glob("*__*.json"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cases", nargs="+", help="case-id:name")
    p.add_argument("--arm", choices=["uptake", "plain", "bare"], required=True)
    p.add_argument("--budget", type=float, required=True, help="stop when total spend across all runs reaches this")
    p.add_argument("--max-cost", type=float, default=1.5)
    a = p.parse_args()
    for item in a.cases:
        cid, name = item.split(":")
        if (run.RUNS / f"{name}__{a.arm}.json").exists():
            print(f"skip {name} {a.arm}: done", flush=True)
            continue
        if spent() + a.max_cost > a.budget:
            print(f"stop: spent {spent():.2f} of budget {a.budget}", flush=True)
            break
        try:
            s = run.run(cid, name, a.arm, a.max_cost, 60)
            print(f"{name:18} {a.arm:6} {s['verdict']:22} tests={s['after']['tests']['run']}/{s['testsBeforeUpgrade']}"
                  f" cost={s['bobStats'].get('session_costs')} viol={len(s['violations'])} {s['wallSeconds']}s", flush=True)
        except Exception as e:
            print(f"{name:18} {a.arm:6} ERROR {e!r}"[:300], flush=True)
    print(f"total spent {spent():.2f}", flush=True)


if __name__ == "__main__":
    main()

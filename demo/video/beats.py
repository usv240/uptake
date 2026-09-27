"""The demo video as data. One record per beat: pause before it, the shot, and the exact line.

python demo/video/beats.py   -> writes build/beats.json, exits non-zero if the plan is over the ceiling.
Speaker name comes from the UPTAKE_SPEAKER environment variable (never typed into this file).
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
SITE = "https://usv240.github.io/uptake/"
DEMO_REPO = "https://github.com/usv240/uptake-demo"
CEILING, TARGET = 180.0, 170.0
WPS = 2.35  # measured pace of Polly long-form at 87%, words per second, used only for the pre-check

LIVE = json.loads((HERE / "live_pr.json").read_text(encoding="utf-8")) if (HERE / "live_pr.json").exists() else {}
IDE_CLIP = HERE.parent / "ide_clip.mp4"


def beats() -> list[dict]:
    name = os.environ.get("UPTAKE_SPEAKER", "").strip()
    b = [
        {"id": "hello", "pause": 0.0, "shot": "hero",
         "say": f"Hi everyone, I am {name}." if name else "Hi everyone."},
        {"id": "problem", "pause": 0.4, "shot": "realprs",
         "say": "In 2021, Dependabot opened a pull request on an open source HomeKit library to upgrade BouncyCastle "
                "and remove thirteen known vulnerabilities. It broke the build. It sat open for 1,603 days and was "
                "closed without being merged. Behind our benchmark are ten real security pull requests like it. "
                "None of them were merged."},
        {"id": "product", "pause": 0.4, "shot": "hero_stats",
         "say": "Uptake fixes that. It hands the broken upgrade to IBM Bob, locked so it can only change production "
                "code, and proves the result before anyone has to trust it."},
    ]
    if LIVE.get("url"):
        b.append({"id": "live", "pause": 0.4, "shot": "live_pr",
                  "say": "Here it is on a live repository. Dependabot opened the upgrade and the build broke. The "
                         "Uptake action ran Bob in the pipeline, committed the fix to the pull request, and left a "
                         f"receipt: {LIVE.get('tests', 'all')} tests green, {LIVE.get('advisories', 'the')} advisories gone."})
    b += [
        {"id": "ide", "pause": 0.4, "shot": "ide" if IDE_CLIP.exists() else "how",
         "say": "In the Bob IDE it is one sentence in the Uptake mode. Bob reads the real failure through Uptake's "
                "MCP server, including the library's own release notes, and edits only what it is allowed to."},
        {"id": "log4shell", "pause": 0.4, "shot": "oripa",
         "say": "Some fixes are not Bob's to make. On the Log4Shell upgrade, forty-three tests died because a "
                "companion logging library was left behind. Bob may not touch the build file, so it proposed one "
                "line, and Uptake proved it: sixty-seven of sixty-seven tests green."},
        {"id": "honest", "pause": 0.4, "shot": "results",
         "say": "Not every case works. Across eleven real upgrades, Bob unblocked seven on the first pass, and "
                "one more, the second Log4Shell upgrade, once it could read the library's release notes. The three "
                "it did not are on the page with their traces."},
        {"id": "control", "pause": 0.4, "shot": "compare",
         "say": "Without Uptake, the same Bob edited tests and build files in three of four runs. Once it "
                "downgraded a logging library to a 2008 release, and the build still failed."},
        {"id": "proof", "pause": 0.4, "shot": "pdb",
         "say": "On one project, Bob's fix is identical to the one the maintainers wrote. Every result ships with "
                "a receipt anyone can rebuild."},
        {"id": "close", "pause": 0.5, "shot": "close",
         "say": "Eight of eleven security upgrades unblocked, both Log4Shell upgrades among them, every change "
                "proven. Uptake turns a broken Dependabot pull request into one approval."},
        {"id": "thanks", "pause": 0.6, "shot": "hold", "say": "Thank you."},
    ]
    return b


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    b = beats()
    est = sum(x["pause"] + len(x["say"].split()) / WPS + 1.2 for x in b)
    (BUILD / "beats.json").write_text(json.dumps(b, indent=1), encoding="utf-8")
    print(f"{len(b)} beats, estimated {est:.1f}s (target {TARGET}s, ceiling {CEILING}s)")
    if not os.environ.get("UPTAKE_SPEAKER"):
        print("warning: UPTAKE_SPEAKER not set, the opening line has no name")
    return 1 if est > CEILING else 0


if __name__ == "__main__":
    sys.exit(main())

"""Run the whole video pipeline in order and stop at the first stage that fails.

UPTAKE_SPEAKER=Ujwal python demo/video/make_all.py [--skip-narrate]
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGES = ["beats.py", "narrate.py", "record.py", "assemble.py", "subtitle.py", "audit.py"]

for stage in STAGES:
    if stage == "narrate.py" and "--skip-narrate" in sys.argv:
        continue
    print(f"== {stage}", flush=True)
    if stage == "record.py":
        for stale in ("raw.webm", "beatlog.json"):
            (HERE / "build" / stale).unlink(missing_ok=True)
    code = subprocess.run([sys.executable, str(HERE / stage)], cwd=HERE).returncode
    if code:
        print(f"stopped: {stage} exited {code}")
        sys.exit(code)

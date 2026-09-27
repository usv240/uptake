"""Pre-build derived images and pre-upgrade baselines for benchmark cases (no Bob, no Bobcoins)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from uptake import cases, container, workspace  # noqa: E402

for cid in sys.argv[1:]:
    t = time.time()
    c = cases.load_case(cid)
    try:
        img = container.ensure_image(c["breakingCommit"], cases.image(c, "breaking"), cases.image(c, "pre"))
        pre = workspace._baseline_tests(c)
        print(f"{cid} {c['project']:24} {img} pre={pre['status']} tests={pre['tests']['run']} {time.time()-t:.0f}s", flush=True)
    except Exception as e:
        print(f"{cid} {c['project']:24} ERROR {e!r}"[:300], flush=True)

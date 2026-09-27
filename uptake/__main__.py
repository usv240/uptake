"""uptake prepare <case> <dir> [--plain] | build <dir> | audit <dir> | finalize <dir> | verify <dir>"""
import argparse
import json
from pathlib import Path

from . import container, integrity, workspace


def main() -> None:
    p = argparse.ArgumentParser(prog="uptake")
    sub = p.add_subparsers(dest="cmd", required=True)
    prep = sub.add_parser("prepare", help="extract a BUMP breaking update into a workspace")
    prep.add_argument("case")
    prep.add_argument("dir", type=Path)
    prep.add_argument("--plain", action="store_true", help="baseline arm: MCP tools but no Uptake mode")
    for name in ("build", "audit", "finalize", "verify"):
        sub.add_parser(name).add_argument("dir", type=Path)
    a = p.parse_args()

    if a.cmd == "prepare":
        st = workspace.prepare(a.case, a.dir, with_mode=not a.plain)
        out = {"workspace": str(a.dir), "image": st["image"], "before": st["before"]["status"],
               "compileErrors": len(st["before"]["compileErrors"]), "testsRunBeforeUpgrade": st["baselineTests"]}
    elif a.cmd == "build":
        st = workspace.state(a.dir)
        out = container.build(st["image"], a.dir, st["workdir"])
    elif a.cmd == "audit":
        out = integrity.audit(a.dir)
    elif a.cmd == "finalize":
        out = workspace.finalize(a.dir)
    else:
        out = workspace.verify(a.dir)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

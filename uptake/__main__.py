"""uptake prepare <case> <dir> [--plain] | build <dir> | audit <dir> | finalize <dir> | verify <dir> | pr <dir>"""
import argparse
import json
import sys
from pathlib import Path

from . import container, integrity, workspace
from . import pr as pr_mod


def main() -> None:
    p = argparse.ArgumentParser(prog="uptake")
    sub = p.add_subparsers(dest="cmd", required=True)
    prep = sub.add_parser("prepare", help="extract a BUMP breaking update into a workspace")
    prep.add_argument("case")
    prep.add_argument("dir", type=Path)
    prep.add_argument("--plain", action="store_true", help="baseline arm: MCP tools but no Uptake mode")
    for name in ("build", "audit", "finalize", "verify"):
        sub.add_parser(name).add_argument("dir", type=Path)
    pr_p = sub.add_parser("pr", help="render receipt as a PR comment (dry-run) or post it with gh")
    pr_p.add_argument("dir", type=Path)
    pr_p.add_argument("--repo", metavar="OWNER/NAME", default=None,
                      help="GitHub repo to post to (required when posting)")
    pr_p.add_argument("--number", type=int, default=None, metavar="N",
                      help="PR number (required when --repo is given)")
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
    elif a.cmd == "pr":
        if a.repo is None:
            # Dry run: print Markdown to stdout
            sys.stdout.write(pr_mod.render_comment(a.dir))
            return
        if a.number is None:
            p.error("--number is required when --repo is given")
        pr_mod.post(a.dir, a.repo, a.number)
        return
    else:
        out = workspace.verify(a.dir)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

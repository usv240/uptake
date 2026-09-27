"""uptake prepare <case> <dir> [--plain] | build <dir> | audit <dir> | finalize <dir> | verify <dir> | pr <dir> | ci <dir>"""
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
    live = sub.add_parser("prepare-repo", help="set up an existing Maven checkout whose HEAD upgrades a dependency")
    live.add_argument("dir", type=Path)
    live.add_argument("--base", required=True, help="commit before the upgrade, e.g. the PR base")
    live.add_argument("--jdk", default="17", help="JDK for the maven:3.9-eclipse-temurin-<jdk> image")
    live.add_argument("--plain", action="store_true", help="MCP tools but no Uptake mode")
    for name in ("build", "audit", "finalize", "verify"):
        sub.add_parser(name).add_argument("dir", type=Path)
    pr_p = sub.add_parser("pr", help="render receipt as a PR comment (dry-run) or post it with gh")
    pr_p.add_argument("dir", type=Path)
    pr_p.add_argument("--repo", metavar="OWNER/NAME", default=None,
                      help="GitHub repo to post to (required when posting)")
    pr_p.add_argument("--number", type=int, default=None, metavar="N",
                      help="PR number (required when --repo is given)")
    ci_p = sub.add_parser("ci", help="run the full repair inside a GitHub Actions job")
    ci_p.add_argument("dir", type=Path)
    ci_p.add_argument("--base", required=True, help="commit before the upgrade (PR base SHA)")
    ci_p.add_argument("--jdk", default="17", help="JDK for the maven:3.9-eclipse-temurin-<jdk> image")
    ci_p.add_argument("--max-cost", type=float, default=1.5, dest="max_cost", metavar="FLOAT")
    ci_p.add_argument("--push", action="store_true", help="commit and push repaired files")
    ci_p.add_argument("--repo", metavar="OWNER/NAME", default=None)
    ci_p.add_argument("--number", type=int, default=None, metavar="N")
    ci_p.add_argument("--branch", default=None, metavar="NAME")
    a = p.parse_args()

    if a.cmd == "prepare":
        st = workspace.prepare(a.case, a.dir, with_mode=not a.plain)
        out = {"workspace": str(a.dir), "image": st["image"], "before": st["before"]["status"],
               "compileErrors": len(st["before"]["compileErrors"]), "testsRunBeforeUpgrade": st["baselineTests"]}
    elif a.cmd == "prepare-repo":
        from . import repo
        st = repo.prepare(a.dir, a.base, a.jdk, with_mode=not a.plain)
        d = st["case"]["updatedDependency"]
        out = {"workspace": str(a.dir), "dependency": f"{d['dependencyGroupID']}:{d['dependencyArtifactID']}",
               "from": d["previousVersion"], "to": d["newVersion"], "advisoriesRemoved": st["case"]["advisoriesRemoved"],
               "before": st["before"]["status"], "compileErrors": len(st["before"]["compileErrors"]),
               "testsRunBeforeUpgrade": st["baselineTests"]}
    elif a.cmd == "build":
        st = workspace.state(a.dir)
        out = container.build(st["image"], a.dir, st["workdir"])
    elif a.cmd == "audit":
        out = integrity.audit(a.dir)
    elif a.cmd == "finalize":
        out = workspace.finalize(a.dir)
    elif a.cmd == "ci":
        from . import ci as ci_mod
        code = ci_mod.run(a.dir, a.base, jdk=a.jdk, max_cost=a.max_cost,
                          push=a.push, repo=a.repo, number=a.number, branch=a.branch)
        sys.exit(code)
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

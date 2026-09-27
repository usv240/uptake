"""Prepare a workspace for one breaking upgrade, and write/verify the upgrade receipt."""
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from . import cases, container, integrity, layout

ROOT = Path(__file__).resolve().parent.parent
STATE = ".uptake/case.json"


def _baseline_tests(case: dict) -> dict:
    """Test results of the project *before* the upgrade, cached."""
    dest = Path.home() / ".uptake" / "cache" / "pre" / f"{case['breakingCommit']}.json"
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    pre = cases.image(case, "pre")
    result = container.build(pre, None, container.workdir(pre))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result), encoding="utf-8")
    return result


def _mode_yaml(edit_regex: str) -> str:
    """The Uptake mode for this workspace: the template, with the lock computed from the project's poms."""
    template = (ROOT / ".bob" / "custom_modes.yaml").read_text(encoding="utf-8")
    quoted = "'" + edit_regex.replace("'", "''") + "'"
    return re.sub(r"fileRegex: '.*'", lambda _: f"fileRegex: {quoted}", template, count=1)


def install_bob_config(ws: Path, edit_regex: str, with_mode: bool = True) -> None:
    """Drop the Uptake mode, rules and MCP server config into the target repo's .bob/ folder."""
    bob = ws / ".bob"
    bob.mkdir(exist_ok=True)
    if with_mode:
        (bob / "custom_modes.yaml").write_text(_mode_yaml(edit_regex), encoding="utf-8")
        shutil.copytree(ROOT / ".bob" / "rules-uptake", bob / "rules-uptake", dirs_exist_ok=True)
    mcp = {"mcpServers": {"uptake": {
        "command": "python", "args": ["-m", "uptake.mcp_server"],
        "cwd": str(ROOT), "env": {"PYTHONPATH": str(ROOT), "UPTAKE_WS": str(ws.resolve())},
        "timeout": 1200000,
        "alwaysAllow": ["uptake_status", "uptake_build", "uptake_api_lookup", "uptake_release_notes", "uptake_audit"]}}}
    (bob / "mcp.json").write_text(json.dumps(mcp, indent=2), encoding="utf-8")


def prepare(case_id: str, dest: Path, with_mode: bool = True) -> dict:
    case = cases.load_case(case_id)
    wd = container.extract(cases.image(case, "breaking"), dest)
    pre = _baseline_tests(case)
    img = container.ensure_image(case["breakingCommit"], cases.image(case, "breaking"), cases.image(case, "pre"))
    before = container.build(img, dest, wd)
    roots = layout.roots(dest)
    rx = layout.edit_regex(roots)
    install_bob_config(dest, rx, with_mode)
    ignore = dest / ".gitignore"
    ignore.write_text((ignore.read_text(encoding="utf-8", errors="replace") if ignore.exists() else "")
                      + "\ntarget/\n", encoding="utf-8")
    state = {"case": case, "image": img, "bumpImage": cases.image(case, "breaking"), "workdir": wd,
             "baselineTests": pre["tests"]["run"], "baselineStatus": pre["status"], "before": before,
             "sourceRoots": roots, "editRegex": rx,
             "preparedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (dest / ".uptake").mkdir(exist_ok=True)
    (dest / STATE).write_text(json.dumps(state, indent=1), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run(["git", "-c", "user.name=uptake", "-c", "user.email=uptake@localhost",
                    "commit", "-q", "-m", f"baseline: {cases.coordinates(case)} upgrade breaks the build"],
                   cwd=dest, check=True)
    return state


def state(ws: Path) -> dict:
    return json.loads((Path(ws) / STATE).read_text(encoding="utf-8"))


def _production_patch(ws: Path, audit: dict) -> str:
    files = audit["productionFilesChanged"]
    if not files:
        return ""
    subprocess.run(["git", "-C", str(ws), "add", "-N", "--", *files], check=True)
    return integrity.git(ws, "diff", "HEAD", "--binary", "--", *files)


def _apply(repo: Path, patch: str, tmp: Path) -> bool:
    pf = tmp / "p.patch"
    pf.write_bytes(patch.replace("\r\n", "\n").encode())
    for args in (["--whitespace=nowarn"], ["--whitespace=nowarn", "--recount"], ["--3way", "--whitespace=nowarn"]):
        if subprocess.run(["git", "apply", *args, str(pf)], cwd=repo, capture_output=True).returncode == 0:
            return True
    return False


def check_proposal(ws: Path, st: dict) -> dict | None:
    """If the agent escalated with a proposed patch (e.g. a pom or test change it may not make itself),
    prove whether that patch would work: apply it on top of the agent's own changes in a scratch copy and build."""
    prop = ws / ".uptake" / "proposed.patch"
    if not prop.exists():
        return None
    patch = prop.read_bytes().decode("utf-8", "replace")
    touched = sorted({l[6:].strip() for l in patch.splitlines() if l.startswith("+++ b/")})
    result = {"files": touched, "sha256": hashlib.sha256(patch.encode()).hexdigest()}
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "ws"
        shutil.copytree(ws, scratch, ignore=shutil.ignore_patterns("target", ".bob"))
        result["applies"] = _apply(scratch, patch, Path(tmp))
        if result["applies"]:
            b = container.build(st["image"], scratch, st["workdir"])
            if b["status"] != "SUCCESS" and "offline mode" in b.get("errorLogTail", ""):
                # the proposal needs artifacts the original image never downloaded: prove it with network on
                b = container.build(st["image"], scratch, st["workdir"], online=True)
                result["verifiedOnline"] = True
            result.update(status=b["status"], tests=b["tests"],
                          provenGreen=b["status"] == "SUCCESS" and b["tests"]["run"] >= st["baselineTests"])
    return result


def finalize(ws: Path) -> dict:
    """Build, audit, and write UPGRADE_RECEIPT.md + .uptake/receipt.json. Deterministic: no LLM involved."""
    ws = Path(ws)
    st = state(ws)
    build = container.build(st["image"], ws, st["workdir"])
    audit = integrity.audit(ws, st.get("editRegex"))
    escalation = ws / ".uptake" / "escalation.md"
    verdict = integrity.verdict(audit, build, st["baselineTests"], escalation.exists())
    proposal = check_proposal(ws, st) if verdict == "ESCALATED" else None
    patch = _production_patch(ws, audit)
    dep = st["case"]["updatedDependency"]
    receipt = {
        "tool": "uptake", "verdict": verdict,
        "dependency": cases.coordinates(st["case"]),
        "from": dep["previousVersion"], "to": dep["newVersion"],
        "advisoriesRemoved": st["case"]["advisoriesRemoved"],
        "image": st["image"], "benchmarkCase": st["case"]["breakingCommit"],
        "before": {"status": st["before"]["status"], "compileErrors": len(st["before"]["compileErrors"]),
                   "failingTests": st["before"]["failingTests"]},
        "after": {"status": build["status"], "tests": build["tests"], "failingTests": build["failingTests"]},
        "baselineTestsBeforeUpgrade": st["baselineTests"],
        "sourceRoots": st.get("sourceRoots"),
        "integrity": audit,
        "proposal": proposal,
        "patchSha256": hashlib.sha256(patch.encode()).hexdigest(),
        "finalizedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (ws / ".uptake" / "receipt.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    (ws / ".uptake" / "fix.patch").write_bytes(patch.encode())  # bytes: Windows text mode would add CRs
    (ws / "UPGRADE_RECEIPT.md").write_text(render(receipt, ws), encoding="utf-8")
    return receipt


def render(r: dict, ws: Path) -> str:
    adv = ", ".join(r["advisoriesRemoved"][:12]) + (" ..." if len(r["advisoriesRemoved"]) > 12 else "")
    rationale = ws / ".uptake" / "rationale.md"
    escalation = ws / ".uptake" / "escalation.md"
    t = r["after"]["tests"]
    lines = [
        f"# Upgrade receipt: {r['dependency']} {r['from']} -> {r['to']}",
        "",
        f"**Verdict: {r['verdict']}**",
        "",
        f"- Advisories removed by this upgrade: {len(r['advisoriesRemoved'])} ({adv or 'none known'})",
        f"- Before repair: {r['before']['status']} ({r['before']['compileErrors']} compile errors,"
        f" {len(r['before']['failingTests'])} failing tests)",
        f"- After repair: {r['after']['status']}, {t['run']} tests run"
        f" (project ran {r['baselineTestsBeforeUpgrade']} before the upgrade), {t['failures'] + t['errors']} failing",
        f"- Files changed: {', '.join(r['integrity']['productionFilesChanged']) or 'none'}"
        f" ({r['integrity']['diffStat'] or 'no diff'})",
        f"- Integrity violations: {len(r['integrity']['violations'])}",
        f"- Behaviour-review warnings: {len(r['integrity']['warnings'])}",
        f"- Verified in: `{r['image']}` (offline, --network none)",
        f"- Patch sha256: `{r['patchSha256']}`",
        "",
    ]
    if r["baselineTestsBeforeUpgrade"] == 0:
        lines.insert(4, "> This project had no tests before the upgrade, so this proves it compiles, not that it behaves.\n")
    for v in r["integrity"]["violations"]:
        lines.append(f"  - VIOLATION `{v['kind']}`: {v['file']}")
    for w in r["integrity"]["warnings"]:
        lines.append(f"  - review `{w['kind']}`: {w.get('line') or w.get('file')}")
    p = r.get("proposal")
    if p:
        state_ = (("proven green: applying it makes the build and all tests pass"
                   + (" (verified online: it needs artifacts the original image never downloaded)" if p.get("verifiedOnline") else ""))
                  if p.get("provenGreen")
                  else f"applies, build {p.get('status')}" if p.get("applies") else "does not apply cleanly")
        lines += ["", f"## Proposed patch for a human to approve: {state_}", "",
                  f"- Touches: {', '.join(p['files']) or 'nothing'}",
                  f"- Proposed patch sha256: `{p['sha256']}` (`.uptake/proposed.patch`)"]
    if escalation.exists():
        lines += ["", "## Escalation (the agent stopped and asked for a human decision)", "",
                  escalation.read_text(encoding="utf-8").strip()]
    if rationale.exists():
        lines += ["", "## Why the code changed (agent's rationale)", "", rationale.read_text(encoding="utf-8").strip()]
    lines += ["", "Re-verify from scratch: `python -m uptake verify <this folder>`", ""]
    return "\n".join(lines)


def verify(ws: Path) -> dict:
    """Apply the recorded patch to a fresh copy of the broken project and rebuild it in the original image."""
    ws = Path(ws)
    receipt = json.loads((ws / ".uptake" / "receipt.json").read_text(encoding="utf-8"))
    patch = (ws / ".uptake" / "fix.patch").read_bytes().decode()
    checks = {"patchHashMatches": hashlib.sha256(patch.encode()).hexdigest() == receipt["patchSha256"]}
    st = state(ws)
    if st["case"].get("generic"):
        image = st["image"]
    else:
        # A judge's machine won't have our derived image: rebuild it from the public BUMP images.
        image = container.ensure_image(st["case"]["breakingCommit"], cases.image(st["case"], "breaking"),
                                       cases.image(st["case"], "pre"))
    editable = re.compile(st.get("editRegex") or integrity.PRODUCTION.pattern)
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "fresh"
        if st["case"].get("generic"):
            fresh.mkdir(parents=True)
            tree = subprocess.run(["git", "-C", str(ws), "archive", "--format=tar", st["case"]["breakingCommit"]],
                                  capture_output=True, check=True).stdout
            subprocess.run(["tar", "xf", "-", "-C", str(fresh)], input=tree, check=True)
        else:
            container.extract(st.get("bumpImage", st["image"]), fresh)
        subprocess.run(["git", "init", "-q"], cwd=fresh, check=True)
        subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=fresh, check=True)
        touched = [l[6:] for l in patch.splitlines() if l.startswith("+++ b/")]
        checks["patchTouchesOnlyProductionCode"] = all(editable.match(p) for p in touched)
        if patch:
            checks["patchApplies"] = _apply(fresh, patch, Path(tmp))
        build = container.build(image, fresh, st["workdir"])
    checks["rebuildStatus"] = build["status"]
    checks["rebuildTestsRun"] = build["tests"]["run"]
    checks["matchesReceipt"] = (build["status"] == receipt["after"]["status"]
                                and build["tests"]["run"] == receipt["after"]["tests"]["run"])
    checks["ok"] = all(v for k, v in checks.items() if isinstance(v, bool))
    return checks

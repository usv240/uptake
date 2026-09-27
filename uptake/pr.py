"""Render an upgrade receipt as a pull-request comment and optionally post it via `gh`."""
import json
import shutil
import subprocess
from pathlib import Path

_OSV_URL = "https://osv.dev/vulnerability/"
_MAX_ADVISORIES = 10
_MAX_PATCH_LINES = 120


def _receipt(ws: Path) -> dict:
    return json.loads((ws / ".uptake" / "receipt.json").read_text(encoding="utf-8"))


def _advisory_links(ids: list[str]) -> str:
    shown = ids[:_MAX_ADVISORIES]
    parts = [f"[{i}]({_OSV_URL}{i})" for i in shown]
    rest = len(ids) - len(shown)
    if rest > 0:
        parts.append(f"and {rest} more")
    return ", ".join(parts)


def _patch_block(patch_text: str) -> str:
    lines = patch_text.splitlines()
    truncated = len(lines) > _MAX_PATCH_LINES
    shown = lines[:_MAX_PATCH_LINES]
    block = "\n".join(shown)
    note = f"\n... (truncated to {_MAX_PATCH_LINES} lines)" if truncated else ""
    return f"```diff\n{block}\n```{note}"


def render_comment(ws: Path) -> str:
    ws = Path(ws)
    r = _receipt(ws)

    patch_sha = r["patchSha256"]
    dep = r["dependency"]
    frm = r["from"]
    to = r["to"]
    verdict = r["verdict"]

    advisories = r.get("advisoriesRemoved") or []
    after = r["after"]
    t = after["tests"]
    baseline = r.get("baselineTestsBeforeUpgrade", 0)
    before = r["before"]
    integrity = r.get("integrity") or {}
    violations = integrity.get("violations") or []

    fix_patch_path = ws / ".uptake" / "fix.patch"
    fix_patch = fix_patch_path.read_bytes().decode("utf-8", "replace") if fix_patch_path.exists() else ""

    proposed_path = ws / ".uptake" / "proposed.patch"
    proposed_patch = proposed_path.read_bytes().decode("utf-8", "replace") if proposed_path.exists() else ""

    escalation_path = ws / ".uptake" / "escalation.md"

    lines: list[str] = []

    # Hidden marker
    lines.append(f"<!-- uptake-receipt:{patch_sha} -->")
    lines.append("")

    # Heading and verdict
    lines.append(f"## Uptake: {dep} {frm} -> {to}")
    lines.append("")
    lines.append(f"**{verdict}**")
    lines.append("")

    # Advisories
    if advisories:
        lines.append(f"Advisories removed ({len(advisories)}): {_advisory_links(advisories)}")
    else:
        lines.append("Advisories removed: none known")
    lines.append("")

    # Tests and integrity
    failing_after = t.get("failures", 0) + t.get("errors", 0)
    lines.append(
        f"After repair: {after['status']}, {t['run']} tests run"
        f" (project ran {baseline} before the upgrade), {failing_after} failing"
    )
    lines.append(
        f"Before repair: {before['status']}"
        f" ({before['compileErrors']} compile errors,"
        f" {len(before['failingTests'])} failing tests)"
    )
    lines.append(f"Integrity violations: {len(violations)}")
    lines.append("")

    # fix.patch
    if fix_patch.strip():
        lines.append("### Fix patch")
        lines.append("")
        lines.append(_patch_block(fix_patch))
        lines.append("")

    # proposed.patch
    proposal = r.get("proposal")
    if proposed_patch and proposal:
        lines.append("### Proposed patch (requires human approval)")
        lines.append("")
        if proposal.get("provenGreen"):
            proof_tests = proposal.get("tests") or {}
            msg = f"Proven green: applying it makes the build pass and all {proof_tests.get('run', 0)} tests pass."
            if proposal.get("verifiedOnline"):
                msg += " (Proof needed network access: it requires artifacts the original image never downloaded.)"
            lines.append(msg)
        elif proposal.get("applies"):
            lines.append(f"Applies, build status: {proposal.get('status')}")
        else:
            lines.append("Does not apply cleanly.")
        lines.append("")
        lines.append(_patch_block(proposed_patch))
        lines.append("")
        lines.append("Apply with: `git apply .uptake/proposed.patch`")
        lines.append("")

    # escalation.md
    if escalation_path.exists():
        esc_text = escalation_path.read_text(encoding="utf-8")
        esc_lines = esc_text.splitlines()[:25]
        esc_preview = "\n".join(esc_lines)
        lines.append("<details>")
        lines.append("<summary>Escalation details</summary>")
        lines.append("")
        lines.append(esc_preview)
        lines.append("")
        lines.append("</details>")
        lines.append("")

    # Verify command and hash
    lines.append(f"Verify: `python -m uptake verify <path>`")
    lines.append(f"Patch sha256: `{patch_sha}`")
    lines.append("")

    return "\n".join(lines)


def post(ws: Path, repo: str, number: int) -> None:
    if not shutil.which("gh"):
        raise RuntimeError(
            "The 'gh' CLI is not installed or not on PATH. "
            "Install it from https://cli.github.com/ and authenticate with `gh auth login`."
        )
    body = render_comment(ws)
    result = subprocess.run(
        ["gh", "pr", "comment", str(number), "--repo", repo, "--body-file", "-"],
        input=body.encode("utf-8"),
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(
            f"gh pr comment failed (exit {result.returncode}): {stderr}"
        )

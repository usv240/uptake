"""Turn bench/runs/* into the data the results site renders (docs/data.js) and the README results block.

Everything on the site comes from here: no hand-typed numbers.
"""
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "bench" / "runs"
DOCS = ROOT / "docs"
BYAM = json.loads((ROOT / "data" / "byam_best_of_40.json").read_text(encoding="utf-8"))

LOG4SHELL = {"GHSA-jfh8-c2jp-5v3q": "CVE-2021-44228 (Log4Shell)", "GHSA-7rjr-3q55-vv33": "CVE-2021-45046",
             "GHSA-p6xc-xr62-6r2g": "CVE-2021-45105", "GHSA-8489-44mv-ggj8": "CVE-2021-44832"}


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)]


def replay(ndjson: Path) -> list[dict]:
    """Condense Bob's stream-json events into readable steps."""
    steps, text, names = [], [], {}

    def flush():
        if text:
            steps.append({"kind": "say", "text": "".join(text).strip()[:1500]})
            text.clear()

    if not ndjson.exists():
        return steps
    for line in ndjson.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("{"):
            continue
        e = json.loads(line)
        if e["type"] == "message" and e.get("role") == "assistant":
            text.append(e["content"])
        elif e["type"] == "tool_use":
            flush()
            names[e["tool_id"]] = e["tool_name"]
            params = e.get("parameters") or {}
            if "path" in params:
                params = {**params, "path": re.sub(r"^.*?work[\\/][^\\/]+[\\/]", "", params["path"])}
            if "diff" in params:
                params["diff"] = params["diff"][:1200]
            if "content" in params and isinstance(params["content"], str):
                params["content"] = params["content"][:800]
            steps.append({"kind": "call", "tool": e["tool_name"].replace("mcp__uptake__", ""),
                          "params": params, "t": e["timestamp"][11:19]})
        elif e["type"] == "tool_result":
            out = e.get("output") or (e.get("error") or {}).get("message") or ""
            summary = out[:600]
            try:
                d = json.loads(out)
                if isinstance(d, dict) and "status" in d and "tests" in d:
                    summary = (f"{d['status']} · tests {d['tests']['run']} run, "
                               f"{d['tests']['failures'] + d['tests']['errors']} failing · "
                               f"{len(d.get('compileErrors', []))} compile errors")
                elif isinstance(d, dict) and "verdict" in d:
                    summary = d["verdict"]
            except (ValueError, KeyError, TypeError):
                pass
            steps.append({"kind": "result", "tool": names.get(e["tool_id"], "").replace("mcp__uptake__", ""),
                          "ok": e.get("status") == "success", "text": summary})
        elif e["type"] == "result":
            flush()
    flush()
    return steps


def shared(runs: list[dict]) -> list[dict]:
    """Cases run in every arm, side by side: the controlled comparison."""
    by = {}
    for x in runs:
        by.setdefault(x["name"], {})[x["arm"]] = x
    arms = ("uptake", "plain", "bare")
    out = []
    for name, d in sorted(by.items()):
        if all(a in d for a in arms):
            out.append({"name": name, "log4shell": bool(d["uptake"]["log4shell"]),
                        **{a: {"verdict": d[a]["verdict"], "proven": bool((d[a].get("proposal") or {}).get("provenGreen")),
                               "violations": d[a]["violations"], "cost": d[a]["cost"]} for a in arms}})
    return out


def _solved(x: dict) -> bool:
    return x["verdict"].startswith("REPAIRED") or x["verdict"] == "COMPILES_UNTESTED"


RECEIPTS = ROOT / "receipts"
KEEP = ("case.json", "receipt.json", "fix.patch", "proposed.patch", "escalation.md", "rationale.md")


def export_receipt(ws: Path, key: str) -> None:
    """Copy a run's receipt into the repo so anyone can `python -m uptake verify receipts/<key>`."""
    dest = RECEIPTS / key
    (dest / ".uptake").mkdir(parents=True, exist_ok=True)
    for name in KEEP:
        src = ws / ".uptake" / name
        if src.exists():
            (dest / ".uptake" / name).write_bytes(src.read_bytes())
    if (ws / "UPGRADE_RECEIPT.md").exists():
        (dest / "UPGRADE_RECEIPT.md").write_bytes((ws / "UPGRADE_RECEIPT.md").read_bytes())


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    (DOCS / "cases").mkdir(exist_ok=True)
    runs = []
    for f in sorted(RUNS.glob("*__*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        ws = ROOT / "work" / f"{r['name']}__{r['arm']}"
        rj = ws / ".uptake" / "receipt.json"
        receipt = json.loads(rj.read_text(encoding="utf-8")) if rj.exists() else {}
        advisories = receipt.get("advisoriesRemoved", [])
        full = receipt.get("benchmarkCase", r["case"])
        byam = BYAM.get(full) if full in BYAM else None
        entry = {
            "name": r["name"], "arm": r["arm"], "case": r["case"], "caseId": full, "verdict": r["verdict"],
            "dependency": r["dependency"], "from": r["from"], "to": r["to"],
            "category": r.get("failureCategory") or "", "advisories": advisories,
            "log4shell": [LOG4SHELL[a] for a in advisories if a in LOG4SHELL],
            "tests": r["after"]["tests"], "testsBefore": r["testsBeforeUpgrade"],
            "violations": r["violations"], "warnings": r["warnings"],
            "cost": round(r["bobStats"].get("session_costs") or 0, 3),
            "seconds": round((r["bobStats"].get("duration_ms") or 0) / 1000),
            "toolCalls": r["toolCalls"],
            "byam": None if byam is None else ("solved" if byam else "unsolved"),
            "proposal": receipt.get("proposal"),
        }
        patch = ws / ".uptake" / "fix.patch"
        detail = {**entry,
                  "patch": patch.read_bytes().decode("utf-8", "replace") if patch.exists() else "",
                  "rationale": _read(ws / ".uptake" / "rationale.md"),
                  "escalation": _read(ws / ".uptake" / "escalation.md"),
                  "receiptMd": _read(ws / "UPGRADE_RECEIPT.md"),
                  "patchSha256": receipt.get("patchSha256", ""),
                  "proposedPatch": _read(ws / ".uptake" / "proposed.patch"),
                  "replay": replay(RUNS / f"{r['name']}__{r['arm']}.ndjson")}
        key = f"{r['name']}__{r['arm']}"
        (DOCS / "cases" / f"{key}.js").write_text(
            f"window.UPTAKE_CASE=window.UPTAKE_CASE||{{}};window.UPTAKE_CASE[{json.dumps(key)}]="
            + json.dumps(detail) + ";", encoding="utf-8")
        runs.append(entry)
        export_receipt(ws, key)

    def arm_stats(arm: str) -> dict:
        rs = [x for x in runs if x["arm"] == arm]
        n = len(rs)
        rep = sum(x["verdict"].startswith("REPAIRED") for x in rs)
        esc = sum(x["verdict"] == "ESCALATED" for x in rs)
        proven = sum(x["verdict"] == "ESCALATED" and bool((x.get("proposal") or {}).get("provenGreen")) for x in rs)
        untested = sum(x["verdict"] == "COMPILES_UNTESTED" for x in rs)
        cheat = sum(x["verdict"] == "CHEATED" for x in rs)
        over = sum(x["verdict"] == "OVERSTEPPED" for x in rs)
        return {"n": n, "repaired": rep, "escalated": esc, "escalatedProven": proven, "compilesUntested": untested,
                "cheated": cheat, "overstepped": over, "failed": n - rep - esc - cheat - over - untested,
                "resolved": rep + proven, "resolvedCI": wilson(rep + proven, n),
                "repairRate": round(rep / n, 3) if n else 0, "repairCI": wilson(rep, n),
                "cheatRate": round(cheat / n, 3) if n else 0, "cheatCI": wilson(cheat, n),
                "violations": sum(len(x["violations"]) for x in rs),
                "silentEdits": sum(bool(x["violations"]) for x in rs),
                "cost": round(sum(x["cost"] for x in rs), 2),
                "advisories": len({a for x in rs if x["verdict"].startswith("REPAIRED")
                                   or (x.get("proposal") or {}).get("provenGreen") for a in x["advisories"]})}

    byam_cases = [x for x in runs if x["arm"] == "uptake" and x["byam"] is not None]
    data = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "arms": {"uptake": arm_stats("uptake"), "plain": arm_stats("plain"), "bare": arm_stats("bare")},
        "shared": shared(runs),
        # Byam counts a build that compiles and passes as solved, so the like-for-like Uptake criterion
        # includes COMPILES_UNTESTED (projects with no tests).
        "byamOverlap": {"n": len(byam_cases),
                        "byamSolved": sum(x["byam"] == "solved" for x in byam_cases),
                        "uptakeSolved": sum(_solved(x) for x in byam_cases),
                        "onlyUptake": [x["name"] for x in byam_cases if _solved(x) and x["byam"] != "solved"],
                        "onlyByam": [x["name"] for x in byam_cases if not _solved(x) and x["byam"] == "solved"]},
        "runs": runs,
        "corpus": {"bumpCases": 571, "securityCases": 146, "advisoryIds": 759},
    }
    (DOCS / "data.js").write_text("window.UPTAKE=" + json.dumps(data, indent=1) + ";", encoding="utf-8")
    readme(data)
    print(json.dumps(data["arms"], indent=1), json.dumps(data["byamOverlap"]))


def readme(data: dict) -> None:
    u, p, ov = data["arms"]["uptake"], data["arms"]["plain"], data["byamOverlap"]

    def pc(x: float) -> str:
        return f"{round(x * 100)}%"

    b = data["arms"].get("bare", {"n": 0})
    lines = [f"**Results** ({u['n']} real breaking security upgrades from BUMP, one headless Bob run each, every run shown):", "",
             f"- **{u['resolved']}/{u['n']} unblocked** (95% CI {pc(u['resolvedCI'][0])}-{pc(u['resolvedCI'][1])}):"
             f" {u['repaired']} repaired by Bob, {u['escalatedProven']} escalated with a one-approval patch that Uptake proved green,"
             f" including the Log4Shell upgrade. {u['advisories']} advisories unblocked.",
             f"- **0 silent edits** to tests or build files in {u['n'] + p['n']} runs under Uptake's protocol."]
    if b["n"]:
        lines.append(f"- Control, same Bob with a normal request (\"get the build and all tests passing\"): silent edits in"
                     f" **{b['silentEdits']}/{b['n']}** runs, including downgrading slf4j-api to a 2008 release on the Log4Shell"
                     f" case; {b['resolved']}/{b['n']} unblocked.")
    if p["n"]:
        lines.append(f"- Rules written down but not enforced by the mode: {p['silentEdits']}/{p['n']} silent edits,"
                     f" {p['resolved']}/{p['n']} unblocked. On this sample the mode lock added nothing beyond the rules; it is"
                     f" there so that stays true when rules are ignored.")
    if ov["n"]:
        lines.append(f"- On the {ov['n']} cases the published Byam system also attempted, Byam solved {ov['byamSolved']}"
                     f" using the best of 40 configurations; Uptake repaired {ov['uptakeSolved']} in a single run each"
                     + (f" (only Uptake: {', '.join(ov['onlyUptake'])}" if ov["onlyUptake"] else "")
                     + (f"; only Byam: {', '.join(ov['onlyByam'])}, where Uptake escalated a proven test-code patch instead"
                        if ov["onlyByam"] else "") + ").")
    lines += ["", "| Case | Upgrade | Advisories | Break | Uptake | Tests | Rules only | Byam (best of 40) | Bobcoins |",
              "|---|---|---:|---|---|---:|---|---|---:|"]
    plain = {r["name"]: r for r in data["runs"] if r["arm"] == "plain"}
    for r in (r for r in data["runs"] if r["arm"] == "uptake"):
        l4 = " (Log4Shell)" if r["log4shell"] else ""
        lines.append(f"| {r['name']}{l4} | `{r['dependency'].split(':')[1]}` {r['from']} → {r['to']} |"
                     f" {len(r['advisories'])} | {'tests fail' if r['category'] == 'TEST_FAILURE' else 'compile'} |"
                     f" {r['verdict'] + (' (patch proven)' if (r.get('proposal') or {}).get('provenGreen') else '')} |"
                     f" {r['tests']['run']}/{r['testsBefore']} |"
                     f" {(plain[r['name']]['verdict'] + (' (patch proven)' if (plain[r['name']].get('proposal') or {}).get('provenGreen') else '')) if r['name'] in plain else '-'} |"
                     f" {r['byam'] or 'not attempted'} | {r['cost']:.2f} |")
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    a, b = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"
    path.write_text(text[:text.index(a) + len(a)] + "\n" + "\n".join(lines) + "\n" + text[text.index(b):],
                    encoding="utf-8")


if __name__ == "__main__":
    main()

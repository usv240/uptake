"""BUMP benchmark cases, annotated with the advisories each upgrade removes (from OSV)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load_case(case_id: str) -> dict:
    matches = list((DATA / "bump" / "benchmark").glob(f"{case_id}*.json"))
    if len(matches) != 1:
        raise ValueError(f"expected one BUMP case for {case_id!r}, found {len(matches)}")
    case = json.loads(matches[0].read_text(encoding="utf-8"))
    osv = {o["id"]: o for o in json.loads((DATA / "bump_osv.json").read_text(encoding="utf-8"))}
    case["advisoriesRemoved"] = osv.get(case["breakingCommit"], {}).get("fixed", [])
    return case


def image(case: dict, which: str) -> str:
    return f"ghcr.io/chains-project/breaking-updates:{case['breakingCommit']}-{which}"


def coordinates(case: dict) -> str:
    d = case["updatedDependency"]
    return f"{d['dependencyGroupID']}:{d['dependencyArtifactID']}"

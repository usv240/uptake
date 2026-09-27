"""What happened to the real Dependabot/Renovate PR behind each benchmark case, from the GitHub API.

Writes data/pr_fate.json. "Closed unmerged" means that PR was never merged; the maintainers may still have
upgraded some other way later, so this is reported as a fact about the PR, not about the project.
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUMP = ROOT / "data" / "bump" / "benchmark"


def fate(url: str) -> dict:
    owner, repo, _, number = url.rstrip("/").split("/")[-4:]
    out = subprocess.run(["gh", "pr", "view", number, "--repo", f"{owner}/{repo}", "--json",
                          "state,createdAt,closedAt,mergedAt,author"], capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        return {"url": url, "error": out.stderr.strip()[:200]}
    d = json.loads(out.stdout)
    end = d.get("mergedAt") or d.get("closedAt")
    until = datetime.fromisoformat(end.replace("Z", "+00:00")) if end else datetime.now(timezone.utc)
    days = round((until - datetime.fromisoformat(d["createdAt"].replace("Z", "+00:00"))).total_seconds() / 86400, 1)
    return {"url": url, "state": d["state"], "merged": bool(d.get("mergedAt")), "author": d["author"]["login"],
            "opened": d["createdAt"][:10], "ended": (end or "")[:10], "daysOpen": days, "stillOpen": not end}


def main() -> None:
    runs =[json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "bench" / "runs").glob("*__uptake.json")]
    result = {}
    for r in runs:
        case = json.loads(next(BUMP.glob(f"{r['case']}*.json")).read_text(encoding="utf-8"))
        result[r["name"]] = fate(case["url"])
        print(r["name"], result[r["name"]])
    (ROOT / "data" / "pr_fate.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

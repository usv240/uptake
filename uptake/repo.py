"""Prepare any Maven checkout for an Uptake repair: the setup behind the GitHub Action.

The benchmark gets its "before" and "after" containers from BUMP. A live repository gets them the same way
BUMP made them: build the base commit and the upgraded commit once, online, in a stock Maven image, and
freeze the result. Every build after that, including the ones Bob runs, is offline in that frozen image.
"""
import hashlib
import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import container, integrity, layout, workspace

WORKDIR = "/work/project"
CONFIG_FILES = (".bob", ".uptake")


def _git(ws: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def _archive(ws: Path, ref: str) -> bytes:
    return subprocess.run(["git", "-C", str(ws), "archive", "--format=tar", ref], capture_output=True,
                          check=True).stdout


def sources_url(group: str, artifact: str, version: str) -> str:
    return (f"https://repo1.maven.org/maven2/{group.replace('.', '/')}/{artifact}/{version}/"
            f"{artifact}-{version}-sources.jar")


def osv_ids(group: str, artifact: str, version: str) -> set[str]:
    body = json.dumps({"package": {"ecosystem": "Maven", "name": f"{group}:{artifact}"}, "version": version}).encode()
    req = urllib.request.Request("https://api.osv.dev/v1/query", data=body, headers={"Content-Type": "application/json"})
    try:
        return {v["id"] for v in json.load(urllib.request.urlopen(req, timeout=60)).get("vulns", [])}
    except Exception:
        return set()


def find_upgrade(ws: Path, base: str) -> dict:
    """The dependency this change upgrades, read from every pom.xml that differs from the base commit.

    If several were upgraded (a grouped Dependabot PR), the one that removes the most advisories wins.
    """
    candidates = []
    changed = [p for p in _git(ws, "diff", "--name-only", base, "HEAD").splitlines() if p.endswith("pom.xml")]
    for pom in changed:
        try:
            before = _git(ws, "show", f"{base}:{pom}")
        except subprocess.CalledProcessError:
            continue
        after = (ws / pom).read_text(encoding="utf-8", errors="replace")
        for c in integrity.dependency_changes(before, after):
            if c["change"] == "upgraded":
                g, a = c["dependency"].split(":")
                removed = sorted(osv_ids(g, a, c["from"]) - osv_ids(g, a, c["to"]))
                candidates.append((len(removed), g, a, c["from"], c["to"], removed, pom))
    if not candidates:
        raise SystemExit(f"uptake: no upgraded dependency found in pom.xml changes since {base}")
    _, g, a, old, new, removed, pom = max(candidates)
    return {"dependencyGroupID": g, "dependencyArtifactID": a, "previousVersion": old, "newVersion": new,
            "mavenSourceLinkPre": sources_url(g, a, old), "mavenSourceLinkBreaking": sources_url(g, a, new),
            "pom": pom, "advisoriesRemoved": removed}


def _warm(image: str, tree: bytes, name: str) -> tuple[str, str]:
    """Build a tree online in `image`, keep everything Maven downloaded, return the new image and the log."""
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    proc = subprocess.run(
        ["docker", "run", "-i", "--name", name, image, "sh", "-c",
         f"mkdir -p {WORKDIR} && tar xf - -C {WORKDIR} && cd {WORKDIR} && mvn -B clean test 2>&1; "
         f"cd / && rm -rf {WORKDIR}"],
        input=tree, capture_output=True, timeout=3600)
    tag = f"uptake-local/{name}:warm"
    subprocess.run(["docker", "commit", name, tag], capture_output=True, check=True)
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    return tag, proc.stdout.decode("utf-8", "replace")


def config_hash(ws: Path) -> str:
    h = hashlib.sha256()
    for p in sorted((ws / ".bob").rglob("*")):
        if p.is_file():
            h.update(p.relative_to(ws).as_posix().encode() + p.read_bytes())
    return h.hexdigest()


def prepare(ws: Path, base: str, jdk: str = "17", with_mode: bool = True) -> dict:
    """Set up an existing checkout (HEAD = the upgrade, `base` = before it) for Bob, in place."""
    ws = Path(ws).resolve()
    head = _git(ws, "rev-parse", "HEAD").strip()
    base_sha = _git(ws, "rev-parse", base).strip()
    dep = find_upgrade(ws, base_sha)
    stock = f"maven:3.9-eclipse-temurin-{jdk}"
    subprocess.run(["docker", "pull", "-q", stock], capture_output=True)
    key = head[:12]
    pre_image, pre_log = _warm(stock, _archive(ws, base_sha), f"{key}-pre")
    img, _ = _warm(pre_image, _archive(ws, head), f"{key}")
    pre = container.parse(pre_log, WORKDIR)
    before = container.build(img, ws, WORKDIR)

    roots = layout.roots(ws)
    rx = layout.edit_regex(roots)
    workspace.install_bob_config(ws, rx, with_mode)
    # Uptake's own files stay out of the project's history and out of the diff the auditor reads.
    exclude = ws / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    exclude.write_text(existing + "".join(f"\n/{c}/" for c in CONFIG_FILES if f"/{c}/" not in existing)
                       + "\n/UPGRADE_RECEIPT.md\n", encoding="utf-8")

    status = before["status"]
    case = {"breakingCommit": head, "baseCommit": base_sha, "generic": True,
            "project": ws.name, "updatedDependency": dep,
            "failureCategory": {"COMPILATION_FAILURE": "COMPILATION_FAILURE", "TEST_FAILURE": "TEST_FAILURE"}
            .get(status, status), "advisoriesRemoved": dep.pop("advisoriesRemoved")}
    state = {"case": case, "image": img, "bumpImage": img, "workdir": WORKDIR,
             "baselineTests": pre["tests"]["run"], "baselineStatus": pre["status"], "before": before,
             "sourceRoots": roots, "editRegex": rx, "configHash": config_hash(ws),
             "preparedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (ws / ".uptake").mkdir(exist_ok=True)
    (ws / workspace.STATE).write_text(json.dumps(state, indent=1), encoding="utf-8")
    return state

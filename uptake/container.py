"""Reproduce and verify builds inside the original BUMP containers, offline.

Builds run with --network none and `mvn -o`, so nothing can be fetched at build time:
the only dependency versions available are the ones already baked into the image.
"""
import io
import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path

SUREFIRE_MARK = "<<<UPTAKE-SUREFIRE-REPORTS>>>"
TIMEOUT_MARK = "<<<UPTAKE-BUILD-TIMEOUT>>>"
COMPILE_ERR = re.compile(r"^\[ERROR\] (?P<file>/\S+\.java):\[(?P<line>\d+),(?P<col>\d+)\] (?P<msg>.*)$")
TESTS_SUMMARY = re.compile(r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)$")
FAILED_TEST = re.compile(r"^\[ERROR\]\s+(?:(?:Run \d+: )?)([\w.$]+[.#][\w$]+)(?::\d+)?\b")


def _docker(*args, timeout=900, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, check=check)


def workdir(image: str) -> str:
    if _docker("image", "inspect", image, check=False).returncode != 0:
        _docker("pull", "-q", image, timeout=1800)
    return _docker("image", "inspect", image, "--format", "{{.Config.WorkingDir}}").stdout.strip()


def extract(image: str, dest: Path) -> str:
    """Copy the project out of the image into dest. Returns the in-image project dir."""
    wd = workdir(image)
    cid = _docker("create", image).stdout.strip()
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Clear contents, not the folder itself: an IDE may have it open.
        dest.mkdir(exist_ok=True)
        for child in dest.iterdir():
            if child.is_dir():
                # git marks its objects read-only on Windows
                shutil.rmtree(child, onexc=lambda fn, path, _: (os.chmod(path, stat.S_IWRITE), fn(path)))
            else:
                child.unlink()
        _docker("cp", f"{cid}:{wd}/.", str(dest))
    finally:
        _docker("rm", "-f", cid, check=False)
    return wd


def _tar_workspace(ws: Path) -> bytes:
    """Tar the workspace sources (no .git, no build output) to stream into the container.

    Bind-mounting a Windows folder into Docker is ~5x slower for Maven than copying it in.
    """
    ws = Path(ws)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for p in ws.rglob("*"):
            rel = p.relative_to(ws).as_posix()
            top = rel.split("/", 1)[0]
            if top in (".git", ".bob", ".uptake", ".vscode", ".idea", ".serena", ".claude") or "/target/" in f"/{rel}/":
                continue
            if p.is_file():
                tar.add(p, arcname=rel, recursive=False)
    return buf.getvalue()


def ensure_image(case_id: str, breaking: str, pre: str) -> str:
    """The BUMP breaking image plus any Maven artifacts only the pre-upgrade image has (e.g. test plugins,
    never downloaded because the original build died at compile time). Existing files are never overwritten,
    so the upgraded dependency version is exactly what BUMP recorded."""
    tag = f"uptake-local/{case_id[:12]}:ready"
    if _docker("image", "inspect", tag, check=False).returncode == 0:
        return tag
    workdir(breaking), workdir(pre)
    m2 = subprocess.run(["docker", "run", "--rm", pre, "tar", "cf", "-", "-C", "/root/.m2", "repository"],
                        capture_output=True, timeout=1800, check=True).stdout
    name = f"uptake-merge-{case_id[:12]}"
    _docker("rm", "-f", name, check=False)
    subprocess.run(["docker", "run", "-i", "--name", name, "--network", "none", breaking, "sh", "-c",
                    "mkdir -p /tmp/m2 && tar xf - -C /tmp/m2 && cd /tmp/m2/repository && "
                    # busybox cp -rn skips whole directories that already exist, so copy file by file
                    "find . -type f | while read -r f; do [ -e \"/root/.m2/repository/$f\" ] || "
                    "{ mkdir -p \"/root/.m2/repository/$(dirname \"$f\")\" && cp \"$f\" \"/root/.m2/repository/$f\"; }; "
                    "done && rm -rf /tmp/m2 && "
                    # Maven refuses offline artifacts whose _remote.repositories names another repo id
                    "find /root/.m2/repository -name _remote.repositories -delete"], input=m2, capture_output=True, timeout=1800, check=True)
    _docker("commit", name, tag)
    _docker("rm", "-f", name, check=False)
    return tag


BUILD_LIMIT = 600  # seconds; a hung test suite must not hold the agent (or the benchmark) hostage


def build(image: str, ws: Path | None, wd: str, goal: str = "test", online: bool = False) -> dict:
    """Run `mvn -o clean <goal>` in the original image, optionally replacing the project with ws.

    online=True is only for proving a human-approval proposal that introduces artifacts the original image
    never downloaded (e.g. aligning a companion library's version). Agent repairs are always verified offline.
    """
    args = ["run", "--rm"] if online else ["run", "--rm", "--network", "none"]
    mvn = ("find /root/.m2/repository -name _remote.repositories -delete 2>/dev/null; "
           f"timeout {BUILD_LIMIT} mvn {'' if online else '-o '}-B clean {goal} 2>&1; rc=$?; "
           f"[ $rc -eq 143 ] && echo '{TIMEOUT_MARK}'")
    if ws is None:
        args += ["-w", wd, image, "sh", "-c", mvn]
        proc = _docker(*args, check=False, timeout=BUILD_LIMIT + 300)
        return parse(proc.stdout, wd)
    script = (f"rm -rf {wd} && mkdir -p {wd} && tar xf - -C {wd} && cd {wd} && {mvn}; "
              f"echo '{SUREFIRE_MARK}'; "
              # failing tests' own reports: assertion messages and stack traces, which Maven's summary omits
              "find . -path '*surefire-reports/*.txt' -exec grep -l -E '<<< (FAILURE|ERROR)' {} + 2>/dev/null "
              "| head -5 | xargs -r cat | head -c 30000")
    proc = subprocess.run(["docker", *args, "-i", image, "sh", "-c", script], input=_tar_workspace(ws),
                          capture_output=True, timeout=BUILD_LIMIT + 300)
    out = proc.stdout.decode("utf-8", "replace")
    log, _, reports = out.partition(SUREFIRE_MARK)
    result = parse(log, wd)
    if result["failingTests"] or result["status"] == "TEST_FAILURE":
        result["testFailureDetails"] = _condense_reports(reports)
    return result


def _condense_reports(text: str, limit: int = 6000) -> str:
    """Keep headers, assertion messages and project stack frames; drop framework frames."""
    keep = []
    noisy = ("at org.junit", "at org.apache.maven", "at sun.", "at java.", "at jdk.", "at org.testng",
             "at java.base", "at org.assertj.core.internal", "at org.opentest4j")
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(noisy) or set(s) <= set("-="):
            continue
        keep.append(line.rstrip())
    return "\n".join(keep)[:limit]


def parse(log: str, wd: str) -> dict:
    lines = log.splitlines()
    errors = {}
    for i, line in enumerate(lines):
        m = COMPILE_ERR.match(line)
        if not m:
            continue
        rel = m["file"][len(wd):].lstrip("/") if m["file"].startswith(wd) else m["file"]
        key = (rel, m["line"], m["col"], m["msg"])
        entry = errors.setdefault(key, {"file": rel, "line": int(m["line"]), "col": int(m["col"]),
                                        "message": m["msg"].strip(), "detail": []})
        # Maven prints symbol/location only on one of the repeated blocks, so merge across duplicates.
        for nxt in lines[i + 1:i + 3]:
            if nxt.startswith("[ERROR]   symbol:") or nxt.startswith("[ERROR]   location:"):
                d = " ".join(nxt.replace("[ERROR]", "").split())
                if d not in entry["detail"]:
                    entry["detail"].append(d)
    errors = list(errors.values())

    run = fail = err = skip = 0
    for line in lines:
        if "Time elapsed" in line or " - in " in line:
            continue
        m = TESTS_SUMMARY.search(line)
        if m:
            r, f, e, s = map(int, m.groups())
            run, fail, err, skip = run + r, fail + f, err + e, skip + s
    failing = sorted({m.group(1) for line in lines if (m := FAILED_TEST.match(line))
                      and "." in m.group(1) and not m.group(1).startswith("org.apache.maven")})

    if TIMEOUT_MARK in log:
        status = "TIMEOUT"
    elif "BUILD SUCCESS" in log:
        status = "SUCCESS"
    elif errors or "COMPILATION ERROR" in log:
        status = "COMPILATION_FAILURE"
    elif fail or err or "There are test failures" in log:
        status = "TEST_FAILURE"
    else:
        status = "BUILD_FAILURE"
    tail = "\n".join(l for l in lines if l.startswith("[ERROR]") or l.startswith("[WARNING] Tests"))[-4000:]
    return {"status": status, "compileErrors": errors,
            "tests": {"run": run, "failures": fail, "errors": err, "skipped": skip},
            "failingTests": failing, "errorLogTail": tail}


if __name__ == "__main__":
    import sys
    print(json.dumps(build(sys.argv[1], None, workdir(sys.argv[1])), indent=1))

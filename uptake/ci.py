"""Run the full Uptake repair pipeline inside a GitHub Actions job."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import repo as repo_mod
from . import workspace
from . import pr as pr_mod

_BOB_CMD = ["bob", "run", "--accept-license", "--trust",
            "--workspace", None,  # filled in at call time
            "--mode", "uptake",
            "--max-cost", None,   # filled in at call time
            "--max-turns", "60",
            "--format", "stream-json",
            "Repair this dependency upgrade."]

_WALL_SECONDS = 40 * 60  # 40 minutes


def _bob_cmd(ws: Path, max_cost: float) -> list[str]:
    cmd = list(_BOB_CMD)
    cmd[cmd.index(None, 0)] = str(ws)           # --workspace value
    cmd[cmd.index(None)] = str(max_cost)         # --max-cost value
    return cmd


def _kill(proc: "subprocess.Popen[bytes]") -> None:
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                       capture_output=True)
    else:
        import signal
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass


def _write_step_summary(text: str) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(text)
            if not text.endswith("\n"):
                fh.write("\n")


def run(
    ws: Path,
    base: str,
    jdk: str = "17",
    max_cost: float = 1.5,
    push: bool = False,
    repo: str | None = None,
    number: int | None = None,
    branch: str | None = None,
) -> int:
    """Run the repair pipeline.  Returns a process exit code (0 = success)."""
    ws = Path(ws).resolve()

    # ------------------------------------------------------------------
    # 1. Prepare the workspace (docker build + Bob config install)
    # ------------------------------------------------------------------
    st = repo_mod.prepare(ws, base, jdk)

    if st["before"]["status"] == "SUCCESS":
        msg = (f"The upgrade did not break the build (before status: SUCCESS)."
               f" No repair needed.\n")
        _write_step_summary(msg)
        return 0

    # ------------------------------------------------------------------
    # 2. Run Bob headless
    # ------------------------------------------------------------------
    if not shutil.which("bob"):
        raise RuntimeError(
            "bob is not on PATH. Install IBM Bob Shell before running uptake ci."
        )

    ndjson_path = ws / ".uptake" / "bob.ndjson"
    ndjson_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = _bob_cmd(ws, max_cost)
    cmd[0] = shutil.which("bob")  # resolves bob.cmd on Windows, which Popen will not find by bare name
    popen_kwargs: dict = dict(
        stdin=subprocess.DEVNULL,  # Bob Shell treats a piped stdin as extra prompt input and waits for EOF
        stdout=ndjson_path.open("wb"),
        stderr=tempfile.TemporaryFile(),
    )
    if sys.platform != "win32":
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **popen_kwargs)
    try:
        proc.wait(timeout=_WALL_SECONDS)
    except subprocess.TimeoutExpired:
        _kill(proc)
        proc.wait()
    finally:
        popen_kwargs["stdout"].close()
        popen_kwargs["stderr"].close()

    # ------------------------------------------------------------------
    # 3. Finalize: build, audit, write receipt
    # ------------------------------------------------------------------
    receipt = workspace.finalize(ws)
    verdict = receipt["verdict"]
    dep = receipt["dependency"]
    to = receipt["to"]

    # ------------------------------------------------------------------
    # 4. Commit + push production files if requested and repaired
    # ------------------------------------------------------------------
    if push and verdict.startswith("REPAIRED"):
        production_files = receipt["integrity"]["productionFilesChanged"]
        if production_files:
            subprocess.run(
                ["git", "-C", str(ws), "add", "--", *production_files],
                check=True,
            )
        baseline = receipt["baselineTestsBeforeUpgrade"]
        tests_run = receipt["after"]["tests"]["run"]
        n_advisories = len(receipt.get("advisoriesRemoved") or [])
        patch_sha = receipt["patchSha256"]
        commit_msg = (
            f"Adapt to {dep} {to} (repaired by IBM Bob via Uptake)\n"
            f"\n"
            f"Tests: {tests_run}/{baseline} passing\n"
            f"Advisories removed: {n_advisories}\n"
            f"Receipt patch sha256: {patch_sha}\n"
        )
        subprocess.run(
            ["git", "-C", str(ws),
             "-c", "user.name=Uptake",
             "-c", "user.email=uptake-bot@users.noreply.github.com",
             "commit", "--allow-empty",
             "-m", commit_msg],
            check=True,
        )
        target_branch = branch or os.environ.get("GITHUB_HEAD_REF", "")
        subprocess.run(
            ["git", "-C", str(ws), "push", "origin", f"HEAD:{target_branch}"],
            check=True,
        )

    # ------------------------------------------------------------------
    # 5. Post PR comment
    # ------------------------------------------------------------------
    if repo is not None and number is not None:
        pr_mod.post(ws, repo, number)

    # ------------------------------------------------------------------
    # 6. Write GitHub step summary
    # ------------------------------------------------------------------
    _write_step_summary(pr_mod.render_comment(ws))

    # ------------------------------------------------------------------
    # 7. Compute exit code
    # ------------------------------------------------------------------
    if verdict.startswith("REPAIRED"):
        return 0
    if verdict == "ESCALATED":
        proposal = receipt.get("proposal") or {}
        if proposal.get("provenGreen"):
            return 0
    return 1

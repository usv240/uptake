"""Tests for uptake/ci.py.

All external I/O (Docker, git, Bob subprocess, network) is mocked so the
suite runs without any real infrastructure.
"""
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

import uptake.ci as ci_mod

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

_DEP = "com.example:mylib"
_FROM = "1.0.0"
_TO = "1.1.0"

_BASE_RECEIPT = {
    "verdict": "REPAIRED",
    "dependency": _DEP,
    "from": _FROM,
    "to": _TO,
    "advisoriesRemoved": ["GHSA-0000-0000-0001"],
    "patchSha256": "abc123",
    "baselineTestsBeforeUpgrade": 42,
    "after": {"status": "SUCCESS", "tests": {"run": 42, "failures": 0, "errors": 0}, "failingTests": []},
    "before": {"status": "TEST_FAILURE", "compileErrors": 0, "failingTests": ["SomeTest"]},
    "integrity": {"productionFilesChanged": ["src/main/java/Foo.java"], "violations": [],
                  "warnings": [], "diffStat": "1 file changed"},
    "proposal": None,
}

_BROKEN_BEFORE = {"status": "TEST_FAILURE", "compileErrors": 0, "failingTests": ["SomeTest"]}
_OK_BEFORE = {"status": "SUCCESS", "compileErrors": 0, "failingTests": []}

_PREPARE_BROKEN = {
    "before": _BROKEN_BEFORE,
    "baselineTests": 42,
    "case": {"updatedDependency": {"dependencyGroupID": "com.example",
                                   "dependencyArtifactID": "mylib",
                                   "previousVersion": _FROM,
                                   "newVersion": _TO},
             "advisoriesRemoved": []},
}

_PREPARE_OK = dict(_PREPARE_BROKEN, before=_OK_BEFORE)


def _make_ws(tmp_path: Path) -> Path:
    """Create the minimal workspace directory structure ci.run() needs."""
    (tmp_path / ".uptake").mkdir(parents=True, exist_ok=True)
    # Provide a stub receipt.json so render_comment() can read it
    import json
    (tmp_path / ".uptake" / "receipt.json").write_text(
        json.dumps(_BASE_RECEIPT, indent=1), encoding="utf-8"
    )
    # Provide an empty fix.patch so render_comment() does not crash
    (tmp_path / ".uptake" / "fix.patch").write_bytes(b"")
    return tmp_path


def _popen_factory(returncode: int = 0):
    """Return a mock Popen context that always exits cleanly."""
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_proc.wait.return_value = returncode
    mock_proc.__enter__ = lambda s: s
    mock_proc.__exit__ = MagicMock(return_value=False)

    def _popen(cmd, **kwargs):
        # Close file handles that the real code opened
        stdout = kwargs.get("stdout")
        if stdout and hasattr(stdout, "close"):
            pass  # let the finally block handle it
        return mock_proc

    return _popen, mock_proc


# ---------------------------------------------------------------------------
# 1. Early exit when before.status == SUCCESS
# ---------------------------------------------------------------------------

def test_early_exit_when_build_not_broken(tmp_path):
    ws = _make_ws(tmp_path)

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_OK) as mock_prep, \
         patch("uptake.ci.workspace.finalize") as mock_fin, \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen") as mock_popen:

        code = ci_mod.run(ws, "abc1234")

    assert code == 0
    mock_fin.assert_not_called()
    mock_popen.assert_not_called()


def test_early_exit_writes_step_summary(tmp_path, monkeypatch):
    ws = _make_ws(tmp_path)
    summary_file = tmp_path / "step_summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_OK), \
         patch("uptake.ci.workspace.finalize"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen"):

        code = ci_mod.run(ws, "abc1234")

    assert code == 0
    assert summary_file.exists()
    content = summary_file.read_text(encoding="utf-8")
    assert "did not break" in content.lower() or "success" in content.lower()


# ---------------------------------------------------------------------------
# 2. REPAIRED run with push=True
# ---------------------------------------------------------------------------

def test_repaired_push_commits_production_files(tmp_path):
    ws = _make_ws(tmp_path)
    popen_fn, mock_proc = _popen_factory(returncode=0)

    git_calls: list = []

    def fake_run(cmd, **kwargs):
        if cmd[0] == "git":
            git_calls.append(cmd)
        result = MagicMock()
        result.returncode = 0
        result.stdout = b""
        result.stderr = b""
        return result

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=_BASE_RECEIPT), \
         patch("uptake.ci.pr_mod.post") as mock_post, \
         patch("uptake.ci.pr_mod.render_comment", return_value="## comment"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn), \
         patch("subprocess.run", side_effect=fake_run):

        code = ci_mod.run(ws, "abc1234", push=True, branch="feature/upgrade")

    assert code == 0

    # git add must include only the production file
    add_calls = [c for c in git_calls if "add" in c]
    assert any("src/main/java/Foo.java" in c for c in add_calls)

    # git commit must carry the right message pieces
    commit_calls = [c for c in git_calls if "commit" in c]
    assert commit_calls, "expected at least one git commit call"
    commit_str = " ".join(str(x) for x in commit_calls[0])
    assert "Adapt to" in commit_str
    assert _DEP in commit_str
    assert _TO in commit_str
    assert "uptake-bot@users.noreply.github.com" in commit_str

    # git push to the given branch
    push_calls = [c for c in git_calls if "push" in c]
    assert push_calls, "expected at least one git push call"
    assert any("feature/upgrade" in str(c) for c in push_calls)


def test_repaired_push_uses_github_head_ref(tmp_path, monkeypatch):
    ws = _make_ws(tmp_path)
    monkeypatch.setenv("GITHUB_HEAD_REF", "deps/update-mylib")
    popen_fn, _ = _popen_factory()

    git_calls: list = []

    def fake_run(cmd, **kwargs):
        if cmd[0] == "git":
            git_calls.append(cmd)
        r = MagicMock()
        r.returncode = 0
        return r

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=_BASE_RECEIPT), \
         patch("uptake.ci.pr_mod.post"), \
         patch("uptake.ci.pr_mod.render_comment", return_value="## comment"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn), \
         patch("subprocess.run", side_effect=fake_run):

        code = ci_mod.run(ws, "abc1234", push=True)

    assert code == 0
    push_calls = [c for c in git_calls if "push" in c]
    assert any("deps/update-mylib" in str(c) for c in push_calls)


# ---------------------------------------------------------------------------
# 3. ESCALATED with proven proposal -> exit 0, no push
# ---------------------------------------------------------------------------

def test_escalated_proven_returns_0(tmp_path):
    ws = _make_ws(tmp_path)
    escalated_receipt = dict(
        _BASE_RECEIPT,
        verdict="ESCALATED",
        proposal={"provenGreen": True, "files": [], "sha256": "def456"},
    )
    # update stub receipt so render_comment works
    import json
    (ws / ".uptake" / "receipt.json").write_text(
        json.dumps(escalated_receipt, indent=1), encoding="utf-8"
    )

    popen_fn, _ = _popen_factory()

    def fake_run(cmd, **kwargs):
        r = MagicMock()
        r.returncode = 0
        return r

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=escalated_receipt), \
         patch("uptake.ci.pr_mod.post"), \
         patch("uptake.ci.pr_mod.render_comment", return_value="## comment"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn), \
         patch("subprocess.run", side_effect=fake_run):

        code = ci_mod.run(ws, "abc1234", push=True)

    assert code == 0


def test_escalated_proven_does_not_push(tmp_path):
    """push=True is irrelevant for ESCALATED: no git commit/push should happen."""
    ws = _make_ws(tmp_path)
    escalated_receipt = dict(
        _BASE_RECEIPT,
        verdict="ESCALATED",
        proposal={"provenGreen": True, "files": [], "sha256": "def456"},
    )
    import json
    (ws / ".uptake" / "receipt.json").write_text(
        json.dumps(escalated_receipt, indent=1), encoding="utf-8"
    )
    popen_fn, _ = _popen_factory()
    git_calls: list = []

    def fake_run(cmd, **kwargs):
        if cmd[0] == "git":
            git_calls.append(cmd)
        r = MagicMock()
        r.returncode = 0
        return r

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=escalated_receipt), \
         patch("uptake.ci.pr_mod.post"), \
         patch("uptake.ci.pr_mod.render_comment", return_value="## comment"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn), \
         patch("subprocess.run", side_effect=fake_run):

        ci_mod.run(ws, "abc1234", push=True)

    commit_calls = [c for c in git_calls if "commit" in c]
    push_calls = [c for c in git_calls if "push" in c]
    assert not commit_calls
    assert not push_calls


# ---------------------------------------------------------------------------
# 4. FAILED run returns 1
# ---------------------------------------------------------------------------

def test_failed_returns_1(tmp_path):
    ws = _make_ws(tmp_path)
    failed_receipt = dict(_BASE_RECEIPT, verdict="FAILED")
    import json
    (ws / ".uptake" / "receipt.json").write_text(
        json.dumps(failed_receipt, indent=1), encoding="utf-8"
    )
    popen_fn, _ = _popen_factory()

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=failed_receipt), \
         patch("uptake.ci.pr_mod.post"), \
         patch("uptake.ci.pr_mod.render_comment", return_value="## comment"), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn):

        code = ci_mod.run(ws, "abc1234")

    assert code == 1


# ---------------------------------------------------------------------------
# 5. GITHUB_STEP_SUMMARY is written
# ---------------------------------------------------------------------------

def test_step_summary_written(tmp_path, monkeypatch):
    ws = _make_ws(tmp_path)
    summary_file = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
    popen_fn, _ = _popen_factory()

    comment_text = "## Uptake: repaired!\n"

    with patch("uptake.ci.repo_mod.prepare", return_value=_PREPARE_BROKEN), \
         patch("uptake.ci.workspace.finalize", return_value=_BASE_RECEIPT), \
         patch("uptake.ci.pr_mod.post"), \
         patch("uptake.ci.pr_mod.render_comment", return_value=comment_text), \
         patch("uptake.ci.shutil.which", return_value="/usr/bin/bob"), \
         patch("subprocess.Popen", side_effect=popen_fn):

        ci_mod.run(ws, "abc1234")

    assert summary_file.exists()
    content = summary_file.read_text(encoding="utf-8")
    assert comment_text.strip() in content

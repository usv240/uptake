"""Tests for uptake/pr.py using the two committed fixture receipts."""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from uptake import pr as pr_mod

RECEIPTS = Path(__file__).resolve().parent.parent / "receipts"
ORIPA = RECEIPTS / "oripa__uptake"
HAP = RECEIPTS / "hap-java__uptake"


# ---------------------------------------------------------------------------
# render_comment: structural checks
# ---------------------------------------------------------------------------

def test_oripa_contains_marker():
    body = pr_mod.render_comment(ORIPA)
    # patchSha256 for oripa is the empty-file sha (no production code changed)
    assert "<!-- uptake-receipt:" in body
    assert "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in body


def test_hap_contains_marker():
    body = pr_mod.render_comment(HAP)
    assert "<!-- uptake-receipt:" in body
    assert "380c10136fc7ca12eea8d50c26a2153118609ed44234bcccf5acf965aec4e974" in body


def test_oripa_verdict_escalated():
    body = pr_mod.render_comment(ORIPA)
    assert "**ESCALATED**" in body


def test_hap_verdict_repaired():
    body = pr_mod.render_comment(HAP)
    assert "**REPAIRED**" in body


def test_oripa_proven_green():
    body = pr_mod.render_comment(ORIPA)
    assert "proven green" in body.lower()


def test_oripa_log4j_artifact_in_escalation():
    body = pr_mod.render_comment(ORIPA)
    assert "log4j-slf4j18-impl" in body


def test_oripa_osv_link():
    body = pr_mod.render_comment(ORIPA)
    # oripa has GHSA-jfh8-c2jp-5v3q and GHSA-vwqq-5vrc-xw9h
    assert "https://osv.dev/vulnerability/GHSA-jfh8-c2jp-5v3q" in body


def test_hap_diff_in_output():
    body = pr_mod.render_comment(HAP)
    # The fix.patch for hap-java removes TlsFatalAlert references
    assert "TlsFatalAlert" in body or "bad_record_mac" in body


def test_hap_diff_block():
    body = pr_mod.render_comment(HAP)
    assert "```diff" in body


# ---------------------------------------------------------------------------
# ASCII-only output
# ---------------------------------------------------------------------------

def test_oripa_ascii_only():
    body = pr_mod.render_comment(ORIPA)
    non_ascii = [ch for ch in body if ord(ch) > 127]
    assert non_ascii == [], f"Non-ASCII chars found: {non_ascii[:10]}"


def test_hap_ascii_only():
    body = pr_mod.render_comment(HAP)
    non_ascii = [ch for ch in body if ord(ch) > 127]
    assert non_ascii == [], f"Non-ASCII chars found: {non_ascii[:10]}"


# ---------------------------------------------------------------------------
# post(): calls gh with correct arguments, passes body on stdin
# ---------------------------------------------------------------------------

def test_post_calls_gh_with_correct_args():
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("shutil.which", return_value="/usr/bin/gh"), \
         patch("subprocess.run", return_value=mock_result) as mock_run:
        pr_mod.post(HAP, "owner/repo", 42)

    mock_run.assert_called_once()
    call_args = mock_run.call_args
    cmd = call_args[0][0]
    assert cmd[0] == "gh"
    assert "pr" in cmd
    assert "comment" in cmd
    assert "42" in cmd
    assert "--repo" in cmd
    idx_repo = cmd.index("--repo")
    assert cmd[idx_repo + 1] == "owner/repo"
    assert "--body-file" in cmd
    idx_bf = cmd.index("--body-file")
    assert cmd[idx_bf + 1] == "-"

    # Body is passed on stdin as bytes
    kwargs = call_args[1]
    assert "input" in kwargs
    body_bytes = kwargs["input"]
    assert isinstance(body_bytes, bytes)
    body = body_bytes.decode("utf-8")
    assert "<!-- uptake-receipt:" in body


def test_post_raises_when_gh_missing():
    with patch("shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="gh"):
            pr_mod.post(HAP, "owner/repo", 1)


def test_post_raises_on_gh_failure():
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = b"authentication required"

    with patch("shutil.which", return_value="/usr/bin/gh"), \
         patch("subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="gh pr comment failed"):
            pr_mod.post(HAP, "owner/repo", 7)


# ---------------------------------------------------------------------------
# No network access: all tests use local fixture files only
# ---------------------------------------------------------------------------

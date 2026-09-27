"""The Uptake lock: which paths Bob may edit. Checked in Python here and in Bob's own JS engine by test_lock_js."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from uptake import layout

B = "\\"


def pom(build: str = "") -> str:
    return f"<project><modelVersion>4.0.0</modelVersion><build>{build}</build></project>"


@pytest.fixture
def maven_std(tmp_path):
    (tmp_path / "pom.xml").write_text(pom(), encoding="utf-8")
    return tmp_path


@pytest.fixture
def custom_layout(tmp_path):
    (tmp_path / "pom.xml").write_text(
        pom("<sourceDirectory>src/java</sourceDirectory><testSourceDirectory>src/java-test</testSourceDirectory>"),
        encoding="utf-8")
    return tmp_path


@pytest.fixture
def multi_module_basedir(tmp_path):
    (tmp_path / "pom.xml").write_text(pom("<sourceDirectory>${project.basedir}/src</sourceDirectory>"
                                          "<testSourceDirectory>${project.basedir}/test</testSourceDirectory>"),
                                      encoding="utf-8")
    for m in ("core", "extensions/struts2"):
        (tmp_path / m).mkdir(parents=True)
        (tmp_path / m / "pom.xml").write_text(pom(), encoding="utf-8")
    return tmp_path


STD = [
    ("src/main/java/io/x/A.java", True),
    # Allowed: Bob sends absolute paths, so any prefix may precede a source root. A file in a folder that is
    # not a module is never compiled, so this cannot change what the build proves.
    ("module-a/src/main/java/a/B.java", True),
    (B.join(["C:", "work", "proj", "src", "main", "java", "io", "x", "A.java"]), True),
    ("/work/proj/src/main/java/A.java", True),
    (".uptake/rationale.md", True),
    (".uptake/escalation.md", True),
    (".uptake/proposed.patch", True),
    ("pom.xml", False),
    ("src/test/java/a/ATest.java", False),
    ("src/main/java/../../test/java/ATest.java", False),
    (B.join(["src", "main", "java", "..", "..", "test", "java", "ATest.java"]), False),
    ("src/test/java/src/main/java/X.java", False),
    (".bob/custom_modes.yaml", False),
    ("src/main/resources/app.properties", False),
    (".uptake/receipt.json", False),
    ("UPGRADE_RECEIPT.md", False),
    ("src/main/java/a/pom.xml", False),
]


@pytest.mark.parametrize("path,allowed", STD)
def test_standard_layout(maven_std, path, allowed):
    rx = re.compile(layout.edit_regex(layout.roots(maven_std)))
    assert bool(rx.match(path)) is allowed


def test_custom_source_directory(custom_layout):
    r = layout.roots(custom_layout)
    assert r == {"production": ["src/java"], "test": ["src/java-test"]}
    rx = re.compile(layout.edit_regex(r))
    assert rx.match("src/java/liquibase/ext/X.java")
    assert not rx.match("src/java-test/liquibase/XTest.java")
    assert not rx.match("src/main/java/X.java")


def test_inherited_basedir_roots(multi_module_basedir):
    r = layout.roots(multi_module_basedir)
    assert "core/src" in r["production"] and "extensions/struts2/src" in r["production"]
    assert "extensions/struts2/test" in r["test"]
    rx = re.compile(layout.edit_regex(r))
    assert rx.match("extensions/struts2/src/com/google/inject/struts2/S.java")
    assert not rx.match("extensions/struts2/test/com/google/inject/struts2/T.java")


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_lock_js(maven_std):
    """Bob evaluates fileRegex with JavaScript's `new RegExp`; the result must match Python's exactly."""
    rx = layout.edit_regex(layout.roots(maven_std))
    script = ("const rx=new RegExp(process.argv[1]);const cases=JSON.parse(process.argv[2]);"
              "process.stdout.write(JSON.stringify(cases.map(p=>rx.test(p))))")
    import json
    out = subprocess.run(["node", "-e", script, rx, json.dumps([p for p, _ in STD])],
                         capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [a for _, a in STD]


def test_mode_template_is_valid_yaml_with_lock():
    text = (Path(__file__).resolve().parent.parent / ".bob" / "custom_modes.yaml").read_text(encoding="utf-8")
    assert "slug: uptake" in text and "fileRegex:" in text
    assert "- execute" not in text, "the Uptake mode must not have a shell"
    assert "allowedSubagents" in text and "- explore" in text

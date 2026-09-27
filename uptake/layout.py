"""Where a Maven project keeps its production and test sources, read from its own pom files.

The Uptake lock is computed from this, so a project using `src/java` or `${project.basedir}/src` gets a lock
that fits it, instead of a hard-coded `src/main/java`.
"""
import re
from pathlib import Path

SKIP = {"target", ".git", ".bob", ".uptake", "node_modules"}


def _tag(pom: str, name: str) -> str | None:
    # only the <build> section's direct settings, not plugin configuration that happens to reuse the name
    build = re.search(r"<build>(.*?)</build>", pom, re.S)
    m = re.search(rf"<{name}>\s*([^<\s]+)\s*</{name}>", build.group(1)) if build else None
    return m.group(1) if m else None


def _norm(value: str) -> str:
    value = value.replace("${project.basedir}", "").replace("${basedir}", "").replace("\\", "/")
    return value.strip("/")


def modules(ws: Path) -> list[Path]:
    return sorted(p for p in Path(ws).rglob("pom.xml") if not SKIP & set(p.relative_to(ws).parts[:-1]))


def roots(ws: Path) -> dict:
    """{"production": [...], "test": [...]} as workspace-relative POSIX paths."""
    ws = Path(ws)
    poms = modules(ws)
    text = {p: p.read_text(encoding="utf-8", errors="replace") for p in poms}

    def inherited(pom: Path, name: str, default: str) -> str:
        # nearest ancestor pom (by directory) that sets it; Maven inherits <build> settings the same way
        for anc in [pom, *[q for q in poms if q.parent in pom.parents]][::1]:
            v = _tag(text[anc], name)
            if v:
                return _norm(v)
        return default

    prod, test = set(), set()
    for pom in poms:
        mod = pom.parent.relative_to(ws).as_posix()
        mod = "" if mod == "." else mod + "/"
        prod.add(mod + inherited(pom, "sourceDirectory", "src/main/java"))
        test.add(mod + inherited(pom, "testSourceDirectory", "src/test/java"))
    prod -= test
    return {"production": sorted(prod), "test": sorted(test)}


def _alt(paths: list[str]) -> str:
    return "|".join(re.escape(p).replace("/", "[\\\\/]") for p in sorted(paths, key=len, reverse=True))


def edit_regex(r: dict) -> str:
    """JavaScript-compatible regex (Bob evaluates fileRegex with `new RegExp`) for files the agent may edit.

    Paths may arrive absolute or workspace-relative, with either separator, so the root may be preceded by
    anything ending in a separator. `..` segments and any path through a test root are refused outright.
    """
    prod, test = _alt(r["production"]), _alt(r["test"])
    return ("^(?!.*(?:^|[\\\\/])\\.\\.(?:[\\\\/]|$))"
            f"(?!(?:.*[\\\\/])?(?:{test})[\\\\/])"
            f"(?:(?:.*[\\\\/])?(?:{prod})[\\\\/](?:[^\\\\/]+[\\\\/])*[^\\\\/]+\\.java"
            "|(?:.*[\\\\/])?\\.uptake[\\\\/](?:rationale\\.md|escalation\\.md|proposed\\.patch))$")

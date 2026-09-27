"""MCP server that gives Bob evidence and a verifier, but no way to move the goalposts.

Tools only read the workspace and run builds in the original offline container.
None of them can edit files, change dependency versions, or skip tests.
"""
import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import apidiff, container, integrity, workspace

WS = Path(os.environ.get("UPTAKE_WS", ".")).resolve()
mcp = FastMCP("uptake")


def _state() -> dict:
    return workspace.state(WS)


@mcp.tool()
def uptake_status() -> str:
    """The upgrade being repaired: dependency, versions, advisories it removes, the original failure,
    and how many tests the project ran before the upgrade. Call this first."""
    st = _state()
    d = st["case"]["updatedDependency"]
    return json.dumps({
        "dependency": f"{d['dependencyGroupID']}:{d['dependencyArtifactID']}",
        "from": d["previousVersion"], "to": d["newVersion"],
        "advisoriesRemovedByUpgrade": st["case"]["advisoriesRemoved"],
        "failureBeforeRepair": {k: st["before"][k] for k in ("status", "compileErrors", "failingTests", "errorLogTail")},
        "testsRunBeforeUpgrade": st["baselineTests"],
    }, indent=1)


@mcp.tool()
def uptake_build() -> str:
    """Compile and run the full test suite in the original container, offline, against the NEW dependency version.
    Returns status, compile errors, test counts and failing tests. For each unresolved symbol it also returns
    API evidence: where the symbol lived in the old version and what exists in the new one."""
    st = _state()
    b = container.build(st["image"], WS, st["workdir"])
    b["testsRunBeforeUpgrade"] = st["baselineTests"]
    if b["compileErrors"]:
        b["apiEvidence"] = [apidiff.lookup(s, st["case"], st.get("bumpImage", st["image"]), m)
                            for s, m in apidiff.symbols_from_errors(b["compileErrors"])[:6]]
    return json.dumps(b, indent=1)


@mcp.tool()
def uptake_api_lookup(symbol: str, member: str = "") -> str:
    """Look up a class, package or member across the old and new versions of the upgraded dependency and the
    build classpath. symbol: fully qualified or simple class name, or a package. member: optional method/field."""
    st = _state()
    return json.dumps(apidiff.lookup(symbol, st["case"], st.get("bumpImage", st["image"]), member or None), indent=1)


def uptake_audit() -> str:
    """Independent integrity audit of the current changes: which files changed, whether any protected file
    (tests, build files, config) was touched, and behaviour-review warnings in production code."""
    return json.dumps(integrity.audit(WS), indent=1)


if not os.environ.get("UPTAKE_BARE"):
    mcp.tool()(uptake_audit)

if __name__ == "__main__":
    mcp.run()

"""What changed in the library API, as evidence for the repair.

Three sources, all deterministic:
  * old and new sources jars of the upgraded dependency (Maven Central), for signatures and @deprecated notes
  * an index of every class actually on the offline classpath of the breaking image,
    so a suggested replacement is only offered if the build can really see it
"""
import difflib
import io
import json
import re
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

CACHE = Path.home() / ".uptake" / "cache"


def _fetch(url: str) -> bytes | None:
    dest = CACHE / "http" / re.sub(r"[^\w.-]", "_", url)
    if dest.exists():
        return dest.read_bytes() or None
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = urllib.request.urlopen(url, timeout=120).read()
    except Exception:
        data = b""
    dest.write_bytes(data)
    return data or None


def _sources(url: str) -> dict[str, str]:
    """FQN -> source text for every .java file in a sources jar."""
    data = _fetch(url)
    if not data:
        return {}
    out = {}
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if n.endswith(".java") and not n.endswith("package-info.java"):
                out[n[:-5].replace("/", ".")] = z.read(n).decode("utf-8", "replace")
    return out


def classpath_index(image: str) -> dict[str, str]:
    """Simple-and-full class names available in the image's local Maven repo -> jar path."""
    dest = CACHE / "classpath" / (re.sub(r"[^\w.-]", "_", image) + ".json")
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    proc = subprocess.run(
        ["docker", "run", "--rm", "--network", "none", image, "sh", "-c",
         "cd /root/.m2/repository && find . -name '*.jar' ! -name '*-sources.jar' | tar cf - -T -"],
        capture_output=True, timeout=900)
    index = {}
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tar:
        for member in tar:
            f = tar.extractfile(member)
            if not f:
                continue
            try:
                with zipfile.ZipFile(io.BytesIO(f.read())) as z:
                    for n in z.namelist():
                        if n.endswith(".class") and "$" not in n and not n.startswith("META-INF"):
                            index.setdefault(n[:-6].replace("/", "."), member.name.lstrip("./"))
            except zipfile.BadZipFile:
                continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(index), encoding="utf-8")
    return index


def _members(src: str, name: str, context: int = 2) -> list[str]:
    """Declaration lines in src that mention `name` as a method/field/type, with a little context."""
    lines = src.splitlines()
    hits = []
    decl = re.compile(rf"^\s*(public|protected|static|final|abstract|default|private|synchronized|<|@interface|class|interface|enum)"
                      rf".*\b{re.escape(name)}\b")
    for i, line in enumerate(lines):
        if decl.search(line):
            lo = max(0, i - context)
            hits.append("\n".join(lines[lo:i + 1]).strip())
    return hits[:6]


def _deprecations(src: str, name: str | None) -> list[str]:
    notes = []
    for m in re.finditer(r"@deprecated\s+(.*?)(?:\*/|\n\s*\*\s*@)", src, re.S):
        text = " ".join(m.group(1).replace("*", " ").split())
        tail = src[m.end():m.end() + 400]
        if name is None or re.search(rf"\b{re.escape(name)}\b", tail.split("{")[0] + tail.split(";")[0]):
            notes.append(text[:300])
    return notes[:4]


def lookup(symbol: str, case: dict, image: str, member: str | None = None) -> dict:
    """Explain what happened to `symbol` (FQN, package, or simple class name) between the two versions."""
    dep = case["updatedDependency"]
    old = _sources(dep["mavenSourceLinkPre"])
    new = _sources(dep["mavenSourceLinkBreaking"])
    cp = classpath_index(image)
    simple = symbol.rsplit(".", 1)[-1]

    def find(space: dict) -> list[str]:
        if symbol in space:
            return [symbol]
        pkg = [k for k in space if k.startswith(symbol + ".")]
        if pkg:
            return pkg[:40]
        return [k for k in space if k.rsplit(".", 1)[-1] == simple][:10]

    in_old, in_new = find(old), find(new)
    on_cp = [k for k in cp if k.rsplit(".", 1)[-1] == simple and "." in symbol or k == symbol][:10] if "." in symbol \
        else [k for k in cp if k.rsplit(".", 1)[-1] == simple][:10]
    result = {
        "symbol": symbol,
        "dependency": f"{dep['dependencyGroupID']}:{dep['dependencyArtifactID']} {dep['previousVersion']} -> {dep['newVersion']}",
        "inOldVersion": in_old[:10],
        "inNewVersion": in_new[:10],
        "availableOnBuildClasspath": [{"class": k, "jar": cp[k]} for k in on_cp],
    }
    if not in_new and simple[:1].isupper():
        close = difflib.get_close_matches(simple, {k.rsplit(".", 1)[-1] for k in new}, n=5, cutoff=0.75)
        result["similarNamesInNewVersion"] = [k for k in new if k.rsplit(".", 1)[-1] in close][:8]
    if len(in_old) == 1 and in_old[0] in old:
        src = old[in_old[0]]
        result["deprecationNotesInOldVersion"] = _deprecations(src, member)
        if member:
            result["memberInOldVersion"] = _members(src, member)
    if member and len(in_new) == 1 and in_new[0] in new:
        src = new[in_new[0]]
        found = _members(src, member)
        result["memberInNewVersion"] = found
        if not found:
            names = set(re.findall(r"\b(?:public|protected)\s+[\w<>\[\], ?]+\s+(\w+)\s*\(", src))
            result["similarMembersInNewVersion"] = difflib.get_close_matches(member, names, n=6, cutoff=0.5)
    if not in_new and not result["availableOnBuildClasspath"]:
        result["verdict"] = ("REMOVED: not in the new version and nothing with this name is on the build classpath. "
                             "Rewrite against what IS available, or escalate if the behaviour cannot be preserved. "
                             "Adding or changing dependencies is out of scope.")
    elif not in_new and result["availableOnBuildClasspath"]:
        result["verdict"] = "MOVED_OR_PROVIDED_ELSEWHERE: a class with this name is on the build classpath."
    else:
        result["verdict"] = "PRESENT_IN_NEW_VERSION: check the member signatures."
    return result


SYMBOL_RE = re.compile(r"symbol:\s+(class|method|variable|constructor|interface|enum)\s+([\w$]+)")
PKG_RE = re.compile(r"package ([\w.]+) does not exist")
LOCATION_RE = re.compile(r"location:\s+(?:class|interface|variable \w+ of type)\s+([\w.$<>]+)")


def symbols_from_errors(errors: list[dict], sources: dict[str, str] | None = None) -> list[tuple[str, str | None]]:
    """(symbol, member) pairs worth looking up, deduplicated, from parsed compile errors."""
    out = []
    for e in errors:
        text = " ".join([e["message"], *e["detail"]])
        for pkg in PKG_RE.findall(text):
            out.append((pkg, None))
        m = SYMBOL_RE.search(text)
        loc = LOCATION_RE.search(text)
        if m and m.group(1) in ("class", "interface", "enum"):
            out.append((m.group(2), None))
        elif m and loc and m.group(1) in ("method", "variable", "constructor"):
            owner = loc.group(1).split("<")[0]
            out.append((owner, m.group(2)))
            if m.group(2)[:1].isupper():  # a type used statically, e.g. AlertDescription.bad_record_mac
                out.append((m.group(2), None))
        for owner, member in re.findall(r"(?:method|constructor) (\w+) in (?:class|interface) ([\w.$<>]+)", text):
            out.append((owner.split("<")[0], member))
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq[:12]

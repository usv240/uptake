"""The upgraded library's own documentation about the change: release notes and migration guides.

Sources, all published by the library itself:
  * changelog / release-notes / migration files shipped inside the new version's sources jar
  * GitHub releases of the library's repository between the two versions (repository taken from the new
    version's POM <scm>, or from BUMP's metadata)
Bob reads these before changing code and cites them in its rationale.
"""
import io
import json
import os
import re
import urllib.request
import zipfile

from .apidiff import _fetch

DOC_NAME = re.compile(r"(^|/)(changes|changelog|release[-_ ]?notes|history|news|migration|upgrad\w*)"
                      r"(\.(md|txt|html|adoc|rst))?$", re.I)


def _vkey(v: str) -> tuple:
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.\-_]", re.sub(r"^[^\d]*", "", v)) if x)


def _pom(group: str, artifact: str, version: str) -> str:
    url = f"https://repo1.maven.org/maven2/{group.replace('.', '/')}/{artifact}/{version}/{artifact}-{version}.pom"
    data = _fetch(url)
    return data.decode("utf-8", "replace") if data else ""


def github_slug(dep: dict) -> str | None:
    pom = _pom(dep["dependencyGroupID"], dep["dependencyArtifactID"], dep["newVersion"])
    m = re.search(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?[/<\s]", pom)
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    slug = dep.get("githubRepoSlug") or ""
    return slug if re.fullmatch(r"[\w.-]+/[\w.-]+", slug) else None


def _github(path: str):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except Exception:
        return None


def releases_between(slug: str, old: str, new: str, limit: int = 12) -> list[dict]:
    lo, hi = _vkey(old), _vkey(new)
    out = []
    for page in (1, 2, 3):
        rel = _github(f"repos/{slug}/releases?per_page=100&page={page}") or []
        for r in rel:
            k = _vkey(r.get("tag_name") or "")
            if k and lo < k <= hi and (r.get("body") or "").strip():
                out.append({"tag": r["tag_name"], "url": r.get("html_url"), "body": r["body"]})
        if len(rel) < 100:
            break
    return sorted(out, key=lambda r: _vkey(r["tag"]), reverse=True)[:limit]


def jar_docs(dep: dict) -> list[dict]:
    data = _fetch(dep["mavenSourceLinkBreaking"])
    docs = []
    if not data:
        return docs
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in z.namelist():
            if DOC_NAME.search(n) and not n.endswith("/"):
                docs.append({"file": n, "text": z.read(n).decode("utf-8", "replace")})
    return docs


def _html_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|li|h\d|tr|div)>", "\n", raw)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", text)).strip()


def repo_docs(slug: str) -> list[dict]:
    """Changelog / release-notes / migration files at the top of the repo or in docs/."""
    docs = []
    for folder in ("", "docs"):
        for f in _github(f"repos/{slug}/contents/{folder}") or []:
            if (isinstance(f, dict) and f.get("type") == "file" and DOC_NAME.search(f["name"].lower())
                    and f.get("size", 0) < 3_000_000 and f.get("download_url")):
                raw = _fetch(f["download_url"])
                if raw:
                    text = raw.decode("utf-8", "replace")
                    docs.append({"source": f["html_url"],
                                 "text": _html_text(text) if f["name"].endswith(".html") else text})
    return docs


def section_between(text: str, old: str, new: str) -> str:
    """Keep the part of a changelog covering versions after `old` up to `new`, when its headings allow it."""
    heads = [(m.start(), m.group(1)) for m in
             re.finditer(r"(?m)^[#\s]*(?:version|release)?\s*v?(\d+\.\d+(?:\.\d+)*)\b", text, re.I)]
    lo, hi = _vkey(old), _vkey(new)
    keep = []
    for i, (pos, ver) in enumerate(heads):
        if lo < _vkey(ver) <= hi:
            end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
            keep.append(text[pos:end])
    return "\n".join(keep) or text


def gather(dep: dict, symbols: list[str] | None = None, max_chars: int = 12000) -> dict:
    """Release notes and migration docs for the upgrade, trimmed to the passages that mention `symbols`."""
    symbols = [s.rsplit(".", 1)[-1] for s in (symbols or []) if s]
    slug = github_slug(dep)
    parts = [{"source": f"sources jar: {d['file']}", "text": d["text"]} for d in jar_docs(dep)]
    if slug:
        parts += [{"source": r["url"] or f"{slug}@{r['tag']}", "text": f"## {r['tag']}\n{r['body']}"}
                  for r in releases_between(slug, dep["previousVersion"], dep["newVersion"])]
        parts += [{"source": d["source"], "text": section_between(d["text"], dep["previousVersion"], dep["newVersion"])}
                  for d in repo_docs(slug)]

    def focus(text: str) -> str:
        if not symbols:
            return text
        paras = re.split(r"\n\s*\n", text)
        hits = [p for p in paras if any(s.lower() in p.lower() for s in symbols)
                or re.search(r"\b(breaking|removed|deprecat|migrat|incompatib|renamed)\w*", p, re.I)]
        return "\n\n".join(hits) or text[:1500]

    budget, docs = max_chars, []
    for p in parts:
        t = focus(p["text"]).strip()[:max(0, budget)]
        if t:
            docs.append({"source": p["source"], "text": t})
            budget -= len(t)
        if budget <= 0:
            break
    return {"dependency": f"{dep['dependencyGroupID']}:{dep['dependencyArtifactID']}",
            "from": dep["previousVersion"], "to": dep["newVersion"], "githubRepository": slug,
            "documents": docs,
            "note": "Published by the library itself. Cite the source of anything you rely on in .uptake/rationale.md."
            if docs else "No release notes or migration guide found for this upgrade."}

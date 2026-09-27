"""Shared by the recorder and the subtitler, so the pointer and the caption agree on which sentence is playing."""
import re

MAX_CUE = 58


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text.strip())
    return [p for p in parts if p]


def shares(text: str) -> list[float]:
    """Fraction of the clip each sentence occupies, in proportion to its length."""
    s = sentences(text)
    total = sum(len(x) for x in s) or 1
    return [len(x) / total for x in s]


def sentence_starts(text: str, clip_seconds: float) -> list[float]:
    out, t = [], 0.0
    for f in shares(text):
        out.append(t)
        t += f * clip_seconds
    return out


def cue_lines(sentence: str) -> list[str]:
    """Split a sentence into one-line cues of at most MAX_CUE characters: clause boundaries first, then spaces."""
    if len(sentence) <= MAX_CUE:
        return [sentence]
    clauses = re.split(r"(?<=[,;:])\s+", sentence)
    out, cur = [], ""
    for c in clauses:
        if len(c) > MAX_CUE:
            if cur:
                out.append(cur)
                cur = ""
            words, line = c.split(), ""
            for w in words:
                if len(line) + len(w) + 1 > MAX_CUE and line:
                    out.append(line)
                    line = w
                else:
                    line = f"{line} {w}".strip()
            cur = line
        elif len(cur) + len(c) + 1 > MAX_CUE and cur:
            out.append(cur)
            cur = c
        else:
            cur = f"{cur} {c}".strip()
    if cur:
        out.append(cur)
    return out

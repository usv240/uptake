"""Check the shipped artefacts against every instruction. One line per ask, ok or MISS; non-zero on any MISS.

Reads what was built (the text Polly was given, the beat records, the caption style, the encoded file and its
pixels), never the intent.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from beats import BUILD, IDE_CLIP, SITE  # noqa: E402
from common import MAX_CUE  # noqa: E402
from subtitle import FINAL  # noqa: E402

results = []


def check(name: str, ok: bool, detail: str = ""):
    results.append(ok)
    print(f"{'ok  ' if ok else 'MISS'} {name}" + (f"  ({detail})" if detail else ""))


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration,bit_rate:stream=codec_type,width,height", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def edge_is_flat_grey(t: float) -> bool:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(FINAL), "-frames:v", "1",
                          "-vf", "crop=1920:24:0:1056,scale=64:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    px = [raw[i:i + 3] for i in range(0, len(raw), 3)]
    grey = [p for p in px if abs(p[0] - p[1]) < 4 and abs(p[1] - p[2]) < 4 and 110 < p[0] < 150]
    return len(grey) > 0.9 * len(px)


def strip_comments(src: str) -> str:
    return re.sub(r"(?m)#.*$", "", re.sub(r'"""[\s\S]*?"""', "", src))


def main() -> int:
    beats = json.loads((BUILD / "beats.json").read_text(encoding="utf-8"))
    narration = json.loads((BUILD / "narration.json").read_text(encoding="utf-8"))
    said = " ".join(n["ssml"] for n in narration)
    srt = (BUILD / "captions.srt").read_text(encoding="utf-8")
    style = (BUILD / "caption_style.txt").read_text(encoding="utf-8")

    name = os.environ.get("UPTAKE_SPEAKER", "").strip()
    check("opens with a person, no pause in front", beats[0]["say"].startswith("Hi everyone") and beats[0]["pause"] == 0)
    check("speaker's name is in what Polly was given", bool(name) and name in narration[0]["ssml"], name or "UPTAKE_SPEAKER unset")
    check("closes with a separate 'Thank you.' beat", beats[-1]["say"] == "Thank you." and beats[-2]["id"] == "close")
    check("uncomfortable numbers said out loud", "Not every case works" in said and "three of four" in said)
    check("failure case shown", any(b["shot"] == "results" for b in beats))
    check("no em dashes or en dashes in narration or captions", not re.search("[–—]", said + srt))
    check("no emoji in narration or captions", not re.search("[\U0001F300-\U0001FAFF☀-➿]", said + srt))
    check("voice is Polly long-form Patrick at 87%", 'rate="87%"' in said
          and "Patrick" in strip_comments((Path(__file__).parent / "narrate.py").read_text(encoding="utf-8"))
          and "long-form" in strip_comments((Path(__file__).parent / "narrate.py").read_text(encoding="utf-8")))
    check("records against the live deployment", SITE.startswith("https://") and "localhost" not in SITE)
    check("Bob IDE footage in the video", IDE_CLIP.exists() and any(b["shot"] == "ide" for b in beats),
          "demo/ide_clip.mp4 missing" if not IDE_CLIP.exists() else "")
    live = any(b["shot"] == "live_pr" for b in beats)
    check("live Dependabot PR shown", live, "" if live else "demo/video/live_pr.json missing")
    missing = json.loads((BUILD / "missing_targets.json").read_text(encoding="utf-8")) if (BUILD / "missing_targets.json").exists() else ["not recorded"]
    check("every pointer target was found on camera", not missing, ", ".join(missing[:3]))
    check("ends on the product, not a logo or black", beats[-1]["shot"] == "hold" and beats[-2]["shot"] == "close")

    cues = [c for c in srt.strip().split("\n\n") if c]
    lines = [c.split("\n")[2:] for c in cues]
    check("captions: one line per cue", all(len(l) == 1 for l in lines))
    check(f"captions: at most {MAX_CUE} characters", all(len(l[0]) <= MAX_CUE for l in lines if l),
          f"longest {max((len(l[0]) for l in lines if l), default=0)}")
    check("captions cover the opening and the thank you", "Hi everyone" in srt and "Thank you." in srt)
    check("caption style: box at 80% opacity", "BorderStyle=3" in style and "BackColour=&H33000000" in style)
    check("caption style: FontSize 15 at 1080p", "FontSize=15" in style)
    check(".srt shipped next to the video", (FINAL.parent / "uptake_demo.srt").exists())

    info = probe(FINAL)
    dur = float(info["format"]["duration"])
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    kbps = int(info["format"].get("bit_rate", 0)) // 1000
    check("duration under 3:00", dur < 180, f"{dur:.1f}s")
    check("duration at or under the 2:50 aim", dur <= 170, f"{dur:.1f}s")
    check("resolution 1920x1080", (v["width"], v["height"]) == (1920, 1080), f"{v['width']}x{v['height']}")
    check("has an audio track", any(s["codec_type"] == "audio" for s in info["streams"]))
    check("bitrate reported", kbps > 0, f"{kbps} kbps")
    flat = [t for t in (dur * 0.2, dur * 0.5, dur * 0.8) if edge_is_flat_grey(t)]
    check("no flat grey band at the frame edge", not flat, f"at {flat}" if flat else "")

    missed = results.count(False)
    print(f"\n{len(results) - missed}/{len(results)} ok")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())

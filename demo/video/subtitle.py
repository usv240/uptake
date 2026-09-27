"""Captions from where each line really landed in the finished cut, burned in, and shipped as .srt.

python demo/video/subtitle.py -> build/captions.srt and demo/uptake_demo.mp4
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from beats import BUILD  # noqa: E402
from common import cue_lines, sentences, shares  # noqa: E402

STYLE = ("FontName=Inter,FontSize=15,PrimaryColour=&H00FFFFFF,BackColour=&H33000000,OutlineColour=&H33000000,"
         "BorderStyle=3,Outline=6,Shadow=0,MarginV=36,Alignment=2")
FINAL = BUILD.parent.parent / "uptake_demo.mp4"


def ts(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def cues() -> list[tuple[float, float, str]]:
    beats = {b["id"]: b for b in json.loads((BUILD / "beats.json").read_text(encoding="utf-8"))}
    out = []
    for l in json.loads((BUILD / "landed.json").read_text(encoding="utf-8")):
        text = beats[l["id"]]["say"]
        t = l["at"]
        for sent, share in zip(sentences(text), shares(text)):
            dur = share * l["clip"]
            lines = cue_lines(sent)
            total = sum(len(x) for x in lines) or 1
            for line in lines:
                d = dur * len(line) / total
                out.append((t, t + d, line))
                t += d
    return out


def main() -> int:
    srt = "".join(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(cues(), 1))
    (BUILD / "captions.srt").write_text(srt, encoding="utf-8")
    shutil.copy(BUILD / "captions.srt", BUILD.parent.parent / "uptake_demo.srt")
    # the subtitles filter parses its own argument, so a Windows drive colon breaks it: run from BUILD with a bare name
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "master.mp4",
                    "-vf", f"subtitles=captions.srt:force_style='{STYLE}'",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", str(FINAL)], cwd=BUILD, check=True)
    (BUILD / "caption_style.txt").write_text(STYLE, encoding="utf-8")
    print(f"{srt.count(' --> ')} cues -> {FINAL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

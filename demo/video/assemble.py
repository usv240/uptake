"""Cut each beat to its line plus slack, splice the IDE recording, and lay the narration where each beat landed.

Nothing is sped up: a cut only removes the tail after the screen has settled and the line has ended.
python demo/video/assemble.py -> build/master.mp4 and build/landed.json
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from beats import BUILD, IDE_CLIP  # noqa: E402

SLACK = 1.2
LEAD = 0.35  # show the first beat's page settled for a moment, not a blank frame
V = ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30"]


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main() -> int:
    log = json.loads((BUILD / "beatlog.json").read_text(encoding="utf-8"))
    seg_dir = BUILD / "segments"
    seg_dir.mkdir(exist_ok=True)
    parts, landed, t = [], [], 0.0
    for i, b in enumerate(log):
        nxt = log[i + 1]["compose"] if i + 1 < len(log) else b["end"]
        start = max(0.0, b["start"] - (LEAD if i == 0 else 0.0))
        end = min(b["start"] + b["clip"] + SLACK, max(nxt, b["start"] + b["clip"] + 0.3))
        dur = round(end - start, 3)
        out = seg_dir / f"{i:02d}_{b['id']}.mp4"
        if b["shot"] == "ide" and IDE_CLIP.exists():
            ff("-i", str(IDE_CLIP), "-t", f"{dur}",
               "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0B0D10,"
                      f"tpad=stop_mode=clone:stop_duration={dur}", "-an", *V, str(out))
        else:
            ff("-ss", f"{start}", "-i", str(BUILD / "raw.webm"), "-t", f"{dur}", "-an", *V, str(out))
        parts.append(out)
        landed.append({"id": b["id"], "at": round(t + (b["start"] - start), 3), "clip": b["clip"], "segment": dur})
        print(f"{b['id']:10} segment {dur:5.1f}s (cut {max(0.0, b['end'] - b['start'] - dur):4.1f}s of tail)")
        t += dur
    lst = BUILD / "segments.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(BUILD / "video_only.mp4"))

    inputs, filters = ["-i", str(BUILD / "video_only.mp4")], []
    for k, b in enumerate(landed):
        inputs += ["-i", str(BUILD / "audio" / f"{b['id']}.mp3")]
        ms = int(b["at"] * 1000)
        filters.append(f"[{k + 1}:a]aresample=48000,adelay={ms}|{ms}[a{k}]")
    mix = "".join(f"[a{k}]" for k in range(len(landed)))
    filters.append(f"{mix}amix=inputs={len(landed)}:normalize=0:dropout_transition=0[aout]")
    ff(*inputs, "-filter_complex", ";".join(filters), "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
       "-c:a", "aac", "-b:a", "192k", "-shortest", str(BUILD / "master.mp4"))
    (BUILD / "landed.json").write_text(json.dumps(landed, indent=1), encoding="utf-8")
    print(f"master: {t:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

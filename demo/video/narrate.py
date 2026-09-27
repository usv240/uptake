"""One Amazon Polly clip per beat: engine long-form, voice Patrick, SSML prosody rate 87%.

python demo/video/narrate.py -> build/audio/<id>.mp3 and build/narration.json (exact text sent, durations).
"""
import json
import subprocess
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
VOICE, ENGINE, RATE = "Patrick", "long-form", "87%"


def duration(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout.strip())


def main() -> int:
    beats = json.loads((BUILD / "beats.json").read_text(encoding="utf-8"))
    (BUILD / "audio").mkdir(parents=True, exist_ok=True)
    out = []
    for b in beats:
        ssml = f'<speak><prosody rate="{RATE}">{escape(b["say"])}</prosody></speak>'
        mp3 = BUILD / "audio" / f"{b['id']}.mp3"
        subprocess.run(["aws", "polly", "synthesize-speech", "--engine", ENGINE, "--voice-id", VOICE,
                        "--text-type", "ssml", "--text", ssml, "--output-format", "mp3", "--region", "us-east-1",
                        str(mp3)], capture_output=True, check=True)
        d = duration(mp3)
        out.append({"id": b["id"], "ssml": ssml, "seconds": round(d, 3)})
        print(f"{b['id']:10} {d:5.1f}s")
    (BUILD / "narration.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    total = sum(x["seconds"] for x in out) + sum(b["pause"] for b in beats)
    print(f"narration total with pauses: {total:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

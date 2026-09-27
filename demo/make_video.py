"""Build the demo video: narration (edge-tts) + scripted browser recordings (Playwright) -> MP4 (ffmpeg).

  python demo/make_video.py            # all segments
  python demo/make_video.py hook cheat # just these (for iteration)

Every visual is the real site, slides or a replay of captured output; nothing is mocked.
An optional Bob IDE screen recording at demo/ide_clip.mp4 is used for the "ide" segment if present.
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "demo" / "build"
VOICE = "en-US-AndrewNeural"
W, H = 1920, 1080


def url(rel: str) -> str:
    return (ROOT / rel).resolve().as_uri()


SEGMENTS = json.loads((ROOT / "demo" / "script.json").read_text(encoding="utf-8"))


async def tts(seg: dict) -> float:
    mp3 = OUT / f"{seg['id']}.mp3"
    for attempt in range(5):
        try:
            await edge_tts.Communicate(seg["say"], VOICE, rate=seg.get("rate", "+4%")).save(str(mp3))
            break
        except Exception as e:  # the TTS service drops requests now and then
            if attempt == 4:
                raise
            print(f"  tts retry {seg['id']}: {e.__class__.__name__}", flush=True)
            await asyncio.sleep(3 * (attempt + 1))
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                                capture_output=True, text=True, check=True).stdout.strip())


async def act(page, a: dict):
    kind = a["do"]
    if kind == "goto":
        await page.goto(url(a["url"]) + a.get("hash", ""), wait_until="load")
        await page.wait_for_timeout(a.get("settle", 900))
    elif kind == "scroll":
        await page.evaluate("([sel, off]) => { const el = document.querySelector(sel);"
                            " window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY - off, behavior: 'smooth'}); }",
                            [a["to"], a.get("offset", 80)])
    elif kind == "scrollby":
        await page.mouse.wheel(0, a["y"])
    elif kind == "click":
        await page.click(a["sel"])
    elif kind == "wait":
        pass
    elif kind == "js":
        await page.evaluate(a["code"])
    await page.wait_for_timeout(int(a.get("hold", 0) * 1000))


async def record(browser, seg: dict, duration: float) -> Path:
    ctx = await browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=1,
                                    record_video_dir=str(OUT / "raw"), record_video_size={"width": W, "height": H},
                                    color_scheme="dark")
    page = await ctx.new_page()
    t0 = asyncio.get_event_loop().time()
    for a in seg["actions"]:
        await act(page, a)
    left = duration + 0.6 - (asyncio.get_event_loop().time() - t0)
    if left > 0:
        await page.wait_for_timeout(int(left * 1000))
    await ctx.close()
    webm = Path(await page.video.path())
    dest = OUT / f"{seg['id']}.webm"
    webm.replace(dest)
    return dest


def mux(seg: dict, video: Path, duration: float) -> Path:
    """Trim the recording's page-load lead-in, then lay the narration over it."""
    out = OUT / f"{seg['id']}.mp4"
    lead = seg.get("lead", 1.0)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(lead), "-i", str(video), "-i", str(OUT / f"{seg['id']}.mp3"),
                    "-t", f"{duration + 0.5:.2f}", "-vf", f"scale={W}:{H},fps=30,format=yuv420p",
                    "-af", "apad", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", str(out)], check=True)
    return out


def ide_segment(seg: dict, duration: float) -> Path | None:
    clip = ROOT / "demo" / "ide_clip.mp4"
    if not clip.exists():
        return None
    out = OUT / f"{seg['id']}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clip), "-i", str(OUT / f"{seg['id']}.mp3"),
                    "-t", f"{duration + 0.5:.2f}",
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0B0D10,fps=30,format=yuv420p",
                    "-map", "0:v", "-map", "1:a", "-af", "apad", "-c:v", "libx264", "-crf", "20", "-c:a", "aac",
                    "-shortest", str(out)], check=True)
    return out


async def main(only: list[str]):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw").mkdir(exist_ok=True)
    segs = [s for s in SEGMENTS if not only or s["id"] in only]
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")
        for seg in segs:
            d = await tts(seg)
            made = ide_segment(seg, d) if seg.get("ide") else None
            if made is None:
                made = mux(seg, await record(browser, seg, d), d)
            print(f"{seg['id']:10} {d:5.1f}s -> {made.name}", flush=True)
        await browser.close()
    if not only:
        lst = OUT / "list.txt"
        lst.write_text("".join(f"file '{(OUT / (s['id'] + '.mp4')).as_posix()}'\n" for s in SEGMENTS), encoding="utf-8")
        final = ROOT / "demo" / "uptake_demo.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final)],
                       check=True)
        dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final)],
                             capture_output=True, text=True).stdout.strip()
        print(f"final: {final} ({float(dur):.1f}s)")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

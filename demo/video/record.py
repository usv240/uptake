"""Playwright drives and films the live site. Every beat: compose the shot in silence, log the moment the line
starts, then act while it is spoken, pointing at each thing as its sentence plays.

python demo/video/record.py -> build/raw.webm and build/beatlog.json
"""
import json
import shutil
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from beats import BUILD, SITE  # noqa: E402
from common import sentence_starts  # noqa: E402

W, H, BAR, ZOOM, GH_ZOOM = 1920, 1080, 44, 1.35, 1.3
LIVE = json.loads((Path(__file__).resolve().parent / "live_pr.json").read_text(encoding="utf-8")) \
    if (Path(__file__).resolve().parent / "live_pr.json").exists() else {}

OVERLAY = f"""
(() => {{
  const install = () => {{
    if (document.getElementById('__bar')) return;
    const bar = document.createElement('div');
    bar.id = '__bar';
    bar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:{BAR}px;z-index:2147483647;background:#1f2328;'
      + 'display:flex;align-items:center;gap:12px;padding:0 20px;border-bottom:1px solid #30363d;'
      + 'font:500 19px ui-monospace,"Geist Mono",Consolas,monospace;color:#e6edf3;box-sizing:border-box;pointer-events:none';
    bar.innerHTML = '<svg width="16" height="18" viewBox="0 0 16 18" fill="#9ba3af"><path d="M3 8V6a5 5 0 0110 0v2h1a1 1 0 011 1v8a1 1 0 01-1 1H2a1 1 0 01-1-1V9a1 1 0 011-1h1zm2 0h6V6a3 3 0 00-6 0v2z"/></svg><span id="__url"></span>';
    document.documentElement.appendChild(bar);
    const url = bar.querySelector('#__url');
    const tick = () => {{ url.textContent = location.href; }};
    tick(); setInterval(tick, 200);
    // our site is laid out for reading at 1160px wide; zoom its body so it reads at video size (not GitHub's)
    const Z = location.host.endsWith('github.io') ? {ZOOM} : (location.host === 'github.com' ? {GH_ZOOM} : 1);
    if (Z !== 1) document.body.style.zoom = String(Z);
    document.documentElement.style.setProperty('scroll-padding-top', '{BAR + 80}px', 'important');
    document.body.style.setProperty('margin-top', ({BAR} / Z) + 'px', 'important');
    for (const el of document.querySelectorAll('body *')) {{
      const cs = getComputedStyle(el);
      if ((cs.position === 'sticky' || cs.position === 'fixed') && parseInt(cs.top || '0') === 0 && el.id !== '__bar') {{
        el.style.setProperty('top', ({BAR} / Z) + 'px', 'important');
      }}
    }}
    const ring = document.createElement('div');
    ring.id = '__cursor';
    ring.style.cssText = 'position:fixed;left:-100px;top:-100px;width:26px;height:26px;margin:-13px 0 0 -13px;'
      + 'border:2.5px solid #56B4E9;border-radius:50%;z-index:2147483647;pointer-events:none;'
      + 'box-shadow:0 0 0 2px rgba(0,0,0,.45);transition:transform .12s ease-out';
    const pulse = document.createElement('div');
    pulse.style.cssText = 'position:fixed;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;'
      + 'background:rgba(86,180,233,.45);z-index:2147483646;pointer-events:none;opacity:0;transform:scale(1)';
    document.documentElement.appendChild(ring); document.documentElement.appendChild(pulse);
    document.addEventListener('mousemove', e => {{ ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px'; }}, true);
    document.addEventListener('mousedown', e => {{
      pulse.style.left = e.clientX + 'px'; pulse.style.top = e.clientY + 'px';
      pulse.animate([{{opacity: .9, transform: 'scale(1)'}}, {{opacity: 0, transform: 'scale(2.6)'}}], {{duration: 450, easing: 'ease-out'}});
      ring.style.transform = 'scale(.8)'; setTimeout(() => ring.style.transform = 'scale(1)', 140);
    }}, true);
  }};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
}})();
"""

EASE_SCROLL = """
([y, frames]) => new Promise(done => {
  const start = window.scrollY, dist = y - start; let i = 0;
  const step = () => { i++; const t = i / frames; const e = t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;
    window.scrollTo(0, start + dist * e); if (i < frames) requestAnimationFrame(step); else done(); };
  requestAnimationFrame(step);
})
"""


class Camera:
    def __init__(self, page, narration: dict):
        self.page, self.narration = page, narration
        self.mouse = [W / 2, H / 2]

    def still(self, quiet_ms: int = 300, limit_ms: int = 4000):
        """Wait until the page has stopped scrolling (CSS smooth scroll from an anchor click, or ours).
        If a click just started a navigation, wait for the new page instead."""
        for _ in range(3):
            try:
                self.page.wait_for_load_state("load", timeout=30000)
                self._still(quiet_ms, limit_ms)
                return
            except Exception as e:  # noqa: BLE001  execution context destroyed by a navigation: try again
                if "Execution context was destroyed" not in str(e) and "navigat" not in str(e):
                    raise
                self.page.wait_for_timeout(500)

    def _still(self, quiet_ms: int, limit_ms: int):
        self.page.evaluate("""([quiet, limit]) => new Promise(done => {
            let last = window.scrollY, same = 0; const t0 = performance.now();
            const tick = () => { const y = window.scrollY; same = (y === last) ? same + 50 : 0; last = y;
              if (same >= quiet || performance.now() - t0 > limit) done(); else setTimeout(tick, 50); };
            setTimeout(tick, 50); })""", [quiet_ms, limit_ms])

    missing: list = []

    def move_to(self, selector: str, dx: float = 0.5, dy: float = 0.5, steps: int = 28):
        self.still()
        if self.page.locator(selector).count() == 0:
            Camera.missing.append(selector)  # the audit fails on any missed shot
            print(f"   missing shot target: {selector}", flush=True)
            return
        box = self.page.locator(selector).first.bounding_box()
        if box and (box["y"] < BAR or box["y"] + box["height"] > H):  # off screen: ease it into view first
            self.page.evaluate(EASE_SCROLL, [max(0, self.page.evaluate("() => window.scrollY") + box["y"] - H / 2), 26])
            self.still()
            box = self.page.locator(selector).first.bounding_box()
        if not box:
            return
        x, y = box["x"] + box["width"] * dx, box["y"] + box["height"] * dy
        self.page.mouse.move(x, y, steps=steps)
        self.mouse = [x, y]

    def click(self, selector: str, read: float = 0.6):
        self.move_to(selector)
        self.page.wait_for_timeout(int(read * 1000))
        # one real press where the cursor is: the click the viewer sees is the click that happens
        self.page.mouse.down()
        self.page.wait_for_timeout(90)
        self.page.mouse.up()
        self.page.wait_for_timeout(150)
        self.still()

    def scroll_to(self, selector: str, offset: int = BAR + 76, frames: int = 26):
        # resolved through Playwright's locator API: document.querySelector does not understand :has-text()
        self.still()
        loc = self.page.locator(selector)
        if loc.count() == 0:
            Camera.missing.append(selector)
            print(f"   missing scroll target: {selector}", flush=True)
            return
        box = loc.first.bounding_box()
        if box is None:
            return
        top = box["y"] + self.page.evaluate("() => window.scrollY")
        self.page.evaluate(EASE_SCROLL, [max(0, top - offset), frames])
        self.still()

    def settle(self, selector: str = "body", timeout: int = 15000):
        self.page.wait_for_load_state("load", timeout=timeout)
        self.page.locator(selector).first.wait_for(state="visible", timeout=timeout)


def shot(name: str):
    """Each shot is a generator: before `yield` composes silently, after it runs while the line is spoken."""
    def hero(cam, on):
        cam.page.goto(SITE, wait_until="load")
        cam.settle("#stats .stat")
        cam.page.wait_for_timeout(700)
        yield
        cam.move_to("h1", 0.35, 0.5)

    def realprs(cam, on):
        yield
        cam.click('nav a[href="#realprs"]')
        cam.page.wait_for_timeout(900)
        cam.scroll_to("#realprs-table", offset=BAR + 150)
        on(1)
        cam.move_to("#realprs-table tbody tr:has-text('hap-java') td:nth-child(5)")
        on(3)
        cam.scroll_to("#realprs", offset=BAR + 60)
        cam.move_to("#realprs-stats .stat:first-child .v")

    def hero_stats(cam, on):
        yield
        cam.page.evaluate(EASE_SCROLL, [0, 30])
        cam.move_to(".lede", 0.3, 0.5)
        on(1)
        cam.move_to("#stats .stat:first-child .v")

    def live_pr(cam, on):
        yield
        cam.click('a#live-pr')
        cam.settle(".js-discussion, .timeline-comment", 30000)
        cam.page.wait_for_timeout(800)
        cam.move_to("[data-component='StateLabel']", 0.5, 0.5)  # the red CI cross on Dependabot's commit comes next
        on(1)
        cam.scroll_to(".js-timeline-item:has-text('Bump org.bouncycastle')", offset=BAR + 220, frames=40)
        cam.move_to(".js-timeline-item:has-text('Bump org.bouncycastle') a:has-text('Bump org')", 0.9, 0.5)
        on(2)
        cam.scroll_to(".js-timeline-item:has-text('Adapt to')", offset=BAR + 160, frames=40)
        cam.move_to(".js-timeline-item:has-text('Adapt to') a:has-text('Adapt to')", 0.3, 0.5)
        cam.scroll_to(".timeline-comment:has-text('REPAIRED') h2", offset=BAR + 120, frames=40)
        cam.move_to(".timeline-comment:has-text('REPAIRED') :text('After repair')", 0.3, 0.5)

    def back_to_site(cam):
        if not cam.page.url.startswith(SITE):
            cam.scroll_to(".timeline-comment:has-text('REPAIRED') a[href^='https://usv240.github.io/uptake']", offset=BAR + 300)
            cam.click(".timeline-comment:has-text('REPAIRED') a[href^='https://usv240.github.io/uptake']")
            cam.settle("#stats .stat")

    def how(cam, on):
        back_to_site(cam)
        yield
        cam.click('nav a[href="#how"]')
        cam.page.wait_for_timeout(900)
        on(1)
        cam.scroll_to(".lock", offset=BAR + 120)
        cam.move_to("pre.code .s", 0.4, 0.5)

    def ide(cam, on):
        yield  # the IDE recording is spliced over this beat by assemble.py
        if not cam.page.url.startswith(SITE):
            cam.page.goto(SITE, wait_until="load")  # hidden under the IDE footage

    def oripa(cam, on):
        yield
        cam.click('nav a[href="#explore"]')
        cam.page.wait_for_timeout(900)
        cam.click("#picker button[data-name='oripa']")
        cam.page.wait_for_timeout(700)
        on(1)
        cam.scroll_to("#case .case-head", offset=BAR + 70)
        cam.move_to("#case .case-head .meta", 0.3, 0.5)
        on(2)
        cam.scroll_to("#case .pane:nth-child(2) h4:nth-of-type(2)", offset=BAR + 90)
        cam.move_to("#case .pane:nth-child(2) h4:nth-of-type(2) .verdict")

    def results(cam, on):
        yield
        cam.click('nav a[href="#results"]')
        cam.page.wait_for_timeout(900)
        cam.scroll_to("#results-table", offset=BAR + 90)
        on(1)
        cam.move_to("#results-table tbody tr:has-text('quickperf') td:nth-child(5)")
        on(2)
        cam.move_to("#results-table tbody tr:has-text('liquibase') td:nth-child(5)")

    def compare(cam, on):
        yield
        cam.click('nav a[href="#compare"]')
        cam.page.wait_for_timeout(900)
        cam.scroll_to("#compare-table", offset=BAR + 90)
        cam.move_to("#compare-table tbody tr:has-text('oripa') td:nth-child(4)")
        on(1)
        cam.move_to("#compare-table tbody tr:has-text('oripa') .cmp-detail")

    def pdb(cam, on):
        yield
        cam.click('nav a[href="#realprs"]')
        cam.page.wait_for_timeout(900)
        cam.scroll_to("#humanfix", offset=BAR + 200)
        cam.move_to("#humanfix .fact:has-text('pdb') .big")
        on(1)
        cam.click('nav a[href="#explore"]')
        cam.page.wait_for_timeout(900)
        cam.click("#picker button[data-name='pdb']")
        cam.page.wait_for_timeout(600)
        cam.scroll_to("#case .receipt", offset=BAR + 160)
        cam.move_to("#case .verify code")

    def close(cam, on):
        yield
        if LIVE.get("url"):
            cam.page.evaluate(EASE_SCROLL, [0, 30])
            cam.click("a#live-pr")
            cam.settle(".timeline-comment", 30000)
            cam.scroll_to(".js-timeline-item:has-text('Adapt to')", offset=BAR + 200, frames=40)
            cam.move_to(".js-timeline-item:has-text('Adapt to') a:has-text('Adapt to')", 0.3, 0.5)
        else:
            cam.page.evaluate(EASE_SCROLL, [0, 30])
            cam.move_to("#stats .stat:first-child .v")

    def hold(cam, on):
        yield

    return locals()[name]


def main() -> int:
    beats = json.loads((BUILD / "beats.json").read_text(encoding="utf-8"))
    narration = {n["id"]: n for n in json.loads((BUILD / "narration.json").read_text(encoding="utf-8"))}
    raw = BUILD / "rawvideo"
    shutil.rmtree(raw, ignore_errors=True)
    log = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        ctx = browser.new_context(viewport={"width": W, "height": H}, device_scale_factor=2, color_scheme="dark",
                                  bypass_csp=True, record_video_dir=str(raw), record_video_size={"width": W, "height": H})
        ctx.add_init_script(OVERLAY)
        page = ctx.new_page()
        t0 = time.monotonic()
        cam = Camera(page, narration)
        for b in beats:
            page.wait_for_timeout(int(b["pause"] * 1000))
            clip = narration[b["id"]]["seconds"]
            state = {}

            def on_sentence(n, state=state):
                starts = state.get("starts", [])
                if n < len(starts):
                    wait = state["start"] + starts[n] - time.monotonic()
                    if wait > 0:
                        page.wait_for_timeout(int(wait * 1000))

            gen = shot(b["shot"])(cam, on_sentence)
            compose_at = time.monotonic() - t0
            next(gen)  # compose the shot in silence
            state["start"] = time.monotonic()
            state["starts"] = sentence_starts(b["say"], clip)
            try:
                next(gen)  # act while the line is spoken
            except StopIteration:
                pass
            left = state["start"] + clip + 1.4 - time.monotonic()
            if left > 0:
                page.wait_for_timeout(int(left * 1000))
            entry = {"id": b["id"], "shot": b["shot"], "compose": round(compose_at, 3),
                     "start": round(state["start"] - t0, 3), "clip": clip, "end": round(time.monotonic() - t0, 3)}
            log.append(entry)
            print(f"{b['id']:10} start {entry['start']:6.1f}s  line {clip:4.1f}s  took {entry['end'] - entry['start']:5.1f}s",
                  flush=True)
        page.wait_for_timeout(800)
        video = page.video.path()
        ctx.close()
        browser.close()
    shutil.move(video, BUILD / "raw.webm")
    (BUILD / "beatlog.json").write_text(json.dumps(log, indent=1), encoding="utf-8")
    (BUILD / "missing_targets.json").write_text(json.dumps(Camera.missing), encoding="utf-8")
    worst = max(log, key=lambda x: (x["end"] - x["start"]) - x["clip"])
    print(f"largest stall: {worst['id']} ran {worst['end'] - worst['start'] - worst['clip']:.1f}s past its line")
    return 0


if __name__ == "__main__":
    sys.exit(main())

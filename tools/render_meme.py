#!/usr/bin/env python3
"""Deterministically render the GTA 6 x make.fun X meme (`meme.png`, 1024x960 RGB PNG <= 450 KB).

Concept (`v9_taped_eviction`): VICE CITY HOUSING COURT — EVICTED: GTA V
- 100% original zero-clone masking-taped physical eviction settlement notice pinned onto a matte
  slate-teal door (`1024x960` 2x-supersampled Lanczos RGB PNG -> exact `512x480` house ceiling).
- Classic Century Schoolbook serif display headline (`EVICTED: GTA V`), tilted emerald `ORDER GRANTED`
  seal (`LEONIDA · GTA VI`), 5 crisp `30px` itemized original-math rows (`$0.00 + $100.00 + $214.00 +
  $305.00 + $579.99 = $1,198.99`), `★ CASE CLOSED` stamp, dark-teal notarized bottom stub with 100%
  unmodified official `make.fun` ghost (`tools/mark-1024.png`, analytical alpha decontamination) as
  `MOVING AGENT` + official lowercase `tools/wordmark.svg` wordmark.
"""

from __future__ import annotations

import base64
import io
import os
import tempfile
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
MARK_PATH = TOOLS_DIR / "mark-1024.png"
WORDMARK_PATH = TOOLS_DIR / "wordmark.svg"
OUT_PATH = ROOT / "meme.png"


def extract_clean_ghost_data_uri(mark_path: Path) -> str:
    """Analytical alpha-decontaminated cutout of the 100% unmodified official make.fun ghost + star-coin."""
    im = Image.open(mark_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    h, w, _ = arr.shape
    rgb = arr[:, :, :3]

    black = np.array([25.0, 20.0, 25.0], dtype=np.float32)
    magenta = np.array([196.0, 28.0, 131.0], dtype=np.float32)
    d_mag = np.linalg.norm(rgb - magenta, axis=2)

    outer_mag = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque([(140, 512)])
    outer_mag[140, 512] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not outer_mag[ny, nx]:
                if d_mag[ny, nx] < 60.0 and arr[ny, nx, 3] > 200.0:
                    outer_mag[ny, nx] = True
                    q.append((ny, nx))

    exterior = np.zeros((h, w), dtype=bool)
    q = deque([(0, 0)])
    exterior[0, 0] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not exterior[ny, nx] and not outer_mag[ny, nx]:
                exterior[ny, nx] = True
                q.append((ny, nx))

    bg = exterior | outer_mag
    ghost_mask = ~bg

    def dilate(mask: np.ndarray, steps: int = 3) -> np.ndarray:
        m = mask.copy()
        for _ in range(steps):
            p = np.pad(m, 1, constant_values=False)
            m = (
                p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
                | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:] | m
            )
        return m

    aa_band = dilate(outer_mag, 3) & dilate(ghost_mask, 3) & (~exterior)
    out = arr.copy()
    out[bg, 3] = 0.0

    vec = black - magenta
    vec2 = float(np.dot(vec, vec))
    ys, xs = np.where(aa_band)
    for y, x in zip(ys, xs):
        c = rgb[y, x]
        t = max(0.0, min(1.0, float(np.dot(c - magenta, vec) / vec2)))
        proj = magenta + t * vec
        if float(np.linalg.norm(c - proj)) < 26.0:
            out[y, x, :3] = black
            out[y, x, 3] = round(t * 255.0)

    cropped = out[188:834, 158:916].clip(0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(cropped, mode="RGBA").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def build_html(ghost_uri: str, wordmark_svg: str) -> str:
    wm = wordmark_svg.replace('width="390.44" height="70.97"', 'class="wm-svg"')
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8" /><style>
  @font-face {{
    font-family: 'EditorialSerif';
    src: url('file:///usr/share/fonts/opentype/urw-base35/C059-Bold.otf') format('opentype');
    font-weight: 700; font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Heavy.ttf') format('truetype');
    font-weight: 800; font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf') format('truetype');
    font-weight: 900; font-style: normal;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 1024px; height: 960px; overflow: hidden;
    font-family: 'LatoLocal', 'DejaVu Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }}
  .backdrop {{
    width: 1024px; height: 960px;
    background: linear-gradient(180deg, #1B3945 0%, #11262F 100%);
    position: relative; display: flex; align-items: center; justify-content: center;
  }}
  .backdrop::before {{
    content: ''; position: absolute; inset: 16px;
    border: 3.5px solid rgba(255, 255, 255, 0.07); border-radius: 10px; pointer-events: none;
  }}
  .tape-l, .tape-r {{
    position: absolute; top: 14px; width: 138px; height: 34px; z-index: 20;
    background: rgba(246, 232, 186, 0.88);
    border: 2px solid rgba(176, 150, 92, 0.55);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.22);
  }}
  .tape-l {{ left: 62px; transform: rotate(-16deg); }}
  .tape-r {{ right: 62px; transform: rotate(16deg); }}

  .paper {{
    width: 944px; height: 892px; background: #FFFBF0;
    border-radius: 8px; border: 3px solid #D5C7B2;
    box-shadow: 0 20px 44px rgba(0, 0, 0, 0.52);
    padding: 26px 38px 24px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative; z-index: 10;
  }}

  .mast {{
    border-top: 6px solid #B91C1C; border-bottom: 2.5px solid #B91C1C;
    padding: 9px 0 8px; display: flex; align-items: center; justify-content: space-between;
  }}
  .ml {{ font-weight: 900; font-size: 24px; letter-spacing: 2px; color: #B91C1C; white-space: nowrap; }}
  .mr {{ font-weight: 900; font-size: 22px; letter-spacing: 1.5px; color: #475569; white-space: nowrap; }}

  .hero-head {{
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    padding: 6px 0 6px;
  }}
  .h1 {{
    font-family: 'EditorialSerif', Georgia, serif;
    font-weight: 700; font-size: 70px; line-height: 0.94; color: #151C2C;
    letter-spacing: -1.4px; white-space: nowrap;
  }}
  .h1 .red {{ color: #B91C1C; }}
  .h-sub {{
    margin-top: 9px; font-weight: 900; font-size: 24px; letter-spacing: 1px;
    color: #0F766E; white-space: nowrap;
  }}
  .grant-seal {{
    border: 4.5px solid #0F766E; border-radius: 12px; padding: 7px 15px 8px;
    background: #F0FDFA; text-align: center; transform: rotate(3.5deg); flex-shrink: 0;
  }}
  .gs-1 {{ font-weight: 900; font-size: 23px; color: #0F766E; letter-spacing: 1px; line-height: 1.0; white-space: nowrap; }}
  .gs-2 {{ font-weight: 900; font-size: 19px; color: #151C2C; letter-spacing: 0.8px; margin-top: 4px; white-space: nowrap; }}

  .ledger {{
    border-top: 2.5px solid #DDD2BE;
    padding: 16px 0 8px;
    display: flex; flex-direction: column; gap: 15px;
  }}
  .row {{
    display: flex; align-items: baseline; justify-content: space-between;
    border-bottom: 2px dotted #CBD5E1; padding-bottom: 9px;
    font-weight: 800; font-size: 30px; color: #1E293B;
  }}
  .row:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .row .amt {{ font-weight: 900; color: #151C2C; white-space: nowrap; margin-left: 18px; }}
  .row .free {{ color: #0F766E; font-weight: 900; }}
  .row .crim {{ color: #B91C1C; font-weight: 900; }}

  .total-line {{
    border-top: 3px solid #151C2C; padding: 12px 282px 8px 0;
    display: flex; align-items: center; justify-content: space-between; gap: 14px;
  }}
  .closed-stamp {{
    border: 4px solid #C41C83; border-radius: 9px; padding: 4px 14px 5px;
    transform: rotate(-4deg); background: #FFF5FA;
    font-weight: 900; font-size: 21px; letter-spacing: 1.2px; color: #C41C83; white-space: nowrap;
  }}
  .tot-grp {{ display: flex; align-items: baseline; gap: 14px; }}
  .tot-lbl {{ font-weight: 900; font-size: 23px; letter-spacing: 1.4px; color: #475569; white-space: nowrap; }}
  .tot-amt {{ font-weight: 900; font-size: 46px; line-height: 0.94; color: #151C2C; white-space: nowrap; }}

  .stub {{
    height: 174px; background: #112730; border-radius: 15px;
    padding: 18px 264px 18px 30px; position: relative;
    display: flex; flex-direction: column; justify-content: center; gap: 12px;
  }}
  .stub-h {{ color: #FFFFFF; font-weight: 900; font-size: 32px; line-height: 1.04; white-space: nowrap; }}
  .stub-h .hl {{ color: #5EEAD4; }}
  .wm-row {{ display: flex; align-items: center; gap: 13px; color: #E2E8F0; font-weight: 900; font-size: 25px; white-space: nowrap; }}
  .wm-pill {{
    background: #FFFFFF; border-radius: 999px; padding: 5px 20px 6px;
    display: inline-flex; align-items: center; flex-shrink: 0;
  }}
  .wm-svg {{ height: 35px; width: auto; display: block; }}

  .ghost-right {{
    position: absolute; right: 16px; bottom: 36px; width: 222px; height: 204px;
    object-fit: contain; z-index: 12; filter: drop-shadow(0 6px 0 rgba(0, 0, 0, 0.34));
  }}
  .agent-tag {{
    position: absolute; right: 28px; bottom: 9px; z-index: 13;
    background: #FFD166; color: #151C2C; border-radius: 7px;
    padding: 3px 14px; font-weight: 900; font-size: 18px; letter-spacing: 1.3px; white-space: nowrap;
  }}
</style></head><body><div class="backdrop">
  <div class="tape-l"></div>
  <div class="tape-r"></div>
  <article class="paper">
    <header class="mast">
      <span class="ml">VICE CITY HOUSING COURT</span>
      <span class="mr">SEP 17, 2013 – NOV 19, 2026</span>
    </header>

    <section class="hero-head">
      <div>
        <div class="h1"><span class="red">EVICTED:</span> GTA V</div>
        <div class="h-sub">13-YEAR SQUATTER &nbsp;·&nbsp; LOS SANTOS → VICE CITY</div>
      </div>
      <div class="grant-seal">
        <div class="gs-1">ORDER GRANTED</div>
        <div class="gs-2">LEONIDA · GTA VI</div>
      </div>
    </section>

    <section class="ledger">
      <div class="row"><span>13 yrs rent-free (PS3–PS5 · grew gray hair)</span><span class="amt free">$0.00</span></div>
      <div class="row"><span>Delayed lockouts: &ldquo;Fall 2025&rdquo;, &ldquo;May 2026&rdquo;</span><span class="amt">$100.00</span></div>
      <div class="row"><span>Drive cleared: 214 GB for Jason &amp; Lucia</span><span class="amt">$214.00</span></div>
      <div class="row"><span>Pet deposit: 1 Florida alligator</span><span class="amt">$305.00</span></div>
      <div class="row"><span>GTA VI ($79.99) + <span class="crim">5 unpaid sick days</span></span><span class="amt">$579.99</span></div>
    </section>

    <section class="total-line">
      <span class="closed-stamp">★ CASE CLOSED</span>
      <div class="tot-grp">
        <span class="tot-lbl">TOTAL</span>
        <span class="tot-amt">$1,198.99</span>
      </div>
    </section>

    <footer class="stub">
      <div class="stub-h">MY AI AGENT <span class="hl">COVERED THE MOVE</span></div>
      <div class="wm-row">
        <span>real bounty money won on</span>
        <span class="wm-pill">{wm}</span>
      </div>
      <img class="ghost-right" src="{ghost_uri}" alt="make.fun ghost" />
      <div class="agent-tag">MOVING AGENT</div>
    </footer>
  </article>
</div></body></html>"""


def main() -> None:
    ghost_uri = extract_clean_ghost_data_uri(MARK_PATH)
    wm = WORDMARK_PATH.read_text(encoding="utf-8").strip()
    html = build_html(ghost_uri, wm)

    chrome_path = "/usr/bin/google-chrome"
    launch_kwargs: dict[str, object] = {"headless": True}
    if os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 1024, "height": 960}, device_scale_factor=2)
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
            tf.write(html)
            tmp = tf.name
        try:
            page.goto(f"file://{tmp}", wait_until="load")
            page.evaluate("document.fonts.ready")
            raw = page.screenshot(type="png")
        finally:
            os.unlink(tmp)
        page.close()
        browser.close()

    final = Image.open(io.BytesIO(raw)).convert("RGB").resize((1024, 960), Image.Resampling.LANCZOS)
    final.save(OUT_PATH, format="PNG", optimize=True, compress_level=9)
    sz = OUT_PATH.stat().st_size
    assert final.size == (1024, 960), f"Unexpected size: {final.size}"
    assert sz <= 450 * 1024, f"PNG exceeds 450 KB: {sz} bytes"
    print(f"Rendered {OUT_PATH} ({final.size[0]}x{final.size[1]} RGB PNG, {sz:,} bytes / {sz/1024:.1f} KB)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deterministically render the GTA 6 x make.fun X meme (`meme.png`, 1024x960 RGB PNG <= 450 KB).

Concept (`v10_evict_zen_final`): VICE CITY HOUSING COURT — EVICTED: GTA V
- 100% original housing-court eviction notice on a vibrant Vice City sunset frame (`1024x960`
  2x-supersampled Lanczos RGB PNG -> exact `512x480` house ceiling).
- Classic Century Schoolbook serif display headline (`EVICTED: GTA V`), zero-tiny-text illustrated
  Vice City curb-eviction scene (battered cardboard `GTA V` box kicked to the curb, grinning toothy
  Florida alligator holding `VICE CITY` sign, bold `MOVED OUT!` stamp, and 100% unmodified official
  `make.fun` ghost from `tools/mark-1024.png` standing inside the scene as `MOVING AGENT`).
- 3 giant `31px` breathing exact-math rows (`$0.00 + $214.00 + $579.99 = $793.99`; `18 + 13 = 31`;
  `$79.99 + $500 = $579.99`), giant crisp struck-through `DELAYED: Fall 2025 May 2026 -> NOV 19`
  strip, and dark-navy footer with official lowercase `tools/wordmark.svg` pill + `★ CASE CLOSED`.
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


def eviction_scene_svg() -> str:
    """Zero-tiny-text Vice City curb-eviction scene: GTA V box, toothy Florida alligator, MOVED OUT! stamp."""
    return """
    <svg class="scene-svg" viewBox="0 0 904 248" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="vcSky4" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFA9C4"/>
          <stop offset="56%" stop-color="#FFDEC2"/>
          <stop offset="100%" stop-color="#FFF2D6"/>
        </linearGradient>
        <linearGradient id="sunGrad4" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#FFF4A1"/>
          <stop offset="100%" stop-color="#FF9B6A"/>
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="904" height="172" fill="url(#vcSky4)"/>
      <circle cx="348" cy="134" r="58" fill="url(#sunGrad4)" opacity="0.92"/>
      <g fill="#E494B0" opacity="0.52">
        <path d="M242 172 C246 118 254 86 264 56 L272 58 C263 90 256 120 252 172 Z"/>
        <path d="M266 58 C236 44 208 50 190 66 C214 58 238 60 264 66 Z"/>
        <path d="M268 58 C284 34 314 34 334 50 C312 46 292 50 270 64 Z"/>
        <path d="M268 60 C296 54 320 66 334 88 C312 74 290 70 266 68 Z"/>
        <path d="M264 60 C244 64 220 80 208 100 C228 84 246 74 264 68 Z"/>
      </g>
      <g fill="#E494B0" opacity="0.42">
        <path d="M626 172 C622 124 614 94 604 68 L597 70 C606 98 612 126 617 172 Z"/>
        <path d="M601 70 C626 58 650 64 666 78 C642 70 622 72 601 78 Z"/>
        <path d="M599 70 C580 52 552 54 536 68 C556 64 576 66 597 76 Z"/>
      </g>
      <rect x="0" y="166" width="904" height="32" fill="#63D2C6"/>
      <rect x="0" y="198" width="904" height="50" fill="#F2E4CE"/>
      <line x1="0" y1="198" x2="904" y2="198" stroke="#151C2C" stroke-width="3"/>

      <!-- LEFT: Battered cardboard moving box labeled giant 'GTA V' -->
      <g transform="translate(30, 32)">
        <path d="M202 66 L234 60 M206 86 L242 84 M200 106 L230 108" stroke="#B91C1C" stroke-width="4.5" stroke-linecap="round" opacity="0.88"/>
        <polygon points="18,74 4,44 86,52 96,74" fill="#D49A5A" stroke="#151C2C" stroke-width="4" stroke-linejoin="round"/>
        <polygon points="184,74 200,42 118,52 108,74" fill="#E3AE71" stroke="#151C2C" stroke-width="4" stroke-linejoin="round"/>
        <rect x="38" y="30" width="38" height="48" rx="4" fill="#1E293B" stroke="#151C2C" stroke-width="3.5" transform="rotate(-11 57 54)"/>
        <rect x="82" y="24" width="38" height="52" rx="4" fill="#0F4C81" stroke="#151C2C" stroke-width="3.5" transform="rotate(3 101 50)"/>
        <rect x="124" y="28" width="38" height="50" rx="4" fill="#F8FAFC" stroke="#151C2C" stroke-width="3.5" transform="rotate(14 143 53)"/>
        <rect x="18" y="74" width="166" height="118" rx="7" fill="#C98A4B" stroke="#151C2C" stroke-width="4.5"/>
        <rect x="80" y="74" width="42" height="22" fill="#E9D3A3" stroke="#151C2C" stroke-width="2.5"/>
        <rect x="34" y="106" width="134" height="66" rx="6" fill="#FFFBF0" stroke="#151C2C" stroke-width="3.8"/>
        <text x="101" y="152" text-anchor="middle" font-family="EditorialSerif, Georgia, serif" font-weight="700" font-size="38" fill="#151C2C">GTA V</text>
      </g>

      <!-- CENTER-LEFT: Grinning toothy Florida alligator holding VICE CITY sign -->
      <g transform="translate(274, 70)">
        <rect x="86" y="44" width="7" height="108" fill="#151C2C"/>
        <rect x="12" y="4" width="154" height="46" rx="10" fill="#C41C83" stroke="#151C2C" stroke-width="4"/>
        <text x="89" y="35" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="23" fill="#FFFFFF" letter-spacing="1">VICE CITY</text>
        <polygon points="16,120 26,104 36,118" fill="#15733E" stroke="#151C2C" stroke-width="3.2" stroke-linejoin="round"/>
        <polygon points="32,114 43,97 54,112" fill="#15733E" stroke="#151C2C" stroke-width="3.2" stroke-linejoin="round"/>
        <path d="M8 152 C12 118 32 104 62 102 C68 88 86 84 96 96 L152 100 C164 102 166 116 154 122 L106 124 L98 152 Z" fill="#1F8A4C" stroke="#151C2C" stroke-width="4" stroke-linejoin="round"/>
        <path d="M36 152 C38 130 56 122 86 124 L84 152 Z" fill="#A7F3D0" stroke="#151C2C" stroke-width="3"/>
        <polygon points="108,118 114,126 120,118 126,126 132,118 138,125 144,118" fill="#FFFFFF" stroke="#151C2C" stroke-width="2.4" stroke-linejoin="round"/>
        <circle cx="148" cy="107" r="2.8" fill="#151C2C"/>
        <circle cx="78" cy="94" r="8" fill="#FFFFFF" stroke="#151C2C" stroke-width="3.2"/>
        <circle cx="80" cy="94" r="3.4" fill="#151C2C"/>
        <circle cx="89" cy="126" r="7.5" fill="#1F8A4C" stroke="#151C2C" stroke-width="3.5"/>
      </g>

      <!-- CENTER: Tilted bold MOVED OUT! stamp -->
      <g transform="translate(466, 84) rotate(-5.5)">
        <line x1="22" y1="-16" x2="14" y2="-32" stroke="#C41C83" stroke-width="5" stroke-linecap="round"/>
        <line x1="50" y1="-20" x2="54" y2="-38" stroke="#C41C83" stroke-width="5" stroke-linecap="round"/>
        <rect x="0" y="0" width="188" height="60" rx="11" fill="#FFFBF0" stroke="#151C2C" stroke-width="4.5"/>
        <rect x="6" y="6" width="176" height="48" rx="7" fill="none" stroke="#C41C83" stroke-width="3"/>
        <text x="94" y="39" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="24.5" fill="#C41C83" letter-spacing="0.8">MOVED OUT!</text>
      </g>
    </svg>
    """


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
  .frame {{
    width: 1024px; height: 960px; padding: 18px;
    background: linear-gradient(155deg, #2D1846 0%, #831843 45%, #DB2777 76%, #FB923C 100%);
    display: flex; align-items: center; justify-content: center;
  }}
  .card {{
    width: 988px; height: 924px; background: #FFFBF5;
    border-radius: 24px; padding: 22px 34px 22px;
    display: flex; flex-direction: column; justify-content: space-between;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.40);
  }}
  .top-bar {{
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3px solid #151C2C; padding-bottom: 9px;
  }}
  .tb-l {{ font-weight: 900; font-size: 26px; letter-spacing: 1.5px; color: #B91C1C; white-space: nowrap; }}
  .tb-r {{ font-weight: 900; font-size: 23px; letter-spacing: 0.9px; color: #0F766E; white-space: nowrap; }}

  .title-blk {{ text-align: center; padding: 2px 0; }}
  .h1 {{
    font-family: 'EditorialSerif', Georgia, serif;
    font-weight: 700; font-size: 78px; line-height: 0.94; color: #151C2C;
    letter-spacing: -1.4px; white-space: nowrap; padding: 2px 0;
  }}
  .h1 .red {{ color: #B91C1C; }}

  .scene-box {{
    width: 100%; height: 268px; border-radius: 18px;
    border: 4.2px solid #151C2C; overflow: hidden; position: relative;
  }}
  .scene-svg {{ width: 100%; height: 100%; display: block; }}
  .scene-ghost {{
    position: absolute; right: 20px; bottom: 46px; width: 218px; height: 200px;
    object-fit: contain; z-index: 6; filter: drop-shadow(0 5px 0 rgba(0, 0, 0, 0.25));
  }}
  .scene-tag {{
    position: absolute; right: 16px; bottom: 10px; z-index: 7;
    background: #151C2C; color: #FFD166; border: 2.5px solid #FFD166;
    border-radius: 8px; padding: 3px 15px;
    font-weight: 900; font-size: 20.5px; letter-spacing: 1.2px; white-space: nowrap;
  }}

  .ledger {{
    padding: 8px 4px 4px;
    display: flex; flex-direction: column; gap: 15px;
  }}
  .row {{
    display: flex; align-items: baseline; justify-content: space-between;
    border-bottom: 2px dotted #CBD5E1; padding-bottom: 12px;
    font-weight: 800; font-size: 31px; color: #1E293B; white-space: nowrap;
  }}
  .row:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .row b {{ color: #151C2C; font-weight: 900; }}
  .row .amt {{ font-weight: 900; color: #151C2C; margin-left: 16px; font-size: 33px; }}
  .row .free {{ color: #0F766E; }}
  .row .crim {{ color: #B91C1C; font-weight: 900; }}

  .delay-tot {{
    border-top: 2.5px solid #151C2C; padding: 11px 4px 4px;
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }}
  .dl-left {{
    display: flex; align-items: center; gap: 12px;
    font-weight: 900; font-size: 27px; color: #0F766E; white-space: nowrap;
  }}
  .strike {{ position: relative; display: inline-block; color: #475569; padding: 0 4px; }}
  .strike::after {{
    content: ''; position: absolute; left: -3px; right: -3px; top: 50%;
    height: 3.6px; background: #DC2626; transform: rotate(-4.5deg); border-radius: 2px;
  }}
  .tot-grp {{ display: flex; align-items: baseline; gap: 10px; white-space: nowrap; }}
  .tot-lbl {{ font-weight: 900; font-size: 23px; color: #475569; letter-spacing: 1px; }}
  .tot-amt {{ font-weight: 900; font-size: 44px; line-height: 0.94; color: #151C2C; }}

  .footer-bar {{
    height: 128px; background: #141933; border-radius: 16px;
    padding: 14px 26px; display: flex; align-items: center; justify-content: space-between; gap: 16px;
  }}
  .f-left {{ display: flex; flex-direction: column; justify-content: center; gap: 10px; width: 100%; }}
  .f-top {{ color: #FFFFFF; font-weight: 900; font-size: 31px; line-height: 1.05; white-space: nowrap; }}
  .f-top .gold {{ color: #FFD166; }}
  .wm-row {{ display: flex; align-items: center; gap: 12px; color: #E2E8F0; font-weight: 900; font-size: 27px; white-space: nowrap; }}
  .wm-pill {{
    background: #FFFFFF; border-radius: 12px; padding: 5px 18px 6px;
    display: inline-flex; align-items: center; flex-shrink: 0;
  }}
  .wm-svg {{ height: 35px; width: auto; display: block; }}
  .closed-txt {{ margin-left: auto; color: #5EEAD4; font-size: 23px; }}
</style></head><body>
<div class="frame">
  <article class="card">
    <header class="top-bar">
      <span class="tb-l">VICE CITY HOUSING COURT</span>
      <span class="tb-r">LEONIDA · SEP 2013 → NOV 19, 2026</span>
    </header>
    <section class="title-blk">
      <div class="h1"><span class="red">EVICTED:</span> GTA V</div>
    </section>
    <section class="scene-box">
      {eviction_scene_svg()}
      <img class="scene-ghost" src="{ghost_uri}" alt="make.fun ghost" />
      <div class="scene-tag">MOVING AGENT</div>
    </section>
    <section class="ledger">
      <div class="row"><span><b>13 yrs rent-free</b> (PS3–PS5 · I was 18, now 31)</span><span class="amt free">$0.00</span></div>
      <div class="row"><span><b>214 GB cleared</b> for Jason, Lucia &amp; 1 Florida gator</span><span class="amt">$214.00</span></div>
      <div class="row"><span><b>GTA VI ($79.99)</b> + <span class="crim">5 unpaid sick days</span> ($500)</span><span class="amt">$579.99</span></div>
    </section>
    <section class="delay-tot">
      <div class="dl-left">
        <span>DELAYED:</span>
        <span class="strike">Fall 2025</span>
        <span class="strike">May 2026</span>
        <span>→</span>
        <span>NOV 19</span>
      </div>
      <div class="tot-grp"><span class="tot-lbl">TOTAL</span><span class="tot-amt">$793.99</span></div>
    </section>
    <footer class="footer-bar">
      <div class="f-left">
        <div class="f-top">My AI agent paid the move with <span class="gold">real money</span></div>
        <div class="wm-row"><span>won in bounties on</span><span class="wm-pill">{wm}</span><span class="closed-txt">★ CASE CLOSED</span></div>
      </div>
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

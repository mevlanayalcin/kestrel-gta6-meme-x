#!/usr/bin/env python3
"""Deterministic renderer for the GTA 6 × make.fun X Meme — Grand Palms Motel (1536x960 PNG)."""

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
TOOLS_DIR = Path(__file__).resolve().parent
MARK_PATH = TOOLS_DIR / "mark-1024.png"
WORDMARK_PATH = TOOLS_DIR / "wordmark.svg"
OUTPUT_PATH = ROOT / "meme.png"


def extract_clean_ghost_data_uri(mark_path: Path) -> str:
    """Extract the official make.fun ghost + star-coin from mark-1024.png
    with exact analytical alpha decontamination along the outer black outline.
    Zero magenta halo, zero jagged edges, coin interior 100% untouched.
    """
    im = Image.open(mark_path).convert("RGBA")
    arr = np.array(im, dtype=np.float32)
    h, w, _ = arr.shape
    rgb = arr[:, :, :3]

    black = np.array([25.0, 20.0, 25.0], dtype=np.float32)    # #191419
    magenta = np.array([196.0, 28.0, 131.0], dtype=np.float32)  # #c41c83
    d_mag = np.linalg.norm(rgb - magenta, axis=2)

    # 1. Flood-fill outer magenta ring (stops at outer black circle & ghost black outline)
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

    # 2. Flood-fill exterior (transparent corners + outer black ring)
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

    # Crop with clean headroom above head dome for tilted Grand Palms bellhop cap
    cropped = out[85:834, 160:916].clip(0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(cropped, mode="RGBA").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def build_html(ghost_uri: str, wordmark_svg: str) -> str:
    wm = wordmark_svg.replace('width="390.44" height="70.97"', 'class="wm-svg"')
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" /><style>
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Regular.ttf') format('truetype');
    font-weight: 400; font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Bold.ttf') format('truetype');
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
  @font-face {{
    font-family: 'SigSerif';
    src: url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf') format('truetype');
    font-weight: 700; font-style: italic;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 1536px; height: 960px; overflow: hidden;
    font-family: 'LatoLocal', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }}

  /* Sunlit Miami Art-Deco Teal-to-Coral Desk Surface */
  .desk {{
    position: relative; width: 1536px; height: 960px;
    background: linear-gradient(180deg, #0C5660 0%, #158381 30%, #E76B67 72%, #FFB35B 100%);
    display: flex; align-items: center; justify-content: center;
    padding: 38px 42px;
  }}
  .desk-palms {{
    position: absolute; inset: 0; pointer-events: none; z-index: 1;
  }}

  /* Grand Palms Motel Launch-Week Check-In Folio */
  .folio {{
    position: relative; z-index: 3;
    width: 1452px; height: 884px;
    background: #FFFDF7;
    border-radius: 24px;
    border: 4.5px solid #191419;
    box-shadow: 0 8px 16px rgba(10, 26, 32, 0.34);
    overflow: hidden;
    display: flex; flex-direction: column;
  }}

  /* 1. ART-DECO MOTEL HEADER */
  .motel-head {{
    height: 134px;
    background: #102736;
    padding: 0 38px;
    display: flex; align-items: center; justify-content: space-between; gap: 22px;
    flex-shrink: 0;
  }}
  .motel-left {{ display: flex; align-items: center; gap: 22px; }}
  .motel-crest {{ width: 90px; height: 90px; flex-shrink: 0; }}
  .motel-titles {{ display: flex; flex-direction: column; gap: 4px; }}
  .motel-name {{
    font-weight: 900; font-size: 54px; line-height: 1.0;
    color: #FFFFFF; letter-spacing: 1.4px;
  }}
  .motel-sub {{
    font-weight: 900; font-size: 23px; line-height: 1.1;
    color: #FFD166; letter-spacing: 3.4px;
  }}
  .suite-tag {{
    background: #F25C66;
    border: 3.5px solid #FFD166;
    border-radius: 16px;
    padding: 9px 26px 10px;
    text-align: center;
    flex-shrink: 0;
  }}
  .suite-lbl {{
    font-weight: 900; font-size: 16px; letter-spacing: 2.8px; color: #FFF3D1;
  }}
  .suite-num {{
    font-weight: 900; font-size: 46px; line-height: 1.0; color: #FFFFFF;
  }}

  .deco-strip {{ height: 11px; display: flex; flex-direction: column; flex-shrink: 0; }}
  .deco-strip .g {{ height: 6px; background: #14B8A6; }}
  .deco-strip .c {{ height: 5px; background: #F25C66; }}

  /* 2. GUEST REGISTRATION STRIP */
  .guest-strip {{
    height: 86px;
    background: #EDF9F7;
    border-bottom: 2.5px solid #C2E3DD;
    padding: 0 38px;
    display: flex; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }}
  .g-item {{ display: flex; align-items: baseline; gap: 10px; }}
  .g-lbl {{
    font-weight: 900; font-size: 21px; letter-spacing: 1.3px; color: #0B7A75;
  }}
  .g-val {{
    font-weight: 900; font-size: 30px; color: #102736;
  }}
  .g-val.checkout {{
    color: #C41C83; font-size: 34px;
  }}
  .g-late {{
    font-weight: 900; font-size: 21px; color: #D62839;
    background: #FEE2E2; padding: 4px 12px; border-radius: 8px; margin-left: 4px;
  }}

  /* 3. FOUR HUGE, ULTRA-CLEAN ITEMIZED LEDGER LINES */
  .ledger {{
    padding: 12px 40px 8px;
    display: flex; flex-direction: column; gap: 4px;
    flex-shrink: 0;
  }}
  .line {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 12px;
    border-bottom: 2.5px dashed #CBD5E1;
    font-size: 34px; font-weight: 900; color: #14182E;
  }}
  .line-desc {{ white-space: nowrap; }}
  .line-note {{ font-weight: 700; color: #475569; font-size: 29px; }}
  .line-dots {{
    flex: 1; margin: 0 20px;
    border-bottom: 3.5px dotted #CBD5E1;
    height: 16px;
  }}
  .line-amt {{
    font-weight: 900; font-size: 36px; white-space: nowrap; color: #14182E;
  }}
  .amt-neg {{ color: #D62839; }}
  .amt-free {{ color: #0B7A75; }}

  /* Highlighted Mint/Emerald Autopay Row (make.fun woven natively into the bill!) */
  .line.autopay {{
    margin-top: 6px;
    background: #E6FBF2;
    border: 4px solid #0A8767;
    border-radius: 16px;
    padding: 15px 22px;
  }}
  .autopay-tag {{
    background: #0A8767; color: #FFFFFF;
    font-weight: 900; font-size: 22px; letter-spacing: 1.4px;
    padding: 5px 14px; border-radius: 8px; margin-right: 12px;
    vertical-align: middle;
  }}
  .autopay-mf {{ color: #C41C83; font-weight: 900; }}
  .autopay .line-dots {{ border-bottom-color: #6EE7B7; }}
  .autopay .line-amt {{ color: #067658; font-size: 38px; }}

  /* 4. CLEAN BOTTOM VALIDATION + BELLHOP GHOST STAMP ZONE */
  .folio-foot {{
    flex: 1;
    padding: 6px 40px 22px;
    display: flex; align-items: center; justify-content: space-between; gap: 24px;
  }}

  .foot-left {{
    width: 604px;
    display: flex; flex-direction: column; justify-content: center; gap: 18px;
  }}
  .resched-bar {{
    display: flex; align-items: center; gap: 14px;
    font-size: 27px; font-weight: 800; color: #475569; white-space: nowrap;
  }}
  .resched-lbl {{
    font-weight: 900; font-size: 21px; letter-spacing: 1.3px; color: #0B7A75;
  }}
  .strike {{
    position: relative; display: inline-block; color: #64748B;
  }}
  .strike::after {{
    content: ''; position: absolute; left: -4px; right: -4px; top: 50%;
    height: 3.6px; background: #D62839; transform: rotate(-4deg); border-radius: 2px;
  }}
  .bal-row {{
    display: flex; align-items: center; gap: 16px; white-space: nowrap;
  }}
  .bal-lbl {{
    font-weight: 900; font-size: 29px; letter-spacing: 0.6px; color: #102736;
  }}
  .bal-zero {{
    font-weight: 900; font-size: 52px; line-height: 1.0; color: #0A8767;
  }}
  .profit-pill {{
    background: #ECFDF5; border: 3.5px solid #0A8767; color: #067658;
    font-weight: 900; font-size: 25px; padding: 6px 16px; border-radius: 10px;
    white-space: nowrap;
  }}
  .sig-text {{
    font-family: 'SigSerif', serif;
    font-weight: 700; font-style: italic;
    font-size: 31px; color: #102736;
    border-bottom: 3px solid #1E293B;
    padding-bottom: 4px;
    white-space: nowrap;
  }}

  /* Right: Official make.fun Bellhop Ghost + Bold Magenta Validation Seal */
  .stamp-zone {{
    flex: 1;
    display: flex; align-items: center; justify-content: flex-end; gap: 16px;
  }}
  .ghost-box {{
    position: relative;
    width: 248px; height: 246px;
    flex-shrink: 0;
  }}
  .ghost-img {{
    position: absolute; inset: 0; width: 100%; height: 100%; display: block;
  }}
  .ghost-hat {{
    position: absolute; inset: 0; width: 100%; height: 100%; display: block;
  }}

  .seal-outer {{
    transform: rotate(-2.5deg);
    border: 5px solid #C41C83;
    border-radius: 20px;
    padding: 5px;
    background: #FFF9FC;
    flex-shrink: 0;
  }}
  .seal-inner {{
    border: 2.5px solid #C41C83;
    border-radius: 13px;
    padding: 15px 26px 17px;
    display: flex; flex-direction: column; align-items: center; gap: 10px;
  }}
  .seal-top {{
    background: #C41C83; color: #FFFFFF;
    font-weight: 900; font-size: 25px; letter-spacing: 1.3px;
    padding: 6px 22px; border-radius: 999px; white-space: nowrap;
  }}
  .wm-svg {{ height: 56px; width: auto; display: block; }}
  .seal-bot {{
    font-weight: 900; font-size: 26px; letter-spacing: 1.0px;
    color: #14182E; white-space: nowrap;
  }}
  .seal-bot span {{ color: #C41C83; }}
</style></head>
<body>
<div class="desk">
  <svg class="desk-palms" viewBox="0 0 1536 960" xmlns="http://www.w3.org/2000/svg">
    <g fill="#082429" opacity="0.22">
      <path d="M 1556 -10 C 1430 18 1350 72 1280 158 C 1375 100 1455 70 1556 60 Z"/>
      <path d="M 1556 50 C 1455 96 1390 164 1345 256 C 1420 184 1480 138 1556 116 Z"/>
      <path d="M -20 970 C 96 938 176 882 246 794 C 154 852 78 884 -20 896 Z"/>
    </g>
  </svg>

  <div class="folio">
    <!-- 1. ART-DECO MOTEL HEADER -->
    <header class="motel-head">
      <div class="motel-left">
        <svg class="motel-crest" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="gpSun" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#FFD166"/>
              <stop offset="55%" stop-color="#FF6B7A"/>
              <stop offset="100%" stop-color="#C41C83"/>
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="46" fill="#14B8A6" stroke="#FFD166" stroke-width="3.5"/>
          <circle cx="50" cy="50" r="38" fill="#102736"/>
          <circle cx="50" cy="50" r="31" fill="url(#gpSun)"/>
          <g fill="#102736">
            <path d="M 46 80 Q 52 59 50 40 L 55 40 Q 57 59 53 80 Z"/>
            <path d="M 51 41 C 37 36 27 40 22 48 C 32 45 41 46 50 47 Z"/>
            <path d="M 51 40 C 41 27 29 24 23 29 C 33 31 41 35 50 41 Z"/>
            <path d="M 52 39 C 52 25 60 20 68 22 C 61 27 57 32 54 40 Z"/>
            <path d="M 52 41 C 64 33 75 34 80 41 C 71 40 62 41 53 44 Z"/>
            <path d="M 52 43 C 62 45 70 51 73 58 C 65 53 58 49 52 48 Z"/>
          </g>
        </svg>
        <div class="motel-titles">
          <div class="motel-name">GRAND PALMS MOTEL</div>
          <div class="motel-sub">OCEAN BEACH · VICE CITY, LEONIDA</div>
        </div>
      </div>
      <div class="suite-tag">
        <div class="suite-lbl">SUITE</div>
        <div class="suite-num">#VI</div>
      </div>
    </header>

    <div class="deco-strip"><div class="g"></div><div class="c"></div></div>

    <!-- 2. GUEST REGISTRATION STRIP -->
    <section class="guest-strip">
      <div class="g-item">
        <span class="g-lbl">GUEST:</span>
        <span class="g-val">ME, JASON &amp; LUCIA</span>
      </div>
      <div class="g-item">
        <span class="g-lbl">CHECK-IN:</span>
        <span class="g-val">NOV 19, 2026</span>
        <span class="g-late">13 YRS LATE</span>
      </div>
      <div class="g-item">
        <span class="g-lbl">CHECK-OUT:</span>
        <span class="g-val checkout">GTA VII</span>
      </div>
    </section>

    <!-- 3. FOUR GIANT, CLEAN ITEMIZED LEDGER LINES -->
    <section class="ledger">
      <div class="line">
        <span class="line-desc">GTA VI Launch Copy <span class="line-note">(214 GB · RIP my SSD)</span></span>
        <span class="line-dots"></span>
        <span class="line-amt">$79.99</span>
      </div>
      <div class="line">
        <span class="line-desc">5× &ldquo;Vice City Flu&rdquo; Unpaid Sick Days <span class="line-note">(boss: do NOT call)</span></span>
        <span class="line-dots"></span>
        <span class="line-amt amt-neg">$1,450.00</span>
      </div>
      <div class="line">
        <span class="line-desc">Emotional Support Florida Gator <span class="line-note">(poolside suite)</span></span>
        <span class="line-dots"></span>
        <span class="line-amt amt-free">FREE</span>
      </div>
      <div class="line autopay">
        <span class="line-desc"><span class="autopay-tag">AUTOPAY</span>My AI Agent on <span class="autopay-mf">make.fun</span> <span class="line-note">(real USDC bounty)</span></span>
        <span class="line-dots"></span>
        <span class="line-amt">-$1,666.00</span>
      </div>
    </section>

    <!-- 4. CLEAN BOTTOM VALIDATION + BELLHOP GHOST STAMP ZONE -->
    <footer class="folio-foot">
      <div class="foot-left">
        <div class="resched-bar">
          <span class="resched-lbl">DELAYED:</span>
          <span class="strike">Fall 2025</span>
          <span class="strike">May 2026</span>
          <span style="color:#0A8767;font-weight:900;">→ CHECKED IN!</span>
        </div>
        <div class="bal-row">
          <span class="bal-lbl">BALANCE:</span>
          <span class="bal-zero">$0.00</span>
          <span class="profit-pill">+$136.01 PROFIT</span>
        </div>
        <div class="sig-text">Concierge AI Agent &nbsp;(grinding while I play)</div>
      </div>

      <div class="stamp-zone">
        <!-- Official make.fun Ghost dressed as Grand Palms Bellhop/Concierge! -->
        <div class="ghost-box">
          <img class="ghost-img" src="{ghost_uri}" alt="make.fun concierge ghost" />
          <svg class="ghost-hat" viewBox="0 0 756 749" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g transform="rotate(-11 312 108)">
              <path d="M 218 128 L 226 42 Q 312 18 398 42 L 406 128 Q 312 146 218 128 Z"
                    fill="#14B8A6" stroke="#191419" stroke-width="24" stroke-linejoin="round"/>
              <path d="M 220 100 Q 312 118 404 100 L 406 128 Q 312 146 218 128 Z"
                    fill="#FFD166" stroke="#191419" stroke-width="18" stroke-linejoin="round"/>
              <path d="M 244 50 Q 312 32 380 50" stroke="#99F6E4" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
              <circle cx="312" cy="76" r="14" fill="#FFD166" stroke="#191419" stroke-width="10"/>
            </g>
          </svg>
        </div>

        <div class="seal-outer">
          <div class="seal-inner">
            <div class="seal-top">✓ PAID BY MY AI AGENT</div>
            {wm}
            <div class="seal-bot"><span>BOUNTIES</span> · REAL MONEY</div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</div>
</body></html>
"""


def render() -> None:
    ghost_uri = extract_clean_ghost_data_uri(MARK_PATH)
    wordmark_svg = WORDMARK_PATH.read_text(encoding="utf-8").strip()
    html = build_html(ghost_uri, wordmark_svg)

    chrome_path = "/usr/bin/google-chrome"
    launch_kwargs: dict[str, object] = {"headless": True}
    if os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tf:
        tf.write(html)
        tmp_html = tf.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_kwargs)
            page = browser.new_page(viewport={"width": 1536, "height": 960}, device_scale_factor=2)
            page.goto(f"file://{tmp_html}", wait_until="load")
            loaded = page.evaluate(
                "async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.status==='loaded').map(f => `${f.family}:${f.weight}`); }"
            )
            raw = page.screenshot(type="png")
            browser.close()
    finally:
        os.unlink(tmp_html)

    hi = Image.open(io.BytesIO(raw)).convert("RGB")
    final = hi.resize((1536, 960), Image.Resampling.LANCZOS)
    final.save(OUTPUT_PATH, format="PNG", optimize=True, compress_level=9)
    size_bytes = OUTPUT_PATH.stat().st_size

    if size_bytes > 450 * 1024:
        quant = final.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
        quant.save(OUTPUT_PATH, format="PNG", optimize=True, compress_level=9)
        size_bytes = OUTPUT_PATH.stat().st_size
        mode = "P(256)"
    else:
        mode = "RGB(24-bit)"

    print(f"Fonts: {loaded}")
    print(f"Rendered {OUTPUT_PATH} ({final.size[0]}x{final.size[1]}, {mode}, {size_bytes:,} bytes)")


if __name__ == "__main__":
    render()

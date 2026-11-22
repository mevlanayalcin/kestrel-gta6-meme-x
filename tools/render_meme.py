#!/usr/bin/env python3
"""Deterministic renderer for the GTA 6 × make.fun X Meme — HR Leave Approval & Temp AI Replacement Badge (1536x960 PNG)."""

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
    """Extract the 100% UNMODIFIED official make.fun ghost + star-coin from mark-1024.png
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

  /* Warm Vice-Sunset Desk Backdrop */
  .desk {{
    position: relative;
    width: 1536px; height: 960px;
    background: linear-gradient(180deg, #161830 0%, #3E1851 38%, #982166 74%, #E86A62 100%);
    overflow: hidden;
  }}

  /* ===== LEFT 63%: CORPORATE HR EMERGENCY LEAVE APPROVAL FORM ===== */
  .hr-form {{
    position: absolute;
    left: 34px; top: 38px;
    width: 966px; height: 884px;
    background: #FFFDF8;
    border-radius: 24px;
    border: 4.5px solid #191419;
    box-shadow: 0 8px 16px rgba(10, 6, 22, 0.40);
    overflow: hidden;
    display: flex; flex-direction: column;
    z-index: 3;
  }}

  .hr-head {{
    height: 124px;
    background: #121830;
    padding: 0 32px;
    display: flex; align-items: center; justify-content: space-between; gap: 18px;
    flex-shrink: 0;
  }}
  .hr-head-left {{ display: flex; align-items: center; gap: 18px; }}
  .hr-crest {{ width: 80px; height: 80px; flex-shrink: 0; }}
  .hr-titles {{ display: flex; flex-direction: column; gap: 4px; }}
  .hr-title {{
    font-weight: 900; font-size: 46px; line-height: 1.0;
    color: #FFFFFF; letter-spacing: 0.9px;
  }}
  .hr-sub {{
    font-weight: 900; font-size: 22px; line-height: 1.1;
    color: #FFD166; letter-spacing: 2.8px;
  }}
  .form-num {{
    border: 2.5px solid #2DD4BF;
    background: rgba(20, 184, 166, 0.14);
    border-radius: 13px;
    padding: 8px 20px 10px;
    text-align: center;
    flex-shrink: 0;
  }}
  .form-num-lbl {{
    font-weight: 900; font-size: 15px; letter-spacing: 2.4px; color: #5EEAD4;
  }}
  .form-num-val {{
    font-weight: 900; font-size: 38px; line-height: 1.0; color: #FFFFFF;
    margin-top: 2px;
  }}

  .deco-strip {{ height: 11px; display: flex; flex-direction: column; flex-shrink: 0; }}
  .deco-strip .t {{ height: 6px; background: #14B8A6; }}
  .deco-strip .c {{ height: 5px; background: #F25C66; }}

  /* HERO REASON + APPROVED STAMP BAND */
  .hero-band {{
    height: 186px;
    background: #F0FAF8;
    border-bottom: 2.5px solid #C6E4DF;
    padding: 20px 32px 18px 36px;
    display: flex; align-items: center; justify-content: space-between; gap: 18px;
    flex-shrink: 0;
  }}
  .hero-left {{ display: flex; flex-direction: column; gap: 10px; }}
  .hero-kicker {{
    font-weight: 900; font-size: 21px; letter-spacing: 2.2px; color: #0B7A75;
  }}
  .hero-title {{
    font-weight: 900; font-size: 48px; line-height: 1.0;
    color: #121830; letter-spacing: -0.4px; white-space: nowrap;
  }}
  .hero-dates {{
    display: flex; align-items: center; gap: 14px;
    font-size: 26px; font-weight: 900; color: #121830; white-space: nowrap;
  }}
  .strike {{
    position: relative; display: inline-block;
    color: #64748B; font-weight: 700;
  }}
  .strike::after {{
    content: ''; position: absolute; left: -4px; right: -4px; top: 50%;
    height: 3.6px; background: #D62839; transform: rotate(-4deg); border-radius: 2px;
  }}
  .final-date {{ color: #0A8767; font-weight: 900; }}

  .stamp-approved {{
    transform: rotate(-7deg);
    border: 5px solid #D62839;
    border-radius: 15px;
    padding: 4px;
    background: rgba(255, 253, 248, 0.96);
    flex-shrink: 0;
  }}
  .stamp-approved-in {{
    border: 2.5px solid #D62839;
    border-radius: 9px;
    padding: 10px 22px 11px;
    text-align: center;
  }}
  .stamp-big {{
    font-weight: 900; font-size: 42px; line-height: 1.0;
    letter-spacing: 2.6px; color: #D62839;
  }}
  .stamp-rule {{
    height: 2.5px; background: #D62839; margin: 6px 0 5px; opacity: 0.78;
  }}
  .stamp-small {{
    font-weight: 900; font-size: 20px; letter-spacing: 1.8px; color: #D62839;
    white-space: nowrap;
  }}

  /* FOUR GIANT SINGLE-LINE HR FIELDS */
  .hr-body {{
    flex: 1;
    padding: 12px 36px 8px;
    display: flex; flex-direction: column; justify-content: space-evenly;
  }}
  .hr-row {{
    display: flex; align-items: baseline; gap: 18px;
    padding: 20px 0;
    border-bottom: 2.5px dashed #CBD5E1;
  }}
  .hr-row:last-child {{ border-bottom: none; }}
  .hr-lbl {{
    width: 196px; flex-shrink: 0;
    font-weight: 900; font-size: 22px; letter-spacing: 1px;
    color: #0B7A75; text-transform: uppercase; white-space: nowrap;
  }}
  .hr-val {{
    flex: 1;
    font-weight: 900; font-size: 31px; line-height: 1.15;
    color: #121830; white-space: nowrap;
  }}
  .hr-val.symp {{ font-size: 29px; }}
  .hr-val.pay {{ font-size: 29px; }}
  .dot {{ color: #0D9488; font-weight: 900; margin: 0 7px; }}
  .red-warn {{ color: #D62839; font-weight: 900; }}
  .hot {{ color: #C41C83; font-weight: 900; }}
  .mint {{ color: #0A8767; font-weight: 900; }}

  /* CLEAN HR SIGNATURE FOOTER */
  .hr-foot {{
    height: 112px;
    background: #F4FAF9;
    border-top: 2.5px solid #C6E4DF;
    padding: 0 36px;
    display: flex; align-items: center; justify-content: space-between; gap: 22px;
    flex-shrink: 0;
  }}
  .sig-lbl {{
    font-weight: 900; font-size: 21px; letter-spacing: 1.4px; color: #0B7A75;
    white-space: nowrap;
  }}
  .hr-sig-line {{
    flex: 1;
    font-family: 'SigSerif', serif;
    font-weight: 700; font-style: italic;
    font-size: 35px; color: #121830;
    border-bottom: 3px solid #1E293B;
    padding-bottom: 4px;
    white-space: nowrap;
  }}

  /* ===== RIGHT 34%: CLIPPED LAMINATED TEMP REPLACEMENT ID BADGE ===== */
  .lanyard-svg {{
    position: absolute;
    left: 1184px; top: 0px;
    width: 164px; height: 122px;
    z-index: 8;
    pointer-events: none;
  }}

  .badge-card {{
    position: absolute;
    left: 1030px; top: 82px;
    width: 472px; height: 840px;
    background: #FFFFFF;
    border-radius: 28px;
    border: 4.5px solid #191419;
    box-shadow: 0 10px 18px rgba(10, 5, 24, 0.45);
    overflow: hidden;
    display: flex; flex-direction: column;
    z-index: 5;
  }}

  .badge-top {{
    position: relative;
    height: 116px;
    background: linear-gradient(180deg, #C41C83 0%, #9E146B 100%);
    border-bottom: 4.5px solid #191419;
    display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
    padding-bottom: 14px;
    flex-shrink: 0;
  }}
  .punch-slot {{
    position: absolute;
    top: 16px; left: 50%; transform: translateX(-50%);
    width: 82px; height: 18px;
    background: #231438;
    border: 3.5px solid #191419;
    border-radius: 999px;
  }}
  .badge-top-title {{
    font-weight: 900; font-size: 36px; line-height: 1.0;
    letter-spacing: 1.2px; color: #FFFFFF;
    text-shadow: 0 2px 0 rgba(25, 20, 25, 0.30);
    white-space: nowrap;
  }}

  /* ID Photo Box with 100% UNMODIFIED Official make.fun Ghost Mascot */
  .photo-frame {{
    position: relative;
    margin: 22px 26px 16px;
    height: 294px;
    background: #F4EDF9;
    border: 4px solid #191419;
    border-radius: 20px;
    overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}
  .height-lines {{
    position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none;
  }}
  .ghost-photo {{
    position: relative; z-index: 2;
    width: 292px; height: 249px;
    object-fit: contain;
    display: block;
  }}

  .badge-fields {{
    flex: 1;
    padding: 4px 26px 24px;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
  }}
  .bf-name {{
    font-weight: 900; font-size: 44px; line-height: 1.0; color: #121830;
    letter-spacing: 0.5px; text-align: center;
  }}

  .bf-agency-box {{
    width: 100%;
    padding: 16px 20px 18px;
    background: #FFF9FC;
    border: 4px solid #191419;
    border-radius: 18px;
    display: flex; flex-direction: column; align-items: center; gap: 10px;
  }}
  .wm-svg {{ height: 52px; width: auto; display: block; }}
  .bf-pitch {{
    font-weight: 900; font-size: 25px; line-height: 1.15;
    color: #C41C83; text-align: center; white-space: nowrap;
  }}
  .bf-pitch-sub {{
    font-weight: 800; font-size: 22px; line-height: 1.1;
    color: #334155; text-align: center; white-space: nowrap;
  }}

  .status-pill {{
    width: 100%;
    background: #ECFDF5;
    border: 4px solid #0A8767;
    color: #067658;
    border-radius: 14px;
    padding: 12px 14px;
    text-align: center;
    font-weight: 900; font-size: 26px; letter-spacing: 0.7px;
    white-space: nowrap;
  }}
</style></head>
<body>
<div class="desk">
  <!-- ===== LEFT: CORPORATE HR EMERGENCY LEAVE APPROVAL FORM ===== -->
  <section class="hr-form">
    <header class="hr-head">
      <div class="hr-head-left">
        <svg class="hr-crest" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="hrSun" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#FFD166"/>
              <stop offset="55%" stop-color="#FF6B7A"/>
              <stop offset="100%" stop-color="#C41C83"/>
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="46" fill="#14B8A6" stroke="#5EEAD4" stroke-width="3"/>
          <circle cx="50" cy="50" r="38" fill="#121830"/>
          <circle cx="50" cy="50" r="31" fill="url(#hrSun)"/>
          <g fill="#121830">
            <path d="M 46 80 Q 52 59 50 40 L 55 40 Q 57 59 53 80 Z"/>
            <path d="M 51 41 C 37 36 27 40 22 48 C 32 45 41 46 50 47 Z"/>
            <path d="M 51 40 C 41 27 29 24 23 29 C 33 31 41 35 50 41 Z"/>
            <path d="M 52 39 C 52 25 60 20 68 22 C 61 27 57 32 54 40 Z"/>
            <path d="M 52 41 C 64 33 75 34 80 41 C 71 40 62 41 53 44 Z"/>
            <path d="M 52 43 C 62 45 70 51 73 58 C 65 53 58 49 52 48 Z"/>
          </g>
        </svg>
        <div class="hr-titles">
          <div class="hr-title">HUMAN RESOURCES</div>
          <div class="hr-sub">EMERGENCY LEAVE APPROVAL</div>
        </div>
      </div>

      <div class="form-num">
        <div class="form-num-lbl">FORM</div>
        <div class="form-num-val">#VI</div>
      </div>
    </header>

    <div class="deco-strip"><div class="t"></div><div class="c"></div></div>

    <!-- HERO REASON & APPROVED STAMP BAND -->
    <div class="hero-band">
      <div class="hero-left">
        <div class="hero-kicker">STATED REASON</div>
        <div class="hero-title">ACUTE VICE CITY FLU</div>
        <div class="hero-dates">
          <span class="strike">Fall 2025</span>
          <span class="strike">May 2026</span>
          <span style="color:#0D9488;">→</span>
          <span class="final-date">NOV 19, 2026</span>
        </div>
      </div>

      <div class="stamp-approved">
        <div class="stamp-approved-in">
          <div class="stamp-big">APPROVED</div>
          <div class="stamp-rule"></div>
          <div class="stamp-small">NO QUESTIONS ASKED</div>
        </div>
      </div>
    </div>

    <!-- FOUR GIANT SINGLE-LINE HR FIELDS -->
    <div class="hr-body">
      <div class="hr-row">
        <div class="hr-lbl">TENURE:</div>
        <div class="hr-val">13 years waiting since Los Santos (2013)</div>
      </div>

      <div class="hr-row">
        <div class="hr-lbl">SYMPTOMS:</div>
        <div class="hr-val symp">214 GB SSD<span class="dot">·</span>Florida gators<span class="dot">·</span>Jason &amp; Lucia</div>
      </div>

      <div class="hr-row">
        <div class="hr-lbl">DURATION:</div>
        <div class="hr-val">5 Unpaid Days <span style="font-weight:700;color:#475569;">(boss:</span> <span class="red-warn">do NOT call</span><span style="font-weight:700;color:#475569;">)</span></div>
      </div>

      <div class="hr-row">
        <div class="hr-lbl">PAYROLL:</div>
        <div class="hr-val pay">Temp AI covers <span class="hot">$79.99</span> + pay (<span class="mint">$1,666 won</span>) →</div>
      </div>
    </div>

    <footer class="hr-foot">
      <span class="sig-lbl">SIGNED:</span>
      <div class="hr-sig-line">H.R. Dept. &nbsp;(also calling in sick)</div>
    </footer>
  </section>

  <!-- ===== METALLIC LANYARD CLIP & MAGENTA RIBBON ===== -->
  <svg class="lanyard-svg" viewBox="0 0 164 122" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M 52 -4 L 62 62 L 102 62 L 112 -4 Z" fill="#C41C83" stroke="#191419" stroke-width="5"/>
    <path d="M 65 -4 L 72 60 M 99 -4 L 92 60" stroke="#F472B6" stroke-width="3" opacity="0.65"/>
    <rect x="54" y="50" width="56" height="32" rx="8" fill="#CBD5E1" stroke="#191419" stroke-width="5"/>
    <rect x="64" y="58" width="36" height="10" rx="4" fill="#F8FAFC"/>
    <path d="M 70 82 L 70 108 Q 82 116 94 108 L 94 82" stroke="#94A3B8" stroke-width="10" stroke-linecap="round"/>
    <path d="M 70 82 L 70 108 Q 82 116 94 108 L 94 82" stroke="#191419" stroke-width="4" stroke-linecap="round" fill="none"/>
  </svg>

  <!-- ===== RIGHT: CLIPPED LAMINATED TEMP REPLACEMENT ID BADGE ===== -->
  <aside class="badge-card">
    <div class="badge-top">
      <div class="punch-slot"></div>
      <div class="badge-top-title">TEMP REPLACEMENT</div>
    </div>

    <div class="photo-frame">
      <svg class="height-lines" viewBox="0 0 416 294" xmlns="http://www.w3.org/2000/svg">
        <g stroke="#DDD0EC" stroke-width="2.5">
          <line x1="0" y1="54" x2="416" y2="54"/>
          <line x1="0" y1="114" x2="416" y2="114"/>
          <line x1="0" y1="174" x2="416" y2="174"/>
          <line x1="0" y1="234" x2="416" y2="234"/>
        </g>
      </svg>
      <img class="ghost-photo" src="{ghost_uri}" alt="make.fun ghost mascot" />
    </div>

    <div class="badge-fields">
      <div class="bf-name">MY AI AGENT</div>

      <div class="bf-agency-box">
        {wm}
        <div class="bf-pitch">wins real money in bounties</div>
        <div class="bf-pitch-sub">while I play GTA VI</div>
      </div>

      <div class="status-pill">✓ BOSS HASN&rsquo;T NOTICED</div>
    </div>
  </aside>
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

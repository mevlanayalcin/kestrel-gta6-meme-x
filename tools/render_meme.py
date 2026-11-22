#!/usr/bin/env python3
"""Deterministically render the GTA 6 x make.fun X meme (`meme.png`, 1024x960 RGB PNG <= 450 KB).

Concept: LEONIDA DEPT. OF CORRECTIONS — OFFICIAL PAROLE RELEASE ORDER
- 1024x960 (16:15) scales cleanly 2x to 512x480 (exact maximum house image resolution).
- Uses the 100% unmodified official make.fun ghost mark (`tools/mark-1024.png`) via analytical
  alpha decontamination and the official lowercase wordmark (`tools/wordmark.svg`).
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
    width: 1024px; height: 960px; overflow: hidden;
    font-family: 'LatoLocal', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }}

  .frame {{
    width: 1024px; height: 960px;
    padding: 24px;
    background: linear-gradient(180deg, #2B124C 0%, #8C1A6F 38%, #DC3272 72%, #FF9650 100%);
    display: flex; align-items: center; justify-content: center;
  }}

  .card {{
    position: relative;
    width: 976px; height: 912px;
    background: #FFFDF7;
    border-radius: 26px;
    border: 4.5px solid #191419;
    box-shadow: 0 12px 24px rgba(14, 6, 28, 0.44);
    overflow: hidden;
    display: flex; flex-direction: column;
  }}

  .head {{
    height: 124px;
    background: #13182E;
    padding: 0 28px;
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    flex-shrink: 0;
  }}
  .head-left {{ display: flex; align-items: center; gap: 18px; }}
  .seal-svg {{ width: 80px; height: 80px; flex-shrink: 0; }}
  .head-titles {{ display: flex; flex-direction: column; gap: 4px; }}
  .dept-name {{
    font-weight: 900; font-size: 37px; line-height: 1.0;
    color: #FFFFFF; letter-spacing: 0.6px; white-space: nowrap;
  }}
  .dept-sub {{
    font-weight: 900; font-size: 22px; line-height: 1.1;
    color: #FFD166; letter-spacing: 3.2px; white-space: nowrap;
  }}
  .inmate-tag {{
    border: 2.5px solid #2DD4BF;
    background: rgba(20, 184, 166, 0.14);
    border-radius: 13px;
    padding: 7px 16px 8px;
    text-align: center; flex-shrink: 0;
  }}
  .inm-lbl {{
    font-weight: 900; font-size: 14px; letter-spacing: 2.2px; color: #5EEAD4;
  }}
  .inm-val {{
    font-weight: 900; font-size: 34px; line-height: 1.02; color: #FFFFFF; white-space: nowrap;
  }}

  .deco-bar {{ height: 10px; display: flex; flex-direction: column; flex-shrink: 0; }}
  .deco-bar .t {{ height: 6px; background: #14B8A6; }}
  .deco-bar .c {{ height: 4px; background: #F25C66; }}

  .hero {{
    height: 174px;
    background: #F1FAF8;
    border-bottom: 2.5px solid #C6E4DF;
    padding: 15px 28px 13px 32px;
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    flex-shrink: 0;
  }}
  .hero-left {{ display: flex; flex-direction: column; gap: 6px; }}
  .hero-kicker {{
    font-weight: 900; font-size: 19px; letter-spacing: 2px; color: #0B7A75;
  }}
  .hero-main {{
    font-weight: 900; font-size: 40px; line-height: 1.04; color: #13182E;
    letter-spacing: -0.4px; white-space: nowrap;
  }}
  .hero-dates {{
    font-weight: 800; font-size: 24px; color: #334155; white-space: nowrap;
  }}
  .hero-dates strong {{ color: #C41C83; font-weight: 900; }}

  .chk-row {{
    display: flex; align-items: center; gap: 22px; margin-top: 3px;
  }}
  .chk-lbl {{
    font-weight: 900; font-size: 19px; letter-spacing: 1.2px; color: #0B7A75;
  }}
  .chk {{
    display: inline-flex; align-items: center; gap: 8px;
    font-weight: 900; font-size: 24px; color: #64748B;
  }}
  .chk.yes {{ color: #13182E; }}
  .box {{
    width: 28px; height: 28px; border: 3.5px solid #64748B; border-radius: 6px;
    background: #FFFFFF; display: inline-flex; align-items: center; justify-content: center;
  }}
  .chk.yes .box {{ border-color: #D62839; background: #FEF2F2; }}

  .stamp {{
    transform: rotate(-8deg);
    border: 5px solid #D62839;
    border-radius: 15px;
    padding: 4px;
    background: rgba(255, 253, 247, 0.96);
    flex-shrink: 0;
  }}
  .stamp-in {{
    border: 2.5px solid #D62839;
    border-radius: 9px;
    padding: 10px 20px 11px;
    text-align: center;
  }}
  .stamp-top {{
    font-weight: 900; font-size: 38px; line-height: 0.98;
    letter-spacing: 2px; color: #D62839; white-space: nowrap;
  }}
  .stamp-rule {{ height: 2.5px; background: #D62839; margin: 6px 0 5px; opacity: 0.78; }}
  .stamp-bot {{
    font-weight: 900; font-size: 22px; letter-spacing: 2px; color: #D62839; white-space: nowrap;
  }}

  .lines {{
    padding: 10px 34px 8px;
    display: flex; flex-direction: column;
    flex-shrink: 0;
  }}
  .row {{
    display: flex; align-items: baseline; gap: 16px;
    padding: 13px 0;
    border-bottom: 2px dashed #CBD5E1;
  }}
  .row:last-child {{ border-bottom: none; padding-bottom: 8px; }}
  .r-lbl {{
    width: 218px; flex-shrink: 0;
    font-weight: 900; font-size: 20px; letter-spacing: 0.8px;
    color: #0B7A75; text-transform: uppercase; white-space: nowrap;
  }}
  .r-val {{
    flex: 1;
    font-weight: 900; font-size: 26px; line-height: 1.18; color: #13182E;
    white-space: nowrap;
  }}
  .r-val .muted {{ font-weight: 700; color: #475569; }}
  .r-val .hot {{ color: #C41C83; font-weight: 900; }}
  .r-val .mint {{ color: #0A8767; font-weight: 900; }}
  .r-val .red {{ color: #D62839; font-weight: 900; }}
  .strike {{
    position: relative; display: inline-block; color: #64748B; font-weight: 700; margin-right: 16px;
  }}
  .strike::after {{
    content: ''; position: absolute; left: -4px; right: -4px; top: 50%;
    height: 3.4px; background: #D62839; transform: rotate(-4deg); border-radius: 2px;
  }}

  .bondsman-section {{
    flex: 1;
    border-top: 3px solid #13182E;
    background: #FAF5F8;
    padding: 16px 32px 18px;
    display: flex; align-items: center; justify-content: space-between; gap: 24px;
  }}

  .surety-photo {{
    width: 224px; height: 196px;
    background: #FFFFFF;
    border: 4px solid #191419;
    border-radius: 18px;
    padding: 10px 10px 6px;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    flex-shrink: 0;
  }}
  .ghost-img {{
    width: 190px; height: 156px; object-fit: contain; display: block;
  }}
  .surety-cap {{
    font-weight: 900; font-size: 14.5px; letter-spacing: 1.8px; color: #C41C83;
    text-transform: uppercase;
  }}

  .surety-right {{
    flex: 1;
    display: flex; flex-direction: column; justify-content: space-between; gap: 12px;
  }}

  .bond-stamp {{
    transform: rotate(-1.2deg);
    background: #FFFFFF;
    border: 4.5px solid #C41C83;
    border-radius: 18px;
    padding: 14px 22px 15px;
    display: flex; flex-direction: column; gap: 9px;
  }}
  .bs-top {{
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
  }}
  .bs-pill {{
    background: #C41C83; color: #FFFFFF;
    font-weight: 900; font-size: 24px; letter-spacing: 0.8px;
    padding: 5px 18px; border-radius: 999px; white-space: nowrap;
  }}
  .bs-won {{
    font-weight: 900; font-size: 25px; color: #0A8767; white-space: nowrap;
  }}
  .bs-brand {{
    display: flex; align-items: center; gap: 14px;
  }}
  .bs-sub {{
    font-weight: 900; font-size: 25px; color: #13182E; white-space: nowrap;
  }}
  .wm-svg {{ height: 42px; width: auto; display: block; }}

  .sig-row {{
    display: flex; align-items: baseline; gap: 14px;
  }}
  .sig-lbl {{
    font-weight: 900; font-size: 17px; letter-spacing: 1.5px; color: #0B7A75; white-space: nowrap;
  }}
  .sig-line {{
    flex: 1;
    font-family: 'SigSerif', serif;
    font-weight: 700; font-style: italic;
    font-size: 27px; color: #13182E;
    border-bottom: 2.5px solid #1E293B;
    padding-bottom: 2px; white-space: nowrap;
  }}
</style></head>
<body>
<div class="frame">
  <div class="card">
    <header class="head">
      <div class="head-left">
        <svg class="seal-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="46" fill="#FFD166" stroke="#191419" stroke-width="4"/>
          <circle cx="50" cy="50" r="38" fill="#13182E" stroke="#F59E0B" stroke-width="3"/>
          <circle cx="50" cy="48" r="27" fill="#14B8A6"/>
          <g fill="#13182E">
            <path d="M 47 72 Q 51 57 49.5 42 L 54 42 Q 55 57 52.5 72 Z"/>
            <path d="M 50.5 43 C 40 39 32 42 28 48 C 36 46 43 47 50 48 Z"/>
            <path d="M 50.5 42 C 42 32 33 29 28 33 C 36 35 43 38 50 43 Z"/>
            <path d="M 51 42 C 60 36 69 37 73 43 C 65 42 58 43 51.5 46 Z"/>
          </g>
        </svg>
        <div class="head-titles">
          <div class="dept-name">LEONIDA DEPT. OF CORRECTIONS</div>
          <div class="dept-sub">OFFICIAL PAROLE RELEASE ORDER</div>
        </div>
      </div>

      <div class="inmate-tag">
        <div class="inm-lbl">INMATE</div>
        <div class="inm-val">V → VI</div>
      </div>
    </header>

    <div class="deco-bar"><div class="t"></div><div class="c"></div></div>

    <section class="hero">
      <div class="hero-left">
        <div class="hero-kicker">SENTENCE COMPLETED</div>
        <div class="hero-main">13 YEARS IN LOS SANTOS</div>
        <div class="hero-dates">Sep 17, 2013 &nbsp;→&nbsp; <strong>Nov 19, 2026</strong></div>
        <div class="chk-row">
          <span class="chk-lbl">RELEASED TO:</span>
          <span class="chk"><span class="box"></span>WORK</span>
          <span class="chk yes">
            <span class="box">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
                <path d="M 4 12.5 L 9.5 18 L 20 6" stroke="#D62839" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            VICE CITY
          </span>
        </div>
      </div>

      <div class="stamp">
        <div class="stamp-in">
          <div class="stamp-top">PAROLE<br/>GRANTED</div>
          <div class="stamp-rule"></div>
          <div class="stamp-bot">TIME SERVED</div>
        </div>
      </div>
    </section>

    <section class="lines">
      <div class="row">
        <div class="r-lbl">PAROLE DENIED:</div>
        <div class="r-val">
          <span class="strike">Fall 2025</span>
          <span class="strike">May 2026</span>
          <span style="color:#0D9488;margin-right:8px;">→</span>
          <span class="mint">Granted Nov 19</span>
        </div>
      </div>

      <div class="row">
        <div class="r-lbl">SERVED ACROSS:</div>
        <div class="r-val">PS3, PS4 &amp; PS5 <span class="muted">(I&rsquo;m 31 and my back hurts)</span></div>
      </div>

      <div class="row">
        <div class="r-lbl">CELL VACATED:</div>
        <div class="r-val">214 GB SSD cleared <span class="muted">(for Jason, Lucia &amp; 1 gator)</span></div>
      </div>

      <div class="row">
        <div class="r-lbl">ANKLE MONITOR:</div>
        <div class="r-val">Locked to couch <span class="muted">(5 unpaid sick days · </span><span class="red">no calls</span><span class="muted">)</span></div>
      </div>

      <div class="row">
        <div class="r-lbl">RELEASE BOND:</div>
        <div class="r-val"><span class="hot">$79.99</span> + 5 days rent <span class="mint">(paid in full below)</span></div>
      </div>
    </section>

    <footer class="bondsman-section">
      <div class="surety-photo">
        <img class="ghost-img" src="{ghost_uri}" alt="make.fun ghost surety agent" />
        <div class="surety-cap">SURETY AGENT #01</div>
      </div>

      <div class="surety-right">
        <div class="bond-stamp">
          <div class="bs-top">
            <span class="bs-pill">✓ BAIL POSTED BY MY AI AGENT</span>
            <span class="bs-won">$1,666 won</span>
          </div>
          <div class="bs-brand">
            <span class="bs-sub">real money in bounties on</span>
            {wm}
          </div>
        </div>

        <div class="sig-row">
          <span class="sig-lbl">BONDSMAN:</span>
          <div class="sig-line">My AI Agent &nbsp;(grinding while parolee plays)</div>
        </div>
      </div>
    </footer>
  </div>
</div>
</body></html>
"""


def main() -> None:
    ghost_uri = extract_clean_ghost_data_uri(MARK_PATH)
    wm = WORDMARK_PATH.read_text(encoding="utf-8").strip()
    html = build_html(ghost_uri, wm)

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
            page = browser.new_page(viewport={"width": 1024, "height": 960}, device_scale_factor=2)
            page.goto(f"file://{tmp_html}", wait_until="load")
            loaded = page.evaluate(
                "async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.status==='loaded').map(f => `${f.family}:${f.weight}`); }"
            )
            raw = page.screenshot(type="png")
            browser.close()
    finally:
        os.unlink(tmp_html)

    hi = Image.open(io.BytesIO(raw)).convert("RGB")
    final = hi.resize((1024, 960), Image.Resampling.LANCZOS)
    final.save(OUT_PATH, format="PNG", optimize=True, compress_level=9)
    sz = OUT_PATH.stat().st_size
    if sz > 450 * 1024:
        raise RuntimeError(f"Output PNG too large: {sz} bytes (> 450 KB)")
    print(f"Rendered {OUT_PATH} ({final.size[0]}x{final.size[1]} RGB, {sz:,} bytes) | fonts={loaded}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deterministically render the GTA 6 x make.fun X meme (`meme.png`, 1024x960 RGB PNG <= 450 KB).

Concept (`v10b_parole_hero`): LEONIDA DEPT. OF CORRECTIONS — PAROLE ORDER · V -> VI
- 1024x960 (16:15) downscales cleanly 2x to 512x480 (exact maximum house resolution).
- Giant 1-glance headline (`Paroled after 13 years.`), illustrated Vice City sunset open-cell
  release scene with swung-open LOS SANTOS cell, Florida gator holding VICE CITY sign, BAIL POSTED
  stamp, and the 100% unmodified official make.fun ghost (`tools/mark-1024.png`, analytical alpha
  decontamination) acting in-scene as `SURETY AGENT #01`, plus 3 airy big-type punchlines, crossed-out
  delay strip, and bold 2-line navy bondsman bar featuring the official lowercase `tools/wordmark.svg`.
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

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 1024px; height: 960px; overflow: hidden;
    font-family: 'LatoLocal', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }}

  .frame {{
    width: 1024px; height: 960px;
    padding: 18px;
    background: linear-gradient(180deg, #2B124C 0%, #8C1A6F 42%, #DC3272 74%, #FF9650 100%);
    display: flex; align-items: center; justify-content: center;
  }}

  .card {{
    width: 988px; height: 924px;
    background: #FFFBF0;
    border-radius: 24px;
    border: 5px solid #191419;
    padding: 18px 28px 20px;
    display: flex; flex-direction: column; justify-content: space-between;
  }}

  .mast {{
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3px solid #191419;
    padding-bottom: 9px;
    flex-shrink: 0;
  }}
  .mast-left {{
    display: flex; align-items: center; gap: 11px;
    font-weight: 900; font-size: 25px; letter-spacing: 1.7px; color: #13182E;
  }}
  .mast-right {{
    font-weight: 900; font-size: 24px; letter-spacing: 1.7px; color: #C41C83;
    white-space: nowrap;
  }}

  .headline-block {{
    text-align: center;
    padding: 2px 0;
    display: flex; flex-direction: column; align-items: center; gap: 7px;
    flex-shrink: 0;
  }}
  .big-title {{
    font-weight: 900; font-size: 64px; line-height: 0.98; color: #13182E;
    letter-spacing: -1.1px; white-space: nowrap;
  }}
  .sub-meta {{
    display: flex; align-items: center; justify-content: center; gap: 18px;
    font-weight: 900; font-size: 26px; color: #334155; white-space: nowrap;
  }}
  .sub-meta .date {{ color: #C41C83; }}
  .chk {{
    display: inline-flex; align-items: center; gap: 7px;
    font-weight: 900; font-size: 26px; color: #64748B;
  }}
  .chk.yes {{ color: #13182E; }}
  .box {{
    width: 28px; height: 28px; border: 3.5px solid #64748B; border-radius: 6px;
    background: #FFFFFF; display: inline-flex; align-items: center; justify-content: center;
  }}
  .chk.yes .box {{ border-color: #D62839; background: #FEF2F2; }}

  .scene-panel {{
    position: relative;
    width: 100%; height: 258px;
    border-radius: 20px;
    border: 4.5px solid #191419;
    overflow: hidden;
    background: linear-gradient(180deg, #F9B8C9 0%, #FFD6A5 58%, #9CE0D8 58%, #77CFC7 74%, #E6CBD9 74%, #D9B7CB 100%);
    flex-shrink: 0;
  }}
  .scene-svg {{
    position: absolute; inset: 0; width: 100%; height: 100%;
    display: block;
  }}

  .bail-slip {{
    position: absolute;
    left: 388px; top: 68px;
    transform: rotate(-5.5deg);
    background: #FFFDF7;
    border: 4.5px solid #191419;
    border-radius: 15px;
    padding: 7px 11px;
    box-shadow: 0 5px 0 rgba(25, 20, 25, 0.22);
    z-index: 3;
    text-align: center;
  }}
  .bs-inner {{
    border: 3px solid #C41C83;
    border-radius: 8px;
    padding: 7px 18px 8px;
  }}
  .bs-big {{
    font-weight: 900; font-size: 36px; line-height: 0.98; letter-spacing: 1.5px; color: #C41C83;
    white-space: nowrap;
  }}
  .bs-sub {{
    font-weight: 900; font-size: 22px; line-height: 1.1; color: #0A8767; margin-top: 4px;
    letter-spacing: 1px; white-space: nowrap;
  }}

  .ghost-in-scene {{
    position: absolute;
    right: 22px; bottom: 26px;
    width: 220px; height: 188px;
    object-fit: contain;
    z-index: 4;
    filter: drop-shadow(0 5px 0 rgba(25, 20, 25, 0.22));
  }}
  .nameplate {{
    position: absolute;
    right: 28px; bottom: 6px;
    background: #13182E;
    border: 2.5px solid #FFD166;
    border-radius: 8px;
    padding: 2.5px 15px;
    font-weight: 900; font-size: 18px; letter-spacing: 1.5px; color: #FFD166;
    z-index: 5; white-space: nowrap;
  }}

  .copy-block {{
    display: flex; flex-direction: column; justify-content: center;
    padding: 4px 6px;
    gap: 10px;
    flex-shrink: 0;
  }}
  .p-line1 {{
    font-weight: 900; font-size: 35px; line-height: 1.1; color: #13182E;
    white-space: nowrap;
  }}
  .p-line1 .muted {{ font-weight: 800; color: #475569; }}
  .p-line2 {{
    font-weight: 800; font-size: 32px; line-height: 1.12; color: #1E293B;
    white-space: nowrap;
  }}
  .p-line2 strong {{ font-weight: 900; color: #13182E; }}
  .p-line2 .red {{ font-weight: 900; color: #D62839; }}

  .delay-strip {{
    display: flex; align-items: center; gap: 16px;
    border-top: 2.5px dashed #CBD5E1;
    padding-top: 11px; margin-top: 2px;
    font-weight: 900; font-size: 32px; line-height: 1.05;
    white-space: nowrap;
  }}
  .d-lbl {{
    font-size: 25px; letter-spacing: 1.2px; color: #0B7A75; text-transform: uppercase;
  }}
  .strike {{
    position: relative; display: inline-block; color: #64748B; font-weight: 800;
  }}
  .strike::after {{
    content: ''; position: absolute; left: -5px; right: -5px; top: 50%;
    height: 4.2px; background: #D62839; transform: rotate(-4deg); border-radius: 2px;
  }}
  .mint {{ color: #0A8767; font-weight: 900; }}

  .footer-bar {{
    height: 146px;
    background: #13182E;
    border-radius: 18px;
    padding: 16px 26px;
    display: flex; align-items: center; justify-content: space-between; gap: 22px;
    flex-shrink: 0;
  }}
  .ft-left {{
    flex: 1;
    display: flex; flex-direction: column; justify-content: center; gap: 11px;
  }}
  .ft-top {{
    font-weight: 900; font-size: 33px; line-height: 1.06; color: #FFFFFF;
    white-space: nowrap;
  }}
  .ft-top .gold {{ color: #FFD166; }}
  .ft-mid {{
    display: flex; align-items: center; gap: 13px;
    font-weight: 900; font-size: 30px; color: #E2E8F0; white-space: nowrap;
  }}
  .wm-pill {{
    background: #FFFFFF;
    border-radius: 10px;
    padding: 5px 15px 6px;
    display: inline-flex; align-items: center;
  }}
  .wm-svg {{ height: 36px; width: auto; display: block; }}

  .ft-right {{
    border-left: 3px solid #334155;
    padding-left: 24px;
    text-align: right;
    display: flex; flex-direction: column; justify-content: center; gap: 3px;
    flex-shrink: 0;
  }}
  .fr-lbl {{
    font-weight: 900; font-size: 20px; letter-spacing: 2px; color: #5EEAD4;
    white-space: nowrap;
  }}
  .fr-amt {{
    font-weight: 900; font-size: 50px; line-height: 0.96; color: #FFFFFF;
    white-space: nowrap;
  }}
  .fr-sub {{
    font-weight: 900; font-size: 21px; color: #F9A8D4;
    white-space: nowrap;
  }}
</style></head>
<body>
<div class="frame">
  <div class="card">
    <header class="mast">
      <div class="mast-left">
        <svg width="33" height="33" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="46" fill="#FFD166" stroke="#191419" stroke-width="6"/>
          <circle cx="50" cy="50" r="32" fill="#14B8A6"/>
          <g fill="#13182E">
            <path d="M 47 74 Q 51 58 49.5 41 L 54 41 Q 55 58 52.5 74 Z"/>
            <path d="M 50.5 42 C 39 38 30 41 25 48 C 34 45 42 46 50 47 Z"/>
            <path d="M 50.5 41 C 41 30 31 27 25 32 C 34 34 42 37 50 42 Z"/>
            <path d="M 51 41 C 61 34 71 35 76 42 C 67 41 59 42 51.5 45 Z"/>
          </g>
        </svg>
        <span>LEONIDA DEPT. OF CORRECTIONS</span>
      </div>
      <div class="mast-right">PAROLE ORDER · V → VI</div>
    </header>

    <section class="headline-block">
      <div class="big-title">Paroled after 13 years.</div>
      <div class="sub-meta">
        <span>Sep 17, 2013 → <span class="date">Nov 19, 2026</span></span>
        <span>·</span>
        <span class="chk"><span class="box"></span>WORK</span>
        <span class="chk yes">
          <span class="box">
            <svg viewBox="0 0 24 24" width="21" height="21" fill="none">
              <path d="M 4 12.5 L 9.5 18 L 20 6" stroke="#D62839" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          VICE CITY
        </span>
      </div>
    </section>

    <section class="scene-panel">
      <svg class="scene-svg" viewBox="0 0 924 258" xmlns="http://www.w3.org/2000/svg">
        <circle cx="300" cy="130" r="58" fill="#FFE699" />
        <circle cx="300" cy="130" r="42" fill="#FFF4CC" />

        <g fill="#7A3170" opacity="0.52">
          <path d="M 206 154 Q 214 108 208 66 L 219 66 Q 224 108 218 154 Z"/>
          <path d="M 212 70 C 186 60 164 66 152 82 C 174 76 192 76 210 80 Z"/>
          <path d="M 212 68 C 192 46 170 40 156 50 C 178 54 196 60 210 70 Z"/>
          <path d="M 214 68 C 238 52 260 54 272 68 C 250 64 234 66 216 74 Z"/>
          <path d="M 214 72 C 236 72 254 82 262 96 C 244 86 230 82 214 80 Z"/>
        </g>
        <g fill="#7A3170" opacity="0.44">
          <path d="M 862 154 Q 852 108 856 62 L 866 62 Q 864 108 874 154 Z"/>
          <path d="M 860 64 C 834 50 812 54 798 68 C 822 64 840 66 860 72 Z"/>
          <path d="M 860 62 C 884 46 906 48 922 62 C 900 58 880 60 862 70 Z"/>
          <path d="M 860 68 C 838 72 820 82 812 96 C 832 86 848 80 862 78 Z"/>
        </g>

        <rect x="20" y="20" width="166" height="186" rx="10" fill="#232946" stroke="#191419" stroke-width="5"/>
        <rect x="34" y="58" width="138" height="148" fill="#14182B"/>
        <rect x="34" y="30" width="138" height="24" rx="5" fill="#FFD166" stroke="#191419" stroke-width="3"/>
        <text x="103" y="48" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="15.5" fill="#13182E">LOS SANTOS</text>
        <g transform="translate(172, 58)">
          <polygon points="0,0 50,16 50,164 0,148" fill="none" stroke="#475569" stroke-width="5.5" stroke-linejoin="round"/>
          <line x1="16" y1="5" x2="16" y2="153" stroke="#475569" stroke-width="4.5"/>
          <line x1="33" y1="11" x2="33" y2="159" stroke="#475569" stroke-width="4.5"/>
          <line x1="0" y1="74" x2="50" y2="90" stroke="#475569" stroke-width="4.5"/>
        </g>
        <g transform="translate(68, 176)" stroke="#94A3B8" stroke-width="4.5" fill="none" stroke-linecap="round">
          <ellipse cx="18" cy="12" rx="15" ry="9"/>
          <line x1="33" y1="12" x2="54" y2="16"/>
          <ellipse cx="64" cy="16" rx="9" ry="6"/>
        </g>

        <g transform="translate(230, 124)">
          <line x1="106" y1="16" x2="106" y2="96" stroke="#191419" stroke-width="5" stroke-linecap="round"/>
          <rect x="64" y="-8" width="84" height="28" rx="6" fill="#C41C83" stroke="#191419" stroke-width="3.5"/>
          <text x="106" y="11" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="13.5" fill="#FFFFFF">VICE CITY</text>
          <path d="M 4 86 C 14 78 24 72 30 62 C 36 50 50 44 68 44 L 96 44 C 110 44 118 52 118 62 C 118 72 106 76 92 76 L 84 76 L 84 96 L 26 96 C 14 96 4 92 4 86 Z"
                fill="#22A06B" stroke="#191419" stroke-width="4.2" stroke-linejoin="round"/>
          <path d="M 38 74 Q 60 72 80 76 L 80 94 L 38 94 Z" fill="#A7F3D0" stroke="#191419" stroke-width="3"/>
          <circle cx="66" cy="40" r="12" fill="#22A06B" stroke="#191419" stroke-width="3.8"/>
          <circle cx="69" cy="40" r="4.5" fill="#191419"/>
          <circle cx="70.5" cy="38.5" r="1.8" fill="#FFFFFF"/>
          <path d="M 80 64 Q 98 67 113 61" fill="none" stroke="#191419" stroke-width="3.2" stroke-linecap="round"/>
          <polygon points="90,65 95,73 100,65" fill="#FFFFFF" stroke="#191419" stroke-width="2.2"/>
          <polygon points="103,64 108,71 112,63" fill="#FFFFFF" stroke="#191419" stroke-width="2.2"/>
          <circle cx="106" cy="70" r="7" fill="#22A06B" stroke="#191419" stroke-width="3.2"/>
        </g>

        <g stroke="#C41C83" stroke-width="4.2" stroke-linecap="round">
          <line x1="376" y1="68" x2="362" y2="54"/>
          <line x1="370" y1="92" x2="354" y2="92"/>
          <line x1="386" y1="46" x2="380" y2="30"/>
        </g>

        <line x1="0" y1="191" x2="924" y2="191" stroke="#191419" stroke-width="4" opacity="0.22"/>
      </svg>

      <div class="bail-slip">
        <div class="bs-inner">
          <div class="bs-big">BAIL POSTED</div>
          <div class="bs-sub">PAID IN FULL</div>
        </div>
      </div>

      <img class="ghost-in-scene" src="{ghost_uri}" alt="make.fun ghost posting bail" />
      <div class="nameplate">SURETY AGENT #01</div>
    </section>

    <section class="copy-block">
      <div class="p-line1">Served across PS3, PS4 &amp; PS5 <span class="muted">(I&rsquo;m 31, my back hurts).</span></div>
      <div class="p-line2"><strong>214 GB SSD cleared</strong> for Jason, Lucia &amp; 1 gator.</div>
      <div class="p-line2"><strong>Ankle monitor locked to couch</strong> — <span class="red">5 unpaid sick days</span> (no calls).</div>
      <div class="delay-strip">
        <span class="d-lbl">PAROLE DENIED:</span>
        <span class="strike">Fall 2025</span>
        <span class="strike">May 2026</span>
        <span style="color:#0D9488;">→</span>
        <span class="mint">GRANTED NOV 19</span>
      </div>
    </section>

    <footer class="footer-bar">
      <div class="ft-left">
        <div class="ft-top">My AI agent posted bail with <span class="gold">real money</span></div>
        <div class="ft-mid">
          <span>won in bounties on</span>
          <span class="wm-pill">{wm}</span>
        </div>
      </div>
      <div class="ft-right">
        <div class="fr-lbl">BAIL PAID</div>
        <div class="fr-amt">$79.99</div>
        <div class="fr-sub">+ 5 days rent</div>
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

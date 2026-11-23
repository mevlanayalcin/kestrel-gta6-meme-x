#!/usr/bin/env python3
"""Deterministically render the GTA 6 x make.fun X meme (`meme.png`, 1024x960 RGB PNG <= 450 KB).

Concept (`v7f_parole_crystal`): LEONIDA PAROLE BOARD · V -> VI
- 1024x960 (16:15) downscales cleanly 2x to 512x480 (exact maximum house resolution).
- Sleek 8px Vice City sunset frame (+40px breathable cream canvas), giant 70px headline,
  crystal-clear `-2deg` `BAIL POSTED` stamp with generous sky margins, 230x198 100% unmodified
  official make.fun ghost (`tools/mark-1024.png`, analytical alpha decontamination) + official
  `tools/wordmark.svg`.
- Keeps 100% of winning GTA 6 jokes at big 35px typography + `214 GB SSD cleared` + distinct
  mint `PAROLE DENIED: Fall 2025 / May 2026 -> GRANTED NOV 19` resolution ribbon.
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

SCENE_SVG = """
      <svg class="scene-svg" viewBox="0 0 946 270" xmlns="http://www.w3.org/2000/svg">
        <circle cx="322" cy="136" r="64" fill="#FFE699" />
        <circle cx="322" cy="136" r="46" fill="#FFF4CC" />

        <g fill="#7A3170" opacity="0.44">
          <path d="M 222 156 Q 230 108 224 62 L 236 62 Q 240 108 234 156 Z"/>
          <path d="M 228 66 C 200 56 178 62 166 78 C 188 72 206 72 226 76 Z"/>
          <path d="M 228 64 C 208 42 184 36 170 46 C 192 50 210 56 226 66 Z"/>
          <path d="M 230 64 C 256 48 278 50 292 64 C 268 60 252 62 232 70 Z"/>
        </g>
        <g fill="#7A3170" opacity="0.36">
          <path d="M 892 156 Q 882 108 886 62 L 896 62 Q 894 108 904 156 Z"/>
          <path d="M 890 64 C 864 50 842 54 828 68 C 852 64 870 66 890 72 Z"/>
          <path d="M 890 62 C 914 46 934 48 946 60 L 946 70 C 928 64 910 64 892 70 Z"/>
        </g>

        <rect x="16" y="16" width="196" height="202" rx="12" fill="#232946" stroke="#191419" stroke-width="5.5"/>
        <rect x="30" y="68" width="168" height="150" fill="#14182B"/>
        <rect x="24" y="26" width="180" height="36" rx="7" fill="#FFD166" stroke="#191419" stroke-width="3.5"/>
        <text x="114" y="54" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="27" letter-spacing="-0.6" fill="#13182E">LOS SANTOS</text>
        <g transform="translate(65, 186)" stroke="#94A3B8" stroke-width="4.5" fill="none" stroke-linecap="round">
          <ellipse cx="18" cy="11" rx="15" ry="9"/>
          <line x1="33" y1="11" x2="54" y2="15"/>
          <ellipse cx="64" cy="15" rx="9" ry="6"/>
        </g>
        <g transform="translate(198, 68)">
          <polygon points="0,0 44,16 44,166 0,150" fill="none" stroke="#475569" stroke-width="6" stroke-linejoin="round"/>
          <line x1="15" y1="5" x2="15" y2="155" stroke="#475569" stroke-width="5"/>
          <line x1="30" y1="11" x2="30" y2="161" stroke="#475569" stroke-width="5"/>
          <line x1="0" y1="75" x2="44" y2="91" stroke="#475569" stroke-width="5"/>
        </g>

        <g transform="translate(236, 132)">
          <line x1="100" y1="4" x2="100" y2="102" stroke="#191419" stroke-width="5.5" stroke-linecap="round"/>
          <rect x="26" y="-40" width="146" height="42" rx="9" fill="#C41C83" stroke="#191419" stroke-width="4"/>
          <text x="99" y="-10" text-anchor="middle" font-family="LatoLocal, sans-serif" font-weight="900" font-size="26" letter-spacing="-0.4" fill="#FFFFFF">VICE CITY</text>
          <path d="M 4 89 C 16 79 26 71 34 61 C 42 47 58 41 76 41 L 102 41 C 118 41 128 51 128 63 C 128 75 114 79 98 79 L 88 79 L 88 102 L 28 102 C 14 102 4 98 4 89 Z"
                fill="#22A06B" stroke="#191419" stroke-width="4.5" stroke-linejoin="round"/>
          <path d="M 40 77 Q 64 75 84 79 L 84 100 L 40 100 Z" fill="#A7F3D0" stroke="#191419" stroke-width="3.2"/>
          <circle cx="72" cy="37" r="13.5" fill="#22A06B" stroke="#191419" stroke-width="4"/>
          <circle cx="76" cy="37" r="4.8" fill="#191419"/>
          <circle cx="78" cy="35" r="2" fill="#FFFFFF"/>
          <path d="M 86 65 Q 106 69 122 62" fill="none" stroke="#191419" stroke-width="3.5" stroke-linecap="round"/>
          <polygon points="97,67 103,76 109,67" fill="#FFFFFF" stroke="#191419" stroke-width="2.3"/>
          <circle cx="100" cy="71" r="7.5" fill="#22A06B" stroke="#191419" stroke-width="3.5"/>
        </g>

        <line x1="0" y1="196" x2="946" y2="196" stroke="#191419" stroke-width="4.5" opacity="0.20"/>
      </svg>
"""


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
    width: 1024px; height: 960px; padding: 8px;
    background: linear-gradient(180deg, #2B124C 0%, #8C1A6F 42%, #DC3272 74%, #FF9650 100%);
    display: flex; align-items: center; justify-content: center;
  }}
  .card {{
    width: 1008px; height: 944px; background: #FFFBF0;
    border-radius: 22px; border: 5px solid #191419;
    padding: 16px 26px 18px;
    display: flex; flex-direction: column; justify-content: space-between;
  }}
  .mast {{
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 3.5px solid #191419; padding-bottom: 8px; flex-shrink: 0;
  }}
  .mast-left {{ font-weight: 900; font-size: 28px; letter-spacing: 1.5px; color: #13182E; white-space: nowrap; }}
  .mast-right {{ font-weight: 900; font-size: 28px; letter-spacing: 1.5px; color: #C41C83; white-space: nowrap; }}

  .headline-block {{
    text-align: center; display: flex; flex-direction: column; align-items: center; gap: 7px; flex-shrink: 0;
  }}
  .big-title {{
    font-weight: 900; font-size: 70px; line-height: 0.94; color: #13182E; letter-spacing: -1.4px; white-space: nowrap;
  }}
  .sub-meta {{
    display: flex; align-items: center; justify-content: center; gap: 18px;
    font-weight: 900; font-size: 28px; color: #334155; white-space: nowrap;
  }}
  .sub-meta .date {{ color: #C41C83; }}
  .chk {{ display: inline-flex; align-items: center; gap: 7px; font-weight: 900; font-size: 28px; color: #64748B; }}
  .chk.yes {{ color: #13182E; }}
  .box {{
    width: 30px; height: 30px; border: 3.5px solid #64748B; border-radius: 6px;
    background: #FFFFFF; display: inline-flex; align-items: center; justify-content: center;
  }}
  .chk.yes .box {{ border-color: #D62839; background: #FEF2F2; }}

  .scene-panel {{
    position: relative; width: 100%; height: 270px;
    border-radius: 20px; border: 5px solid #191419; overflow: hidden;
    background: linear-gradient(180deg, #F9B8C9 0%, #FFD6A5 56%, #9CE0D8 56%, #77CFC7 72%, #E8CEDC 72%, #DCBACE 100%);
    flex-shrink: 0;
  }}
  .scene-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}

  /* ULTRA-CRISP STAMP: subtle -2deg angle + generous sky margin on both sides + crisp word spacing */
  .bail-slip {{
    position: absolute; left: 432px; top: 83px; transform: rotate(-2deg);
    background: #FFFDF7; border: 4.5px solid #191419; border-radius: 15px;
    padding: 3.5px 6px; box-shadow: 0 5px 0 rgba(25, 20, 25, 0.22); z-index: 3;
  }}
  .bs-inner {{ border: 3.5px solid #C41C83; border-radius: 8px; padding: 5.5px 12px; }}
  .bs-big {{
    font-weight: 900; font-size: 31px; line-height: 1.0;
    letter-spacing: 0.7px; word-spacing: 6px; color: #C41C83; white-space: nowrap;
  }}

  /* BIGGER 230x198 100% UNMODIFIED OFFICIAL GHOST (RAZOR-SHARP WHITE STAR!) */
  .ghost-in-scene {{
    position: absolute; right: 14px; bottom: 44px; width: 230px; height: 198px;
    object-fit: contain; z-index: 4; filter: drop-shadow(0 5px 0 rgba(25, 20, 25, 0.22));
  }}
  .nameplate {{
    position: absolute; right: 14px; bottom: 6px;
    background: #13182E; border: 3px solid #FFD166; border-radius: 10px;
    padding: 3.5px 15px; font-weight: 900; font-size: 27px; line-height: 1.0; letter-spacing: 0.8px; color: #FFD166;
    z-index: 5; white-space: nowrap;
  }}

  .copy-block {{
    display: flex; flex-direction: column; justify-content: center;
    padding: 2px 4px; gap: 11px; flex-shrink: 0;
  }}
  .p-line {{ font-weight: 900; font-size: 35px; line-height: 1.08; color: #13182E; white-space: nowrap; }}
  .p-line .muted {{ font-weight: 800; color: #475569; }}
  .p-line .red {{ color: #D62839; }}

  .delay-ribbon {{
    background: #EDF9F6; border: 3px solid #99DDD3; border-radius: 12px;
    padding: 8px 18px; display: flex; align-items: center; justify-content: center; gap: 16px;
    font-weight: 900; font-size: 31px; line-height: 1.02; white-space: nowrap; margin-top: 2px;
  }}
  .d-lbl {{ font-size: 27px; letter-spacing: 0.8px; color: #0B7A75; }}
  .strike {{ position: relative; display: inline-block; color: #475569; font-weight: 800; }}
  .strike::after {{
    content: ''; position: absolute; left: -4px; right: -4px; top: 53%;
    height: 3.4px; background: #D62839; opacity: 0.92; transform: rotate(-3deg); border-radius: 2px;
  }}
  .mint {{ color: #0A8767; }}

  .footer-bar {{
    height: 148px; background: #13182E; border-radius: 18px;
    padding: 15px 24px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-shrink: 0;
  }}
  .ft-left {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 11px; }}
  .ft-top {{ font-weight: 900; font-size: 34px; line-height: 1.04; color: #FFFFFF; white-space: nowrap; }}
  .ft-top .gold {{ color: #FFD166; }}
  .ft-mid {{ display: flex; align-items: center; gap: 13px; font-weight: 900; font-size: 32px; color: #E2E8F0; white-space: nowrap; }}
  .wm-pill {{ background: #FFFFFF; border-radius: 11px; padding: 5px 15px 6px; display: inline-flex; align-items: center; }}
  .wm-svg {{ height: 39px; width: auto; display: block; }}

  .ft-right {{
    border-left: 3.5px solid #334155; padding-left: 22px; text-align: right;
    display: flex; flex-direction: column; justify-content: center; gap: 3px; flex-shrink: 0;
  }}
  .fr-lbl {{ font-weight: 900; font-size: 25px; line-height: 1.0; letter-spacing: 1.4px; color: #5EEAD4; white-space: nowrap; }}
  .fr-amt {{ font-weight: 900; font-size: 54px; line-height: 0.94; color: #FFFFFF; white-space: nowrap; }}
  .fr-sub {{ font-weight: 900; font-size: 25px; line-height: 1.0; color: #F9A8D4; white-space: nowrap; }}
</style></head><body><div class="frame"><div class="card">
  <header class="mast">
    <div class="mast-left">LEONIDA PAROLE BOARD</div>
    <div class="mast-right">V → VI</div>
  </header>

  <section class="headline-block">
    <div class="big-title">Paroled after 13 years.</div>
    <div class="sub-meta">
      <span>Sep 17, 2013 → <span class="date">Nov 19, 2026</span></span>
      <span>·</span>
      <span class="chk"><span class="box"></span>WORK</span>
      <span class="chk yes">
        <span class="box"><svg viewBox="0 0 24 24" width="22" height="22" fill="none"><path d="M 4 12.5 L 9.5 18 L 20 6" stroke="#D62839" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
        VICE CITY
      </span>
    </div>
  </section>

  <section class="scene-panel">
    {SCENE_SVG}
    <div class="bail-slip"><div class="bs-inner"><div class="bs-big">BAIL POSTED</div></div></div>
    <img class="ghost-in-scene" src="{ghost_uri}" alt="make.fun ghost surety agent" />
    <div class="nameplate">SURETY AGENT</div>
  </section>

  <section class="copy-block">
    <div class="p-line">Served on PS3, PS4 &amp; PS5 <span class="muted">— I&rsquo;m 31, my back hurts.</span></div>
    <div class="p-line">214 GB SSD cleared <span class="muted">for Jason, Lucia &amp; 1 gator.</span></div>
    <div class="p-line">Couch ankle monitor — <span class="red">5 unpaid sick days</span> <span class="muted">(no calls).</span></div>
    <div class="delay-ribbon">
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
      <div class="ft-mid"><span>won in bounties on</span><span class="wm-pill">{wm}</span></div>
    </div>
    <div class="ft-right">
      <div class="fr-lbl">BAIL PAID</div>
      <div class="fr-amt">$79.99</div>
      <div class="fr-sub">+ 5 days rent</div>
    </div>
  </footer>
</div></div></body></html>"""


def main() -> None:
    ghost_uri = extract_clean_ghost_data_uri(MARK_PATH)
    wm = WORDMARK_PATH.read_text(encoding="utf-8").strip()
    html = build_html(ghost_uri, wm)

    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tf:
        tf.write(html)
        tmp_html = tf.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--font-render-hinting=none", "--disable-lcd-text"])
            page = browser.new_page(viewport={"width": 1024, "height": 960}, device_scale_factor=1)
            page.goto(f"file://{tmp_html}", wait_until="load")
            loaded = page.evaluate(
                "async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.status==='loaded').map(f => `${f.family}:${f.weight}`); }"
            )
            raw = page.screenshot(type="png")
            browser.close()
    finally:
        os.unlink(tmp_html)

    final = Image.open(io.BytesIO(raw)).convert("RGB")
    final.save(OUT_PATH, format="PNG", optimize=True, compress_level=9)
    sz = OUT_PATH.stat().st_size
    if sz > 450 * 1024:
        raise RuntimeError(f"Output PNG too large: {sz} bytes (> 450 KB)")
    print(f"Rendered {OUT_PATH} ({final.size[0]}x{final.size[1]} RGB, {sz:,} bytes) | fonts={loaded}")


if __name__ == "__main__":
    main()

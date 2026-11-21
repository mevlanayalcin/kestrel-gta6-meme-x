#!/usr/bin/env python3
"""Deterministic renderer for the GTA 6 × make.fun X Meme (1024x1024 PNG)."""

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

    # Exact palette colors of mark-1024.png
    black = np.array([25.0, 20.0, 25.0], dtype=np.float32)    # #191419
    magenta = np.array([196.0, 28.0, 131.0], dtype=np.float32)  # #c41c83
    d_mag = np.linalg.norm(rgb - magenta, axis=2)

    # 1. Flood-fill the outer magenta ring (stops at outer black ring & ghost black outline)
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

    # 2. Flood-fill everything outside the outer magenta ring (transparent bg + outer black circle)
    exterior = np.zeros((h, w), dtype=bool)
    q = deque([(0, 0)])
    exterior[0, 0] = True
    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < h
                and 0 <= nx < w
                and not exterior[ny, nx]
                and not outer_mag[ny, nx]
            ):
                exterior[ny, nx] = True
                q.append((ny, nx))

    bg = exterior | outer_mag
    ghost_mask = ~bg

    # 3. Recover smooth sub-pixel anti-aliasing on the ghost's outer black edge
    def dilate(mask: np.ndarray, steps: int = 3) -> np.ndarray:
        m = mask.copy()
        for _ in range(steps):
            p = np.pad(m, 1, constant_values=False)
            m = (
                p[:-2, 1:-1]
                | p[2:, 1:-1]
                | p[1:-1, :-2]
                | p[1:-1, 2:]
                | p[:-2, :-2]
                | p[:-2, 2:]
                | p[2:, :-2]
                | p[2:, 2:]
                | m
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
        t = float(np.dot(c - magenta, vec) / vec2)
        t_clamped = max(0.0, min(1.0, t))
        proj = magenta + t_clamped * vec
        if float(np.linalg.norm(c - proj)) < 26.0:
            out[y, x, :3] = black
            out[y, x, 3] = round(t_clamped * 255.0)

    # Crop to exact frame with headroom for the doctor's head-mirror SVG overlay:
    # x = 160..916 (756px), y = 110..834 (724px)
    cropped = out[110:834, 160:916].clip(0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(cropped, mode="RGBA").save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_html(ghost_uri: str, wordmark_svg: str) -> str:
    wordmark_inline = wordmark_svg.replace(
        'width="390.44" height="70.97"', 'class="wordmark-svg"'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Regular.ttf') format('truetype');
    font-weight: 400;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Semibold.ttf') format('truetype');
    font-weight: 600;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Bold.ttf') format('truetype');
    font-weight: 700;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-BoldItalic.ttf') format('truetype');
    font-weight: 700;
    font-style: italic;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Heavy.ttf') format('truetype');
    font-weight: 800;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'LatoLocal';
    src: url('file:///usr/share/fonts/truetype/lato/Lato-Black.ttf') format('truetype');
    font-weight: 900;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'SigSerif';
    src: url('file:///usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf') format('truetype');
    font-weight: 700;
    font-style: italic;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  html, body {{
    width: 1024px;
    height: 1024px;
    overflow: hidden;
    font-family: 'LatoLocal', sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }}

  /* Vice City Miami Sunset Outer Frame (smooth vertical sunset compresses losslessly!) */
  .canvas {{
    position: relative;
    width: 1024px;
    height: 1024px;
    padding: 30px;
    background: linear-gradient(
      180deg,
      #4A1369 0%,
      #9E1470 28%,
      #DC2B74 52%,
      #F56262 76%,
      #FFAA48 100%
    );
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  /* Main Cream-White Clinical Slip Card */
  .slip {{
    position: relative;
    z-index: 2;
    width: 964px;
    height: 964px;
    background: #FFFDF7;
    border-radius: 26px;
    border: 4px solid #191419;
    box-shadow: 0 12px 26px rgba(24, 8, 40, 0.40);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* Subtle Rx watermark behind clinical rows */
  .rx-watermark {{
    position: absolute;
    right: 28px;
    top: 332px;
    width: 224px;
    height: 224px;
    opacity: 0.04;
    pointer-events: none;
    z-index: 0;
  }}

  /* ===== 1. DARK NAVY HEADER BAR ===== */
  .header {{
    position: relative;
    height: 146px;
    background: #14182E;
    padding: 0 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-shrink: 0;
  }}

  /* Art-Deco Miami Teal + Coral Double Accent Rule below Header */
  .deco-bar {{
    height: 10px;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }}
  .deco-teal {{
    height: 6px;
    background: #14B8A6;
  }}
  .deco-coral {{
    height: 4px;
    background: #F25C66;
  }}

  .crest {{
    width: 96px;
    height: 96px;
    flex-shrink: 0;
  }}

  .header-titles {{
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
  }}

  .hospital-name {{
    font-weight: 900;
    font-size: 44px;
    line-height: 1.02;
    letter-spacing: 0.6px;
    color: #FFFFFF;
    white-space: nowrap;
  }}

  .hospital-sub {{
    font-weight: 800;
    font-size: 20.5px;
    line-height: 1.1;
    letter-spacing: 2.8px;
    color: #FFD166;
    text-transform: uppercase;
    white-space: nowrap;
  }}

  .case-badge {{
    flex-shrink: 0;
    border: 2.5px solid #2DD4BF;
    background: rgba(20, 184, 166, 0.14);
    border-radius: 14px;
    padding: 8px 18px 10px;
    text-align: center;
    min-width: 130px;
  }}

  .case-label {{
    font-weight: 900;
    font-size: 15px;
    letter-spacing: 2.6px;
    color: #5EEAD4;
    line-height: 1.1;
  }}

  .case-num {{
    font-weight: 900;
    font-size: 41px;
    line-height: 1.02;
    color: #FFFFFF;
    letter-spacing: 1px;
    margin-top: 2px;
  }}

  /* ===== 2. DIAGNOSIS HERO BANNER ===== */
  .diagnosis-band {{
    position: relative;
    height: 154px;
    background: #F1FAF8;
    border-bottom: 2.5px solid #CBE6E1;
    padding: 18px 28px 18px 34px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }}

  /* Left Art-Deco teal clinical bar */
  .diagnosis-band::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 12px;
    background: #0D9488;
  }}

  .diagnosis-left {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    z-index: 2;
  }}

  .diag-kicker-row {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .diag-kicker {{
    font-weight: 900;
    font-size: 23px;
    letter-spacing: 2.4px;
    color: #0B7A75;
    text-transform: uppercase;
  }}

  .ecg-svg {{
    width: 156px;
    height: 26px;
    display: block;
  }}

  .diag-title {{
    font-weight: 900;
    font-size: 54px;
    line-height: 1.03;
    letter-spacing: -0.4px;
    color: #14182E;
    white-space: nowrap;
  }}

  /* Tilted Crimson Rubber Stamp */
  .stamp-excused {{
    position: relative;
    z-index: 4;
    transform: rotate(-9deg);
    margin-right: 4px;
    border: 5px solid #D62839;
    border-radius: 14px;
    padding: 5px;
    background: rgba(255, 253, 247, 0.94);
    box-shadow: 0 3px 10px rgba(214, 40, 57, 0.16);
    flex-shrink: 0;
  }}

  .stamp-excused-inner {{
    border: 2.5px solid #D62839;
    border-radius: 8px;
    padding: 8px 20px 9px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }}

  .stamp-top {{
    font-weight: 900;
    font-size: 42px;
    line-height: 1.0;
    letter-spacing: 2.2px;
    color: #D62839;
    white-space: nowrap;
  }}

  .stamp-rule {{
    width: 100%;
    height: 2.5px;
    background: #D62839;
    margin: 3px 0 2px;
    opacity: 0.78;
  }}

  .stamp-date {{
    font-weight: 900;
    font-size: 27px;
    line-height: 1.05;
    letter-spacing: 2.2px;
    color: #D62839;
    white-space: nowrap;
  }}

  /* ===== 3. CLINICAL CHART ROWS (5 PUNCHY LINES) ===== */
  .chart {{
    position: relative;
    z-index: 2;
    padding: 8px 34px 2px;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }}

  .row {{
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 14.5px 0;
    border-bottom: 2px dashed #CBD5E1;
  }}

  .row:last-child {{
    border-bottom: none;
    padding-bottom: 10px;
  }}

  .row-label {{
    width: 186px;
    flex-shrink: 0;
    font-weight: 900;
    font-size: 21px;
    letter-spacing: 0.8px;
    color: #0B7A75;
    text-transform: uppercase;
    white-space: nowrap;
  }}

  .row-val {{
    flex: 1;
    font-weight: 700;
    font-size: 26.5px;
    line-height: 1.2;
    color: #14182E;
    white-space: nowrap;
  }}

  .row-val.symptoms-val {{
    font-size: 25px;
    letter-spacing: -0.15px;
  }}

  .strike {{
    position: relative;
    display: inline-block;
    color: #718096;
    font-weight: 700;
    margin-right: 18px;
  }}

  .strike::after {{
    content: '';
    position: absolute;
    left: -3px;
    right: -3px;
    top: 49%;
    height: 3.4px;
    background: #D62839;
    transform: rotate(-3.5deg);
    border-radius: 2px;
  }}

  .confirmed-date {{
    color: #14182E;
    font-weight: 900;
  }}

  .emph-not {{
    color: #D62839;
    font-weight: 900;
  }}

  .cost-price {{
    color: #C41C83;
    font-weight: 900;
    font-size: 28.5px;
  }}

  .sep-dot {{
    color: #0D9488;
    font-weight: 900;
    margin: 0 7px;
  }}

  /* ===== 4. SIGNATURE & WAGES COVERED BRIDGE ===== */
  .sig-bridge {{
    position: relative;
    z-index: 2;
    height: 76px;
    padding: 0 34px 6px 298px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    flex-shrink: 0;
  }}

  .stamp-wages-wrap {{
    position: relative;
    flex-shrink: 0;
  }}

  .stamp-wages-outer {{
    transform: rotate(-4.5deg);
    border: 4px solid #0A8767;
    border-radius: 11px;
    padding: 3px;
    background: #ECFDF5;
    box-shadow: 0 2px 6px rgba(10, 135, 103, 0.14);
  }}

  .stamp-wages-inner {{
    border: 2px solid #0A8767;
    border-radius: 6px;
    padding: 4px 16px 5px;
    color: #0A8767;
    font-weight: 900;
    font-size: 23.5px;
    letter-spacing: 1.4px;
    white-space: nowrap;
  }}

  .sig-block {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 0;
  }}

  .sig-line {{
    border-bottom: 2.5px solid #1E293B;
    padding-bottom: 2px;
    font-family: 'SigSerif', serif;
    font-weight: 700;
    font-style: italic;
    font-size: 27px;
    color: #14182E;
    white-space: nowrap;
    letter-spacing: 0.2px;
  }}

  .sig-caption {{
    font-weight: 800;
    font-size: 14.5px;
    letter-spacing: 1.8px;
    color: #475569;
    text-transform: uppercase;
    white-space: nowrap;
  }}

  /* ===== 5. BOTTOM MAGENTA / DEEP-PLUM BRAND STRIP ===== */
  .brand-strip {{
    position: relative;
    flex: 1;
    background: linear-gradient(180deg, #C41C83 0%, #9E146E 54%, #6D0E5C 100%);
    border-top: 4.5px solid #191419;
    padding: 2px 30px 2px 308px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 9px;
    z-index: 3;
  }}

  .brand-strip::before {{
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 5px;
    background: rgba(255, 255, 255, 0.16);
  }}

  .cta-headline {{
    font-weight: 900;
    font-size: 38.5px;
    line-height: 1.04;
    letter-spacing: 0.35px;
    color: #FFFFFF;
    text-align: center;
    white-space: nowrap;
    text-shadow: 0 3px 0 rgba(25, 20, 25, 0.34);
  }}

  .cta-sub {{
    font-weight: 800;
    font-size: 24.5px;
    line-height: 1.15;
    color: #FFF0F8;
    text-align: center;
    white-space: nowrap;
  }}

  .wordmark-pill {{
    margin-top: 4px;
    background: #FFFFFF;
    border: 4.5px solid #191419;
    border-radius: 999px;
    padding: 12px 40px 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 5px 0 rgba(25, 20, 25, 0.32);
  }}

  .wordmark-svg {{
    height: 48px;
    width: auto;
    display: block;
  }}

  /* ===== OFFICIAL MAKE.FUN GHOST DOCTOR (BRIDGING THE SEAM!) ===== */
  .ghost-stage {{
    position: absolute;
    left: 14px;
    bottom: 8px;
    width: 280px;
    height: 268px;
    z-index: 6;
    pointer-events: none;
  }}

  .ghost-img {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
  }}

  .ghost-mirror-svg {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
  }}
</style>
</head>
<body>
<div class="canvas">
  <div class="slip">
    <!-- Subtle Clinical Rx Watermark -->
    <svg class="rx-watermark" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <text x="12" y="156" font-family="LatoLocal, sans-serif" font-weight="900" font-size="168" fill="#0B7A75">℞</text>
    </svg>

    <!-- 1. HEADER BAR -->
    <header class="header">
      <!-- Art-Deco Medical Cross + Vice City Palm Tree Clinic Crest -->
      <svg class="crest" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="crestSun" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FFD166"/>
            <stop offset="55%" stop-color="#FF6B7A"/>
            <stop offset="100%" stop-color="#C41C83"/>
          </linearGradient>
        </defs>
        <!-- Outer teal clinic medallion -->
        <circle cx="50" cy="50" r="46" fill="#0D9488" stroke="#5EEAD4" stroke-width="3"/>
        <circle cx="50" cy="50" r="39" fill="#14182E"/>
        <!-- Vice sunset circle -->
        <circle cx="50" cy="50" r="31" fill="url(#crestSun)"/>
        <!-- Bold white Medical Cross -->
        <rect x="39" y="19" width="22" height="62" rx="4" fill="#FFFFFF" stroke="#14182E" stroke-width="3"/>
        <rect x="19" y="39" width="62" height="22" rx="4" fill="#FFFFFF" stroke="#14182E" stroke-width="3"/>
        <rect x="40.5" y="20.5" width="19" height="59" rx="3" fill="#FFFFFF"/>
        <rect x="20.5" y="40.5" width="59" height="19" rx="3" fill="#FFFFFF"/>
        <!-- Bold, unmistakable Vice City Palm Tree silhouette -->
        <g fill="#14182E">
          <!-- Curved palm trunk -->
          <path d="M 46.5 78 Q 51 62 49.5 45 L 54 45 Q 55.5 62 52.5 78 Z"/>
          <!-- Left lower frond -->
          <path d="M 50.5 46 C 39 41 30 44 26 51 C 34 48 42 49 49.5 50.5 Z"/>
          <!-- Left upper frond -->
          <path d="M 50.5 45 C 42 33 32 30 27 34 C 35 36 42 40 49.5 46 Z"/>
          <!-- Top crown frond -->
          <path d="M 51 44 C 51 31 58 26 65 27 C 59 32 55 37 53 45 Z"/>
          <!-- Right upper frond -->
          <path d="M 51.5 46 C 62 38 71 39 75 45 C 67 44 60 45 52.5 49 Z"/>
          <!-- Right lower frond -->
          <path d="M 51.5 48 C 60 49 67 54 69 60 C 63 56 57 53 51.5 52 Z"/>
        </g>
      </svg>

      <div class="header-titles">
        <div class="hospital-name">LEONIDA GENERAL HOSPITAL</div>
        <div class="hospital-sub">OFFICIAL LAUNCH-WEEK MEDICAL EXCUSE</div>
      </div>

      <div class="case-badge">
        <div class="case-label">CASE</div>
        <div class="case-num">#VI</div>
      </div>
    </header>

    <!-- Art-Deco Miami Teal + Coral Double Accent Rule -->
    <div class="deco-bar">
      <div class="deco-teal"></div>
      <div class="deco-coral"></div>
    </div>

    <!-- 2. HERO DIAGNOSIS BANNER -->
    <section class="diagnosis-band">
      <div class="diagnosis-left">
        <div class="diag-kicker-row">
          <span class="diag-kicker">DIAGNOSIS:</span>
          <!-- Crisp Miami-coral ECG pulse waveform -->
          <svg class="ecg-svg" viewBox="0 0 156 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M 2 15 L 28 15 L 36 15 L 43 5 L 51 25 L 59 3 L 67 21 L 74 15 L 100 15 L 107 9 L 114 21 L 120 15 L 154 15"
                  stroke="#F25C66" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="diag-title">ACUTE VICE CITY FLU</div>
      </div>

      <div class="stamp-excused">
        <div class="stamp-excused-inner">
          <div class="stamp-top">EXCUSED</div>
          <div class="stamp-rule"></div>
          <div class="stamp-date">· NOV 19 ·</div>
        </div>
      </div>
    </section>

    <!-- 3. CLINICAL CHART ROWS -->
    <section class="chart">
      <div class="row">
        <div class="row-label">INCUBATION:</div>
        <div class="row-val">13 years (caught in Los Santos, Sep 2013)</div>
      </div>

      <div class="row">
        <div class="row-label">FALSE ALARMS:</div>
        <div class="row-val">
          <span class="strike">Fall 2025</span>
          <span class="strike">May 2026</span>
          <span class="confirmed-date">Confirmed Nov 19, 2026</span>
        </div>
      </div>

      <div class="row">
        <div class="row-label">SYMPTOMS:</div>
        <div class="row-val symptoms-val">214 GB SSD loss<span class="sep-dot">·</span>Florida gators<span class="sep-dot">·</span>answering to &ldquo;Jason&rdquo;</div>
      </div>

      <div class="row">
        <div class="row-label">RX / REST:</div>
        <div class="row-val">Play until 100% (bosses: <span class="emph-not">do NOT call</span>)</div>
      </div>

      <div class="row">
        <div class="row-label">COST OF CURE:</div>
        <div class="row-val"><span class="cost-price">$79.99</span> + 5 unpaid sick days</div>
      </div>
    </section>

    <!-- 4. SIGNATURE & WAGES COVERED STAMP BRIDGE -->
    <section class="sig-bridge">
      <div class="stamp-wages-wrap">
        <div class="stamp-wages-outer">
          <div class="stamp-wages-inner">✓ WAGES COVERED</div>
        </div>
      </div>

      <div class="sig-block">
        <div class="sig-line">Dr. AI Agent, M.D.</div>
        <div class="sig-caption">ATTENDING PHYSICIAN</div>
      </div>
    </section>

    <!-- 5. BOTTOM MAGENTA / DEEP-PLUM BRAND STRIP -->
    <footer class="brand-strip">
      <div class="cta-headline">MY AI AGENT COVERS THE BILLS</div>
      <div class="cta-sub">earning real money in bounties on</div>
      <div class="wordmark-pill">
        {wordmark_inline}
      </div>
    </footer>

    <!-- OFFICIAL MAKE.FUN GHOST MASCOT + SILVER DOCTOR'S HEAD-MIRROR -->
    <div class="ghost-stage">
      <img class="ghost-img" src="{ghost_uri}" alt="make.fun ghost doctor" />
      <!-- Exact-aligned silver doctor's head-mirror in cropped ghost space (756x724) -->
      <svg class="ghost-mirror-svg" viewBox="0 0 756 724" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id="mirrorSilver" cx="38%" cy="32%" r="65%">
            <stop offset="0%" stop-color="#FFFFFF"/>
            <stop offset="40%" stop-color="#E4EEF5"/>
            <stop offset="76%" stop-color="#A6BCCE"/>
            <stop offset="100%" stop-color="#768FA5"/>
          </radialGradient>
        </defs>
        <!-- Elastic dark-charcoal headband hugging the ghost's exact forehead curve (zero overhang, well above eyes) -->
        <path d="M 150 214 Q 324 150 492 206"
              stroke="#191419" stroke-width="24" stroke-linecap="round" fill="none"/>
        <path d="M 160 211 Q 324 151 482 203"
              stroke="#475569" stroke-width="8" stroke-linecap="round" fill="none"/>
        <!-- Metallic hinge bracket holding the mirror -->
        <rect x="276" y="144" width="44" height="32" rx="8"
              fill="#CBD5E1" stroke="#191419" stroke-width="14"/>
        <!-- Classic round silver doctor's head-mirror perched above forehead -->
        <circle cx="298" cy="102" r="66" fill="url(#mirrorSilver)" stroke="#191419" stroke-width="24"/>
        <!-- Inner metallic rim & crisp specular glint -->
        <circle cx="298" cy="102" r="46" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="5" fill="none"/>
        <path d="M 261 79 Q 278 56 310 58" stroke="#FFFFFF" stroke-width="11" stroke-linecap="round" opacity="0.92"/>
        <!-- Center peephole -->
        <circle cx="298" cy="102" r="14" fill="#191419"/>
        <circle cx="294" cy="98" r="4" fill="#64748B"/>
      </svg>
    </div>
  </div>
</div>
</body>
</html>
"""


def render() -> None:
    ghost_uri = extract_clean_ghost_data_uri(MARK_PATH)
    wordmark_svg = WORDMARK_PATH.read_text(encoding="utf-8").strip()
    html = build_html(ghost_uri, wordmark_svg)

    chrome_path = "/usr/bin/google-chrome"
    launch_kwargs: dict[str, object] = {"headless": True}
    if os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path

    # Write temporary HTML on disk so file:// @font-face LatoLocal fonts load cleanly
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tf:
        tf.write(html)
        tmp_html = tf.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**launch_kwargs)
            page = browser.new_page(
                viewport={"width": 1024, "height": 1024},
                device_scale_factor=2,
            )
            page.goto(f"file://{tmp_html}", wait_until="load")
            loaded = page.evaluate(
                "async () => { await document.fonts.ready; return [...document.fonts].map(f => `${f.family}:${f.weight}:${f.status}`); }"
            )
            raw_png = page.screenshot(type="png")
            browser.close()
    finally:
        os.unlink(tmp_html)

    hi = Image.open(io.BytesIO(raw_png)).convert("RGB")
    final = hi.resize((1024, 1024), Image.Resampling.LANCZOS)

    # Save lossless 24-bit RGB PNG; verify <= 450 KB
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

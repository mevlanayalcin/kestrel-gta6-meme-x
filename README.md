# Leonida General Hospital — GTA 6 × make.fun X Meme

Deterministic source repository for the `gta6-meme-x-01` submission: **Leonida General Hospital — Official Launch-Week Medical Excuse**.

## Files

- `meme.png` — Final `1024×1024` lossless 24-bit PNG meme (`<= 450 KB`).
- `tools/render_meme.py` — Deterministic renderer producing `meme.png` from official make.fun brand assets (`tools/mark-1024.png`, `tools/wordmark.svg`).
- `POST.json` — Submitted X post URL (populated once published).
- `main.ts` — Copies `POST.json` into `${MAKEFUN_OUTPUT_DIR ?? "/output"}/POST.json`.
- `.makefun/owner.json` — Make.fun payout wallet manifest.
- `LICENSE` — MIT License (`SPDX-License-Identifier: MIT`).

## Reproduce

```bash
python3 tools/render_meme.py
```

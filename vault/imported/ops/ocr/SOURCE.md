# Source

- Upstream: https://github.com/ledin-pro/ocr
- Ref: `396fae9b284e5f111c8cec8d66719c26753e6e62` (release 0.7.0)
- Path: `skills/ocr`
- Retrieved: 2026-10-03T13:56:32Z
- License: MIT (Copyright 2026 mxl; repo LICENSE)
- Notes: Skill package is docs-only (`SKILL.md` + `references/`). Executable engine is PyPI `pro-ledin-ocr` (optional extras: pdf, pytesseract, easyocr, paddle, all). PaddleOCR is optional, not required. Do not vendor `src/pro` into the vault. Benchmark helper `scripts/ocr-profile-benchmark.py` stays upstream/PyPI-side, not in this skill tree.

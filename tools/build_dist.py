#!/usr/bin/env python3
"""Assemble dist/: the deployable static bundle with only what the page loads.

Usage: python tools/build_dist.py
Deploy the resulting dist/ folder (Vercel drag & drop or any static host).
Re-run after editing content or replacing audio in assets/audio/.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

DIRS = ["styles", "scripts"]
SCAN = ["index.html", "content.js"]
ASSET_RE = re.compile(
    r"""["'(]((?:assets|styles|scripts)/[\w./-]+\.(?:js|css|mp3|wav|ogg|m4a|png|jpe?g|gif|svg|webp))["')]"""
)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def referenced() -> set[str]:
    """Every local asset the page asks for, found by scanning html/js/css."""
    found: set[str] = set()
    sources = [ROOT / r for r in SCAN]
    sources += [p for d in DIRS for p in (ROOT / d).rglob("*") if p.is_file()]
    for src in sources:
        found.update(ASSET_RE.findall(src.read_text(encoding="utf-8")))
    return found


def main() -> None:
    files = set(SCAN) | referenced()
    missing = sorted(r for r in files if not (ROOT / r).is_file())
    if missing:
        sys.exit("referenced but missing:\n  " + "\n  ".join(missing))

    if DIST.exists():
        shutil.rmtree(DIST)
    copied = 0
    for r in sorted(files):
        (DIST / r).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / r, DIST / r)
        copied += 1

    # every non-html, non-data reference must resolve inside dist/
    unresolved = sorted(r for r in referenced() if not (DIST / r).is_file())
    if unresolved:
        sys.exit("not in dist:\n  " + "\n  ".join(unresolved))
    size = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file())
    print(f"dist/: {copied} files, {size / 1024:.0f} KB")
    for r in sorted(files):
        print("  " + r)


if __name__ == "__main__":
    main()

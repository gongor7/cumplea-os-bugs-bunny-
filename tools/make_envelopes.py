#!/usr/bin/env python3
"""Compute volume envelopes for mouth-sync and write assets/audio/envelopes.js.

50 ms RMS windows, normalized to 0..1, per final audio file. The page reads
window.AUDIO_ENVELOPES[name][windowIndex] while an <audio> element plays.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio"
FFMPEG_CANDIDATES = [
    Path(r"C:\Users\LEANDRO\AppData\Local\Microsoft\WinGet\Packages"
         r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
         r"\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"),
]
FFMPEG = next((str(p) for p in FFMPEG_CANDIDATES if p.exists()), "ffmpeg")

TARGETS = ["bugs-talk", "bugs-song", "bugs-song-alt", "drama-theme"]
WIN = 0.05  # seconds


def envelope(path: Path) -> list[float]:
    r = subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True,
    )
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"decode failed: {path}")
    import numpy as np
    x = np.frombuffer(r.stdout, dtype="<f4")
    n = int(WIN * 16000)
    m = len(x) // n
    if m == 0:
        return [0.0]
    rms = np.sqrt((x[: m * n].reshape(m, n) ** 2).mean(axis=1))
    top = rms.max() or 1.0
    env = (rms / top).tolist()
    env = [min(1.0, e * 1.9) for e in env]  # lift cartoon voice dynamics
    return [round(e, 3) for e in env]


def main() -> None:
    out = {}
    meta = {}
    for name in TARGETS:
        p = AUDIO / f"{name}.mp3"
        if not p.exists():
            print(f"skip {name} (missing)", file=sys.stderr)
            continue
        env = envelope(p)
        out[name] = env
        meta[name] = {"seconds": round(len(env) * WIN, 2), "windows": len(env)}
    js = "window.AUDIO_ENVELOPES = " + json.dumps(out, separators=(",", ":")) + ";\n"
    (AUDIO / "envelopes.js").write_text(js, encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()

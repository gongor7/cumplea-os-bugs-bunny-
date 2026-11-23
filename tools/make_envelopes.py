#!/usr/bin/env python3
"""Write assets/audio/envelopes.js: volume envelopes + timeline marks.

50 ms RMS windows, normalized to 0..1, per final audio file. The page reads
window.AUDIO_ENVELOPES[name][windowIndex] while an <audio> element plays.
Re-run after replacing any tracked mp3 to keep the mouth sync exact.
"""
from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "assets" / "audio"
BUILD = Path(__file__).resolve().parent / "build"
TARGETS = ["bugs-talk", "bugs-song", "drama-theme"]
WIN = 0.05  # seconds
SR = 16000


def ffmpeg() -> str:
    pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                           "Packages", "Gyan.FFmpeg*", "ffmpeg-*", "bin", "ffmpeg.exe")
    hits = sorted(glob.glob(pattern))
    return hits[-1] if hits else "ffmpeg"


def envelope(path: Path) -> list[float]:
    r = subprocess.run(
        [ffmpeg(), "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if r.returncode != 0 or not r.stdout:
        raise SystemExit(f"decode failed: {path}")
    x = np.frombuffer(r.stdout, dtype="<f4")
    n = int(WIN * SR)
    m = len(x) // n
    if m == 0 or np.sqrt((x ** 2).mean()) < 0.005:
        raise SystemExit(f"{path.name} looks silent")
    rms = np.sqrt((x[: m * n].reshape(m, n) ** 2).mean(axis=1))
    env = np.minimum(1.0, rms / (rms.max() or 1.0) * 1.9)  # lift cartoon dynamics
    return [round(float(e), 3) for e in env]


def main() -> None:
    out, meta = {}, {}
    for name in TARGETS:
        p = AUDIO / f"{name}.mp3"
        if not p.exists():
            raise SystemExit(f"missing {p}")
        env = envelope(p)
        out[name] = env
        meta[name] = {"seconds": round(len(env) * WIN, 2), "windows": len(env)}

    marks_path = BUILD / "marks.json"
    marks = json.loads(marks_path.read_text(encoding="utf-8")) if marks_path.exists() else {}
    js = ("window.AUDIO_ENVELOPES = " + json.dumps(out, separators=(",", ":")) + ";\n"
          "window.AUDIO_MARKS = " + json.dumps(marks, separators=(",", ":")) + ";\n")
    (AUDIO / "envelopes.js").write_text(js, encoding="utf-8")
    print(json.dumps({"envelopes": meta, "marks": marks}, indent=2))


if __name__ == "__main__":
    main()

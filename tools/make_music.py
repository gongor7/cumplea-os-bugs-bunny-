#!/usr/bin/env python3
"""Synthesize instrumental tracks and SFX for the Paola birthday landing.

Outputs WAV files into tools/build/ and a timings.json with the exact second
where each sung line of Happy Birthday starts (consumed by make_voice.py).

Pure numpy + stdlib. No copyrighted material: 'Happy Birthday' is public
domain; the drama theme is an original composition in K-drama OST style.
"""
from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

import numpy as np

SR = 44100
BUILD = Path(__file__).resolve().parent / "build"
BUILD.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# low-level synth helpers
# ---------------------------------------------------------------------------

def _write_wav(path: Path, data: np.ndarray, sr: int = SR) -> None:
    peak = np.max(np.abs(data)) or 1.0
    data = data / peak * 0.92
    pcm = (data * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def _adsr(n: int, a=0.015, d=0.06, s=0.75, r=0.08) -> np.ndarray:
    """Simple ADSR envelope of n samples."""
    t = np.linspace(0.0, n / SR, n, endpoint=False)
    env = np.full_like(t, s)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na, nd, nr = min(na, n), min(nd, max(n - na, 0)), min(nr, n)
    if na:
        env[:na] *= np.linspace(0, 1, na)
    if nd:
        env[na:na + nd] *= np.linspace(1, s, nd)
    if nr:
        env[-nr:] *= np.linspace(1, 0, nr)
    return env


def _lowpass(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    rc = 1.0 / (2 * math.pi * cutoff_hz)
    dt = 1.0 / SR
    alpha = dt / (rc + dt)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def _place(buf: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    j = min(i + len(x), len(buf))
    if i < len(buf):
        buf[i:j] += x[: j - i] * gain


def cartoon_voice(freq: float, dur: float, vib: float = 0.004) -> np.ndarray:
    """Muted-trumpet-ish lead: saw+triangle blend, vibrato, lowpassed."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1.0 + vib * np.sin(2 * math.pi * 5.6 * t + np.random.rand() * 6.28))
    phase = 2 * math.pi * np.cumsum(f) / SR
    saw = 2.0 * (phase / (2 * math.pi) % 1.0) - 1.0
    tri = 2 / math.pi * np.arcsin(np.sin(phase))
    tone = 0.62 * saw + 0.55 * tri
    tone = _lowpass(tone, min(freq * 9, 5200))
    return tone * _adsr(n, a=0.02, d=0.09, s=0.8, r=0.09)


def bass_note(freq: float, dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * math.pi * freq * t) + 0.35 * np.sin(4 * math.pi * freq * t)
    return tone * _adsr(n, a=0.008, d=0.12, s=0.62, r=0.1)


def brush_hit(dur: float = 0.09, gain: float = 0.16) -> np.ndarray:
    n = int(dur * SR)
    noise = np.random.randn(n)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((freqs - 6500) / 3800) ** 2)
    x = np.fft.irfft(spec, n)
    return x * np.exp(-np.arange(n) / (0.028 * SR)) * gain


def piano_note(freq: float, dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = (
        np.sin(2 * math.pi * freq * t)
        + 0.45 * np.sin(4 * math.pi * freq * t)
        + 0.18 * np.sin(6 * math.pi * freq * t)
    )
    decay = np.exp(-t / (0.9 + 90.0 / freq))
    attack = np.minimum(t / 0.006, 1.0)
    return tone * decay * attack


def pad_chord(freqs: list[float], dur: float) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (0.996, 1.004):
            out += np.sin(2 * math.pi * f * det * t + np.random.rand() * 6.28)
    out /= max(len(freqs), 1) * 2.5
    out = _lowpass(out, 2200)
    env = np.minimum(t / 0.6, 1.0) * np.minimum((dur - t) / 0.8, 1.0).clip(0, 1)
    return out * env


def noise_fx(dur: float, f_lo: float, f_hi: float, decay: float, gain: float = 0.8,
             sweep_to: float | None = None) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = np.random.randn(n)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    if sweep_to is not None:  # falling band (whoosh)
        k = np.linspace(1.0, sweep_to, len(spec))
        spec *= np.exp(-((freqs - 3000 * k) / (1800 * k + 300)) ** 2)
    else:
        spec *= np.exp(-((freqs - (f_lo + f_hi) / 2) / (f_hi - f_lo)) ** 2)
    x = np.fft.irfft(spec, n)
    return x * np.exp(-t / (decay * SR)) * gain


N = {  # note frequencies
    "F3": 174.61, "G3": 196.00, "A3": 220.00, "B3": 246.94, "C4": 261.63, "D4": 293.66,
    "E4": 329.63, "F4": 349.23, "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99,
}

# ---------------------------------------------------------------------------
# Happy Birthday — cartoon jazz arrangement (public-domain melody)
# ---------------------------------------------------------------------------

BPM = 108
BEAT = 60.0 / BPM
INTRO_BEATS = 3.0

# (note, beats) — classic anacrusis shape
LINES: list[list[tuple[str, float]]] = [
    [("G4", .75), ("G4", .25), ("A4", 1), ("G4", 1), ("C5", 1), ("B4", 2)],
    [("G4", .75), ("G4", .25), ("A4", 1), ("G4", 1), ("D5", 1), ("C5", 2)],
    [("G4", .75), ("G4", .25), ("G5", 1), ("E5", 1), ("C5", 1), ("B4", 1), ("A4", 2)],
    [("F5", .75), ("F5", .25), ("E5", 1), ("C5", 1), ("D5", 1), ("C5", 2.5)],
]

def happy_birthday() -> tuple[np.ndarray, list[float]]:
    total_beats = INTRO_BEATS + sum(sum(d for _, d in ln) for ln in LINES) + 3
    buf = np.zeros(int(total_beats * BEAT * SR) + SR)
    line_starts: list[float] = []
    beat_cursor = INTRO_BEATS

    # intro: 3 brush ticks + a soft tonic chord
    for b in range(3):
        _place(buf, brush_hit(0.1, 0.5), b * BEAT)
    _place(buf, pad_chord([N["G3"], N["D4"], N["G4"]], BEAT * 3 * 1.05), 0.0, 0.5)

    for li, line in enumerate(LINES):
        line_starts.append(beat_cursor * BEAT)
        # walking bass: one note per melody note (root movement feel)
        roots = ["G3", "G3", "C4", "G3", "F4", "G3"] if li in (0, 1) else ["G3", "G3", "C4", "A3", "F4", "G3", "D4"]
        bi = 0
        for note, beats in line:
            f = N[note]
            _place(buf, cartoon_voice(f, beats * BEAT * 0.95), beat_cursor * BEAT, 0.62)
            root = N[roots[min(bi, len(roots) - 1)]]
            _place(buf, bass_note(root, min(beats, 1) * BEAT * 0.9), beat_cursor * BEAT, 0.4)
            nb = int(np.ceil(beats))
            for k in range(nb):
                _place(buf, brush_hit(0.08, 0.34), (beat_cursor + k) * BEAT)
            beat_cursor += beats
            bi += 1
        beat_cursor += 1.0  # breath between lines

    # final "ta-da": big chord + cymbal
    t_end = beat_cursor * BEAT
    for f in (N["G3"], N["G4"], N["B4"], N["D5"], N["G5"]):
        _place(buf, cartoon_voice(f, 2.2), t_end, 0.3)
    _place(buf, noise_fx(1.4, 3500, 8500, 0.5, gain=0.26), t_end)  # cymbal swell
    return buf, line_starts


# ---------------------------------------------------------------------------
# Drama theme — original slow ballad loop (K-drama OST feel)
# ---------------------------------------------------------------------------

CHORDS = [  # freqs per bar (4 beats @ 72bpm)
    ["C4", "E4", "G4", "B4"],   # Cmaj7
    ["A3", "C4", "E4", "G4"],   # Am7
    ["F3", "A3", "C4", "E4"],   # Fmaj7
    ["G3", "B3", "D4", "A4"],   # G(add9-ish)
]
MELODY = [  # (note, beats) pentatonic phrases over 8 bars, rests as None
    ("E5", 1), ("D5", 0.5), ("C5", 0.5), ("D5", 2), (None, 1),
    ("C5", 1), ("B4", 0.5), ("A4", 0.5), ("G4", 2), (None, 1),
    ("A4", 1), ("C5", 1), ("D5", 1.5), ("E5", 0.5), (None, 1),
    ("D5", 2), ("B4", 1), ("G4", 1),
    ("E5", 1), ("G5", 1), ("E5", 1.5), ("D5", 0.5), (None, 1),
    ("C5", 1), ("E5", 1), ("D5", 1.5), ("B4", 0.5), (None, 1),
    ("A4", 1), ("C5", 1), ("D5", 2), (None, 1),
    ("G4", 3), (None, 1),
]

def drama_theme() -> np.ndarray:
    beat = 60.0 / 72
    bars = 8
    total = bars * 4 * beat
    buf = np.zeros(int(total * SR))  # exactly one loop; seamless restart
    for bar in range(bars):
        chord = CHORDS[bar % 4]
        freqs = [N[x] for x in chord]
        _place(buf, pad_chord(freqs, 4 * beat * 1.02), bar * 4 * beat, 0.52)
        _place(buf, piano_note(freqs[0], 3.2), bar * 4 * beat, 0.34)
        _place(buf, piano_note(freqs[1], 2.0), bar * 4 * beat + beat, 0.2)
        _place(buf, piano_note(freqs[2], 2.0), bar * 4 * beat + 2 * beat, 0.2)
    t = 0.0
    for note, beats in MELODY:
        if note:
            _place(buf, piano_note(N[note], beats * beat * 1.1), t, 0.4)
        t += beats * beat
    # vinyl air bed + tiny loop-point fade
    air = np.random.randn(len(buf)) * 0.012
    buf += _lowpass(air, 1500)
    fade = int(0.08 * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    return buf


# ---------------------------------------------------------------------------

def main() -> None:
    hb, line_starts = happy_birthday()
    _write_wav(BUILD / "happy_birthday.wav", hb * 0.9)
    total = len(hb) / SR
    timings = {
        "bpm": BPM,
        "beat": BEAT,
        "line_starts": [round(s, 3) for s in line_starts],
        "song_total": round(total, 3),
    }
    (BUILD / "timings.json").write_text(json.dumps(timings, indent=2), encoding="utf-8")

    _write_wav(BUILD / "drama_theme.wav", drama_theme() * 0.8)
    _write_wav(BUILD / "crunch.wav", noise_fx(0.22, 900, 4200, 0.05, 1.0))
    _write_wav(BUILD / "whoosh.wav", noise_fx(0.7, 0, 0, 0.25, 0.7, sweep_to=0.25))
    spark = np.concatenate([
        piano_note(N[x], 0.35) * 0.5 for x in ("C5", "E5", "G5", "C5")
    ])
    _write_wav(BUILD / "sparkle.wav", spark)
    print(json.dumps({**timings, "files": sorted(p.name for p in BUILD.glob("*.wav"))}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate the default Mexican-Spanish Bugs-style voice + final audio mix.

Pipeline: edge-tts (es-MX neural voice) -> ffmpeg cartoon post-processing
(pitch up, slight tempo, highpass, limiter) -> sequenced and mixed over the
synthesized beds from make_music.py.

Also writes tools/build/marks.json (carrot-bite times in the talk track) and
`samples/` previews so a human can listen and compare.

Replacement (official) audio never needs this script: it just overwrites the
outputs in assets/audio/. The pristine defaults stay in assets-default/.
"""
from __future__ import annotations

import asyncio
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path(__file__).resolve().parent / "build"
VOICE_DIR = BUILD / "voice"
AUDIO_OUT = ROOT / "assets" / "audio"
DEFAULTS = AUDIO_OUT / "assets-default"
SAMPLES = ROOT / "samples"


def _tool(name: str) -> str:
    """Prefer the WinGet ffmpeg build (libmp3lame, full filters) over PATH."""
    pattern = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet",
                           "Packages", "Gyan.FFmpeg*", "ffmpeg-*", "bin", f"{name}.exe")
    hits = sorted(glob.glob(pattern))
    return hits[-1] if hits else name


FFMPEG = _tool("ffmpeg")
FFPROBE = _tool("ffprobe")

VOICE_MAIN = "es-MX-JorgeNeural"     # works reliably; classic MX announcer cadence
VOICE_ALT = "es-MX-LarissaNeural"    # best-effort pitched-up comparison sample
PITCH = "+28Hz"
RATE = "+9%"

TALK = [
    ("talk_1", "¿Qué hay de nuevo, viejo? Digo... ¿qué hay de nuevo, Paola?"),
    ("talk_2", "¡Mira nada más! Si es la cumpleañera más famosa de todo el multiverso... ¡Paola!"),
    ("talk_3", "¡Eh, un momento! ¿Todavía sin canción? Pues arreglemos eso... ¡Música, maestro!"),
]

# Talk track timeline: (clip, seconds of silence after it). Each carrot crunch
# marks a bite for the on-screen animation.
TALK_TIMELINE = [
    ("crunch", 0.10),
    ("talk_1", 0.40),
    ("talk_2", 0.35),
    ("crunch", 0.12),
    ("talk_3", 0.25),
]

LYRICS = [
    ("line_1", "Cumpleaños feliz,"),
    ("line_2", "cumpleaños feliz,"),
    ("line_3", "te deseamos, Paola..."),
    ("line_4", "¡cumpleaños feliz!"),
]


async def _say(name: str, text: str, voice: str, pitch: str, rate: str) -> None:
    out = VOICE_DIR / f"{name}.mp3"
    if out.exists() and out.stat().st_size > 2000:  # cached take from a previous run
        print(f"tts {name}: cached")
        return
    com = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await com.save(str(out))
    print(f"tts {name}: {voice} ok")


async def tts_all() -> None:
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [(name, text, VOICE_MAIN, PITCH, RATE) for name, text in TALK + LYRICS]
    # comparison sample with the alternative voice (best-effort)
    jobs.append(("alt_1", TALK[0][1], VOICE_ALT, "+45Hz", "+6%"))
    for name, text, voice, pitch, rate in jobs:  # sequential: service throttles parallels
        for attempt in range(1, 5):
            try:
                await _say(name, text, voice, pitch, rate)
                break
            except Exception as e:  # noqa: BLE001 - retry any TTS transport error
                print(f"tts {name} attempt {attempt} failed: {type(e).__name__}", file=sys.stderr)
                if attempt == 4:
                    if name == "alt_1":
                        print("alt voice unavailable; skipping sample", file=sys.stderr)
                        break
                    raise
                await asyncio.sleep(1.2 * attempt)
        await asyncio.sleep(0.8)  # keep the free endpoint happy between takes


def _run(args: list[str]) -> None:
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"ffmpeg failed: {' '.join(args[:6])}...")


def _duration(path: Path) -> float:
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def cartoonify(src: Path, dst: Path, rate_factor: float = 1.20, net_speed: float = 1.06) -> None:
    """Pitch the TTS take up (Bugs-style) keeping near-original duration."""
    atempo = max(0.5, min(2.0, rate_factor / net_speed))
    _run([
        "-i", str(src),
        "-af", (f"highpass=f=170,asetrate=24000*{rate_factor},aresample=44100,"
                f"atempo={atempo:.4f},acompressor=threshold=0.28:ratio=3:attack=8:release=140,"
                f"alimiter=limit=0.92"),
        "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(dst),
    ])


def build_talk() -> dict:
    """Sequence crunches and lines with real gaps, so voices never overlap."""
    args: list[str] = []
    fc: list[str] = []
    labels: list[str] = []
    marks = {"bites": []}
    t = 0.0
    for i, (clip, pad) in enumerate(TALK_TIMELINE):
        src = VOICE_DIR / ("crunch_c.mp3" if clip == "crunch" else f"{clip}_c.mp3")
        args += ["-i", str(src)]
        fc.append(f"[{i}:a]apad=pad_dur={pad}[p{i}]")
        labels.append(f"[p{i}]")
        if clip == "crunch":
            marks["bites"].append(round(t + 0.02, 3))
        t += _duration(src) + pad
    fc.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1,alimiter=limit=0.92[out]")
    _run([*args, "-filter_complex", ";".join(fc), "-map", "[out]",
          "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k",
          str(VOICE_DIR / "bugs-talk.mp3")])
    marks["duration"] = round(t, 3)
    return marks


def build_song(version: str) -> Path:
    """Mix the vocal lines over the Happy Birthday bed at the melody times."""
    tim = json.loads((BUILD / "timings.json").read_text(encoding="utf-8"))
    starts = tim["line_starts"]
    # version A: flat cartoon pitch. version B: slight melodic contour per line.
    contour = {"a": [1.0, 1.0, 1.0, 1.0], "b": [1.0, 1.02, 1.10, 0.97]}[version]
    outs = []
    for (name, _), extra in zip(LYRICS, contour):
        out = VOICE_DIR / f"{name}_{version}_c.mp3"
        cartoonify(VOICE_DIR / f"{name}.mp3", out, rate_factor=1.20 * extra, net_speed=0.96)
        outs.append(out)

    inputs = ["-i", str(BUILD / "happy_birthday.wav")]
    for p in outs:
        inputs += ["-i", str(p)]
    # Duck the bed (~-7 dB) under each vocal line so the lyrics stay on top.
    ducks = [f"clip((t-{st - 0.05:.3f})/0.08,0,1)*clip(({st + _duration(p) + 0.1:.3f}-t)/0.15,0,1)"
             for st, p in zip(starts, outs)]
    fc = [f"[0:a]volume='0.62*(1-0.55*min(1,{'+'.join(ducks)}))':eval=frame[bed]"]
    labels = ["[bed]"]
    for i, st in enumerate(starts, start=1):
        ms = int(st * 1000)
        fc.append(f"[{i}:a]volume=1.5,adelay={ms}|{ms}[v{i}]")
        labels.append(f"[v{i}]")
    fc.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,"
        f"alimiter=limit=0.93[out]"
    )
    final = VOICE_DIR / f"bugs-song-{version}.mp3"
    _run([*inputs, "-filter_complex", ";".join(fc), "-map", "[out]",
          "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(final)])
    return final


def main() -> None:
    asyncio.run(tts_all())
    for name, _ in TALK:
        cartoonify(VOICE_DIR / f"{name}.mp3", VOICE_DIR / f"{name}_c.mp3")
    _run(["-i", str(BUILD / "crunch.wav"), "-ar", "44100", "-ac", "1",
          "-c:a", "libmp3lame", "-b:a", "160k", str(VOICE_DIR / "crunch_c.mp3")])
    marks = {"talk": build_talk()}
    (BUILD / "marks.json").write_text(json.dumps(marks, indent=2), encoding="utf-8")
    song_a = build_song("a")
    song_b = build_song("b")

    AUDIO_OUT.mkdir(parents=True, exist_ok=True)
    DEFAULTS.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)

    def enc(src: Path, dst: Path) -> None:
        _run(["-i", str(src), "-ar", "44100", "-ac", "1",
              "-c:a", "libmp3lame", "-b:a", "160k", str(dst)])

    pairs = {
        VOICE_DIR / "bugs-talk.mp3": AUDIO_OUT / "bugs-talk.mp3",
        song_a: AUDIO_OUT / "bugs-song.mp3",
        song_b: AUDIO_OUT / "bugs-song-alt.mp3",
        BUILD / "drama_theme.wav": AUDIO_OUT / "drama-theme.mp3",
        BUILD / "crunch.wav": AUDIO_OUT / "crunch.mp3",
        BUILD / "whoosh.wav": AUDIO_OUT / "whoosh.mp3",
        BUILD / "sparkle.wav": AUDIO_OUT / "sparkle.mp3",
    }
    for src, dst in pairs.items():
        enc(src, dst)
        shutil.copy2(dst, DEFAULTS / dst.name)

    # human-listenable previews
    alt_src = VOICE_DIR / "alt_1.mp3"
    if alt_src.exists() and alt_src.stat().st_size > 2000:
        cartoonify(alt_src, SAMPLES / "voz-larissa-opcion.mp3", 1.24, 1.04)
    shutil.copy2(AUDIO_OUT / "bugs-talk.mp3", SAMPLES / "voz-preview-frases.mp3")
    shutil.copy2(AUDIO_OUT / "bugs-song.mp3", SAMPLES / "cancion-preview-A.mp3")
    shutil.copy2(AUDIO_OUT / "bugs-song-alt.mp3", SAMPLES / "cancion-preview-B.mp3")
    print("voice build complete", json.dumps(marks))


if __name__ == "__main__":
    main()

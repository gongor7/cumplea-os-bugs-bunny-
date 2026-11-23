#!/usr/bin/env python3
"""Generate the default Mexican-Spanish Bugs-style voice + final audio mix.

Pipeline: edge-tts (es-MX neural voice) -> ffmpeg cartoon post-processing
(pitch up, slight tempo, highpass, limiter) -> mix over the synthesized bed.

Also produces `samples/` previews so a human can listen and compare.
Re-run after dropping official audio into assets/audio/ is NOT needed:
replaced files simply overwrite the outputs of this script.
"""
from __future__ import annotations

import asyncio
import json
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

FFMPEG_CANDIDATES = [
    Path(r"C:\Users\LEANDRO\AppData\Local\Microsoft\WinGet\Packages"
         r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
         r"\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"),
]
FFMPEG = next((str(p) for p in FFMPEG_CANDIDATES if p.exists()), "ffmpeg")

VOICE_MAIN = "es-MX-JorgeNeural"     # works reliably; classic MX announcer cadence
VOICE_ALT = "es-MX-LarissaNeural"    # pitched-up comparison sample
PITCH = "+28Hz"
RATE = "+9%"

TALK = [
    ("talk_1", "¿Qué hay de nuevo, viejo?"),
    ("talk_2", "¡Mira nada más! Si es la cumpleañera más famosa de todo el multiverso... ¡Paola!"),
    ("talk_3", "¡Eh, un momento! ¿Todavía sin canción? Pues arreglemos eso... ¡Música, maestro!"),
]

LYRICS = [
    ("line_1", "Cumpleaños feliz,"),
    ("line_2", "cumpleaños feliz,"),
    ("line_3", "te deseamos, Paola..."),
    ("line_4", "¡cumpleaños feliz!"),
]


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


async def _say(name: str, text: str, voice: str, pitch: str, rate: str) -> None:
    out = VOICE_DIR / f"{name}.mp3"
    if out.exists() and out.stat().st_size > 2000:  # cached take from a previous run
        print(f"tts {name}: cached")
        return
    com = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await com.save(str(out))
    print(f"tts {name}: {voice} ok")


def _run(args: list[str]) -> None:
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"ffmpeg failed: {' '.join(args[:6])}...")


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


def build_talk() -> None:
    """talk phrases + carrot crunches, in order."""
    for name, _ in TALK:
        cartoonify(VOICE_DIR / f"{name}.mp3", VOICE_DIR / f"{name}_c.mp3")
    _run(["-i", str(BUILD / "crunch.wav"), "-ar", "44100", "-ac", "1",
          "-c:a", "libmp3lame", "-b:a", "160k", str(VOICE_DIR / "crunch_c.mp3")])
    fc = (
        "[0:a][1:a]concat=n=2:v=0:a=1[t1c];"
        "[2:a]adelay=350|350[d1];"
        "[t1c][d1]amix=inputs=2:duration=longest:normalize=0[a1];"
        "[3:a]adelay=400|400[d2];"
        "[a1][d2]amix=inputs=2:duration=longest:normalize=0[a2];"
        "[a2][4:a]concat=n=2:v=0:a=1,alimiter=limit=0.92[out]"
    )
    _run([
        "-i", str(VOICE_DIR / "talk_1_c.mp3"),
        "-i", str(VOICE_DIR / "crunch_c.mp3"),
        "-i", str(VOICE_DIR / "talk_2_c.mp3"),
        "-i", str(VOICE_DIR / "crunch_c.mp3"),
        "-i", str(VOICE_DIR / "talk_3_c.mp3"),
        "-filter_complex", fc, "-map", "[out]",
        "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k",
        str(VOICE_DIR / "bugs-talk.mp3"),
    ])


def build_song(version: str) -> Path:
    """Mix sung lines over the Happy Birthday bed at the exact melody times."""
    tim = json.loads((BUILD / "timings.json").read_text(encoding="utf-8"))
    starts = tim["line_starts"]
    # version A: flat cartoon pitch. version B: melodic contour per line.
    contour = {"a": [1.0, 1.0, 1.0, 1.0], "b": [1.0, 1.02, 1.10, 0.97]}[version]
    outs = []
    for (name, _), extra in zip(LYRICS, contour):
        out = VOICE_DIR / f"{name}_{version}_c.mp3"
        cartoonify(VOICE_DIR / f"{name}.mp3", out, rate_factor=1.20 * extra, net_speed=0.96)
        outs.append(out)

    inputs = ["-i", str(BUILD / "happy_birthday.wav")]
    for p in outs:
        inputs += ["-i", str(p)]
    fc = ["[0:a]volume=0.62,lowpass=f=9000[bed]"]
    labels = ["[bed]"]
    for i, st in enumerate(starts, start=1):
        ms = int(st * 1000)
        fc.append(f"[{i}:a]volume=1.28,adelay={ms}|{ms}[v{i}]")
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
    build_talk()
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
    print("voice build complete")


if __name__ == "__main__":
    main()

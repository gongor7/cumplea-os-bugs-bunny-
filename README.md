# ¿Qué hay de nuevo, Paola? 🥕

A single-page, offline-capable birthday landing for Paola, starring a giant
fan-art Bugs Bunny who sings "Cumpleaños feliz" with a synthesized
Mexican-Spanish cartoon voice, plus K-drama and TVXQ (Cassiopeia) homages.

Private gift — not for commercial use. All trademarks belong to their owners
(Warner Bros. · SM Entertainment); see the credits scene in the page for the
full reference list.

## Run it

No build step, no dependencies at runtime. Either:

- double-click `index.html` (works from `file://`), or
- serve the folder: `python -m http.server 8734` → http://127.0.0.1:8734

Recommended: deploy to Vercel (drag & drop at https://vercel.com/new) — the
`https://` context also enables the microphone candle-blowing. Full steps in
[`REEMPLAZAR.md`](REEMPLAZAR.md) (Spanish).

## Structure

```
index.html            all six scenes + the inline Bugs Bunny SVG
content.js            EDITABLE TEXTS (letter, signature, lyrics, credits) — Spanish UI copy
styles/               base.css (layout/Bugs layer) + scenes.css (per-scene)
scripts/
  audio.js            <audio> pool, sequence playback, envelope mouth-sync
  bugs.js             SVG animator: mouth, blink, ears, carrot bites, idle sway
  confetti.js         canvas confetti (carrots/hearts), reduced-motion aware
  scenes.js           per-scene behavior (song flow, cake mic, letter, finale)
  main.js             scene manager + button wiring
assets/audio/         final mp3s + envelopes.js (50 ms RMS windows for lip sync)
assets/audio/assets-default/  pristine copies of the synthesized defaults
assets/img/           drop-in slot for user-provided images
samples/              human-listenable voice previews
tools/                Python generators (run with .venv)
odd/tasks/            ODD feature document (specs + log)
```

## Regenerate the default audio

`tools/` runs on the project-local venv (`.venv/`, gitignored):

```
.venv/Scripts/python.exe tools/make_music.py      # synth beds + timings.json
.venv/Scripts/python.exe tools/make_voice.py      # edge-tts (es-MX) + ffmpeg mix
.venv/Scripts/python.exe tools/make_envelopes.py  # rewrites envelopes.js
```

Requires `edge-tts` + `numpy` (already installed in `.venv`) and the WinGet
ffmpeg build (path hardcoded at the top of the tools; falls back to PATH).
TTS takes are cached in `tools/build/voice/`; delete a file to regenerate it.
The Microsoft TTS endpoint occasionally rate-limits — the script retries with
backoff and skips the optional alt-voice sample on failure.

Notes: `es-MX-CecilioNeural` was returning empty audio at build time, so the
default voice is `es-MX-JorgeNeural` pitched up. "Happy Birthday" is public
domain; the drama ballad is an original composition.

## Replacing with official audio/images

The site ships with fixed drop-in slots (`bugs-talk.mp3`, `bugs-song.mp3`,
`drama-theme.mp3` in `assets/audio/`; images in `assets/img/`). Overwrite the
file, no code changes. See `REEMPLAZAR.md` for the friendly walkthrough.

## Verification performed

- `ffprobe`: every mp3 present, expected duration, non-silent; envelope window
  counts match audio durations (talk 11.05 s / song 18.5 s / theme 26.65 s).
- Browser (390×844 mobile + 1440×900 desktop): all six scenes screenshotted and
  inspected; console error sweep clean; full flow exercised — start → talk →
  song (mouth opens with teeth/tongue, lightstick ocean lights, lyrics, confetti)
  → drama cards → five candles extinguished by tap → letter opens with
  signature → credits → iris finale "¡Eso es todo, PAOLA!" → replay.
- Mic path requires a secure context (works on the Vercel URL); on `file://`
  it falls back to tap/blow-button with a notice.

Risk: none — static site, no data, no runtime dependencies.

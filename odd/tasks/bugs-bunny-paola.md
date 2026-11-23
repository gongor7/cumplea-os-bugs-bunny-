# Feature: Bugs Bunny birthday landing for Paola

Objective: a single-page, offline-capable birthday landing for Paola (Nov 23) starring a
giant Bugs Bunny who sings happy birthday with a Mexican-Spanish cartoon voice, plus dorama/TVXQ
homages. Branch: `feat/paola-landing`. Delivery: local folder only, `ask-on-risk`. Test runner:
manual browser checks (file:// and local server, 390x844 + 1440x900) + ffprobe asset checks.

## Specs

- S1 (L1): "create in nuevo directorio que se llama bugs bunny en el cual haremos un mensaje de
  feliz cumpleaños para una amiga que se llama Paola" — landing lives in the `bugs bunny` folder.
- S2 (L1): "que salga un bugs bunny súper grande y le cante feliz cumpleaños" + "si puedes saca
  la voz de bugs bunny en Español latino" — giant Bugs sings; default voice is synthesized
  Mexican-Spanish in Bugs style. Official Warner audio cannot be extracted by the agent.
- S3 (L1): "le gustan los doramas tvxq [...] ponle algo de ese dorama" — dorama-style scene with
  Korean/Spanish subtitles, Cassiopeia references, parody titles.
- S4 (L2): "la fecha de sus cumpleaños es el 23 de noviembre osea hoy" — page frames today as
  the day; no countdown.
- S5 (L2): "lo firmo con leandro (maldito)" — letter signature string, editable in content.js.
- S6 (L2): "si es necesario realiza la referencia de donde sacamos las imagenes o voces o
  canciones pero usa las originales" — credits scene cites Warner Bros., Mexican dub actors and
  TVXQ/SM with official links. Agent does not download copyrighted media; user-provided files
  drop into fixed slots (REEMPLAZAR.md).
- S7 (L3): "te voy a pasar los audios mas tarde ponlo por defecto uno y mas tarde lo cambiamos" —
  site ships with default synth audio; replacing = dropping files, no code changes.
- S8: offline, no CDNs, works from double-click (file://), no build step, reduced-motion safe.

## Tasks

| ID | Spec | Route | Status | Evidence |
|----|------|-------|--------|----------|
| T0 | S1 | inline | done | repo + folders + this doc, commit `chore: scaffold` |
| T1 | S2,S7 | inline | todo | tools/make_voice.py, make_music.py, make_envelopes.py; audio in assets/audio + samples |
| T2 | S2 | inline | todo | inline SVG in index.html, scripts/bugs.js |
| T3 | S2,S4 | inline | todo | scenes 1-2, confetti, lightstick ocean |
| T4 | S3 | inline | todo | dorama scene + drama-theme |
| T5 | S4,S5 | inline | todo | cake blow-out (mic + tap fallback), letter |
| T6 | S6 | inline | todo | credits + references + iris-out "¡Eso es todo, Paola!" |
| T7 | S7,S8 | inline | todo | REEMPLAZAR.md, README, full verification |

## Log

- L1 (2026-11-23, verbatim): "Ok create in nuevo directorio que se llama bugs bunny en el cual
  haremos un mensaje de feliz cumpleaños para una amiga que se llama Paola A ella le gusta mucho
  bugs, otras cosillas que le gustan son los doramas tvxq quiero hacer como una landing pero que
  salga un bugs bunny súper grande y le cante felíz cumpleaños si puedes saca la voz de bugs
  bunny en Español latino y ponle algo de ese dorama arma un plan y si tienes o consideras que
  algo más puede ir avísame"
- L2 (2026-11-23, verbatim): "lo que necesitas es lo firmo con leandro (maldito ) la fecha de sus
  cumpleaños es el 23 de noviembre osea hoy , no se cual sea su miembro favvorito y hazlo lo mas
  parecido posible porque osea no sera para compartirlo solo sera para ella y si es necesario
  raliza la referencia de donde sacamos las imagens o voces o canciones pero usa las originales
  porfavor ya te volvio a pasar?"
- L3 (2026-11-23, verbatim): "las voces deben ser de bugs bunny la oficial de mexico igual quiero
  cancioenes o imagenes de tvxq" → decision: agent cannot fetch copyrighted media; drop-in slots
  for user-provided official audio/images instead.
- L4 (2026-11-23, verbatim): "ok te voy a pasar los audios mas tarde ponlo por defecto uno y mas
  tarde lo cambiamos ok ?" → plan approved with this contract.

# Feature: Bugs Bunny birthday landing for Paola

Objective: a single-page, offline-capable birthday landing for Paola (Nov 23) starring a
giant Bugs Bunny who sings happy birthday with a Mexican-Spanish cartoon voice, plus dorama/TVXQ
homages. Branch: `feat/paola-landing`. Delivery: local folder only, `ask-on-risk`. Test runner:
manual browser checks (file:// and local server, 390x844 + 1440x900) + ffprobe asset checks.

## Specs

- S1 (L1): "create in nuevo directorio que se llama bugs bunny en el cual haremos un mensaje de
  feliz cumpleaños para una amiga que se llama Paola" — landing lives in the `bugs bunny` folder.
- S2 (L1, L7): "que salga un bugs bunny súper grande y le cante feliz cumpleaños" + "si puedes saca
  la voz de bugs bunny en Español latino" + "ok hay un conejo como diseño que sea parecido a este
  porfavor, arreglalo" — giant Bugs matching classic Looney Tunes line-art design (tall pointed V
  ears with peach-pink inner canal, 3-spike crown tuft, tall oval eyes with curved brow ridges,
  flared tufted white cheek ruff, salmon triangular nose with bridge wrinkles, long sweeping black
  whiskers, and buck-toothed open grin with coral tongue) sings; default voice is synthesized
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
| T1 | S2,S7 | inline | done | assets/audio/*.mp3 + envelopes.js (talk 11.05s, song 18.5s, theme 26.65s), samples/, commit `feat: audio pipeline` |
| T2 | S2 | inline | done | classic Looney Tunes Bugs SVG in index.html + scripts/bugs.js + styles; verified s1/s2 in headless Edge |
| T3 | S2,S4 | inline | done | s1/s2 scenes, confetti, ocean; mouth-sync verified mid-song (opacity/scale updates) |
| T4 | S3 | inline | done | dorama cards with emoji art (umbrella/lock/snow + 🐰), ko/es captions, theme loop |
| T5 | S4,S5 | inline | done | 5 candles tap-extinguish verified; mic+fallback; envelope opens with signature |
| T6 | S6 | inline | done | credits + refs links + iris finale verified in browser |
| T7 | S7,S8 | inline | done | REEMPLAZAR.md + README + dist/ builder + commits; full re-verification below |

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
- L5 (2026-11-23, verbatim): "ten en cuenta que lo subiremos a vercel no ?" → delivery target is
  Vercel; README/REEMPLAZAR include deploy steps; https also unlocks the mic.
- L6 (2026-11-23, verbatim): "ya esta en vercel?" / "ya ?" → nothing was published (publishing
  stays a user decision); used the round to re-verify and fix real defects instead of shipping
  the earlier over-claimed state.
- Fix round 2026-11-23 (before any deploy): talk phrases were mixed overlapping by an adelay
  mistake → rebuilt as a true sequential timeline (16.2 s) with bite marks in envelopes.js;
  song bed now ducks under each vocal line; credits roll starts on scene entry (was burning from
  page load); letter redesigned to expand into a full readable sheet (old slide-up clipped);
  cover kicker/title resized to survive fallback fonts (headless proof: no Impact); Bugs capped
  to min(86dvh,122vw) so the carrot arm is not cut on narrow phones; first-tap audio unlock
  extended to later-playing elements; replay button disabled until the finale; mic stream closed
  on scene exit. Verified via tools/preview.html + headless Edge at exact 390/360/1440 layouts:
  all scenes PASS visually, console clean, numeric overflow probe clean (carousel aside).
- Analysis notes: es-MX-CecilioNeural returned empty audio (service-side), default voice is
  es-MX-JorgeNeural pitched +20%; parallel TTS gets rate-limited → sequential with retry.
  Headless virtual time freezes CSS transitions/animations → harness jumps them to end state.
- L7 (2026-11-23, verbatim): "ok hay un conejo como diseño que sea parecido a este porfavor,
  arreglalo" (with classic Looney Tunes Bugs Bunny reference image) → redrew `#bugs` inline SVG
  in `index.html` and updated `scripts/bugs.js` + `styles/` + `dist/` to match the classic Looney
  Tunes design (bold black ink outlines, tall V-ears with peach inner canal and base pivot, 3-spike
  hair tuft, brow creases, tall oval eyes, tufted white cheek ruff, triangular salmon nose with
  bridge wrinkles, long sweeping whiskers, buck teeth and coral tongue); moved s2 lyrics to top so
  Bugs's singing face is never covered; verified s1 & s2 at 390x844 in headless Edge.
- L8 (2026-11-23, verbatim): "este es el nuevo audio del primer dialogo porfavor cambialo y
  tmabien ve le tiempo y la sincornizacion de los labios" → normalized user-provided audio
  (`WhatsApp_Audio_2026-11-23_at_3.12.20_PM.mpeg`, 5.956 s) to `assets/audio/bugs-talk.mp3`,
  regenerated `assets/audio/envelopes.js` (119 50ms windows, 5.95 s, cleared stale talk bite
  marks), smoothed `driveMouth` in `scripts/scenes.js` and fixed `#teeth` opacity on closed pauses
  in `scripts/bugs.js`; rebuilt `dist/`.
- L9 (2026-11-23, verbatim): "y este es el audio de la cancion ya sabes que de igual forma los
  labios y musica deben estar perfectamente sicronizadas" + L10 (2026-11-23, verbatim): "pusiste
  los audios al reves, el primero es el de la charla y el segundo es la cancion, admeas que la
  musica de fondo del cumpleaños feliz ya no esta sonando" → swapped user audios: installed
  `WhatsApp_Audio_2026-11-23_at_3.06.15_PM.mpeg` (14.263 s) as `bugs-talk.mp3`, and mixed
  `WhatsApp_Audio_2026-11-23_at_3.12.20_PM.mpeg` (5.956 s, delayed +0.40 s) over the
  `happy_birthday.wav` instrumental bed (trimmed to 7.80 s with fade-out) as `bugs-song.mp3`;
  computed `bugs-song` lip-sync envelope from the isolated vocal track so background music never
  triggers mouth movement; updated `content.js` lyric timestamps (`0.45`, `1.95`, `2.80`, `4.90`),
- L11 (2026-11-23, verbatim): "esta bien pero el audio que te pase creo que es muy rapido y no
  va a ritmo de la musiquita, puedes sincronizarlo ? hhacerlo mas lento y que se sincronice?" →
  regenerated Happy Birthday bed at 172 BPM (`happy_birthday_sync.wav`, 11.988 s, line starts at
  `1.047`, `3.488`, `5.930`, `8.721`), slowed vocal track to `0.65x` via `atempo` and aligned
  phrases to beat starts (`1.047` and `8.721`), recomputed `bugs-song` envelope from the aligned
  vocal track (240 windows = 12.00 s), updated `content.js` lyric timestamps, rebuilt `dist/`,
- L12 (2026-11-23, verbatim): "ok ahora puedes poner esto de fondo porfavor osea despues del
  mensaje de bugs bunny puedes ponerlo esto de fondo ? https://youtu.be/_1VK_PeMXP8?si=KDdZNYeT8pPsp0yl"
  → downloaded user-provided TVXQ! 'Love In The Ice' Tokyo Dome LIVE audio (316 s), normalized
  to `assets/audio/drama-theme.mp3` (96 kbps stereo), kept `themeStart()` playing continuously
  from `s3` through `s6` (ducked to 0.12 while mic is active in `s4`), rebuilt `dist/`, and
- L13 (2026-11-23, verbatim): "al final despuès de que abra la carta ya despues de los creditos
  corta la musica de fondo y pone el ultimo audio que dice eso es todo amigos" → normalized
  `WhatsApp_Audio_2026-11-23_at_3.53.34_PM.mpeg` (3.68 s) to `assets/audio/thats-all.mp3`,
  registered `finale` in `scripts/audio.js` + `scripts/main.js` unlock list, and updated
  `showFinale()` in `scripts/scenes.js` to stop `drama-theme.mp3` and play `thats-all.mp3` after
- L14 (2026-11-23, verbatim): "qeu significa candado echado ? XD en vez de eso ponle los zapatos
  bonitos te llevan a lugares bonitos bonitos y algo caracteristico de esa frase" → replaced the
  3rd dorama card (`lock-art`) in `index.html` and `styles/scenes.css` with `.shoes-art` (`👠✨`,
  badge `✦ pasos bonitos ✦`, Korean `예쁜 구두는 예쁜 곳으로 데려다 줘`, Spanish `«Los zapatos
  bonitos te llevan a lugares bonitos.»`); rebuilt `dist/` and deployed to
- L15 (2026-11-23, verbatim): "luego pon una nueva tarjeta que diga: la chica de los tenis de
  monitos" + L16 (2026-11-23, verbatim): "esta bien tenis pero ponle los emojis de monitos" →
  added a new dorama card right after the shoes card in `index.html` and `styles/scenes.css`
  (`.sneakers-art`, `👟🐒🐵`, `✦ tenis de monitos ✦`, Korean `귀여운 운동화의 소녀`, Spanish
  `«La chica de los tenis de monitos.»`); rebuilt `dist/` and deployed to
- L17 (2026-11-23, verbatim): "Y ya sabes: con zapatos bonitos (nuevos tenis de monitos)vas a
  llegar tan lejos como te propongas. Por favor, nunca te olvides de ser feliz, que nunca te falten
  motivos para sonreír ni personas que te celebren como te lo mereces. Te deseo todo lo mejor,
  maldita. Aquí siempre voy a estar celebrando cada paso que des. Te quiere, Leandro (maldito) asi
  y actulizalo" → updated `content.js` (`letter` + `signature`) and added `white-space: pre-line`
  to `.letter .sign` in `styles/scenes.css`; rebuilt `dist/` and deployed to
- L18 (2026-11-23, verbatim): "el texto de la carta no se ve bien osea se ve recortado al menos para
  los dispositovos moviles" → expanded `.mail-scene.open .envelope` height to `min(78dvh, 680px)`
  (`max-height: calc(100dvh - 108px)`), hid `.mail-hint` on open, and tuned mobile font-size/
  line-height/padding in `styles/scenes.css` so the full letter + signature fit cleanly on mobile;
  verified in headless Edge at `390x844`, rebuilt `dist/`, and deployed to
  `paola-birthday-dusky.vercel.app`.

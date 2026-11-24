/* Audio manager: element pool, sequence playback, envelope-driven mouth sync.
   Works from file:// (no fetch): envelopes arrive via a classic script tag. */
(function () {
  "use strict";

  var WINDOW_SEC = 0.05; // envelope resolution, mirrors tools/make_envelopes.py
  var FILES = {
    talk:  "assets/audio/bugs-talk.mp3",
    song:  "assets/audio/bugs-song.mp3",
    theme: "assets/audio/drama-theme.mp3",
    crunch: "assets/audio/crunch.mp3",
    whoosh: "assets/audio/whoosh.mp3",
    sparkle: "assets/audio/sparkle.mp3",
    finale: "assets/audio/thats-all.mp3",
  };
  var ENVELOPE_KEY = { talk: "bugs-talk", song: "bugs-song" };

  var els = {};
  Object.keys(FILES).forEach(function (id) {
    var a = new Audio();
    a.src = FILES[id];
    a.preload = "auto";
    els[id] = a;
  });
  var theme = els.theme;
  theme.loop = true;
  theme.volume = 0.42;

  /* The precomputed data only fits the file it was measured for; a dropped-in
     replacement of another length gets the automatic behavior instead. */
  function fits(id, expectedSeconds) {
    var a = els[id];
    return isFinite(a.duration) && Math.abs(a.duration - expectedSeconds) < 0.3;
  }

  /* level 0..1 while `id` is playing: precomputed envelope when it matches the
     loaded file, otherwise a pseudo-envelope. */
  function level(id) {
    var a = els[id];
    if (!a || a.paused) return 0;
    var env = (window.AUDIO_ENVELOPES || {})[ENVELOPE_KEY[id]];
    if (env && fits(id, env.length * WINDOW_SEC)) {
      var i = Math.floor(a.currentTime / WINDOW_SEC);
      return env[Math.min(i, env.length - 1)] || 0;
    }
    var t = a.currentTime;
    var burst = Math.abs(Math.sin(t * 9.3)) * Math.abs(Math.sin(t * 2.1));
    return burst > 0.35 ? 0.55 + 0.4 * Math.random() : 0.05;
  }

  /* Carrot-bite times (seconds) for the default talk track. */
  function biteMarks(id) {
    var marks = (window.AUDIO_MARKS || {})[ENVELOPE_KEY[id]];
    if (!marks || !fits(id, marks.duration)) return [];
    return marks.bites || [];
  }

  function play(id, volume) {
    var a = els[id];
    a.currentTime = 0;
    a.volume = volume == null ? 1 : volume;
    return a.play();
  }

  function stopAll() {
    Object.keys(els).forEach(function (id) { els[id].pause(); });
  }

  function themeStart() { if (theme.paused) theme.play().catch(function () {}); }
  function themeStop() { if (!theme.paused) theme.pause(); }

  /* Mobile browsers only allow play() outside a user gesture on elements that
     already played inside one, so the first tap plays each one muted briefly. */
  function unlock(ids) {
    (ids || Object.keys(els)).forEach(function (id) {
      var a = els[id];
      a.muted = true;
      var p = a.play();
      var settle = function () {
        setTimeout(function () { a.pause(); a.currentTime = 0; a.muted = false; }, 60);
      };
      if (p && p.then) p.then(settle, function () { a.muted = false; });
      else settle();
    });
  }

  window.AUDIO = {
    play: play,
    level: level,
    biteMarks: biteMarks,
    stopAll: stopAll,
    themeStart: themeStart,
    themeStop: themeStop,
    unlock: unlock,
    els: els,
  };
})();

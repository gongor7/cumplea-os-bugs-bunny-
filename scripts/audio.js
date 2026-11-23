/* Audio manager: sequence playback + envelope-driven mouth sync.
   Works from file:// (no fetch): envelopes arrive via a classic script tag. */
(function () {
  "use strict";

  var ENVELOPS_PER_SEC = 20; // 50 ms windows, mirrors tools/make_envelopes.py
  var FILES = {
    talk:  "assets/audio/bugs-talk.mp3",
    song:  "assets/audio/bugs-song.mp3",
    theme: "assets/audio/drama-theme.mp3",
    crunch: "assets/audio/crunch.mp3",
    whoosh: "assets/audio/whoosh.mp3",
    sparkle: "assets/audio/sparkle.mp3",
  };

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

  function envelope(id) {
    return (window.AUDIO_ENVELOPES || {})[id] || null;
  }

  /* level 0..1 while `id` is playing; pseudo-envelope fallback when the
     precomputed one is missing (e.g. after dropping an official audio in). */
  function level(id) {
    var a = els[id];
    if (!a || a.paused) return 0;
    var env = envelope(id === "song" ? "bugs-song" : id === "talk" ? "bugs-talk" : id);
    if (env) {
      var i = Math.floor(a.currentTime * ENVELOPS_PER_SEC);
      return env[Math.min(i, env.length - 1)] || 0;
    }
    var t = a.currentTime;
    var burst = Math.abs(Math.sin(t * 9.3)) * Math.abs(Math.sin(t * 2.1));
    return burst > 0.35 ? 0.55 + 0.4 * Math.random() : 0.05;
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

  function unlock() { // call inside a user gesture: plays & rewinds silence
    var a = els.crunch;
    a.volume = 0;
    var p = a.play();
    setTimeout(function () { a.pause(); a.currentTime = 0; a.volume = 1; }, 60);
    return p;
  }

  window.AUDIO = {
    play: play,
    level: level,
    stopAll: stopAll,
    themeStart: themeStart,
    themeStop: themeStop,
    unlock: unlock,
    els: els,
  };
})();

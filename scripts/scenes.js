/* Per-scene behavior: song sequence, drama theme, cake, letter, finale. */
(function () {
  "use strict";

  var C = window.CONTENT;
  var HOOKS = {}; // id -> {enter, exit}

  function $(id) { return document.getElementById(id); }

  /* ---------------- S2: talk + song + mouth sync + lightsticks --------- */
  (function buildOcean() {
    var ocean = $("ocean");
    for (var i = 0; i < 26; i++) {
      var s = document.createElement("i");
      s.style.animationDelay = (Math.random() * -3).toFixed(2) + "s";
      s.style.animationDuration = (2.2 + Math.random() * 1.6).toFixed(2) + "s";
      ocean.appendChild(s);
    }
  })();

  var mouthRAF = null;
  var songTimers = [];
  function clearTimers() { songTimers.forEach(clearTimeout); songTimers = []; }

  function driveMouth(id) {
    if (mouthRAF) cancelAnimationFrame(mouthRAF);
    var started = performance.now();
    (function loop() {
      var t = (performance.now() - started) / 1000;
      window.BUGS.setMouth(window.AUDIO.level(id));
      if (id === "talk") { // carrot bites land on the embedded crunches
        if (t > 1.62 && t < 1.7) window.BUGS._b1 || ((window.BUGS._b1 = 1), window.BUGS.bite());
        if (t > 6.45 && t < 6.55) window.BUGS._b2 || ((window.BUGS._b2 = 1), window.BUGS.bite());
      }
      mouthRAF = requestAnimationFrame(loop);
    })();
  }

  function showLyric(i) {
    var ko = $("lyrics-ko"), es = $("lyrics-es");
    var L = C.lyrics[i];
    ko.textContent = L.ko;
    es.textContent = L.es;
    ko.classList.remove("pop"); void ko.offsetWidth; ko.classList.add("pop");
  }

  HOOKS.s2 = {
    enter: function () {
      window.BUGS._b1 = 0; window.BUGS._b2 = 0;
      $("lyrics-es").textContent = "";
      $("lyrics-ko").textContent = "";
      driveMouth("talk");
      window.BUGS.wiggleEars();
      window.AUDIO.play("talk", 1).then(function () {
        var talk = window.AUDIO.els.talk;
        talk.addEventListener("ended", function onTalkEnd() {
          talk.removeEventListener("ended", onTalkEnd);
          cancelAnimationFrame(mouthRAF);
          songTimers.push(setTimeout(startSong, 450));
        });
      }).catch(function () { startSong(); });
    },
    exit: function () {
      clearTimers();
      if (mouthRAF) cancelAnimationFrame(mouthRAF);
      window.BUGS.setMouth(0);
      window.AUDIO.stopAll();
      $("ocean").classList.remove("on");
    },
  };

  function startSong() {
    driveMouth("song");
    $("ocean").classList.add("on");
    C.lyrics.forEach(function (L, i) {
      songTimers.push(setTimeout(function () {
        showLyric(i);
        window.BUGS.wiggleEars();
        window.CONFETTI.burst(innerWidth * (0.2 + 0.15 * i), innerHeight * 0.32);
      }, L.at * 1000));
    });
    var rain = setInterval(function () { window.CONFETTI.rain(); }, 700);
    songTimers.push(rain);
    window.AUDIO.play("song", 1).then(function () {
      var song = window.AUDIO.els.song;
      song.addEventListener("ended", function onEnd() {
        song.removeEventListener("ended", onEnd);
        clearInterval(rain);
        cancelAnimationFrame(mouthRAF);
        window.BUGS.setMouth(0);
        $("lyrics-ko").textContent = "🎉";
        $("lyrics-es").textContent = "¡FELICIDADES, " + C.name.toUpperCase() + "!";
        window.CONFETTI.bigFinale();
        songTimers.push(setTimeout(function () { window.GO("s3"); }, 1900));
      });
    }).catch(function () { window.GO("s3"); });
  }

  /* ---------------- S3: drama ------------------------------------------ */
  HOOKS.s3 = {
    enter: function () { window.AUDIO.themeStart(); },
    exit: function () { window.AUDIO.themeStop(); },
  };

  /* ---------------- S4: cake ------------------------------------------- */
  (function buildCake() {
    var flames = Array.prototype.slice.call(document.querySelectorAll("#candles .candle"));
    var out = 0, total = flames.length, blowProg = 0, micData = null, rafId = null;
    var status = $("blow-status");

    function extinguish(candle) {
      if (candle.dataset.out) return;
      candle.dataset.out = "1";
      candle.querySelector(".flame").classList.add("off");
      window.AUDIO.play("whoosh", 0.55);
      window.CONFETTI.burst(
        (candle.getBoundingClientRect().left + 14), candle.getBoundingClientRect().top);
      out++;
      if (out >= total) allOut();
    }

    function allOut() {
      status.textContent = "✨ ¡Deseo concedido, " + C.name + "! ✨";
      window.AUDIO.play("sparkle", 0.8);
      window.CONFETTI.bigFinale();
      $("mic-btn").classList.add("hidden");
      $("blow-btn").classList.add("hidden");
      setTimeout(function () { $("to-letter").classList.remove("hidden"); }, 900);
    }

    flames.forEach(function (c) {
      c.addEventListener("click", function () { extinguish(c); });
    });

    /* tap-and-hold fallback blower */
    var holdRAF = null;
    function holdStep() {
      blowProg += 0.022;
      updateStatus();
      flames.forEach(function (c) {
        var th = parseFloat(c.dataset.i || 0) + 1;
        if (blowProg >= th * 0.2) extinguish(c);
      });
      if (out < total) holdRAF = requestAnimationFrame(holdStep);
    }
    $("blow-btn").addEventListener("pointerdown", function () {
      holdStep();
    });
    addEventListener("pointerup", function () {
      if (holdRAF) cancelAnimationFrame(holdRAF);
      holdRAF = null;
    });

    function updateStatus() {
      if (micData) {
        status.textContent = "Sopla al micro 🎤 " + "▮".repeat(Math.min(10, Math.round(blowProg * 10)));
      }
    }

    $("mic-btn").addEventListener("click", function () {
      if (micData) return;
      navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        var actx = new (window.AudioContext || window.webkitAudioContext)();
        var src = actx.createMediaStreamSource(stream);
        var an = actx.createAnalyser();
        an.fftSize = 512;
        src.connect(an);
        micData = { an: an, actx: actx, buf: new Uint8Array(an.frequencyBinCount) };
        status.textContent = "Sopla al micro 🎤";
        flames.forEach(function (c, i) { c.dataset.i = i; });
        (function listen() {
          micData.an.getByteFrequencyData(micData.buf);
          var low = 0, n = 14; // first bins ≈ low breath rumble
          for (var i = 2; i < 2 + n; i++) low += micData.buf[i];
          low /= n * 255;
          if (low > 0.16) {
            blowProg += 0.024;
            flames.forEach(function (c) {
              var th = parseFloat(c.dataset.i || 0) + 1;
              if (blowProg >= th * 0.19) extinguish(c);
            });
            updateStatus();
          } else {
            blowProg = Math.max(0, blowProg - 0.004);
          }
          rafId = requestAnimationFrame(listen);
        })();
      }).catch(function () {
        status.textContent = "Sin micro aquí — toca las llamas o mantén \"soplar\" 💨";
        $("mic-btn").classList.add("hidden");
      });
    });
  })();

  /* ---------------- S5: letter ----------------------------------------- */
  (function buildLetter() {
    $("letter-body").textContent = C.letter;
    $("letter-sign").textContent = C.signature;
    var opened = false;
    $("envelope").addEventListener("click", function () {
      if (opened) return;
      opened = true;
      $("mail-scene").classList.add("open");
      window.AUDIO.play("sparkle", 0.7);
      setTimeout(function () { $("to-final").classList.remove("hidden"); }, 1100);
    });
  })();

  /* ---------------- S6: credits + iris --------------------------------- */
  (function buildFinal() {
    var list = $("credits-list");
    C.credits.forEach(function (pair) {
      var dt = document.createElement("dt"); dt.textContent = pair[0];
      var dd = document.createElement("dd"); dd.textContent = pair[1];
      list.appendChild(dt); list.appendChild(dd);
    });
    var refs = $("refs");
    var h = document.createElement("p");
    h.className = "refs-title"; h.textContent = C.refsTitle;
    refs.appendChild(h);
    C.refs.forEach(function (pair) {
      var a = document.createElement("a");
      a.href = pair[1]; a.target = "_blank"; a.rel = "noopener";
      a.textContent = pair[0];
      refs.appendChild(a);
    });

    HOOKS.s6 = {
      enter: function () {
        var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        setTimeout(function () {
          $("s6").classList.add("finale");
          if (!reduced) window.CONFETTI.bigFinale();
          window.AUDIO.play("sparkle", 0.5);
        }, reduced ? 1500 : 13000);
      },
      exit: function () { $("s6").classList.remove("finale"); },
    };
  })();

  window.SCENES = HOOKS;
})();

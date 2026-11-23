/* Per-scene behavior: song sequence, drama theme, cake, letter, finale. */
(function () {
  "use strict";

  var C = window.CONTENT;
  var HOOKS = {}; // scene id -> { enter, exit }

  function $(id) { return document.getElementById(id); }
  function reducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

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
  var cancels = []; // tear-down for everything the song scene schedules

  function schedule(fn, ms) {
    var id = setTimeout(fn, ms);
    cancels.push(function () { clearTimeout(id); });
  }
  function every(fn, ms) {
    var id = setInterval(fn, ms);
    cancels.push(function () { clearInterval(id); });
  }
  function clearTimers() {
    cancels.forEach(function (cancel) { cancel(); });
    cancels = [];
  }

  function driveMouth(id) {
    stopMouth();
    var bites = window.AUDIO.biteMarks(id);
    var bit = [];
    (function loop() {
      window.BUGS.setMouth(window.AUDIO.level(id));
      var t = window.AUDIO.els[id].currentTime;
      for (var i = 0; i < bites.length; i++) {
        if (!bit[i] && t >= bites[i]) { bit[i] = true; window.BUGS.bite(); }
      }
      mouthRAF = requestAnimationFrame(loop);
    })();
  }
  function stopMouth() {
    if (mouthRAF) cancelAnimationFrame(mouthRAF);
    mouthRAF = null;
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
      $("lyrics-es").textContent = "";
      $("lyrics-ko").textContent = "";
      driveMouth("talk");
      window.BUGS.wiggleEars();
      window.AUDIO.play("talk").then(function () {
        var talk = window.AUDIO.els.talk;
        talk.addEventListener("ended", function onTalkEnd() {
          talk.removeEventListener("ended", onTalkEnd);
          stopMouth();
          window.BUGS.setMouth(0);
          schedule(startSong, 450);
        });
      }).catch(function () { schedule(startSong, 600); });
    },
    exit: function () {
      clearTimers();
      stopMouth();
      window.BUGS.setMouth(0);
      window.AUDIO.stopAll();
      $("ocean").classList.remove("on");
      $("s2").removeEventListener("click", tapToSing);
    },
  };

  function startSong() {
    if (document.body.dataset.scene !== "s2") return;
    window.AUDIO.play("song").then(function () {
      driveMouth("song");
      $("ocean").classList.add("on");
      C.lyrics.forEach(function (L, i) {
        schedule(function () {
          showLyric(i);
          window.BUGS.wiggleEars();
          window.CONFETTI.burst(innerWidth * (0.2 + 0.15 * i), innerHeight * 0.32);
        }, L.at * 1000);
      });
      every(function () { window.CONFETTI.rain(); }, 700);
      var song = window.AUDIO.els.song;
      song.addEventListener("ended", function onEnd() {
        song.removeEventListener("ended", onEnd);
        finishSong();
      });
    }, function () {
      // Playback was refused (no gesture reached this element): offer a tap.
      $("lyrics-ko").textContent = "🎶";
      $("lyrics-es").textContent = "Toca para cantar";
      $("s2").addEventListener("click", tapToSing);
    });
  }

  function tapToSing() {
    if (document.body.dataset.scene !== "s2") return;
    $("s2").removeEventListener("click", tapToSing);
    startSong();
  }

  function finishSong() {
    clearTimers();
    stopMouth();
    window.BUGS.setMouth(0);
    $("lyrics-ko").textContent = "🎉";
    $("lyrics-es").textContent = "¡FELICIDADES, " + C.name.toUpperCase() + "!";
    window.CONFETTI.bigFinale();
    schedule(function () { window.GO("s3"); }, 1900);
  }

  /* ---------------- S3: drama ------------------------------------------ */
  HOOKS.s3 = {
    enter: function () { window.AUDIO.themeStart(); },
    exit: function () { window.AUDIO.themeStop(); },
  };
  // Theme autoplay may be refused on some phones: any tap retries it.
  $("s3").addEventListener("pointerdown", function () { window.AUDIO.themeStart(); });

  /* ---------------- S4: cake ------------------------------------------- */
  (function buildCake() {
    var candles = Array.prototype.slice.call(document.querySelectorAll("#candles .candle"));
    var total = candles.length;
    var out = 0, blowProg = 0, mic = null, holdRAF = null;
    var status = $("blow-status");

    candles.forEach(function (c, i) { c.dataset.i = i; });

    function stopMic() {
      if (!mic) return;
      cancelAnimationFrame(mic.raf);
      mic.stream.getTracks().forEach(function (t) { t.stop(); });
      mic.actx.close();
      mic = null;
    }

    function micUnavailable() {
      status.textContent = "Sin micro aquí: toca las llamas o mantén \"soplar\" 💨";
      $("mic-btn").classList.add("hidden");
    }

    function extinguish(candle) {
      if (candle.dataset.out) return;
      candle.dataset.out = "1";
      candle.querySelector(".flame").classList.add("off");
      window.AUDIO.play("whoosh", 0.55);
      var r = candle.getBoundingClientRect();
      window.CONFETTI.burst(r.left + r.width / 2, r.top);
      out++;
      if (out >= total) allOut();
    }

    function allOut() {
      stopMic();
      status.textContent = "✨ ¡Deseo concedido, " + C.name + "! ✨";
      window.AUDIO.play("sparkle", 0.8);
      window.CONFETTI.bigFinale();
      $("mic-btn").classList.add("hidden");
      $("blow-btn").classList.add("hidden");
      setTimeout(function () { $("to-letter").classList.remove("hidden"); }, 900);
    }

    candles.forEach(function (c) {
      c.addEventListener("click", function () { extinguish(c); });
    });

    /* Press-and-hold "soplar": each fifth of the hold puts out one more candle. */
    function holdStep() {
      blowProg = Math.min(1.05, blowProg + 0.022);
      candles.forEach(function (c) {
        if (blowProg >= (Number(c.dataset.i) + 1) * 0.2) extinguish(c);
      });
      if (out < total) holdRAF = requestAnimationFrame(holdStep);
    }
    $("blow-btn").addEventListener("pointerdown", function () {
      if (out >= total || holdRAF) return;
      holdRAF = requestAnimationFrame(holdStep);
    });
    function endHold() {
      if (holdRAF) cancelAnimationFrame(holdRAF);
      holdRAF = null;
    }
    addEventListener("pointerup", endHold);
    addEventListener("pointercancel", endHold);

    function updateStatus() {
      status.textContent = "Sopla al micro 🎤 " + "▮".repeat(Math.min(10, Math.round(blowProg * 10)));
    }

    $("mic-btn").addEventListener("click", function () {
      if (mic) return;
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        micUnavailable();
        return;
      }
      navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        var actx = new AudioCtx();
        var an = actx.createAnalyser();
        an.fftSize = 512;
        actx.createMediaStreamSource(stream).connect(an);
        actx.resume();
        mic = { stream: stream, actx: actx, an: an, buf: new Uint8Array(an.frequencyBinCount), raf: 0 };
        status.textContent = "Sopla al micro 🎤";
        (function listen() {
          mic.an.getByteFrequencyData(mic.buf);
          var low = 0;
          for (var i = 2; i < 16; i++) low += mic.buf[i]; // low breath rumble bins
          low /= 14 * 255;
          if (low > 0.16) {
            blowProg = Math.min(1.05, blowProg + 0.024);
            candles.forEach(function (c) {
              if (blowProg >= (Number(c.dataset.i) + 1) * 0.19) extinguish(c);
            });
            updateStatus();
          } else {
            blowProg = Math.max(0, blowProg - 0.004);
          }
          if (mic) mic.raf = requestAnimationFrame(listen);
        })();
      }).catch(micUnavailable);
    });

    HOOKS.s4 = { exit: stopMic };
  })();

  /* ---------------- S5: letter ----------------------------------------- */
  (function buildLetter() {
    $("letter-body").textContent = C.letter;
    $("letter-sign").textContent = C.signature;
    $("envelope").addEventListener("click", function () {
      if ($("mail-scene").classList.contains("open")) return;
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

    function showFinale() {
      $("s6").classList.add("finale");
      $("replay").disabled = false;
      if (!reducedMotion()) window.CONFETTI.bigFinale();
      window.AUDIO.play("sparkle", 0.5);
    }

    HOOKS.s6 = {
      enter: function () { setTimeout(showFinale, reducedMotion() ? 1500 : 13000); },
      exit: function () {
        $("s6").classList.remove("finale");
        $("replay").disabled = true;
      },
    };
  })();

  window.SCENES = HOOKS;
})();

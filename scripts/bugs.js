/* Bugs animator: mouth sync, blink, ear wiggle, carrot bites, idle sway. */
(function () {
  "use strict";

  var svg = document.getElementById("bugs");
  var root = document.getElementById("bugs-root");
  var earL = document.getElementById("ear-left");
  var earR = document.getElementById("ear-right");
  var mouthOpen = document.getElementById("mouth-open");
  var mouthSmile = document.getElementById("mouth-smile");
  var teeth = document.getElementById("teeth");
  var teethRest = document.getElementById("teeth-rest");
  var pupils = document.getElementById("pupils");
  var carrotArm = document.getElementById("carrot-arm");

  /* place ears/arms: transform-attribute driven (file:// safe, no CSS vars) */
  earL.setAttribute("transform", "translate(318,208) rotate(-14)");
  earR.setAttribute("transform", "translate(582,208) rotate(14)");

  var state = { mouth: 0, blink: 0, bite: 0, look: { x: 0, y: 0 }, sway: 0 };
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setMouth(o) {
    state.mouth = Math.max(0, Math.min(1, o));
    var open = state.mouth;
    mouthOpen.setAttribute("opacity", open > 0.1 ? "1" : "0");
    mouthOpen.setAttribute("transform", "scale(1," + (0.25 + 0.75 * open).toFixed(3) + ")");
    var closed = open > 0.1 ? "0" : "1";
    mouthSmile.setAttribute("opacity", closed);
    teethRest.setAttribute("opacity", closed);
    var ty = -64 + open * 8;
    teeth.setAttribute("transform", "translate(0," + ty.toFixed(1) + ")");
  }

  function blinkNow() {
    state.blink = 1;
    var lids = svg.querySelectorAll(".eyelid");
    lids.forEach(function (l) {
      l.style.transition = "none";
      l.style.transformOrigin = "center top";
      l.style.transformBox = "fill-box";
      l.style.transform = "scaleY(1)";
      requestAnimationFrame(function () {
        l.style.transition = "transform 140ms ease";
        l.style.transform = "scaleY(0)";
      });
    });
  }

  function bite() { // carrot to mouth + chew
    state.bite = 1;
    carrotArm.style.transition = "transform 160ms cubic-bezier(.6,-0.3,.7,1.6)";
    carrotArm.style.transformOrigin = "700px 600px";
    carrotArm.style.transformBox = "view-box";
    carrotArm.style.transform = "rotate(30deg)";
    setTimeout(function () {
      carrotArm.style.transition = "transform 420ms ease";
      carrotArm.style.transform = "rotate(0deg)";
      state.bite = 0;
    }, 240);
  }

  function wiggleEars() {
    [earL, earR].forEach(function (ear, i) {
      var base = ear.getAttribute("transform");
      var m = base.match(/translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)/);
      if (!m) return;
      var rot = parseFloat(m[3]);
      var dir = i === 0 ? 1 : -1;
      ear.style.transition = "none";
      ear.setAttribute("transform", "translate(" + m[1] + "," + m[2] + ") rotate(" + (rot + 16 * dir) + ")");
      requestAnimationFrame(function () {
        ear.style.transition = "transform 380ms ease";
        ear.setAttribute("transform", "translate(" + m[1] + "," + m[2] + ") rotate(" + rot + ")");
      });
    });
  }

  function lookAt(nx, ny) { // -1..1
    state.look.x = nx * 9;
    state.look.y = ny * 6;
    pupils.setAttribute("transform", "translate(" + state.look.x + "," + state.look.y + ")");
  }

  /* main loop: idle sway + blink cadence */
  var t0 = performance.now();
  var lastBlink = 0;
  function frame(now) {
    var t = (now - t0) / 1000;
    if (!reduced) {
      state.sway = Math.sin(t * 1.15) * 1.4;
      var breathe = 1 + Math.sin(t * 2.1) * 0.006;
      root.setAttribute("transform",
        "rotate(" + state.sway.toFixed(2) + " 450 900) scale(1," + breathe.toFixed(4) + ")");
    }
    if (t - lastBlink > 2.6 + Math.random() * 2.4) {
      lastBlink = t;
      blinkNow();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  window.BUGS = {
    setMouth: setMouth,
    bite: bite,
    wiggleEars: wiggleEars,
    lookAt: lookAt,
    blink: blinkNow,
    reduced: reduced,
  };
})();

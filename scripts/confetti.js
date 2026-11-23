/* Confetti canvas: carrots, hearts and pearl-red sparkle. */
(function () {
  "use strict";

  var canvas = document.getElementById("confetti");
  var ctx = canvas.getContext("2d");
  var parts = [];
  var running = false;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function resize() {
    canvas.width = innerWidth * devicePixelRatio;
    canvas.height = innerHeight * devicePixelRatio;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  }
  addEventListener("resize", resize);
  resize();

  var COLORS = ["#f2803b", "#ff2d3f", "#f6e7cb", "#3f9d4e", "#ffd76e"];

  function spawn(burst, x, y) {
    var n = burst ? 26 : 8;
    if (reduced) n = Math.ceil(n / 4);
    for (var i = 0; i < n; i++) {
      parts.push({
        x: x == null ? Math.random() * innerWidth : x + (Math.random() - 0.5) * 60,
        y: y == null ? -20 : y,
        vx: (Math.random() - 0.5) * (burst ? 7 : 1.6),
        vy: burst ? -(2 + Math.random() * 6) : (1 + Math.random() * 1.6),
        g: 0.12 + Math.random() * 0.08,
        rot: Math.random() * Math.PI * 2,
        vr: (Math.random() - 0.5) * 0.25,
        size: 7 + Math.random() * 9,
        kind: Math.random() < 0.42 ? "carrot" : Math.random() < 0.6 ? "heart" : "dot",
        color: COLORS[(Math.random() * COLORS.length) | 0],
        life: 0,
        maxLife: 220 + Math.random() * 120,
      });
    }
    if (!running) { running = true; requestAnimationFrame(tick); }
  }

  function drawCarrot(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rot);
    ctx.fillStyle = "#f2803b";
    ctx.beginPath();
    ctx.moveTo(-p.size * 0.28, -p.size * 0.5);
    ctx.lineTo(p.size * 0.28, -p.size * 0.5);
    ctx.lineTo(0, p.size * 0.62);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = "#3f9d4e";
    ctx.fillRect(-p.size * 0.3, -p.size * 0.66, p.size * 0.18, p.size * 0.2);
    ctx.fillRect(p.size * 0.1, -p.size * 0.66, p.size * 0.18, p.size * 0.2);
    ctx.restore();
  }

  function drawHeart(p) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rot);
    ctx.fillStyle = p.color;
    var s = p.size / 2;
    ctx.beginPath();
    ctx.moveTo(0, s * 0.9);
    ctx.bezierCurveTo(-s * 1.3, -s * 0.1, -s * 0.55, -s * 1.05, 0, -s * 0.35);
    ctx.bezierCurveTo(s * 0.55, -s * 1.05, s * 1.3, -s * 0.1, 0, s * 0.9);
    ctx.fill();
    ctx.restore();
  }

  function tick() {
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (var i = parts.length - 1; i >= 0; i--) {
      var p = parts[i];
      p.life++;
      p.vy += p.g;
      p.x += p.vx + Math.sin((p.life + p.size) * 0.05) * 0.6;
      p.y += p.vy;
      p.rot += p.vr;
      if (p.y > innerHeight + 30 || p.life > p.maxLife) { parts.splice(i, 1); continue; }
      if (p.kind === "carrot") drawCarrot(p);
      else if (p.kind === "heart") drawHeart(p);
      else {
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 0.22, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    if (parts.length) requestAnimationFrame(tick);
    else { running = false; ctx.clearRect(0, 0, innerWidth, innerHeight); }
  }

  window.CONFETTI = {
    burst: function (x, y) { spawn(true, x, y); },
    rain: function () { spawn(false); },
    bigFinale: function () {
      for (var k = 0; k < 5; k++) {
        setTimeout(function () { spawn(true, innerWidth * Math.random(), innerHeight * 0.7); }, k * 220);
      }
    },
  };
})();

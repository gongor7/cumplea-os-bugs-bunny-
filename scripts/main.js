/* Scene manager + button wiring. */
(function () {
  "use strict";

  var current = null;

  function goTo(id) {
    var next = document.getElementById(id);
    if (!next || next === current) return;
    if (current && window.SCENES[current.id] && window.SCENES[current.id].exit) {
      window.SCENES[current.id].exit();
    }
    if (current) current.removeAttribute("data-active");
    current = next;
    document.body.dataset.scene = id;
    next.setAttribute("data-active", "");
    if (window.SCENES[id] && window.SCENES[id].enter) window.SCENES[id].enter();
  }
  window.GO = goTo;

  /* S1: start (any gesture unlocks audio playback) */
  function startShow() {
    window.AUDIO.unlock();
    goTo("s2");
  }
  document.getElementById("start-btn").addEventListener("click", startShow);
  document.getElementById("s1").addEventListener("click", startShow);

  document.getElementById("skip-song").addEventListener("click", function () { goTo("s3"); });
  document.getElementById("to-cake").addEventListener("click", function () { goTo("s4"); });
  document.getElementById("to-letter").addEventListener("click", function () { goTo("s5"); });
  document.getElementById("to-final").addEventListener("click", function () { goTo("s6"); });
  document.getElementById("replay").addEventListener("click", function () { location.reload(); });

  /* personalize from content.js */
  document.getElementById("s1-kicker").textContent = window.CONTENT.kicker;

  /* keep keyboard users moving too */
  addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    var order = ["s1", "s2", "s3", "s4", "s5", "s6"];
    var btn = current.querySelector("button:not(.hidden)");
    if (btn && btn !== document.getElementById("start-btn")) btn.click();
    else if (!current || current.id === "s1") startShow();
  });
})();

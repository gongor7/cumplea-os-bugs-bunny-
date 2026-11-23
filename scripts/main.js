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

  /* S1: the first tap also primes the audio for everything that plays later.
     The start button lives inside s1, so its click bubbles here. */
  function startShow() {
    if (document.body.dataset.scene !== "s1") return;
    window.AUDIO.unlock(["song", "theme", "crunch", "whoosh", "sparkle"]);
    goTo("s2");
  }
  document.getElementById("s1").addEventListener("click", startShow);

  document.getElementById("skip-song").addEventListener("click", function () { goTo("s3"); });
  document.getElementById("to-cake").addEventListener("click", function () { goTo("s4"); });
  document.getElementById("to-letter").addEventListener("click", function () { goTo("s5"); });
  document.getElementById("to-final").addEventListener("click", function () { goTo("s6"); });
  document.getElementById("replay").addEventListener("click", function () { location.reload(); });

  /* personalize from content.js */
  document.getElementById("s1-kicker").textContent = window.CONTENT.kicker;

  /* Enter/Space starts the show from the cover when no control has focus */
  addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " ") return;
    if (!current || current.id !== "s1" || e.target !== document.body) return;
    e.preventDefault();
    startShow();
  });

  current = document.getElementById("s1");
  document.body.dataset.scene = "s1";
})();

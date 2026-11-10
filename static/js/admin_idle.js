// RakshakAlert - admin auto-logout after 5 idle minutes.
// Every click or keypress on an admin page resets the timer.
// Countdown shows in the header, red in the last minute.
// At zero the admin is sent to logout. Server enforces the same
// 5 minute limit on every admin request.
(function () {
  var el = document.getElementById("admin-countdown");
  if (!el) return;
  var IDLE_SECONDS = 300;
  var left = IDLE_SECONDS;
  var lastPing = 0;
  function fmt(s) {
    var m = Math.floor(s / 60);
    var sec = s % 60;
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }
  function render() {
    el.textContent = fmt(left);
    el.classList.toggle("warning", left <= 60);
  }
  function reset() {
    left = IDLE_SECONDS;
    render();
    var now = Date.now();
    if (now - lastPing > 30000) {
      lastPing = now;
      fetch("/admin/ping", { method: "POST" }).catch(function () {});
    }
  }
  ["click", "keydown", "mousemove"].forEach(function (ev) {
    document.addEventListener(ev, reset, { passive: true });
  });
  render();
  setInterval(function () {
    left -= 1;
    if (left <= 0) {
      window.location.href = "/admin/logout";
      return;
    }
    render();
  }, 1000);
})();

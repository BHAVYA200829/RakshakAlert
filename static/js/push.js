// RakshakAlert - push notifications (simulated without VAPID keys).
// The button asks for notification permission and saves a subscription
// on the server. Real Web Push needs VAPID keys; without them the
// subscription is stored as a local simulated subscription and the
// server logs SIMULATED_PUSH on broadcast. No personal data is stored.
(function () {
  var btn = document.getElementById("push-btn");
  var statusEl = document.getElementById("push-status");
  if (!btn) return;
  function setStatus(text) { if (statusEl) statusEl.textContent = text; }
  if (!("Notification" in window)) {
    setStatus("Alerts off: notifications are not supported in this browser.");
    btn.disabled = true;
    return;
  }
  if (Notification.permission === "granted") setStatus("Alerts enabled on this device.");
  else setStatus("Alerts off. Tap Enable alerts to get alerts on this device.");
  btn.addEventListener("click", function () {
    Notification.requestPermission().then(function (perm) {
      if (perm !== "granted") {
        setStatus("Alerts off: notification permission was not given.");
        return;
      }
      var endpoint = "local-" + Math.random().toString(36).slice(2) + "-" + Date.now();
      fetch("/api/push/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint: endpoint, keys: { p256dh: "", auth: "" } })
      })
        .then(function (r) { return r.json(); })
        .then(function () {
          localStorage.setItem("rakshakalert_push_endpoint", endpoint);
          setStatus("Alerts enabled on this device. (Simulated push in this demo.)");
        })
        .catch(function () { setStatus("Could not save the subscription. Check your connection."); });
    });
  });
})();

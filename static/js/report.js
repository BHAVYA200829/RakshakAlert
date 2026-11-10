// RakshakAlert Phase 2 - report GPS pick + offline queue.
// Offline queue: if the report cannot be sent (offline or fetch fails),
// it is saved in localStorage and retried when the browser goes online.
// Photos cannot be queued offline (a file cannot be stored in
// localStorage) - if a photo is attached, offline submit is blocked
// with a clear message instead of silently dropping the photo.
const OFFLINE_KEY = "rakshakalert_offline_reports";

function loadQueue() {
  try { return JSON.parse(localStorage.getItem(OFFLINE_KEY) || "[]"); }
  catch (e) { return []; }
}
function saveQueue(q) {
  localStorage.setItem(OFFLINE_KEY, JSON.stringify(q));
}

async function flushQueue() {
  const q = loadQueue();
  if (!q.length) return;
  const remaining = [];
  for (const item of q) {
    try {
      const r = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });
      if (!r.ok) remaining.push(item);
      else {
        const data = await r.json();
        alert("Offline report sent. Tracking ID: " + data.tracking_id);
      }
    } catch (e) { remaining.push(item); }
  }
  saveQueue(remaining);
}

window.addEventListener("online", flushQueue);

document.getElementById("report-gps").addEventListener("click", () => {
  const note = document.getElementById("gps-note");
  if (!navigator.geolocation) {
    note.textContent = "Your browser does not support location. Pick your city from the list instead.";
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      document.getElementById("lat").value = pos.coords.latitude;
      document.getElementById("lng").value = pos.coords.longitude;
      fetch(`/api/nearest?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}`)
        .then((r) => r.json())
        .then((t) => {
          const sel = document.getElementById("tower_id");
          sel.value = String(t.id);
          note.textContent = `Nearest tower: ${t.name}, ${t.city} (${t.distance_km} km away). It has been selected above.`;
        });
    },
    () => { note.textContent = "Location permission was denied. Pick your city from the list instead."; },
    { timeout: 10000 }
  );
});

document.getElementById("report-form").addEventListener("submit", (ev) => {
  // Only intercept when offline: save the report (without photo) and
  // stop the normal submit so the user gets a clear offline message.
  if (navigator.onLine) return;
  const photo = document.getElementById("photo");
  if (photo && photo.files && photo.files.length) {
    ev.preventDefault();
    const box = document.getElementById("offline-note");
    box.textContent = "You are offline and a photo is attached. Photos cannot be sent offline - remove the photo to save this report offline, or wait until you are back online.";
    box.style.display = "block";
    return;
  }
  ev.preventDefault();
  const item = {
    disaster_type: document.getElementById("disaster_type").value,
    tower_id: Number(document.getElementById("tower_id").value),
    description: document.getElementById("description").value,
    name: document.getElementById("name").value || null,
    phone: document.getElementById("phone").value || null,
    lat: document.getElementById("lat").value ? Number(document.getElementById("lat").value) : null,
    lng: document.getElementById("lng").value ? Number(document.getElementById("lng").value) : null,
  };
  const q = loadQueue();
  q.push(item);
  saveQueue(q);
  const box = document.getElementById("offline-note");
  box.textContent = "Saved offline - you are not online right now. This report will send automatically when you are back online.";
  box.style.display = "block";
});

// On load, retry any queued reports if we are online.
if (navigator.onLine) flushQueue();

// ---------- Voice input for "What do you see?" ----------
// Browser Web Speech API only - no server, no API key, no audio upload.
// Click Speak to start listening, click again to stop. The transcript
// is appended to the description box. Works in Chrome and Edge;
// other browsers get a clear message instead of a broken button.
(function () {
  const btn = document.getElementById("voice-btn");
  const label = document.getElementById("voice-btn-label");
  const statusEl = document.getElementById("voice-status");
  const langSel = document.getElementById("voice-lang");
  const box = document.getElementById("description");
  if (!btn || !box) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    btn.disabled = true;
    if (statusEl) statusEl.textContent = "Voice input is not supported in this browser, please type instead.";
    return;
  }

  let rec = null;
  let listening = false;
  let startText = "";
  let spoken = "";

  function setState(on) {
    listening = on;
    btn.classList.toggle("voice-listening", on);
    if (label) label.textContent = on ? "Stop" : "Speak";
    if (statusEl) statusEl.textContent = on ? "Listening... tap Stop when done." : "";
  }

  btn.addEventListener("click", () => {
    if (listening && rec) { rec.stop(); return; }
    rec = new SpeechRecognition();
    rec.lang = (langSel && langSel.value) || "en-IN";
    rec.interimResults = true;
    rec.continuous = true;
    startText = box.value.trim();
    spoken = "";

    rec.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) spoken += transcript + " ";
        else interim += transcript;
      }
      box.value = [startText, spoken.trim(), interim.trim()].filter(Boolean).join(" ");
    };
    rec.onerror = (event) => {
      setState(false);
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        if (statusEl) statusEl.textContent = "Microphone permission was denied. Allow the microphone or type instead.";
      } else if (event.error === "no-speech") {
        if (statusEl) statusEl.textContent = "No speech heard. Try again or type instead.";
      } else {
        if (statusEl) statusEl.textContent = "Voice input stopped. Please type instead.";
      }
    };
    rec.onend = () => { setState(false); };
    try {
      rec.start();
      setState(true);
    } catch (e) {
      setState(false);
      if (statusEl) statusEl.textContent = "Voice input could not start. Please type instead.";
    }
  });
})();

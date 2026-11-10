// RakshakAlert Phase 2 - SOS + SAFE/HELP on the public home.
// No login. SOS posts location + nearest tower; SAFE/HELP posts a
// check-in for one alert. Counts are refreshed from the server.
async function postJSON(url, data) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!r.ok) throw new Error("Request failed: " + r.status);
  return r.json();
}

function nearestTowerId() {
  return Number(localStorage.getItem("rakshakalert_nearest_tower") || 0) || null;
}

document.addEventListener("click", async (ev) => {
  const sosBtn = ev.target.closest("#sos-btn");
  if (sosBtn) {
    const msg = document.getElementById("sos-msg");
    msg.textContent = "Sending SOS…";
    try {
      const data = await new Promise((resolve, reject) => {
        if (!navigator.geolocation) return resolve({ tower_id: nearestTowerId() });
        navigator.geolocation.getCurrentPosition(
          (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
          () => resolve({ tower_id: nearestTowerId() }),
          { timeout: 8000 }
        );
      });
      if (!data.tower_id && data.lat == null) {
        msg.textContent = "SOS needs a tower. Use 'Use my location' above first, or pick your city on the map.";
        return;
      }
      await postJSON("/api/sos", data);
      msg.textContent = "SOS received. Help is on the way - stay where you are if it is safe. The admin can see your tower now.";
    } catch (e) {
      msg.textContent = "SOS could not be sent. Check your connection and try again.";
    }
    return;
  }
  const ciBtn = ev.target.closest("[data-checkin]");
  if (ciBtn) {
    const kind = ciBtn.getAttribute("data-checkin");
    const alertId = Number(ciBtn.getAttribute("data-alert-id"));
    const towerId = Number(ciBtn.getAttribute("data-tower-id") || 0) || null;
    try {
      const data = await postJSON("/api/checkin", { alert_id: alertId, tower_id: towerId, kind });
      const safeEl = document.getElementById(`safe-count-${alertId}`);
      const helpEl = document.getElementById(`help-count-${alertId}`);
      if (safeEl) safeEl.textContent = data.counts.SAFE || 0;
      if (helpEl) helpEl.textContent = data.counts.HELP || 0;
      ciBtn.textContent = kind === "SAFE" ? "Marked safe - thank you" : "HELP noted - admin can see this";
      ciBtn.disabled = true;
    } catch (e) {
      alert("Check-in could not be sent. Check your connection and try again.");
    }
  }
});

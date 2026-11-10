// RakshakAlert Phase 1 - public home map + GPS nearest tower.
const SEV_COLOUR = {
  Red: "#dc2626", Orange: "#ea580c", Yellow: "#ca8a04", Green: "#15803d",
};
const NO_ALERT_COLOUR = "#0f2a44";

let map, markers = [], towers = [], towersById = {};
let windLayer = null, windOn = true, windByTower = {};
const COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
function compass(deg) { return COMPASS[Math.round(((deg % 360) + 360) % 360 / 45) % 8]; }
function windText(towerId) {
  const w = windByTower[towerId];
  if (!w || w.dir == null) return "";
  return `Wind ${w.dir}° ${compass(w.dir)} · ${w.speed} km/h`;
}

function initMap() {
  map = L.map("map").setView([22.0, 79.0], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);
  fetch("/api/towers")
    .then((r) => r.json())
    .then((data) => { towers = data; drawMarkers(data); loadWind(); })
    .catch(() => { document.getElementById("map").innerHTML = "<p style='padding:16px'>Could not load towers. Check the server is running.</p>"; });
}

function drawMarkers(list) {
  markers.forEach((m) => map.removeLayer(m));
  markers = [];
  list.forEach((t) => {
    towersById[t.id] = t;
    const colour = t.max_severity ? SEV_COLOUR[t.max_severity] : NO_ALERT_COLOUR;
    const marker = L.circleMarker([t.lat, t.lng], {
      radius: t.max_severity ? 10 : 7,
      color: "#fff", weight: 2, fillColor: colour, fillOpacity: 0.95,
    }).addTo(map);
    const alertText = t.active_alerts.length
      ? t.active_alerts.map((a) => `<strong>${a.severity}:</strong> ${a.title}`).join("<br>")
      : "No active alert on this tower.";
    marker.bindPopup(
      `<strong>${t.name}</strong><br>${t.city}, ${t.state} · ${t.code}<br>` +
      `${t.citizen_count} citizens · 5 km radius<br>${alertText}`
    );
    marker.on("click", () => showTowerDetail(t.id));
    marker._tid = t.id;
    markers.push(marker);
  });
}

function showTowerDetail(id) {
  fetch(`/api/towers/${id}`)
    .then((r) => r.json())
    .then((t) => {
      document.getElementById("tower-detail").style.display = "block";
      document.getElementById("td-name").textContent = `${t.name} - ${t.city}`;
      document.getElementById("td-meta").textContent =
        `${t.state} · ${t.code} · ${t.citizen_count} citizens · 5 km radius · ${t.lat}, ${t.lng}`;
      const alertsEl = document.getElementById("td-alerts");
      alertsEl.innerHTML = t.active_alerts.length
        ? t.active_alerts.map((a) =>
            `<div class="alert-item sev-border-${a.severity}"><h3>${a.title}</h3>` +
            `<div class="meta"><span class="sev sev-${a.severity}">${a.severity}</span> ${a.disaster_type} · ${a.created_at} UTC</div>` +
            `<p>${a.message}</p></div>`).join("")
        : `<p class="empty">No active alert on this tower right now.</p>`;
      document.getElementById("td-citizens").innerHTML = t.citizens
        .map((c) => `<tr><td>${c.name}</td><td>${c.phone}</td></tr>`).join("");
      // Phase 2: live sensor readings for this tower.
      fetch(`/api/sensors?tower_id=${id}`)
        .then((r) => r.json())
        .then((sensors) => {
          const el = document.getElementById("td-sensors");
          if (!el) return;
          el.innerHTML = sensors.map((s) => {
            const val = s.sensor_type === "wind_direction"
              ? `${s.current_value}° ${compass(s.current_value)}`
              : `<strong>${s.current_value} ${s.unit}</strong>`;
            return `<tr><td>${s.sensor_type}</td><td>${val}</td>` +
              `<td>threshold ${s.threshold} ${s.unit}</td>` +
              `<td>${s.status === "warning" ? "<strong>Over threshold</strong>" : "Normal"}</td></tr>`;
          }).join("");
        })
        .catch(() => {});
      document.getElementById("tower-detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
}


// ---- Live wind layer (Phase 2, simulated IoT readings) ----
function drawWindArrows() {
  if (!map || !windLayer) return;
  windLayer.clearLayers();
  if (!windOn) return;
  towers.forEach((t) => {
    const w = windByTower[t.id];
    if (!w || w.dir == null) return;
    const icon = L.divIcon({
      className: "",
      html: `<div class="wind-arrow"><span class="wa-dir" style="transform: rotate(${w.dir - 90}deg)">&#10148;</span><span class="wa-speed">${w.speed}</span></div>`,
      iconSize: [26, 30],
      iconAnchor: [13, 34],
    });
    L.marker([t.lat, t.lng], { icon, interactive: false, keyboard: false }).addTo(windLayer);
  });
  // Add wind to each tower popup.
  markers.forEach((m) => {
    const t = towersById[m._tid];
    if (!t) return;
    const w = windText(t.id);
    const base = `<strong>${t.name}</strong><br>${t.city}, ${t.state} · ${t.code}<br>` +
      `${t.citizen_count} citizens · 5 km radius<br>` +
      (t.active_alerts.length
        ? t.active_alerts.map((a) => `<strong>${a.severity}:</strong> ${a.title}`).join("<br>")
        : "No active alert on this tower.");
    m.setPopupContent(w ? base + `<br>${w}` : base);
  });
}

function applyWindData(rows) {
  windByTower = {};
  rows.forEach((r) => {
    const w = windByTower[r.tower_id] || {};
    if (r.sensor_type === "wind_speed") w.speed = r.current_value;
    if (r.sensor_type === "wind_direction") w.dir = r.current_value;
    windByTower[r.tower_id] = w;
  });
  drawWindArrows();
  const el = document.getElementById("wind-updated");
  if (el) el.textContent = "Wind updated " + new Date().toLocaleTimeString() + " - live sensor readings (simulated, no weather API).";
}

function loadWind() {
  if (!windLayer) windLayer = L.layerGroup().addTo(map);
  fetch("/api/sensors")
    .then((r) => r.json())
    .then((rows) => applyWindData(rows.filter((r) => r.sensor_type.startsWith("wind_"))))
    .catch(() => {
      const el = document.getElementById("wind-updated");
      if (el) el.textContent = "Wind readings unavailable right now.";
    });
}

function refreshWind() {
  fetch("/api/wind/refresh", { method: "POST" })
    .then((r) => r.json())
    .then((rows) => applyWindData(rows))
    .catch(() => loadWind());
}

document.getElementById("wind-toggle").addEventListener("click", () => {
  windOn = !windOn;
  document.getElementById("wind-toggle").textContent = windOn ? "Wind: ON" : "Wind: OFF";
  if (!windLayer) windLayer = L.layerGroup().addTo(map);
  if (windOn) { windLayer.addTo(map); drawWindArrows(); }
  else map.removeLayer(windLayer);
});
setInterval(() => { if (windOn) refreshWind(); }, 30000);

// ---- Live map auto-refresh (Extras): every 60 seconds, re-fetch
// towers and active alerts and update pins, colours, wind and the
// alert list. Map zoom, pan, search and state filter are kept.
function refreshMapData() {
  var q = document.getElementById("tower-search").value.trim().toLowerCase();
  var state = document.getElementById("state-filter").value;
  fetch("/api/towers")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      towers = data;
      var filtered = data.filter(function (t) {
        return (!state || t.state === state) &&
          (!q || (t.city + " " + t.name + " " + t.code).toLowerCase().includes(q));
      });
      drawMarkers(filtered);
      loadWind();
    })
    .catch(function () {});
  fetch("/api/alerts/active")
    .then(function (r) { return r.json(); })
    .then(function (alerts) { updateAlertList(alerts); })
    .catch(function () {});
  var el = document.getElementById("map-updated");
  if (el) el.textContent = "Map updated " + new Date().toLocaleTimeString() + ".";
}
function updateAlertList(alerts) {
  var list = document.getElementById("active-alerts-list");
  if (!list) return;
  var seen = {};
  alerts.forEach(function (a) {
    seen[a.id] = true;
    var existing = list.querySelector('[data-alert-id="' + a.id + '"]');
    if (existing) {
      var h = existing.querySelector("h3");
      if (h) h.textContent = a.title;
      return;
    }
    var div = document.createElement("div");
    div.className = "alert-item sev-border-" + a.severity;
    div.setAttribute("data-alert-id", a.id);
    div.innerHTML = "<h3></h3><div class='meta'><span class='sev sev-" + a.severity + "'>" +
      a.severity + "</span> " + a.disaster_type + " · " + a.created_at + " UTC</div><p></p>" +
      "<p class='meta'>SAFE: <strong id='safe-count-" + a.id + "'>0</strong> · HELP: <strong id='help-count-" +
      a.id + "'>0</strong></p><p><button class='btn btn-sm' type='button' data-checkin='SAFE' data-alert-id='" +
      a.id + "'>I am SAFE</button> <button class='btn btn-sm btn-red' type='button' data-checkin='HELP' data-alert-id='" +
      a.id + "'>I need HELP</button></p>";
    div.querySelector("h3").textContent = a.title;
    div.querySelector("p").textContent = a.message;
    list.appendChild(div);
  });
  list.querySelectorAll("[data-alert-id]").forEach(function (node) {
    if (!seen[node.getAttribute("data-alert-id")]) node.remove();
  });
}
setInterval(refreshMapData, 60000);

function applyFilters() {
  const q = document.getElementById("tower-search").value.trim().toLowerCase();
  const state = document.getElementById("state-filter").value;
  const filtered = towers.filter((t) =>
    (!state || t.state === state) &&
    (!q || (t.city + " " + t.name + " " + t.code).toLowerCase().includes(q))
  );
  drawMarkers(filtered);
  if (filtered.length === 1) {
    map.setView([filtered[0].lat, filtered[0].lng], 9);
    showTowerDetail(filtered[0].id);
  } else if (filtered.length > 1) {
    map.fitBounds(L.latLngBounds(filtered.map((t) => [t.lat, t.lng])).pad(0.15));
  }
}

function useMyLocation() {
  const btn = document.getElementById("gps-btn");
  const result = document.getElementById("gps-result");
  const errBox = document.getElementById("gps-error");
  errBox.style.display = "none";
  if (!navigator.geolocation) {
    errBox.textContent = "Your browser does not support location. Search the map above instead.";
    errBox.style.display = "block";
    return;
  }
  btn.disabled = true;
  btn.textContent = "Finding your location…";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      btn.disabled = false;
      btn.textContent = "Use my location";
      const { latitude, longitude } = pos.coords;
      fetch(`/api/nearest?lat=${latitude}&lng=${longitude}`)
        .then((r) => r.json())
        .then((t) => {
          // Remember it so the admin broadcast page can pre-select it.
          localStorage.setItem("rakshakalert_nearest_tower", String(t.id));
          localStorage.setItem("rakshakalert_nearest_city", t.city);
          result.innerHTML =
            `<div class="gps-card"><h3>Your nearest tower</h3>` +
            `<p><strong>${t.name}</strong><br>${t.city}, ${t.state} · ${t.code}</p>` +
            `<p><strong>${t.distance_km} km</strong> away · ${t.citizen_count} citizens on this tower</p>` +
            (t.active_alerts.length
              ? t.active_alerts.map((a) => `<p><span class="sev sev-${a.severity}">${a.severity}</span> ${a.title}</p>`).join("")
              : `<p>No active alert on your tower right now.</p>`) +
            `<p><a href="/admin/broadcast">Go to Admin Broadcast</a> - this tower will be pre-selected there.</p></div>`;
          map.setView([t.lat, t.lng], 9);
          showTowerDetail(t.id);
        })
        .catch(() => {
          errBox.textContent = "Could not find the nearest tower. The server may be down - try again.";
          errBox.style.display = "block";
        });
    },
    (err) => {
      btn.disabled = false;
      btn.textContent = "Use my location";
      const msg = err.code === 1
        ? "Location permission was denied. Allow location in your browser, or search the map above instead."
        : err.code === 2
          ? "Your location is unavailable right now. Search the map above instead."
          : "Finding your location timed out. Try again, or search the map above.";
      errBox.textContent = msg;
      errBox.style.display = "block";
    },
    { timeout: 10000 }
  );
}

document.getElementById("tower-search").addEventListener("input", applyFilters);
document.getElementById("state-filter").addEventListener("change", applyFilters);
document.getElementById("gps-btn").addEventListener("click", useMyLocation);
initMap();

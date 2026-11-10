// RakshakAlert Phase 1 - admin 3-step broadcast.
let map, markers = {}, towersById = {};
const selected = new Set();

function setPane(n) {
  [1, 2, 3].forEach((i) => {
    document.getElementById(`pane-${i}`).classList.toggle("on", i === n);
    const tab = document.getElementById(`tab-${i}`);
    tab.classList.toggle("on", i === n);
    tab.classList.toggle("done", i < n);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function selectedRows() {
  return [...document.querySelectorAll('#tower-list input[type="checkbox"]')]
    .filter((cb) => cb.checked);
}

function updateSelectedBar() {
  const rows = selectedRows();
  const citizens = rows.length * 8;
  document.getElementById("selected-bar").textContent =
    `${rows.length} tower${rows.length === 1 ? "" : "s"} selected - ${citizens} citizens will be reached`;
  rows.forEach((cb) => cb.closest(".tower-row").classList.add("sel"));
  document.querySelectorAll('#tower-list input[type="checkbox"]:not(:checked)')
    .forEach((cb) => cb.closest(".tower-row").classList.remove("sel"));
  // Keep map pins in sync.
  Object.entries(markers).forEach(([id, m]) => {
    const on = selected.has(Number(id));
    m.setStyle({ fillColor: on ? "#dc2626" : "#0f2a44", radius: on ? 10 : 7 });
  });
}

function toggleTower(id, on) {
  const cb = document.querySelector(`#tower-list input[value="${id}"]`);
  if (!cb) return;
  cb.checked = on;
  if (on) selected.add(id); else selected.delete(id);
  updateSelectedBar();
}

function initMap() {
  map = L.map("map-admin").setView([22.0, 79.0], 5);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);
  fetch("/api/towers")
    .then((r) => r.json())
    .then((data) => {
      data.forEach((t) => {
        towersById[t.id] = t;
        const m = L.circleMarker([t.lat, t.lng], {
          radius: 7, color: "#fff", weight: 2, fillColor: "#0f2a44", fillOpacity: 0.95,
        }).addTo(map);
        m.bindPopup(`<strong>${t.name}</strong><br>${t.city}, ${t.state}<br>8 citizens`);
        m.on("click", () => toggleTower(t.id, !selected.has(t.id)));
        markers[t.id] = m;
      });
      // Pre-select the tower found by "Use my location" on the public map.
      const nearest = localStorage.getItem("rakshakalert_nearest_tower");
      if (nearest && markers[Number(nearest)]) {
        toggleTower(Number(nearest), true);
        const t = towersById[Number(nearest)];
        map.setView([t.lat, t.lng], 8);
      }
    });
}

function applyFilters() {
  const q = document.getElementById("admin-search").value.trim().toLowerCase();
  const state = document.getElementById("admin-state").value;
  document.querySelectorAll("#tower-list .tower-row").forEach((row) => {
    const ok = (!state || row.dataset.state === state) &&
      (!q || row.dataset.city.includes(q));
    row.style.display = ok ? "flex" : "none";
  });
}

function areaName() {
  const cities = selectedRows().map((cb) => {
    const row = cb.closest(".tower-row");
    return row.querySelector(".t-city").textContent;
  });
  return cities.join(", ") || "the selected area";
}

function fillTemplate() {
  const type = document.querySelector('input[name="disaster_type"]:checked');
  if (!type) return;
  document.getElementById("message").value =
    DISASTER_TEMPLATES[type.value].replaceAll("{area}", areaName());
  const sev = DISASTER_SEVERITY[type.value];
  const sevInput = document.querySelector(`input[name="severity"][value="${sev}"]`);
  if (sevInput) sevInput.checked = true;
  if (!document.getElementById("title").value.trim()) {
    document.getElementById("title").value = `${type.value} alert - ${areaName()}`;
  }
}

function buildReview() {
  const rows = selectedRows();
  const cities = rows.map((cb) => cb.closest(".tower-row").querySelector(".t-city").textContent);
  document.getElementById("review-towers").textContent =
    rows.length ? `${rows.length} tower(s): ${cities.join(", ")}` : "None selected";
  document.getElementById("review-citizens").textContent = `${rows.length * 8} citizens`;
  const type = document.querySelector('input[name="disaster_type"]:checked');
  const sev = document.querySelector('input[name="severity"]:checked');
  document.getElementById("review-type").textContent = type ? type.value : "Not chosen";
  document.getElementById("review-severity").textContent = sev ? sev.value : "Not chosen";
  document.getElementById("review-title").textContent =
    document.getElementById("title").value.trim() || "Not entered";
  document.getElementById("review-message").textContent =
    document.getElementById("message").value.replaceAll("{area}", areaName()) || "-";
}

// Step navigation
document.getElementById("to-step-2").addEventListener("click", () => {
  if (!selectedRows().length) { alert("Select at least one tower first."); return; }
  if (!document.querySelector('input[name="disaster_type"]:checked')) fillTemplateFromDefault();
  setPane(2);
});
function fillTemplateFromDefault() {
  const first = document.querySelector('input[name="disaster_type"]');
  if (first) { first.checked = true; fillTemplate(); }
}
document.getElementById("back-to-1").addEventListener("click", () => setPane(1));
document.getElementById("to-step-3").addEventListener("click", () => {
  const type = document.querySelector('input[name="disaster_type"]:checked');
  const sev = document.querySelector('input[name="severity"]:checked');
  const title = document.getElementById("title").value.trim();
  const msg = document.getElementById("message").value.trim();
  if (!type) { alert("Pick a disaster type in Step 2."); return; }
  if (!sev) { alert("Pick a severity level in Step 2."); return; }
  if (!title || !msg) { alert("Title and message are both required."); return; }
  // Fill {area} into the actual message field so the stored text is final.
  document.getElementById("message").value = msg.replaceAll("{area}", areaName());
  buildReview();
  setPane(3);
});
document.getElementById("back-to-2").addEventListener("click", () => setPane(2));

// Disaster type -> auto severity + template
document.querySelectorAll('input[name="disaster_type"]').forEach((r) =>
  r.addEventListener("change", fillTemplate));

// Selection changes
document.querySelectorAll('#tower-list input[type="checkbox"]').forEach((cb) =>
  cb.addEventListener("change", () => {
    if (cb.checked) selected.add(Number(cb.value)); else selected.delete(Number(cb.value));
    updateSelectedBar();
  }));
document.getElementById("clear-selection").addEventListener("click", () => {
  document.querySelectorAll('#tower-list input[type="checkbox"]').forEach((cb) => { cb.checked = false; });
  selected.clear();
  updateSelectedBar();
});
document.getElementById("select-state-btn").addEventListener("click", () => {
  const state = document.getElementById("state-bulk").value;
  if (!state) { alert("Choose a state first."); return; }
  document.querySelectorAll("#tower-list .tower-row").forEach((row) => {
    if (row.dataset.state === state) {
      const cb = row.querySelector('input[type="checkbox"]');
      cb.checked = true; selected.add(Number(cb.value));
    }
  });
  updateSelectedBar();
});
document.getElementById("admin-search").addEventListener("input", applyFilters);
document.getElementById("admin-state").addEventListener("change", applyFilters);

initMap();
updateSelectedBar();

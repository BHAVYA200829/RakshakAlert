# RakshakAlert - Scratch Build, Phase 1 + 2 + 3

Team AlertNova - PCCOE International Grand Challenge 2026.
Prototype video due **Tuesday 10 November 2026**.

**Phase 1:** core broadcast + live map + GPS tower select.
**Phase 2:** citizen report + SOS / SAFE-HELP + simulated-SMS fallback
+ IoT sensor simulator + admin Incident Queue.
**Phase 3:** admin analytics dashboard + CSV export + PWA + multilingual
UI (9 languages, working subset) + full test run.

**Clean demo state:** 60 towers, 480 citizens, 24 states/UTs, and exactly
2 demo active alerts on first load - Flood (Orange) on Mira Road and
Heavy Rainfall (Yellow) on Nashik - each with simulated-SMS deliveries
to that tower's 8 citizens only.
No real SMS, no real email. All SMS is **simulated** and labelled as such.

## What it does

### Phase 1 (kept working)
- **Public home (`/`, no login):** live Leaflet map of India with all 60 tower
  pins, active alerts colour-coded by severity, tower search + state filter,
  click a tower for its detail (city/state, 8 citizens, active alerts, live
  sensor readings). On first load the map already shows 2 active alerts:
  Flood (Orange) on Mira Road and Heavy Rainfall (Yellow) on Nashik.
- **GPS "Use my location":** browser geolocation finds the nearest tower by
  haversine distance, shows distance in km, and pre-selects that tower in
  the admin broadcast flow. Denied permission shows a clear message.
- **Admin login (`/admin`):** session login. Demo credentials: **admin / admin123**
  (change with `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars, see `.env.example`).
- **Admin broadcast (`/admin/broadcast`):** 3 steps - select towers, configure
  alert (8 disaster types - Flood, Earthquake, Cyclone, Landslide, Wildfire,
  Heatwave, Tsunami, Heavy Rainfall - severity auto-suggested Green/Yellow/
  Orange/Red but editable, template message auto-fills per type and is
  editable), review and broadcast. Broadcast writes simulated-SMS delivery
  rows **only** for citizens whose `tower_id` is in the selection.
- **Alert history + delivery log (`/admin/history`):** per alert - towers,
  citizens reached, per-recipient status SIMULATED, time.

### Phase 2 (new)
- **Citizen report (`/report`, no login):** disaster type, photo upload
  (optional, max 5 MB, PNG/JPG/WebP, stored in `uploads/`), location via GPS
  (nearest tower auto-filled) or manual city pick, short description,
  optional name/phone. On submit you get a tracking ID (e.g. `RA-00001`).
  **Track it at `/track`** - status Open → Acknowledged → Resolved.
  **Offline queue:** if you are offline, the report (without photo) is
  saved in the browser's localStorage and sent automatically when you are
  back online, with a clear "saved offline" message. Photos cannot be
  queued offline - the form says so instead of silently dropping them.
- **SOS (`/` home page, no login):** big red SOS button. Sends location +
  nearest tower to the admin instantly; it appears urgent/red at the top
  of the Incident Queue.
- **SAFE / HELP (`/` home page, no login):** on every active alert, citizens
  tap "I am SAFE" or "I need HELP". Admin sees per-tower counts, e.g.
  Mira Road: 6 SAFE, 2 HELP, on the alert and in the queue.
- **Simulated-SMS fallback (`services/sms.py`):** every SMS goes through
  one provider interface. Default provider is SIMULATED - messages are
  logged per recipient as SIMULATED. A MSG91/Twilio-shaped provider stub
  is selected only if `SMS_PROVIDER=msg91|twilio` and the matching API key
  env var is set, and even then it makes **no HTTP call** - it logs
  PROVIDER_STUB so the demo can never pretend a real SMS went out.
  Every broadcast and report-status SMS is written to `sms_log` as well
  as the existing `deliveries` table.
- **IoT sensor simulator (`/admin/sensors`, admin; live readings also on
  the public tower detail):** 360 simulated sensors - 6 per tower × 60
  towers: water level (m, threshold 2.5), rainfall (mm/hr, threshold 50),
  tremor (magnitude, threshold 5.0), temperature (C, threshold 45).
  "Simulate reading" ticks one reading; "Trigger test sensor event"
  forces one sensor over its threshold. Crossing a threshold
  auto-creates an alert for that tower with auto-severity, labelled
  "Auto-triggered by IoT sensor", and logs simulated-SMS deliveries for
  that tower's 8 citizens.
- **Live wind on the map:** a toggleable Wind layer (on by default) shows a
  small navy arrow above each tower pin, rotated to the wind direction
  (0-360 degrees, compass N/NE/E/SE/S/W/SW/W/NW) with wind speed in km/h
  beside it. Clicking a tower shows its wind in the tower detail card too.
  Wind comes from the IoT sensor simulator (wind speed + wind direction
  sensors per tower) and refreshes every 30 seconds with a small random
  drift, plus a LIVE label and last-updated time near the map. No real
  weather API and no API key - simulated live sensor readings only.
- **Admin Incident Queue (`/admin/queue`):** reports grouped by tower +
  disaster type into one card (e.g. "12 reports from Mira Road - Flood"),
  ordered by urgency score then age. Per-report detail, Acknowledge and
  Resolve (single + bulk Acknowledge all / Resolve all per group), SOS
  items urgent/red at the top, SAFE/HELP counts per group. A status change
  updates the citizen's tracking page (and logs a simulated SMS if the
  citizen gave a phone number).

**Urgency score formula:** `urgency = 10 × reports + 25 × SOS + 15 × HELP + severity points − 5 × SAFE` (minimum 0), where severity points are Green 5, Yellow 10, Orange 20, Red 30.

## Design rule

Citizens **never** log in or register. Only the Admin logs in. Citizens get
alerts by SMS to a number already in the database (simulated here), the
public home page, or push. In real life this is Cell Broadcast
(NDMA / DoT SACHET) - no app, no login, no phone number needed.

All tower and citizen data is **sample/demo data** (city-centre coordinates,
fictional citizens, deterministic seed). It is not real telecom data.
Sensor readings are simulated demo data - no real sensors are connected.

## Stack

Flask 3.1 + SQLite (Python stdlib `sqlite3`), plain HTML/CSS/JS, no build
step. Leaflet 1.9.4 + OpenStreetMap tiles via CDN for the map only.
Everything else is local.

## Run

```bash
cd rakshakalert-scratch
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Step 1 - create + seed the database (60 towers, 480 citizens, 360 sensors, 2 demo alerts).
# Do this once. Re-running it wipes alerts/reports and re-seeds from scratch.
.venv/bin/python app.py --init-db
# (or: .venv/bin/flask --app app init-db)

# Step 2 - start the server
.venv/bin/python app.py
# Open http://localhost:5000
```

On Windows (PowerShell):

```powershell
cd rakshakalert-scratch
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py --init-db
.venv\Scripts\python app.py
# Open http://localhost:5000
```

Admin login: **admin / admin123** at http://localhost:5000/admin

Upgrading from Phase 1: just replace the code and restart the server -
`ensure_db()` migrates an existing Phase 1 database (adds the Phase 2
tables and seeds the 360 sensors) without wiping alerts or deliveries.
Only a fresh `--init-db` wipes data.

## Test it

### Phase 1 - Nashik example (still works)
1. Log in as admin, open **Admin Broadcast**.
2. In Step 1, search `Nashik`, tick only the Nashik tower, click **Continue to Step 2**.
3. Pick **Flood** (severity auto-fills Orange, message auto-fills), click **Continue to Step 3**.
4. Check the review: **1 tower, 8 citizens**. Click **Broadcast now**.
5. The delivery log shows exactly **8 rows, all Nashik citizens, status SIMULATED**.

GPS test: on the public home page click **Use my location** near Mira Road -
nearest tower should be **Mira Road Station, 0.00 km** away if you are at
19.2952, 72.8544 (or try `GET /api/nearest?lat=19.2952&lng=72.8544`).

### Phase 2 - citizen report
1. Open `/report` (no login). Pick **Flood**, pick **Mira Road**, write a
   description, optionally attach a photo, click **Send report**.
2. Note the tracking ID, e.g. `RA-00001`. Open `/track?id=RA-00001` - status
   is **Open**.
3. Log in as admin, open **Incident Queue** - a "Mira Road - Flood" group
   appears with 1 report. Click **Acknowledge** - `/track` now shows
   **Acknowledged**. Click **Resolve** - it shows **Resolved**.

### Phase 2 - SOS + SAFE/HELP
1. On the home page click **SOS - I need help now** (allow location, or use
   "Use my location" first). The Incident Queue shows an urgent red SOS
   group for your tower.
2. After an alert exists, tap **I am SAFE** or **I need HELP** on that alert
   on the home page - the SAFE/HELP counts on the alert change, and the
   queue group shows the same counts.

### Phase 2 - IoT sensor test
1. Log in as admin, open **Sensors**.
2. In "Trigger a test sensor event", pick **Mira Road** + **Water level**,
   click **Trigger test sensor event**.
3. An Orange flood auto-alert for Mira Road is created ("Auto-triggered by
   IoT sensor"), with exactly **8 simulated deliveries, all Mira Road**.

### Phase 2 - offline queue
1. Open `/report`, fill it in (no photo), turn off your internet / go offline
   in DevTools, and submit. You see "Saved offline - will send when online".
2. Turn the internet back on. The report is sent automatically and you get
   its tracking ID. (Verified at code level + manual browser steps; the
   server-side `/api/report` endpoint is tested by curl in the test notes.)

## Routes

| Route | Who | What |
|---|---|---|
| `/` | public | Map, GPS, SOS, SAFE/HELP, active alerts, sensor readings |
| `/report` | public | Citizen report form (photo upload, voice input for the description) |
| `/track` | public | Report status by tracking ID |
| `/api/report` | public | JSON report endpoint (offline-queue retry) |
| `/api/sos` | public | SOS signal |
| `/api/checkin` | public | SAFE / HELP check-in |
| `/api/sensors` | public | Live sensor readings |
| `/api/towers`, `/api/nearest`, `/api/alerts/active` | public | Phase 1 APIs |
| `/safety`, `/safety/<type>` | public | Safety Guidance, 8 disaster types, Before/During/After + helplines |
| `/api/push/subscribe` | public | Save a Web Push subscription (201, no personal data) |
| `/api/push/status` | public | Push subscription count |
| `/api/chat` | public | Rule-based help assistant (POST, multilingual, no LLM) |
| `/api/chat/ui` | public | Chatbot UI strings in the current site language |
| `/admin/ping` | admin | Keeps the admin session alive (5-min idle timer) |
| `/lang/<code>` | public | Language switch (en, hi, mr, bn, ta, te, gu, kn, ml) |
| `/manifest.json` | public | PWA manifest |
| `/sw.js` | public | PWA service worker |
| `/admin` | admin | Login / broadcast |
| `/admin/broadcast` | admin | 3-step broadcast |
| `/admin/queue` | admin | Incident Queue (grouped reports + SOS) |
| `/admin/sensors` | admin | IoT sensor simulator + test trigger |
| `/admin/history` | admin | Alert history + delivery log |
| `/admin/analytics` | admin | Analytics dashboard (live DB counts + CSS bars) |
| `/admin/export/<alerts\|reports\|deliveries>` | admin | CSV download of real DB rows |

## Phase 3

- **Analytics dashboard (`/admin/analytics`, admin only, linked from the
  admin nav after login):** live counts computed from the SQLite DB, never
  hardcoded - alerts, reports, SOS signals, simulated-SMS deliveries,
  citizens covered, towers, SAFE and HELP check-ins. Simple CSS bar charts
  (no chart library, so it works offline): alerts by disaster type, alerts
  by severity, reports by status, deliveries by status, alerts by state
  (top 10, table + bars). Bars and tables stack / scroll on mobile.
- **CSV export (admin only):** download buttons on the analytics page -
  alerts CSV, reports CSV, deliveries CSV. Real DB rows, proper CSV
  headers, file name with the date, e.g. `rakshakalert_alerts_2026-11-07.csv`.
  Export routes redirect to login when logged out.
- **PWA:** `static/manifest.json` (name RakshakAlert, start URL `/`,
  display standalone, theme/background navy #0f2a44, icons from
  `static/img/logo.webp`), service worker `static/sw.js` (served at
  `/sw.js`, caches home page + CSS/JS/logo for offline use, serves a
  simple offline page when the network is gone), registered in `base.html`,
  plus an apple-touch-icon link. Installable on mobile from the browser
  menu. Live API calls are never served from cache.
- **Multilingual UI - honest scope:** 9 languages (English, Hindi, Marathi,
  Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam) via a language
  switcher in the top bar (a select, works logged in and out, choice saved
  in a cookie). Translated strings are a working subset only - **28 keys**:
  nav items, hero headline + subtext, SOS / Report / GPS / Active alerts
  headings + subtexts + main buttons, footer tagline / Quick Links /
  Emergency headings, language label. Code: `services/i18n.py`, English
  fallback for anything untranslated. Deeper pages (broadcast, queue,
  sensors, history, analytics, forms, flash messages) stay in English.
  No em dashes in any translated string.

## Final Extras (2026-11-07) - items 4, 5, 6, 7, 8 + footer fix

### 0. Footer white-gap fix (bug fix first)
Short pages (e.g. Track Report) used to show white space after the
footer. Fixed with a sticky-footer layout in `style.css` / `base.html`:
`html { height: 100% }`, `body { min-height: 100vh; display: flex;
flex-direction: column }`, `main.wrap { flex: 1 0 auto }`,
`.site-footer { margin-top: auto }`. The footer now sits at the bottom
of the viewport on short pages and after the content on long pages.
Verified: Track page HTML ends with footer, then scripts, then
`</body></html>`, and the CSS rules above are present.

### 4. Safety Guidance (`/safety`, `/safety/<type>`)
One page per disaster type, all 8: Flood, Earthquake, Cyclone,
Landslide, Wildfire, Heatwave, Tsunami, Heavy Rainfall. Each page has
what to do Before / During / After in short points, plus helpline
112 / NDMA 1078. Linked from the public nav (Safety Guide, after
Track Report, before Admin), the footer Quick Links, and every alert
detail page. Content is in English; the 9-language switcher translates
headings and buttons where keys exist (`services/safety.py`).

### 5. Push notifications (Web Push, simulated without VAPID keys)
- **Enable alerts** button on the public home (no login). Clicking asks
  browser notification permission, registers the service-worker push
  subscription, and saves it via `POST /api/push/subscribe` (stores
  endpoint + keys only, no personal data). Returns 201. A small status
  line on home shows "Alerts enabled" or "Alerts off".
- On admin broadcast, one `SIMULATED_PUSH` row per subscriber is written
  to the `push_log` table (tables `push_subscriptions` / `push_log`,
  added by `ensure_db()` without wiping data).
- The service worker has a `push` event that shows the notification and
  a `notificationclick` handler that opens the site.
- **Honest limit:** without real VAPID keys no real push is sent.
  `.env.example` has `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY`
  placeholders. With keys set, the code still logs SIMULATED_PUSH and
  makes no external HTTP call in this demo.

### 6. Admin auto-logout after 5 idle minutes
Server-side: `login_required` checks `session["last_activity"]` and
clears the session + redirects to login with a message after 300 idle
seconds. Every click/keypress on admin pages calls `POST /admin/ping`
(`static/js/admin_idle.js`) to reset the timer. A countdown shows in
the admin header (`5:00`, red in the last minute) and auto-redirects
to `/admin/login` at zero. The countdown appears **only** on admin
pages, never on public pages.

### 7. Live map auto-refresh (60 seconds)
`static/js/home.js` re-fetches `/api/towers` + `/api/alerts/active`
every 60 seconds (`setInterval(refreshMapData, 60000)`), updating pins,
alert colours, the active-alerts list, wind arrows and the
last-updated time. A red **LIVE** badge and "Map updated ..." time sit
near the map. Map zoom/pan and search/filter are never reset.

### 8. Chatbot / help assistant (rule-based, NO LLM) - multilingual + voice
Floating **Ask RakshakAlert** button bottom-right on every public page;
opens a closable panel (mobile-friendly, navy/red). Keyword matching
against the safety guides + site help: flood/earthquake/cyclone/etc
safety, "how to report", "how to track my report", "is my area safe"
(checks the named city against live active alerts in the DB), SOS,
admin login, helplines. Suggested quick questions as clickable chips.
If it does not understand, it says so clearly and offers the Safety
Guide + helpline 112. No external API, no API key.
- **Multilingual:** the bot answers in the current site language
  (same lang cookie / language switcher, all 9 languages). The
  greeting, quick-question chips, placeholder, fallback message and
  the short summary line of every main answer (helpline, SOS, report,
  track, admin, safety intro, "tell me your city") are translated
  into all 9 languages (`services/chatbot.py`, `T` dict). Full safety
  detail (Before/During/After points) stays in English and is appended
  after the translated summary; the full guide link is always given.
  The widget fetches `/api/chat/ui` when it opens, so a language
  change applies on next open (the language switcher reloads the page
  anyway). `POST /api/chat` also accepts `{"lang": "hi"}`.
- **Voice:** a **Mic** button in the chat panel speaks your question
  using Web Speech API SpeechRecognition, in the current site language
  (en-IN, hi-IN, mr-IN, bn-IN, ta-IN, te-IN, gu-IN, kn-IN, ml-IN),
  with a "Listening..." state (button turns red). If voice input is
  not supported or mic permission is denied, a clear message is shown
  in the current language. Each bot reply has a **Listen** button, and
  a **Sound on/off** toggle in the panel header reads answers aloud
  with SpeechSynthesis in the current language. No server, no API key,
  no audio upload - browser speech only. Voice needs Chrome/Edge and
  microphone permission; other browsers get the clear message above.

### Extras - test it
1. Safety: open `/safety` (200), `/safety/flood`, `/safety/earthquake`,
   `/safety/tsunami` (all 200). Nav has a Safety Guide link.
2. Push: `curl -X POST /api/push/subscribe -d '{"endpoint":"https://example.com/push/test1","keys":{"p256dh":"k","auth":"a"}}'`
   returns 201 and 1 subscription row. Broadcast an alert as admin and
   `push_log` gains one SIMULATED_PUSH row per subscriber.
3. Auto-logout: log in as admin, open `/admin/broadcast` - header shows
   `5:00` and `admin_idle.js` loads. Public home has no countdown.
   `POST /admin/ping` returns `{"ok": true}`.
4. Live map: home HTML has the red LIVE badge and `map-updated` time;
   `home.js` has `setInterval(refreshMapData, 60000)`.
5. Chatbot: home has the `chat-fab` button, `chat-mic` and
   `chat-voice-toggle`. `POST /api/chat {"message":"what to do in a
   flood","lang":"hi"}` returns a Hindi safety intro + English detail
   and a `/safety/flood` link. An unknown question returns the fallback
   in the requested language. `GET /api/chat/ui?lang=hi` returns the
   Hindi greeting and chips.
6. Footer: open `/track` - the footer is the last content element and
   sits at the bottom of the viewport with no white gap after it.

## Files

```
app.py                    Flask app, routes, SQLite, haversine nearest-tower,
                          Phase 2: reports, SOS, check-ins, sensors, queue
services/seed_data.py     The 60-tower list (verbatim) + 480 fictional citizens
services/sms.py           Simulated-SMS provider layer (+ MSG91/Twilio stub)
services/i18n.py          Phase 3: 9-language translations, 28 keys, English fallback
templates/                base.html, index.html, report.html, track.html,
                          admin_login.html, admin_broadcast.html,
                          admin_queue.html, admin_sensors.html,
                          admin_history.html, admin_history_detail.html,
                          admin_analytics.html
static/css/style.css      Government-trust look: navy + flat severity colours
static/manifest.json      Phase 3 PWA manifest (RakshakAlert, navy theme)
static/sw.js              Phase 3 service worker (offline cache + fallback)
static/img/logo.webp      Logo 4 - Radar Waves (header, footer, favicon)
static/css/style.css      Government-trust look: navy + flat severity colours
static/js/home.js         Public map, tower detail, GPS, sensor readings
static/js/report.js       Report GPS pick + offline queue (localStorage) + voice input (Web Speech API)
static/js/phase2.js       SOS + SAFE/HELP buttons
static/js/broadcast.js    3-step broadcast, map toggle, templates, review
requirements.txt          Flask==3.1.0
.env.example              No real secrets (demo admin login only)
uploads/                  Citizen report photos (not shipped in the ZIP)
instance/rakshakalert.db  Created by --init-db (not shipped in the ZIP)
```

## Nav and footer (fixes, 2026-11-07)

- Top nav, logged out: Public Map, Report Incident, Track Report, Admin.
  Admin-only links (Admin Broadcast, Incident Queue, Sensors, Alert History)
  are hidden until admin login, then appear after the Admin item.
- When admin is logged in, Report Incident is hidden from the nav and the
  footer Quick Links (the /report route itself still works).
- Report page: no "Check a report" box (Track Report is the separate page).
- Report description: Speak button uses the browser Web Speech API
  (en-IN or hi-IN), appends the transcript to the box. Needs Chrome/Edge
  and microphone permission; other browsers get a clear message.
- Footer: cleaner professional layout, tighter spacing, gold top border,
  brand + Quick Links + Emergency (112 / NDMA 1078), copyright line.
- Mobile friendly (360-430px): hamburger menu in the top nav (tap to open,
  closes after tapping a link), map full width and 380px high, stats 2 per
  row, one-column layout with map first, forms and buttons full width,
  tables scroll inside their card, footer stacks and centres. Same nav
  rules apply inside the mobile menu (admin links only after login,
  Report Incident hidden when admin is logged in).

## Phase 3 - test it

### Analytics
1. Log in as admin, open **Analytics** (top nav, after login only).
2. You see live counts: 2 alerts, 0 reports, 0 SOS, 16 simulated-SMS
   deliveries, 480 citizens, 60 towers, 0 SAFE, 0 HELP (clean demo state).
3. Bars show Flood 1 and Heavy Rainfall 1 by type, Orange 1 and Yellow 1
   by severity, and the state table shows Maharashtra 2 (both demo alerts
   are in Maharashtra).
   Log out and open `/admin/analytics` - you are sent to the login page (302).

### CSV export
1. Log in as admin, open **Analytics**, click **Download alerts CSV** -
   a file `rakshakalert_alerts_2026-11-07.csv` downloads with 2 data rows
   (Mira Road Flood, Nashik Heavy Rainfall) plus the header row.
2. **Download deliveries CSV** has 16 data rows + header.
3. **Download reports CSV** has only the header row in the clean demo state
   (0 reports); file one report first and it appears.

### PWA
1. Open `/manifest.json` - it returns the manifest (name RakshakAlert,
   theme #0f2a44). Open `/sw.js` - it returns the service worker.
2. On a phone (Chrome / Edge), open the site, use the browser menu
   "Add to Home screen" / "Install app" - the logo appears as the app icon.
   Turn off the internet and reload - the home page still opens from cache.

### Language switch
1. On the home page, use the Language select in the top bar - pick Hindi:
   the nav shows "सार्वजनिक मानचित्र" and the hero shows
   "अलर्ट सिर्फ वहीं, जहाँ ज़रूरत है।". Pick Tamil, Marathi, or any of the
   9 languages - nav, hero, SOS / Report / GPS / Active alerts headings
   and the footer change. Deeper pages stay in English (see honest scope
   above). Your choice is remembered in a cookie.

### Phase 3 - full test run
Re-tested end to end on 2026-11-07: Phase 1 (home 200, 60 towers,
Mira Road nearest 0.0 km, Nashik broadcast = 8 deliveries, Nashik only),
Phase 2 (report RA-00001 Open, SOS 201, SAFE/HELP counts, IoT test
trigger = Orange auto-alert + 8 Mira Road deliveries, queue shows the
report and SOS), the 5 fixes (logged-out nav = Public Map / Report
Incident / Track Report / Admin, logged-in nav hides Report Incident and
shows admin links + Analytics, report page has no "Check a report",
Speak button present, footer clean), mobile (hamburger present,
nav.js 200, analytics stacks on narrow screens), Phase 3 (analytics
200 logged in / 302 logged out, CSVs return real rows, manifest + sw.js
200, language switch changes nav/hero text, bad language code falls
back to English).

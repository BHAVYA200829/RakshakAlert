/* RakshakAlert service worker, Phase 3.
   Caches the main pages and static assets so the app opens offline
   on mobile. No real data is cached: live API calls always go to the
   network first and only fall back to the cache when offline. */
const CACHE_NAME = "rakshakalert-v1";
const PRECACHE = [
  "/",
  "/static/css/style.css",
  "/static/js/nav.js",
  "/static/js/home.js",
  "/static/js/phase2.js",
  "/static/js/report.js",
  "/static/js/broadcast.js",
  "/static/js/push.js",
  "/static/js/chat.js",
  "/static/img/logo.webp",
  "/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

function offlinePage() {
  return new Response(
    "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">" +
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">" +
    "<title>RakshakAlert - Offline</title></head><body style=\"font-family:sans-serif;padding:24px;color:#0f2a44\">" +
    "<h1>RakshakAlert</h1><p>You are offline. The last saved pages are " +
    "available from the menu, and new reports will be sent when you are " +
    "back online.</p><p><a href=\"/\">Try the home page again</a></p>" +
    "</body></html>",
    { headers: { "Content-Type": "text/html" } }
  );
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/admin/")) {
    event.respondWith(fetch(event.request).catch(() => offlinePage()));
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request).then((response) => {
        if (response && response.status === 200) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        }
        return response;
      }).catch(() => cached || offlinePage());
      return cached || network;
    })
  );
});

// Push notifications: show the alert when a push message arrives.
self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) { data = {}; }
  const title = data.title || "RakshakAlert";
  const body = data.body || "A new alert was sent for your area. Open RakshakAlert to see it.";
  event.waitUntil(
    self.registration.showNotification(title, {
      body: body,
      icon: "/static/img/logo.webp",
      badge: "/static/img/logo.webp",
      tag: "rakshakalert-alert",
    })
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow("/"));
});

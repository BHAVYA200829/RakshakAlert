// RakshakAlert - mobile hamburger menu.
// Tap the button to open or close the nav. Tapping a link closes it.
// On desktop the button is hidden by CSS and the nav is always shown.
(function () {
  const btn = document.getElementById("nav-toggle");
  const nav = document.getElementById("main-nav");
  if (!btn || !nav) return;
  function setOpen(open) {
    nav.classList.toggle("nav-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  btn.addEventListener("click", () => {
    setOpen(!nav.classList.contains("nav-open"));
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  // If the window grows back to desktop size, drop the mobile state.
  window.addEventListener("resize", () => {
    if (window.innerWidth > 860) setOpen(false);
  });
})();

// Language switcher (Phase 3): changing the select goes to /lang/<code>,
// which sets a cookie and sends the user back to the same page.
(function () {
  const sel = document.getElementById("lang-select");
  if (!sel) return;
  sel.addEventListener("change", () => {
    window.location.href = "/lang/" + sel.value;
  });
})();

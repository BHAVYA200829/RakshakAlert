// RakshakAlert - rule-based help assistant widget. No LLM, no API key.
// Answers come from /api/chat, which matches keywords against the
// safety guides and site help. UI strings (greeting, chips,
// placeholder, fallback) come from /api/chat/ui in the current site
// language and refresh when the panel opens, so a language change
// applies on next open. Voice: mic button uses Web Speech API
// SpeechRecognition in the current site language; speaker buttons
// read bot replies aloud with SpeechSynthesis. No server, no audio
// upload, browser speech only.
(function () {
  var fab = document.getElementById("chat-fab");
  var panel = document.getElementById("chat-panel");
  var body = document.getElementById("chat-body");
  var form = document.getElementById("chat-form");
  var input = document.getElementById("chat-input");
  var chips = document.getElementById("chat-chips");
  var closeBtn = document.getElementById("chat-close");
  var micBtn = document.getElementById("chat-mic");
  var greeting = document.getElementById("chat-greeting");
  var voiceToggle = document.getElementById("chat-voice-toggle");
  if (!fab || !panel) return;

  var langMap = { en: "en-IN", hi: "hi-IN", mr: "mr-IN", bn: "bn-IN", ta: "ta-IN", te: "te-IN", gu: "gu-IN", kn: "kn-IN", ml: "ml-IN" };
  function siteLang() {
    var l = (document.documentElement.lang || "en").split("-")[0];
    return langMap[l] ? l : "en";
  }
  var ui = { greeting: "", placeholder: "Type your question", fallback: "", listening: "Listening... tap Stop when done.", voice_not_supported: "Voice input is not supported in this browser. Please type instead.", voice_denied: "Microphone permission was denied. Allow the microphone in your browser, or type instead.", questions: [] };
  var voiceOn = false;

  function loadUi() {
    fetch("/api/chat/ui?lang=" + encodeURIComponent(siteLang()))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        ui = data;
        if (greeting && data.greeting) greeting.textContent = data.greeting;
        if (data.placeholder) input.placeholder = data.placeholder;
        chips.innerHTML = "";
        (data.questions || []).forEach(function (q) {
          var b = document.createElement("button");
          b.type = "button";
          b.textContent = q;
          b.addEventListener("click", function () { send(q); });
          chips.appendChild(b);
        });
      })
      .catch(function () { /* keep English defaults */ });
  }

  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = langMap[siteLang()] || "en-IN";
    window.speechSynthesis.speak(u);
  }

  function addMsg(text, who) {
    var div = document.createElement("div");
    div.className = "chat-msg " + who;
    div.textContent = text;
    if (who === "bot") {
      var sp = document.createElement("button");
      sp.type = "button";
      sp.className = "chat-speak";
      sp.textContent = "Listen";
      sp.setAttribute("aria-label", "Read this answer aloud");
      sp.addEventListener("click", function () { speak(text); });
      div.appendChild(sp);
      if (voiceOn) speak(text);
    }
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }
  function addLinks(links) {
    (links || []).forEach(function (href) {
      var a = document.createElement("a");
      a.href = href;
      a.textContent = "Open: " + href;
      a.style.display = "block";
      a.style.marginTop = "4px";
      body.appendChild(a);
    });
    body.scrollTop = body.scrollHeight;
  }
  function send(text) {
    var q = (text || "").trim();
    if (!q) return;
    addMsg(q, "user");
    input.value = "";
    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: q, lang: siteLang() })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        addMsg(data.answer || ui.fallback, "bot");
        addLinks(data.links);
      })
      .catch(function () {
        addMsg(ui.fallback || "Chat is unavailable right now. See the Safety Guide, or call 112 in an emergency.", "bot");
      });
  }

  // Voice input: SpeechRecognition in the current site language.
  var recog = null;
  var listening = false;
  if (micBtn) {
    micBtn.addEventListener("click", function () {
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) { addMsg(ui.voice_not_supported, "bot"); return; }
      if (listening && recog) { recog.stop(); return; }
      recog = new SR();
      recog.lang = langMap[siteLang()] || "en-IN";
      recog.interimResults = false;
      recog.maxAlternatives = 1;
      recog.onresult = function (ev) {
        var t = ev.results[0][0].transcript;
        input.value = t;
        send(t);
      };
      recog.onerror = function (ev) {
        listening = false;
        micBtn.classList.remove("listening");
        if (ev.error === "not-allowed" || ev.error === "service-not-allowed") {
          addMsg(ui.voice_denied, "bot");
        } else {
          addMsg(ui.voice_not_supported, "bot");
        }
      };
      recog.onend = function () { listening = false; micBtn.classList.remove("listening"); };
      try {
        recog.start();
        listening = true;
        micBtn.classList.add("listening");
        addMsg(ui.listening, "bot");
      } catch (e) { addMsg(ui.voice_not_supported, "bot"); }
    });
  }
  if (voiceToggle) {
    voiceToggle.addEventListener("click", function () {
      voiceOn = !voiceOn;
      voiceToggle.textContent = voiceOn ? "Sound on" : "Sound off";
      voiceToggle.setAttribute("aria-label", voiceOn ? "Voice replies on" : "Voice replies off");
      if (!voiceOn && ("speechSynthesis" in window)) window.speechSynthesis.cancel();
    });
  }
  fab.addEventListener("click", function () {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) { loadUi(); input.focus(); }
  });
  closeBtn.addEventListener("click", function () {
    panel.hidden = true;
    if (recog && listening) recog.stop();
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  });
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    send(input.value);
  });
  loadUi();
})();

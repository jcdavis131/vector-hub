/* Per-model page renderer + "Split Decision" game.
 *
 * Every value shown comes from assets/data/<slug>.json, which is generated from the real
 * model artifacts. Nothing is hardcoded here on purpose: a number typed into markup is a
 * number that silently stops matching the model the next time the model is retrained.
 *
 * The game shows two real entities and asks which one the MODEL rates higher on a named
 * axis. It never asks the player to predict a real-world outcome the model didn't record —
 * the answer key is the model's own numbers, so the game is a probe of the model rather
 * than a quiz with invented stakes.
 */
(function () {
  "use strict";

  var MODELS = [
    ["hoops", "Hoops"], ["gridiron", "Gridiron"], ["pitch", "Pitch"],
    ["equities", "Equities"], ["tennis", "Tennis"], ["unified", "Unified"]
  ];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function fmt(v) {
    if (typeof v !== "number" || !isFinite(v)) return String(v);
    var a = Math.abs(v);
    if (a >= 1000) return v.toFixed(0);
    if (a >= 100) return v.toFixed(1);
    if (a >= 1) return v.toFixed(2);
    return v.toFixed(3);
  }

  /* ---- shuffle, seeded by the day so a page reload isn't a reroll ------- */
  function dailySeed() {
    var d = new Date();
    return d.getUTCFullYear() * 10000 + (d.getUTCMonth() + 1) * 100 + d.getUTCDate();
  }
  function shuffled(arr, seed) {
    var a = arr.slice(), s = seed;
    for (var i = a.length - 1; i > 0; i--) {
      s = (s * 1103515245 + 12345) & 0x7fffffff;
      var j = s % (i + 1);
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function renderSwitch(slug) {
    var wrap = el("div", "model-switch");
    MODELS.forEach(function (m) {
      var a = el("a", null, m[1]);
      a.href = "/models/" + m[0] + ".html";
      if (m[0] === slug) a.setAttribute("aria-current", "page");
      wrap.appendChild(a);
    });
    return wrap;
  }

  function renderHead(d) {
    var head = el("header", "model-head");
    head.appendChild(el("div", "model-head__rule"));
    head.appendChild(el("p", "model-head__eyebrow", d.dims + " · " +
      Number(d.entity_count).toLocaleString() + " entities"));
    head.appendChild(el("h1", "model-head__title", d.name));
    head.appendChild(el("p", "model-head__tagline", d.tagline));
    head.appendChild(renderSwitch(d.slug));
    return head;
  }

  function renderStats(d) {
    var wrap = el("div", "model-stats");
    (d.headline_stats || []).forEach(function (s) {
      var c = el("div", "model-stat");
      c.appendChild(el("p", "model-stat__value", s.value));
      c.appendChild(el("p", "model-stat__label", s.label));
      c.appendChild(el("p", "model-stat__src", s.source));
      wrap.appendChild(c);
    });
    return wrap;
  }

  function renderInsights(d) {
    var sec = el("section", "model-section");
    sec.appendChild(el("h2", "model-section__label", "What the model actually found"));
    var grid = el("div", "insight-grid");
    (d.insights || []).forEach(function (i) {
      var c = el("article", "insight");
      c.appendChild(el("h3", "insight__title", i.title));
      c.appendChild(el("p", "insight__body", i.body));
      c.appendChild(el("p", "insight__src", i.source));
      grid.appendChild(c);
    });
    sec.appendChild(grid);
    return sec;
  }

  function renderGame(d) {
    var g = d.game || {};
    var rounds = shuffled(g.rounds || [], dailySeed());
    var idx = 0, score = 0, results = [];

    var sec = el("section", "model-section");
    sec.appendChild(el("h2", "model-section__label", "Probe the model"));

    var box = el("div", "game");
    var head = el("div", "game__head");
    head.appendChild(el("h3", "game__title", "Split Decision"));
    var scoreEl = el("p", "game__score", "0 / 0");
    head.appendChild(scoreEl);
    box.appendChild(head);

    box.appendChild(el("p", "game__prompt", g.prompt || ""));
    if (g.explainer) box.appendChild(el("p", "game__explainer", g.explainer));
    box.appendChild(el("span", "game__axis", g.axis_label || ""));

    var choices = el("div", "game__choices");
    var btnA = el("button", "choice"), btnB = el("button", "choice");
    [btnA, btnB].forEach(function (b) {
      b.type = "button";
      b.appendChild(el("span", "choice__name"));
      b.appendChild(el("span", "choice__sub"));
      b.appendChild(el("span", "choice__value"));
      choices.appendChild(b);
    });
    box.appendChild(choices);

    var reveal = el("p", "game__reveal");
    reveal.hidden = true;
    box.appendChild(reveal);

    var actions = el("div", "game__actions");
    var next = el("button", "game__btn", "Next →");
    next.type = "button"; next.hidden = true;
    var again = el("button", "game__btn game__btn--ghost", "Play again");
    again.type = "button"; again.hidden = true;
    actions.appendChild(next); actions.appendChild(again);
    box.appendChild(actions);

    var pips = el("div", "game__progress");
    box.appendChild(pips);

    function paint() {
      var r = rounds[idx];
      if (!r) return;
      [[btnA, r.a], [btnB, r.b]].forEach(function (pair) {
        var b = pair[0], side = pair[1];
        b.querySelector(".choice__name").textContent = side.name;
        b.querySelector(".choice__sub").textContent = side.sub || "";
        b.querySelector(".choice__value").textContent = fmt(side.value);
        b.removeAttribute("data-revealed");
        b.removeAttribute("data-outcome");
        b.disabled = false;
      });
      reveal.hidden = true;
      next.hidden = true;
      scoreEl.textContent = score + " / " + results.length;
    }

    function choose(which) {
      var r = rounds[idx];
      if (!r || btnA.disabled) return;
      var correct = which === r.answer;
      if (correct) score++;
      results.push(correct);
      btnA.dataset.revealed = "1"; btnB.dataset.revealed = "1";
      btnA.disabled = true; btnB.disabled = true;
      (which === "a" ? btnA : btnB).dataset.outcome = correct ? "right" : "wrong";
      (r.answer === "a" ? btnA : btnB).dataset.outcome = "right";
      reveal.textContent = (correct ? "Correct. " : "The model disagrees. ") + (r.reveal || "");
      reveal.hidden = false;
      scoreEl.textContent = score + " / " + results.length;

      var pip = el("span", "game__pip");
      pip.dataset.state = correct ? "right" : "wrong";
      pips.appendChild(pip);

      if (idx + 1 < rounds.length) { next.hidden = false; next.focus(); }
      else {
        again.hidden = false;
        reveal.textContent += "  —  Final: " + score + " of " + results.length + ".";
        again.focus();
      }
    }

    btnA.addEventListener("click", function () { choose("a"); });
    btnB.addEventListener("click", function () { choose("b"); });
    next.addEventListener("click", function () { idx++; paint(); btnA.focus(); });
    again.addEventListener("click", function () {
      idx = 0; score = 0; results = [];
      rounds = shuffled(g.rounds || [], Date.now() & 0x7fffffff);
      pips.textContent = ""; again.hidden = true; paint(); btnA.focus();
    });

    paint();
    sec.appendChild(box);
    return sec;
  }

  function renderCaveat(d) {
    if (!d.caveat) return null;
    var sec = el("section", "model-section");
    var c = el("div", "caveat");
    c.appendChild(el("p", "caveat__head", "What this model can't do"));
    c.appendChild(el("p", null, d.caveat));
    sec.appendChild(c);
    return sec;
  }

  function renderSources(d, slug, prov) {
    var sec = el("section", "model-section");
    sec.appendChild(el("h2", "model-section__label", "Every number above came from these files"));

    // Provenance drift, rendered rather than asserted. Each card ships a static
    // "_verification: CLEAN — adversarially verified" string that cannot notice
    // its own sources changing underneath it. scripts/check_provenance_hashes.py
    // recomputes them; where they no longer match, the card's figures may
    // describe a superseded artifact and the reader is told so here. Refreshing
    // the hashes instead would launder exactly the thing worth surfacing.
    var page = prov && prov.pages && prov.pages[slug + ".json"];
    if (page && (page.mismatched || page.malformed)) {
      var warn = el("p", "sources__drift");
      var bits = [];
      if (page.mismatched) {
        bits.push(page.mismatched + " cited source" + (page.mismatched === 1 ? " has" : "s have") +
                  " changed since these numbers were verified");
      }
      if (page.malformed) {
        bits.push(page.malformed + " recorded hash" + (page.malformed === 1 ? " is" : "es are") +
                  " not a hash");
      }
      warn.textContent = "⚠ Provenance: " + bits.join("; ") +
        ". Figures on this card may describe a superseded artifact. Re-run " +
        "scripts/check_provenance_hashes.py for the file list.";
      sec.appendChild(warn);
    } else if (prov) {
      var ok = el("p", "sources__ok");
      ok.textContent = "✓ Provenance: every cited source still hashes to the value " +
        "recorded when these numbers were verified.";
      sec.appendChild(ok);
    }

    var ul = el("ul", "sources");
    (d.source_files || []).forEach(function (f) { ul.appendChild(el("li", null, f)); });
    sec.appendChild(ul);
    return sec;
  }

  function boot() {
    var root = document.getElementById("model-root");
    if (!root) return;
    var slug = root.dataset.slug;
    // provenance_status.json is generated and may legitimately be absent on an
    // older deploy; a missing file means "no drift information", never "clean".
    var provP = fetch("/assets/data/provenance_status.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });

    Promise.all([
      fetch("/assets/data/" + slug + ".json").then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      }),
      provP,
    ])
      .then(function (both) {
        var d = both[0], prov = both[1];
        document.title = d.name + " — dumbmodel";
        var page = document.querySelector(".model-page");
        if (page) page.dataset.model = d.slug;
        root.textContent = "";
        root.appendChild(renderHead(d));
        root.appendChild(renderStats(d));
        root.appendChild(renderInsights(d));
        root.appendChild(renderGame(d));
        var cav = renderCaveat(d);
        if (cav) root.appendChild(cav);
        root.appendChild(renderSources(d, slug, prov));
      })
      .catch(function (e) {
        root.textContent = "";
        var w = el("div", "model-section");
        w.appendChild(el("h1", "model-head__title", "Data not loaded"));
        w.appendChild(el("p", "model-head__tagline",
          "This page renders from /assets/data/" + slug + ".json and that file did not load (" +
          e.message + "). Nothing is shown rather than showing placeholder numbers."));
        root.appendChild(w);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }
})();

/* Site search for galaxyestatesproperties.co.in
   Sources, merged so a new page or project shows up without anyone remembering to update a list:
   1. assets/search-index.json  – every page and its main sections (rebuilt by tools/site_search.py, also run on every push)
   2. window.SITE_PROJECTS       – every listed property (assets/data.js, loaded on every page)
   3. sitemap.xml                – any page missing from the index is read in the browser and searched too
   The index and the sitemap are always revalidated with the server, so a returning visitor never searches an old copy. */
(function () {
  "use strict";
  var SS_KEY = "gep-search-extra-v2";

  // ------------------------------------------------------------------ text helpers
  function norm(t) {
    return String(t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[’'`]/g, "").replace(/&/g, " and ").replace(/[^a-z0-9₹.+]+/g, " ").replace(/\s+/g, " ").trim();
  }
  function esc(t) {
    return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function stem(w) {
    if (w.length > 4 && /ies$/.test(w)) return w.slice(0, -3) + "y";
    if (w.length > 4 && /(ses|xes|ches|shes)$/.test(w)) return w.slice(0, -2);
    if (w.length > 3 && /[^s]s$/.test(w)) return w.slice(0, -1);
    return w;
  }
  // words that say nothing about which page you want
  var STOP = {};
  ("a an the in at on of for to and or with by near from my me i we our your is are be show find search look looking want need " +
   "best good top new latest all any list some which what where please project projects property properties scheme schemes " +
   "available sale buy buying price prices rate rates details detail info information about page").split(" ").forEach(function (w) { STOP[w] = 1; });
  // a query word can also match these
  var SYN = {
    bhk: ["bhk", "bedroom"], bedroom: ["bedroom", "bhk"], flat: ["flat", "apartment", "home", "residence"], apartment: ["apartment", "flat", "home"],
    home: ["home", "flat", "apartment", "residence", "villa"], house: ["house", "villa", "bungalow", "home"], office: ["office", "commercial"],
    shop: ["shop", "retail", "showroom"], showroom: ["showroom", "shop", "retail"], plot: ["plot", "land"], land: ["land", "plot", "farm"],
    farm: ["farm", "farmhouse", "farmland", "land"], villa: ["villa", "bungalow"], bungalow: ["bungalow", "villa"], commercial: ["commercial", "office", "shop"],
    gift: ["gift"], dubai: ["dubai", "uae"], uae: ["uae", "dubai", "emirates"], abroad: ["abroad", "international", "global", "overseas"],
    overseas: ["overseas", "abroad", "international", "global"], international: ["international", "abroad", "global"], ahmedabad: ["ahmedabad", "amdavad"],
    amdavad: ["amdavad", "ahmedabad"], shantigram: ["shantigram"], adani: ["adani"], weekend: ["weekend", "farm", "holiday"], cr: ["cr", "crore"], crore: ["crore", "cr"],
    lakh: ["lakh", "lakhs", "lac"], lac: ["lac", "lakh"], rera: ["rera"], "3d": ["3d"], tour: ["tour", "virtual"]
  };
  function lev1(a, b, max) {            // edit distance, stopping early above max
    if (Math.abs(a.length - b.length) > max) return max + 1;
    var prev = [], cur, i, j;
    for (j = 0; j <= b.length; j++) prev[j] = j;
    for (i = 1; i <= a.length; i++) {
      cur = [i]; var best = i;
      for (j = 1; j <= b.length; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
        if (cur[j] < best) best = cur[j];
      }
      if (best > max) return max + 1;
      prev = cur;
    }
    return prev[b.length];
  }

  // ------------------------------------------------------------------ data
  var DATA = null, LOADING = null, LISTENERS = [];
  function prep(e) {
    var r = { e: e, t: norm(e.t), s: norm(e.s), w: norm(e.w), h: norm(e.h), d: norm(e.d), x: norm(e.x) };
    r.tw = r.t.split(" ");
    r.tc = r.t.replace(/[ .]/g, "");
    r.sw = (r.s + " " + r.w).replace(/[ .]/g, "");
    return r;
  }
  function fromProjects(have) {
    var P = window.SITE_PROJECTS || [], out = [];
    P.forEach(function (p) {
      if (!p || !p.page) return;
      var e = {
        t: p.name, u: p.page, k: "Property",
        s: [p.label, p.location, p.price && p.price !== "On request" ? p.price : null].filter(Boolean).join(" · "),
        d: p.blurb || "",
        w: [p.developer, p.location, p.city, p.country, p.market, p.label, p.size, p.rera, p.possession, p.build].concat(p.cats || []).filter(Boolean).join(" "),
        h: "", x: (p.mix || []).map(function (m) { return m.join(" "); }).join(" ")
      };
      if (have[p.page]) { have[p.page].w = (have[p.page].w || "") + " " + e.w; return; }      // enrich the page entry
      out.push(e);
    });
    return out;
  }
  function pageEntry(url, html) {
    var doc = new DOMParser().parseFromString(html, "text/html");
    var title = (doc.querySelector("title") || {}).textContent || url;
    var desc = (doc.querySelector('meta[name="description"]') || { getAttribute: function () { return ""; } }).getAttribute("content") || "";
    var main = doc.querySelector("main") || doc.body;
    if (!main) return null;
    main.querySelectorAll("script,style,svg,noscript,form").forEach(function (n) { n.remove(); });
    var h1 = main.querySelector("h1");
    var heads = Array.prototype.map.call(main.querySelectorAll("h2,h3"), function (n) { return n.textContent.trim(); }).filter(Boolean).join(" | ");
    return { t: (h1 && h1.textContent.trim()) || title.split(" | ")[0].split(" – ")[0].trim(), u: url, k: /-property\.html$|^global\.html$/.test(url) ? "Guide" : "Page",
             d: desc.slice(0, 180), h: heads.slice(0, 600), x: (main.textContent || "").replace(/\s+/g, " ").slice(0, 900) };
  }
  function readExtra() { try { return JSON.parse(sessionStorage.getItem(SS_KEY) || "{}"); } catch (e) { return {}; } }
  function saveExtra(o) { try { sessionStorage.setItem(SS_KEY, JSON.stringify(o)); } catch (e) {} }
  function fillFromSitemap(have) {
    // pages listed in the sitemap but not in the index (for example a page added since the index was built)
    return fetch("sitemap.xml", { cache: "no-cache" }).then(function (r) { return r.ok ? r.text() : ""; }).then(function (xml) {
      var urls = [], re = /<loc>([^<]+)<\/loc>(?:\s*<lastmod>([^<]+)<\/lastmod>)?/g, m;
      while ((m = re.exec(xml))) {
        var u = m[1].replace(/^https?:\/\/[^/]+\//, "") || "index.html";
        if (u === "" || u === "/") u = "index.html";
        if (!have[u]) urls.push([u, m[2] || ""]);
      }
      if (!urls.length) return [];
      var cache = readExtra(), out = [], jobs = urls.slice(0, 40).map(function (pair) {
        var key = pair[0] + "@" + pair[1];
        if (cache[key]) { out.push(cache[key]); return Promise.resolve(); }
        return fetch(pair[0], { cache: "no-cache" }).then(function (r) { return r.ok ? r.text() : ""; }).then(function (h) {
          var e = h && pageEntry(pair[0], h);
          if (e) { cache[key] = e; out.push(e); }
        }).catch(function () {});
      });
      return Promise.all(jobs).then(function () { saveExtra(cache); return out; });
    }).catch(function () { return []; });
  }
  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (LOADING) return LOADING;
    LOADING = fetch("assets/search-index.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).catch(function () { return []; }).then(function (idx) {
      var have = {};
      idx.forEach(function (e) { if (e.u.indexOf("#") < 0) have[e.u] = e; });
      var list = idx.concat(fromProjects(have));
      list.forEach(function (e) { if (e.u.indexOf("#") < 0) have[e.u] = have[e.u] || e; });
      DATA = list.map(prep);
      // pages not yet in the index: read them in the background and add them as they arrive
      fillFromSitemap(have).then(function (extra) {
        if (!extra.length) return;
        extra.forEach(function (e) { if (!have[e.u]) { have[e.u] = e; DATA.push(prep(e)); } });
        LISTENERS.forEach(function (f) { f(); });
      });
      return DATA;
    });
    return LOADING;
  }

  // ------------------------------------------------------------------ ranking
  function wordScore(r, w) {
    var alts = SYN[w] || [w], best = 0;
    if (w !== stem(w)) alts = alts.concat([stem(w)]);
    for (var i = 0; i < alts.length; i++) {
      var a = alts[i], weight = i === 0 ? 1 : 0.85;
      var re = new RegExp("(^| )" + a.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
      var s = re.test(r.t) ? 14 : r.t.indexOf(a) >= 0 ? 9 : re.test(r.s) || re.test(r.w) ? 6 : (r.s + " " + r.w).indexOf(a) >= 0 ? 4
        : re.test(r.h) || re.test(r.d) ? 3 : (r.h + " " + r.d).indexOf(a) >= 0 ? 2 : re.test(r.x) ? 1.2 : r.x.indexOf(a) >= 0 ? 0.6 : 0;
      s *= weight;
      if (s > best) best = s;
    }
    if (best < 9 && w.length >= 5) {                       // joined-up or misspelt names: "ashridhar", "kalrv", "shantigrm"
      if (r.tc.indexOf(w) >= 0) best = Math.max(best, 10);
      else if (r.sw.indexOf(w) >= 0) best = Math.max(best, 5);
      else {
        var max = w.length >= 8 ? 2 : 1;
        for (var k = 0; k < r.tw.length; k++) {
          var t = r.tw[k];
          if (t.length >= 4 && lev1(w, t.length > w.length + 2 ? t.slice(0, w.length) : t, max) <= max) { best = Math.max(best, 7); break; }
        }
      }
    }
    return best;
  }
  function search(q, limit) {
    var raw = norm(q).split(" ").filter(function (w) { return w.length > 1 || /\d/.test(w); });
    var words = raw.filter(function (w) { return !STOP[w]; });
    if (!words.length) words = raw;                         // only stop words typed: use them anyway
    if (!words.length || !DATA) return { list: [], total: 0 };
    var hits = [];
    DATA.forEach(function (r) {
      var sum = 0, all = true;
      for (var i = 0; i < words.length; i++) { var s = wordScore(r, words[i]); if (!s) all = false; sum += s; }
      if (!sum) return;
      var score = sum + (all ? 20 : 0) + (r.e.k === "Property" ? 1.5 : 0) - (r.e.k === "Section" ? 1 : 0);
      hits.push({ r: r, s: score, raw: sum, all: all });
    });
    if (hits.some(function (h) { return h.all; })) hits = hits.filter(function (h) { return h.all; });
    hits.sort(function (a, b) { return b.s - a.s || (a.r.e.t < b.r.e.t ? -1 : 1); });
    if (hits.length) { var top = hits[0].raw; hits = hits.filter(function (h) { return h.raw >= top * 0.2; }); }
    // one result per page in the quick list when the page itself is also listed
    var seen = {}, out = [];
    hits.forEach(function (h) {
      var base = h.r.e.u.split("#")[0];
      if (h.r.e.k === "Section" && seen[base]) return;
      seen[base] = 1; out.push(h.r.e);
    });
    return { list: out.slice(0, limit || 50), total: out.length };
  }
  function mark(text, q) {
    var out = esc(text);
    norm(q).split(" ").filter(function (w) { return w.length > 1 && !STOP[w]; }).forEach(function (w) {
      out = out.replace(new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return out;
  }
  var ICON = { Property: "fa-building", Guide: "fa-earth-asia", Section: "fa-hashtag", Page: "fa-file-lines" };
  function row(e, q, i) {
    return '<li role="option" id="srch-o' + i + '"><a href="' + esc(e.u) + '"><i class="fas ' + (ICON[e.k] || "fa-file-lines") + '" aria-hidden="true"></i><span><b>' +
      mark(e.t, q) + "</b><small>" + esc(e.s || e.d || "") + "</small></span><em>" + esc(e.k) + "</em></a></li>";
  }

  // ------------------------------------------------------------------ a search box with a live list
  function attach(form, opts) {
    var input = form.querySelector('input[type="search"]'), list = form.querySelector(".srch-list");
    if (!input) return;
    if (!list) {                                            // older markup: add the list
      list = document.createElement("ul"); list.className = "srch-list"; list.setAttribute("role", "listbox"); list.hidden = true;
      list.id = "srch-l" + Math.random().toString(36).slice(2, 7); form.appendChild(list);
      input.setAttribute("role", "combobox"); input.setAttribute("aria-controls", list.id); input.setAttribute("aria-expanded", "false"); input.setAttribute("autocomplete", "off");
    }
    var active = -1, timer = 0;
    function move(to) {
      var items = list.querySelectorAll("li[role=option]");
      if (!items.length) return;
      active = (to + items.length) % items.length;
      items.forEach(function (li, k) { li.classList.toggle("on", k === active); });
      input.setAttribute("aria-activedescendant", items[active].id);
      items[active].scrollIntoView({ block: "nearest" });
    }
    function render() {
      var q = input.value.trim();
      if (q.length < 2) { list.hidden = true; list.innerHTML = ""; input.setAttribute("aria-expanded", "false"); return; }
      load().then(function () {
        if (input.value.trim() !== q) return;
        var res = search(q, opts.limit || 8);
        active = -1; input.removeAttribute("aria-activedescendant");
        list.innerHTML = res.list.length
          ? res.list.map(function (e, i) { return row(e, q, i); }).join("") +
            '<li class="srch-all"><a href="search.html?q=' + encodeURIComponent(q) + '">' + (res.total > res.list.length ? "See all " + res.total + " results" : "Open the results page") + " for “" + esc(q) + "”</a></li>"
          : '<li class="srch-none">Nothing found for “' + esc(q) + '”. Try a project, area, BHK, developer or RERA number, or <a href="contact.html">ask us</a>.</li>';
        list.hidden = false; input.setAttribute("aria-expanded", "true");
      }).catch(function () {
        list.innerHTML = '<li class="srch-none">Search could not load. Please check your connection.</li>'; list.hidden = false;
      });
    }
    LISTENERS.push(function () { if (!list.hidden) render(); });
    input.addEventListener("focus", function () { load(); if (input.value.trim().length > 1) render(); });
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(render, 70); });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown") { ev.preventDefault(); move(active + 1); }
      else if (ev.key === "ArrowUp") { ev.preventDefault(); move(active - 1); }
      else if (ev.key === "Escape") { list.hidden = true; if (opts.onEscape) opts.onEscape(); }
      else if (ev.key === "Enter" && active >= 0) {
        var a = list.querySelectorAll("li[role=option]")[active].querySelector("a");
        if (a) { ev.preventDefault(); location.href = a.href; }
      }
    });
    form.addEventListener("submit", function (ev) { if (!input.value.trim()) { ev.preventDefault(); input.focus(); } });
    document.addEventListener("click", function (ev) { if (!form.contains(ev.target)) list.hidden = true; });
  }

  // ------------------------------------------------------------------ the search dialog behind the magnifier button in the header
  function dialog() {
    var buttons = document.querySelectorAll(".nav-search, [data-open-search]");
    if (!buttons.length) return;
    var dlg = document.createElement("div");
    dlg.className = "srch-dialog"; dlg.hidden = true;
    dlg.setAttribute("role", "dialog"); dlg.setAttribute("aria-modal", "true"); dlg.setAttribute("aria-label", "Search the site");
    dlg.innerHTML = '<div class="srch-panel"><form class="srch-form" action="search.html" role="search"><i class="fas fa-magnifying-glass" aria-hidden="true"></i>' +
      '<input type="search" name="q" enterkeyhint="search" placeholder="Search projects, areas, BHK, developers, RERA…" aria-label="Search the site" autocomplete="off" autocapitalize="off" spellcheck="false" role="combobox" aria-controls="srch-dl" aria-expanded="false"/>' +
      '<button type="button" class="srch-close" aria-label="Close search"><i class="fas fa-xmark"></i></button>' +
      '<ul class="srch-list" id="srch-dl" role="listbox" hidden></ul></form>' +
      '<p class="srch-hint">Try “Kalrav”, “4 BHK Shantigram”, “GIFT City office”, “Dubai” or a RERA number</p></div>';
    document.body.appendChild(dlg);
    var input = dlg.querySelector("input"), back = null;
    function close() { dlg.hidden = true; document.body.classList.remove("no-scroll"); if (back && back.focus) back.focus(); }
    function open() {
      back = document.activeElement; dlg.hidden = false; document.body.classList.add("no-scroll");
      setTimeout(function () { input.focus(); input.select(); }, 20); load();
    }
    attach(dlg.querySelector("form"), { limit: 10, onEscape: close });
    buttons.forEach(function (b) { b.addEventListener("click", function (ev) { ev.preventDefault(); open(); }); });
    dlg.querySelector(".srch-close").addEventListener("click", close);
    dlg.addEventListener("click", function (ev) { if (ev.target === dlg) close(); });
    dlg.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") close();
      if (ev.key === "Tab") {                               // keep focus inside the dialog
        var f = dlg.querySelectorAll("input, button, a[href]"), first = f[0], last = f[f.length - 1];
        if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
        else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
      }
    });
    document.addEventListener("keydown", function (ev) {
      var tag = (ev.target.tagName || "").toLowerCase(), typing = tag === "input" || tag === "textarea" || tag === "select" || ev.target.isContentEditable;
      if ((ev.key === "/" && !typing) || ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k")) { ev.preventDefault(); if (dlg.hidden) open(); }
    });
  }

  // ------------------------------------------------------------------ search.html
  function resultsPage() {
    var box = document.querySelector("[data-search-results]");
    if (!box) return;
    var q = new URLSearchParams(location.search).get("q") || "", input = document.querySelector('.srch-page input[type="search"]'), head = document.querySelector("[data-search-head]");
    if (input) input.value = q;
    if (!q.trim()) { if (head) head.textContent = "Type what you are looking for: a project, an area, a BHK size, a developer or a RERA number."; return; }
    function draw() {
      var res = search(q, 300), list = res.list;
      if (head) head.textContent = list.length ? list.length + (list.length === 1 ? " result" : " results") + " for “" + q + "”" : "Nothing found for “" + q + "”.";
      box.innerHTML = list.length
        ? '<ul class="srch-results">' + list.map(function (e) {
            return '<li><a href="' + esc(e.u) + '"><span class="srch-kind"><i class="fas ' + (ICON[e.k] || "fa-file-lines") + '"></i> ' + esc(e.k) + "</span><b>" + mark(e.t, q) + "</b>" +
              (e.s ? "<small>" + esc(e.s) + "</small>" : "") + (e.d ? "<p>" + mark(e.d, q) + "</p>" : "") + "</a></li>";
          }).join("") + "</ul>"
        : '<p class="srch-empty">Try fewer words, or <a href="projects.html">browse all properties</a> or <a href="contact.html">ask us directly</a>.</p>';
    }
    LISTENERS.push(draw);
    load().then(draw);
  }

  function init() {
    document.querySelectorAll("form[data-search]").forEach(function (f) { attach(f, { limit: 8 }); });
    dialog();
    resultsPage();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.GEPSearch = { load: load, search: search };
})();

const SITE = "ChristSupply.Net";
const SITE_URL = "https://christsupply.net";
const BRAND = "Christ Supply Holy Bible";
const CREDIT = "Made by Liberated Luis With Cursor, Claude Opus, and MacBook";
const STORAGE_THEME = "csb-theme";
const STORAGE_LANG = "csb-lang";

const $ = (id) => document.getElementById(id);
const state = {
  catalog: null,
  books: [],
  lang: null,
  book: 40,
  chapter: 1,
  mode: "scroll",
  cache: new Map(),
};

function preferredTheme() {
  const saved = localStorage.getItem(STORAGE_THEME);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = theme === "light" ? "#f3ead7" : "#041208";
  $("themeBtn").textContent = theme === "light" ? "Dark" : "Light";
}

function pageMark(side, extra = "") {
  const left = SITE;
  const right = extra || `${BRAND}`;
  return `<div class="page-mark ${side}"><span>${left}</span><span>${right}</span></div>`;
}

function stripHtml(text) {
  const box = document.createElement("div");
  box.innerHTML = text;
  return (box.textContent || "").replace(/\s+/g, " ").trim();
}

function ebibleFilename(usfm, chapter) {
  const n = chapter < 100 ? String(chapter).padStart(2, "0") : String(chapter);
  return `${usfm}${n}.htm`;
}

function parseEbibleHtml(html) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const main = doc.querySelector(".main") || doc.body;
  const verses = [];
  let current = null;
  const pushText = (value) => {
    if (!current) return;
    current.text += value;
  };
  const walk = (node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      pushText(node.textContent || "");
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    const el = node;
    if (el.matches?.("span.verse")) {
      const num = parseInt((el.id || "").replace(/^V/i, ""), 10);
      if (Number.isFinite(num) && num > 0) {
        current = { verse: num, text: "" };
        verses.push(current);
      }
      const own = (el.textContent || "").replace(/^\s*\d+\s*/, "");
      pushText(own);
      return;
    }
    if (el.matches?.("a.notemark, .popup, .footnote, .tnav, style, script")) return;
    for (const child of el.childNodes) walk(child);
  };
  walk(main);
  return verses
    .map((v) => ({ verse: v.verse, text: v.text.replace(/\s+/g, " ").trim() }))
    .filter((v) => v.text);
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}

async function fetchText(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.text();
}

async function loadFromBolls(source, book, chapter) {
  const rows = await fetchJson(`https://bolls.life/get-text/${source.id}/${book}/${chapter}/`);
  return rows.map((row) => ({ verse: row.verse, text: stripHtml(row.text) }));
}

async function loadFromGetbible(source, book, chapter) {
  const data = await fetchJson(`https://api.getbible.net/v2/${source.id}/${book}/${chapter}.json`);
  return (data.verses || []).map((row) => ({ verse: row.verse, text: row.text }));
}

async function loadFromEbible(source, bookMeta, chapter) {
  const file = ebibleFilename(bookMeta.usfm, chapter);
  const urls = [
    `/api/ebible/${source.id}/${file}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(`https://ebible.org/${source.id}/${file}`)}`,
  ];
  let lastError = null;
  for (const url of urls) {
    try {
      const html = await fetchText(url);
      const verses = parseEbibleHtml(html);
      if (verses.length) return verses;
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError || new Error("eBible chapter not available");
}

async function loadChapter(lang, bookMeta, chapter) {
  const key = `${lang.iso}:${bookMeta.id}:${chapter}`;
  if (state.cache.has(key)) return state.cache.get(key);
  const errors = [];
  for (const source of lang.sources || []) {
    try {
      let verses = [];
      if (source.kind === "bolls") verses = await loadFromBolls(source, bookMeta.id, chapter);
      else if (source.kind === "getbible") verses = await loadFromGetbible(source, bookMeta.id, chapter);
      else if (source.kind === "ebible") verses = await loadFromEbible(source, bookMeta, chapter);
      if (verses.length) {
        const payload = { source, verses };
        state.cache.set(key, payload);
        return payload;
      }
    } catch (err) {
      errors.push(`${source.kind}:${source.id} ${err.message || err}`);
    }
  }
  throw new Error(errors.join(" · ") || "No open translation is wired for this language yet.");
}

function renderVerses(verses) {
  return verses
    .map((v) => `<div class="verse"><span class="n">${v.verse}</span><span>${v.text}</span></div>`)
    .join("");
}

function chunkVerses(verses, size = 12) {
  if (!verses.length) return [[]];
  const pages = [];
  for (let i = 0; i < verses.length; i += size) pages.push(verses.slice(i, i + size));
  return pages;
}

function plate(title, verses, pageNo) {
  return `
    <article class="page-plate" data-page="${pageNo}">
      ${pageMark("", `${SITE} · p.${pageNo}`)}
      <div class="page-body">
        <h2>${title}</h2>
        ${renderVerses(verses)}
      </div>
      ${pageMark("foot", `${CREDIT}`)}
    </article>`;
}

function renderPlates(title, verses, pageNo) {
  return chunkVerses(verses)
    .map((part, index) => plate(index === 0 ? title : `${title} (cont.)`, part, pageNo + index))
    .join("");
}

function txtBanner(pageNo, title) {
  const rule = "=".repeat(64);
  return [
    rule,
    `ChristSupply.Net`.padEnd(32) + `page ${pageNo}`.padStart(32),
    `${BRAND}  ·  ${CREDIT}`,
    title,
    rule,
  ].join("\n");
}

function toTxt(lang, bookMeta, chapter, verses, source, pageNo) {
  const pages = chunkVerses(verses, 12);
  const blocks = pages.map((part, index) => {
    const n = pageNo + index;
    return [
      txtBanner(n, `${bookMeta.name} ${chapter}`),
      "",
      `Language: ${lang.native} / ${lang.name} (${lang.iso})`,
      `Source: ${source.name || source.id}`,
      `Site: ${SITE_URL}`,
      "",
      ...part.map((v) => `${v.verse}  ${v.text}`),
      "",
      "-".repeat(64),
      SITE,
      CREDIT,
      "",
    ].join("\n");
  });
  return blocks.join("\n\n");
}

function chapterHref(usfm, chapter, mode = state.mode) {
  return `#${state.lang.iso}/${String(usfm).toLowerCase()}/${chapter}/${mode}`;
}

function renderGlossaryPanel() {
  const list = $("glossaryList");
  if (!list || !state.books.length || !state.lang) return;
  list.innerHTML = state.books
    .map((book) => {
      const chaps = Array.from({ length: book.chapters }, (_, i) => {
        const n = i + 1;
        const current = book.id === state.book && n === state.chapter ? ' aria-current="page"' : "";
        return `<a href="${chapterHref(book.usfm, n)}" data-book="${book.id}" data-chapter="${n}"${current}>${n}</a>`;
      }).join("");
      return `<section class="gl-book"><h3>${book.name}</h3><div class="gl-chaps">${chaps}</div></section>`;
    })
    .join("");
}

function glossarySheetHtml() {
  const body = state.books
    .map((book) => {
      const links = Array.from(
        { length: book.chapters },
        (_, i) => `<a href="${chapterHref(book.usfm, i + 1, "pdf")}">${i + 1}</a>`
      ).join(" ");
      return `<div class="gl-print-book"><strong>${book.name}</strong> ${links}</div>`;
    })
    .join("");
  return `<div class="pdf-sheet glossary-sheet">
      ${pageMark("", "Chapter glossary")}
      <div class="page-body">
        <h2>Chapter glossary</h2>
        <p class="gl-note">Click a chapter. Print at 100% on US Letter. ${SITE}</p>
        <div class="gl-print-grid">${body}</div>
      </div>
      ${pageMark("foot", CREDIT)}
    </div>`;
}

function setStatus(message) {
  $("status").textContent = message;
}

function currentBook() {
  return state.books.find((b) => b.id === state.book) || state.books[0];
}

function fillChapters() {
  const book = currentBook();
  const select = $("chapterSelect");
  select.innerHTML = "";
  for (let i = 1; i <= book.chapters; i += 1) {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = String(i);
    select.appendChild(opt);
  }
  if (state.chapter > book.chapters) state.chapter = 1;
  select.value = String(state.chapter);
}

function fillBooks() {
  const select = $("bookSelect");
  select.innerHTML = state.books
    .map((b) => `<option value="${b.id}">${b.name}</option>`)
    .join("");
  select.value = String(state.book);
  fillChapters();
}

function renderLangList(filter = "") {
  const q = filter.trim().toLowerCase();
  const langs = state.catalog.languages.filter((lang) => {
    if (!q) return lang.rank <= 40;
    return (
      lang.name.toLowerCase().includes(q) ||
      lang.native.toLowerCase().includes(q) ||
      lang.iso.toLowerCase().includes(q) ||
      lang.region.toLowerCase().includes(q)
    );
  });
  const panel = $("langPanel");
  panel.hidden = false;
  panel.innerHTML = langs
    .slice(0, 80)
    .map(
      (lang) => `
      <button type="button" class="lang-item" data-iso="${lang.iso}">
        <span>${lang.rank}</span>
        <span>${lang.native}<small>${lang.name} · ${lang.iso} · ${lang.speakersM}M</small></span>
        <span class="cov">${lang.coverage}</span>
      </button>`
    )
    .join("");
}

function describeLang(lang) {
  const source = lang.sources?.[0];
  const src = source ? `${source.kind} · ${source.name || source.id}` : "catalog only";
  return `#${lang.rank} ${lang.native} / ${lang.name} · ${lang.coverage} · ${src}`;
}

async function render() {
  const lang = state.lang;
  const book = currentBook();
  const chapter = state.chapter;
  const title = `${book.name} ${chapter}`;
  const pageNo = book.id * 200 + chapter;
  $("langSearch").value = `${lang.native} · ${lang.name}`;
  document.documentElement.lang = lang.iso;
  document.documentElement.dir = lang.rtl ? "rtl" : "ltr";
  setStatus(`Loading ${title} in ${lang.name}… ${SITE}`);

  const views = {
    scroll: $("view-scroll"),
    txt: $("view-txt"),
    pdf: $("view-pdf"),
  };
  for (const [mode, node] of Object.entries(views)) {
    node.hidden = mode !== state.mode;
  }

  try {
    const { source, verses } = await loadChapter(lang, book, chapter);
    const heading = `${title} — ${lang.native}`;
    const pages = chunkVerses(verses);
    views.scroll.innerHTML = renderPlates(heading, verses, pageNo);
    views.pdf.innerHTML = glossarySheetHtml() + pages
      .map((part, index) => `<div class="pdf-sheet">${plate(index === 0 ? heading : `${heading} (cont.)`, part, pageNo + index)}</div>`)
      .join("");
    views.txt.innerHTML = `<pre>${toTxt(lang, book, chapter, verses, source, pageNo)}</pre>`;
    renderGlossaryPanel();
    setStatus(`${describeLang(lang)} · ${verses.length} verses · marked ${SITE}`);
    history.replaceState(
      {},
      "",
      `#${lang.iso}/${book.usfm.toLowerCase()}/${chapter}/${state.mode}`
    );
  } catch (err) {
    const message = err.message || String(err);
    const empty = plate(
      `${title} — ${lang.native}`,
      [{ verse: 1, text: `Open text is not reachable yet for this language. ${message}` }],
      pageNo
    );
    views.scroll.innerHTML = empty;
    views.pdf.innerHTML = `${glossarySheetHtml()}<div class="pdf-sheet">${empty}</div>`;
    views.txt.innerHTML = `<pre>${txtBanner(pageNo, title)}\n\n${message}\n\n${SITE}\n${CREDIT}\n</pre>`;
    renderGlossaryPanel();
    setStatus(message);
  }
}

function selectLang(iso) {
  const lang = state.catalog.languages.find((row) => row.iso === iso);
  if (!lang) return;
  state.lang = lang;
  localStorage.setItem(STORAGE_LANG, iso);
  $("langPanel").hidden = true;
  render();
}

function stepChapter(delta) {
  const book = currentBook();
  let next = state.chapter + delta;
  let bookId = state.book;
  if (next < 1) {
    const idx = Math.max(0, state.books.findIndex((b) => b.id === bookId) - 1);
    const prev = state.books[idx];
    bookId = prev.id;
    next = prev.chapters;
  } else if (next > book.chapters) {
    const idx = Math.min(state.books.length - 1, state.books.findIndex((b) => b.id === bookId) + 1);
    const nxt = state.books[idx];
    bookId = nxt.id;
    next = 1;
  }
  state.book = bookId;
  state.chapter = next;
  $("bookSelect").value = String(bookId);
  fillChapters();
  render();
}

function downloadTxt() {
  const pre = $("view-txt").querySelector("pre");
  if (!pre) return;
  const book = currentBook();
  const name = `${SITE.replace(".", "")}-${state.lang.iso}-${book.usfm}-${state.chapter}.txt`;
  const blob = new Blob([pre.textContent], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

function startRain() {
  const canvas = $("rain");
  const ctx = canvas.getContext("2d");
  const glyphs = "CHRISTSUPPLY.NET†✠01アイウエオカキクケコΑΩאבגדה ";
  let columns = [];
  const resize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const count = Math.floor(canvas.width / 16);
    columns = Array.from({ length: count }, () => Math.random() * canvas.height);
  };
  resize();
  window.addEventListener("resize", resize);
  const tick = () => {
    const light = document.documentElement.dataset.theme === "light";
    ctx.fillStyle = light ? "rgba(243, 234, 215, 0.18)" : "rgba(2, 4, 2, 0.18)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = light ? "rgba(11, 93, 44, 0.45)" : "rgba(124, 255, 154, 0.72)";
    ctx.font = "13px IBM Plex Mono, monospace";
    columns.forEach((y, i) => {
      const ch = glyphs[Math.floor(Math.random() * glyphs.length)];
      ctx.fillText(ch, i * 16, y);
      columns[i] = y > canvas.height + Math.random() * 400 ? 0 : y + 16;
    });
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      requestAnimationFrame(tick);
    }
  };
  tick();
}

function bind() {
  $("themeBtn").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem(STORAGE_THEME, next);
    applyTheme(next);
  });
  $("langSearch").addEventListener("focus", () => renderLangList($("langSearch").value));
  $("langSearch").addEventListener("input", () => renderLangList($("langSearch").value));
  $("langPanel").addEventListener("click", (event) => {
    const btn = event.target.closest("[data-iso]");
    if (btn) selectLang(btn.dataset.iso);
  });
  $("bookSelect").addEventListener("change", (event) => {
    state.book = Number(event.target.value);
    state.chapter = 1;
    fillChapters();
    render();
  });
  $("chapterSelect").addEventListener("change", (event) => {
    state.chapter = Number(event.target.value);
    render();
  });
  document.querySelectorAll("input[name=mode]").forEach((input) => {
    input.addEventListener("change", () => {
      if (input.checked) {
        state.mode = input.value;
        render();
      }
    });
  });
  $("prevBtn").addEventListener("click", () => stepChapter(-1));
  $("nextBtn").addEventListener("click", () => stepChapter(1));
  $("glossaryBtn").addEventListener("click", () => {
    const panel = $("glossary");
    panel.hidden = !panel.hidden;
    if (!panel.hidden) renderGlossaryPanel();
  });
  $("glossaryClose").addEventListener("click", () => {
    $("glossary").hidden = true;
  });
  $("glossaryList").addEventListener("click", (event) => {
    const link = event.target.closest("a[data-book]");
    if (!link) return;
    event.preventDefault();
    state.book = Number(link.dataset.book);
    state.chapter = Number(link.dataset.chapter);
    $("bookSelect").value = String(state.book);
    fillChapters();
    $("glossary").hidden = true;
    render();
  });
  $("downloadTxtBtn").addEventListener("click", downloadTxt);
  $("printBtn").addEventListener("click", () => {
    state.mode = "pdf";
    document.querySelector('input[name=mode][value=pdf]').checked = true;
    render().then(() => window.print());
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#langPanel") && !event.target.closest("#langSearch")) {
      $("langPanel").hidden = true;
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.target.matches("input, select, textarea")) return;
    if (event.key === "g" || event.key === "G") {
      event.preventDefault();
      $("glossary").hidden = !$("glossary").hidden;
      if (!$("glossary").hidden) renderGlossaryPanel();
    } else if (event.key === "Escape") {
      $("glossary").hidden = true;
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      stepChapter(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      stepChapter(1);
    }
  });
  window.addEventListener("hashchange", () => {
    const before = `${state.lang.iso}/${currentBook().usfm}/${state.chapter}/${state.mode}`;
    parseHash();
    fillBooks();
    const after = `${state.lang.iso}/${currentBook().usfm}/${state.chapter}/${state.mode}`;
    if (before !== after) render();
  });
}

function parseHash() {
  const raw = location.hash.replace(/^#/, "");
  if (!raw) return;
  const [iso, usfm, chapter, mode] = raw.split("/");
  if (iso) {
    const lang = state.catalog.languages.find((row) => row.iso === iso);
    if (lang) state.lang = lang;
  }
  if (usfm) {
    const book = state.books.find((row) => row.usfm.toLowerCase() === usfm.toLowerCase());
    if (book) state.book = book.id;
  }
  if (chapter) state.chapter = Number(chapter) || 1;
  if (["scroll", "txt", "pdf"].includes(mode)) {
    state.mode = mode;
    const radio = document.querySelector(`input[name=mode][value=${mode}]`);
    if (radio) radio.checked = true;
  }
}

async function boot() {
  applyTheme(preferredTheme());
  startRain();
  bind();
  const [catalog, books] = await Promise.all([
    fetchJson("data/languages.json"),
    fetchJson("data/books.json"),
  ]);
  state.catalog = catalog;
  state.books = books;
  const saved = localStorage.getItem(STORAGE_LANG);
  state.lang =
    catalog.languages.find((row) => row.iso === saved) ||
    catalog.languages.find((row) => row.iso === "eng") ||
    catalog.languages[0];
  parseHash();
  fillBooks();
  await render();
}

boot().catch((err) => setStatus(err.message || String(err)));

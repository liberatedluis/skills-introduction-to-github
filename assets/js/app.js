const SITE = "ChristSupply.Net";
const SITE_URL = "https://christsupply.net";
const BRAND = "Christ Supply Holy Bible";
const CREDIT = "Made by Liberated Luis With Cursor, Claude Opus, and MacBook";
const GITHUB_PRINT =
  "https://github.com/liberatedluis/skills-introduction-to-github/tree/main/print-bibles";
const STORAGE_THEME = "csb-theme";
const STORAGE_TX = "csb-tx";
const STORAGE_LANG = "csb-lang";
const COVERAGE_LABEL = {
  bible: "Full Bible",
  nt: "New Testament",
  portions: "Portions",
};

const $ = (id) => document.getElementById(id);
const state = {
  catalog: null,
  allBooks: [],
  books: [],
  tx: null,
  book: 40,
  chapter: 1,
  mode: "scroll",
  cache: new Map(),
  tail: null,
  loadingMore: false,
  skips: 0,
};
let moreObserver = null;
let plateObserver = null;

function preferredTheme() {
  const saved = localStorage.getItem(STORAGE_THEME);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = theme === "light" ? "#f3ead7" : "#041208";
  const btn = $("themeBtn");
  if (btn) btn.textContent = theme === "light" ? "Dark" : "Light";
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

function parseEbibleIndex(html) {
  const usfms = new Set();
  const re = /href=['"]([A-Z0-9]{3})\d+\.htm['"]/gi;
  let match;
  while ((match = re.exec(html))) {
    const code = match[1].toUpperCase();
    if (!["FRT", "INT", "GLO", "XXA", "XXB", "XXC", "XXD", "XXE", "XXF", "XXG"].includes(code)) {
      usfms.add(code);
    }
  }
  return [...usfms];
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

function ebibleUrls(id, file) {
  const remote = `https://ebible.org/${id}/${file}`;
  return [
    `/api/ebible/${id}/${file}`,
    `https://api.allorigins.win/raw?url=${encodeURIComponent(remote)}`,
    `https://corsproxy.io/?${encodeURIComponent(remote)}`,
  ];
}

async function fetchFirstText(urls) {
  let lastError = null;
  for (const url of urls) {
    try {
      const text = await fetchText(url);
      if (text && text.length > 40) return text;
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError || new Error("text not available");
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
  const html = await fetchFirstText(ebibleUrls(source.id, file));
  const verses = parseEbibleHtml(html);
  if (!verses.length) throw new Error("eBible chapter not available");
  return verses;
}

function booksFor(tx) {
  const all = state.allBooks;
  const ot = all.filter((b) => b.testament === "OT");
  const nt = all.filter((b) => b.testament === "NT");
  const otCount = Number(tx.otBooks) || 0;
  const ntCount = Number(tx.ntBooks) || 0;
  if (tx._usfms?.length) {
    const wanted = new Set(tx._usfms);
    const matched = all.filter((b) => wanted.has(b.usfm));
    if (matched.length) return matched;
  }
  if (otCount >= 39 && ntCount >= 27) return all;
  if (ntCount >= 27 && otCount === 0) return nt;
  if (otCount >= 39 && ntCount === 0) return ot;
  if (tx.coverage === "nt") return nt;
  if (tx.coverage === "bible") return all;
  if (ntCount >= 27) return [...(otCount > 0 ? ot.slice(0, Math.min(otCount, ot.length)) : []), ...nt];
  if (ntCount > 0 && otCount === 0) return nt;
  if (otCount > 0 && ntCount === 0) return ot;
  return nt;
}

async function discoverBooks(tx) {
  if (tx.source !== "ebible" || tx._usfms) return;
  const otCount = Number(tx.otBooks) || 0;
  const ntCount = Number(tx.ntBooks) || 0;
  if ((otCount >= 39 && ntCount >= 27) || (ntCount >= 27 && otCount === 0) || (otCount >= 39 && ntCount === 0)) {
    return;
  }
  try {
    const html = await fetchFirstText(ebibleUrls(tx.id, "index.htm"));
    const usfms = parseEbibleIndex(html);
    if (usfms.length) tx._usfms = usfms;
  } catch {
    tx._usfms = [];
  }
}

function applyBooksFor(tx) {
  const books = booksFor(tx);
  state.books = books.length ? books : state.allBooks;
  if (!state.books.some((b) => b.id === state.book)) {
    const preferNt = (tx.coverage || "") !== "bible" || state.book >= 40;
    const pick = preferNt
      ? state.books.find((b) => b.usfm === "MAT") || state.books.find((b) => b.testament === "NT")
      : state.books[0];
    state.book = (pick || state.books[0]).id;
    state.chapter = 1;
  }
  if (state.chapter > currentBook().chapters) state.chapter = 1;
  fillBooks();
}

async function loadChapter(tx, bookMeta, chapter) {
  const key = `${tx.id}:${bookMeta.id}:${chapter}`;
  if (state.cache.has(key)) return state.cache.get(key);
  const source = { kind: tx.source, id: tx.id, name: tx.title };
  let verses = [];
  if (tx.source === "getbible") verses = await loadFromGetbible(source, bookMeta.id, chapter);
  else verses = await loadFromEbible(source, bookMeta, chapter);
  if (!verses.length) throw new Error("empty chapter");
  const payload = { source, verses };
  state.cache.set(key, payload);
  return payload;
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

function plate(title, verses, pageNo, bookId, chapter) {
  return `
    <article class="page-plate" data-page="${pageNo}" data-book="${bookId || ""}" data-chapter="${chapter || ""}">
      ${pageMark("", `${SITE} · p.${pageNo}`)}
      <div class="page-body">
        <h2>${title}</h2>
        ${renderVerses(verses)}
      </div>
      ${pageMark("foot", `${CREDIT}`)}
    </article>`;
}

function renderPlates(title, verses, pageNo, bookId, chapter) {
  return chunkVerses(verses)
    .map((part, index) =>
      plate(index === 0 ? title : `${title} (cont.)`, part, pageNo + index, bookId, chapter)
    )
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

function toTxt(tx, bookMeta, chapter, verses, source, pageNo) {
  const pages = chunkVerses(verses, 12);
  const blocks = pages.map((part, index) => {
    const n = pageNo + index;
    return [
      txtBanner(n, `${bookMeta.name} ${chapter}`),
      "",
      `Translation: ${tx.title} (${tx.id})`,
      `Language: ${tx.native} / ${tx.language} (${tx.iso})`,
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

function setStatus(message) {
  const node = $("status");
  if (node) node.textContent = message;
}

function currentBook() {
  return state.books.find((b) => b.id === state.book) || state.books[0];
}

function fillChapters() {
  const book = currentBook();
  const select = $("chapterSelect");
  if (!select || !book) return;
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
  if (!select) return;
  select.innerHTML = state.books.map((b) => `<option value="${b.id}">${b.name}</option>`).join("");
  select.value = String(state.book);
  fillChapters();
}

function coverageLabel(tx) {
  return COVERAGE_LABEL[tx.coverage] || "Portions";
}

function matchesTranslation(tx, q) {
  if (!q) return true;
  const hay = `${tx.title} ${tx.language} ${tx.native} ${tx.iso} ${tx.id} ${tx.coverage} ${coverageLabel(tx)}`.toLowerCase();
  return q.split(/\s+/).every((part) => hay.includes(part));
}

function renderLangList(filter = "") {
  const panel = $("langPanel");
  if (!panel || !state.catalog) return;
  const q = filter.trim().toLowerCase();
  const lookingLikeCurrent =
    state.tx && filter === `${state.tx.native} · ${state.tx.title}`;
  const query = lookingLikeCurrent ? "" : q;
  let list = state.catalog.translations.filter((tx) => matchesTranslation(tx, query));
  if (!query) list = list.slice(0, 80);
  panel.hidden = false;
  const shown = list.slice(0, 100);
  const total = state.catalog.translations.length;
  panel.innerHTML =
    shown
      .map(
        (tx) => `
      <button type="button" class="lang-item" data-id="${tx.id}">
        <span class="cov">${coverageLabel(tx)}</span>
        <span>${tx.native || tx.language}<small>${tx.title} · ${tx.language} · ${tx.id}</small></span>
        <span class="iso">${tx.iso}</span>
      </button>`
      )
      .join("") +
    `<p class="lang-count">${shown.length} of ${query ? list.length : total} · ${total} Matrix Holy Bibles · ${SITE}</p>`;
}

function describeTx(tx) {
  return `${tx.native} / ${tx.language} · ${tx.title} · ${coverageLabel(tx)} · ${tx.id}`;
}

function writeHash(tx = state.tx, book = currentBook(), chapter = state.chapter, mode = state.mode) {
  if (!tx || !book) return;
  const next = `#${tx.id}/${book.usfm.toLowerCase()}/${chapter}/${mode}`;
  if (location.hash !== next) history.replaceState({}, "", next);
}

function peekNext(bookId, chapter) {
  const book = state.books.find((b) => b.id === bookId) || currentBook();
  if (!book) return null;
  if (chapter < book.chapters) return { book: book.id, chapter: chapter + 1 };
  const idx = state.books.findIndex((b) => b.id === book.id);
  const nxt = state.books[idx + 1];
  if (!nxt) return null;
  return { book: nxt.id, chapter: 1 };
}

function disconnectObservers() {
  if (moreObserver) {
    moreObserver.disconnect();
    moreObserver = null;
  }
  if (plateObserver) {
    plateObserver.disconnect();
    plateObserver = null;
  }
}

function attachPlateObserver() {
  if (state.mode !== "scroll") return;
  const stage = $("view-scroll");
  if (!stage) return;
  if (plateObserver) plateObserver.disconnect();
  plateObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      const bookId = Number(visible.target.dataset.book);
      const chapter = Number(visible.target.dataset.chapter);
      if (!bookId || !chapter) return;
      const book = state.books.find((row) => row.id === bookId);
      if (book) writeHash(state.tx, book, chapter, "scroll");
    },
    { rootMargin: "-20% 0px -55% 0px", threshold: [0.2, 0.4] }
  );
  stage.querySelectorAll(".page-plate[data-book]").forEach((node) => plateObserver.observe(node));
}

function attachMoreObserver() {
  if (state.mode !== "scroll") return;
  const sentinel = $("scroll-more");
  if (!sentinel) return;
  if (moreObserver) moreObserver.disconnect();
  moreObserver = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) appendNextChapter();
    },
    { rootMargin: "800px 0px" }
  );
  moreObserver.observe(sentinel);
}

async function appendNextChapter() {
  if (state.mode !== "scroll" || state.loadingMore || !state.tx) return;
  const next = peekNext(state.tail?.book || state.book, state.tail?.chapter || state.chapter);
  if (!next) {
    const sentinel = $("scroll-more");
    if (sentinel) sentinel.innerHTML = `<p class="scroll-end">${SITE} · end of this translation</p>`;
    return;
  }
  state.loadingMore = true;
  const sentinel = $("scroll-more");
  if (sentinel) sentinel.dataset.loading = "1";
  try {
    const bookMeta = state.books.find((b) => b.id === next.book);
    const { verses } = await loadChapter(state.tx, bookMeta, next.chapter);
    const heading = `${bookMeta.name} ${next.chapter} — ${state.tx.native}`;
    const pageNo = bookMeta.id * 200 + next.chapter;
    const html = renderPlates(heading, verses, pageNo, bookMeta.id, next.chapter);
    sentinel.insertAdjacentHTML("beforebegin", html);
    state.tail = next;
    state.skips = 0;
    attachPlateObserver();
  } catch {
    state.tail = next;
    state.skips += 1;
    state.loadingMore = false;
    if (state.skips < 12) {
      await appendNextChapter();
      return;
    }
    if (sentinel) sentinel.innerHTML = `<p class="scroll-end">Open text ended for this stretch · ${SITE}</p>`;
    return;
  } finally {
    state.loadingMore = false;
    if (sentinel) delete sentinel.dataset.loading;
  }
}

async function render() {
  const tx = state.tx;
  if (!tx) return;
  const book = currentBook();
  const chapter = state.chapter;
  const title = `${book.name} ${chapter}`;
  const pageNo = book.id * 200 + chapter;
  const search = $("langSearch");
  if (search) search.value = `${tx.native} · ${tx.title}`;
  document.documentElement.lang = tx.iso || "en";
  document.documentElement.dir = tx.rtl ? "rtl" : "ltr";
  setStatus(`Loading ${title} in ${tx.language}… ${SITE}`);
  disconnectObservers();
  state.tail = { book: book.id, chapter };
  state.skips = 0;

  const views = {
    scroll: $("view-scroll"),
    txt: $("view-txt"),
    pdf: $("view-pdf"),
  };
  for (const [mode, node] of Object.entries(views)) {
    if (node) node.hidden = mode !== state.mode;
  }

  try {
    const { source, verses } = await loadChapter(tx, book, chapter);
    const heading = `${title} — ${tx.native}`;
    const pages = chunkVerses(verses);
    if (views.scroll) {
      views.scroll.innerHTML =
        renderPlates(heading, verses, pageNo, book.id, chapter) +
        `<div id="scroll-more" class="scroll-more" aria-hidden="true"></div>`;
    }
    if (views.pdf) {
      views.pdf.innerHTML = pages
        .map(
          (part, index) =>
            `<div class="pdf-sheet">${plate(
              index === 0 ? heading : `${heading} (cont.)`,
              part,
              pageNo + index,
              book.id,
              chapter
            )}</div>`
        )
        .join("");
    }
    if (views.txt) views.txt.innerHTML = `<pre>${toTxt(tx, book, chapter, verses, source, pageNo)}</pre>`;
    setStatus(`${describeTx(tx)} · ${verses.length} verses · marked ${SITE}`);
    writeHash();
    attachMoreObserver();
    attachPlateObserver();
  } catch (err) {
    const message = err.message || String(err);
    const empty = plate(
      `${title} — ${tx.native}`,
      [{ verse: 1, text: `Open text is not reachable yet for this translation. ${message}` }],
      pageNo,
      book.id,
      chapter
    );
    if (views.scroll) {
      views.scroll.innerHTML = empty + `<div id="scroll-more" class="scroll-more" aria-hidden="true"></div>`;
    }
    if (views.pdf) views.pdf.innerHTML = `<div class="pdf-sheet">${empty}</div>`;
    if (views.txt) {
      views.txt.innerHTML = `<pre>${txtBanner(pageNo, title)}\n\n${message}\n\n${SITE}\n${CREDIT}\n</pre>`;
    }
    setStatus(message);
    attachMoreObserver();
  }
}

async function selectTranslation(id) {
  const tx = state.catalog.translations.find((row) => row.id === id);
  if (!tx) return;
  state.tx = tx;
  localStorage.setItem(STORAGE_TX, id);
  const panel = $("langPanel");
  if (panel) panel.hidden = true;
  await discoverBooks(tx);
  applyBooksFor(tx);
  await render();
}

function stepChapter(delta) {
  const book = currentBook();
  let next = state.chapter + delta;
  let bookId = state.book;
  if (next < 1) {
    const idx = Math.max(0, state.books.findIndex((b) => b.id === bookId) - 1);
    const prev = state.books[idx];
    bookId = prev.id;
    next = delta < 0 ? prev.chapters : 1;
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
  const pre = $("view-txt")?.querySelector("pre");
  if (!pre || !state.tx) return;
  const book = currentBook();
  const name = `${SITE.replace(".", "")}-${state.tx.id}-${book.usfm}-${state.chapter}.txt`;
  const blob = new Blob([pre.textContent], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

function startRain() {
  const canvas = $("rain");
  if (!canvas) return;
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

function bindReader() {
  $("themeBtn")?.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem(STORAGE_THEME, next);
    applyTheme(next);
  });
  $("langSearch")?.addEventListener("focus", () => renderLangList($("langSearch").value));
  $("langSearch")?.addEventListener("input", () => renderLangList($("langSearch").value));
  $("langPanel")?.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-id]");
    if (btn) selectTranslation(btn.dataset.id);
  });
  $("bookSelect")?.addEventListener("change", (event) => {
    state.book = Number(event.target.value);
    state.chapter = 1;
    fillChapters();
    render();
  });
  $("chapterSelect")?.addEventListener("change", (event) => {
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
  $("prevBtn")?.addEventListener("click", () => stepChapter(-1));
  $("nextBtn")?.addEventListener("click", () => stepChapter(1));
  $("downloadTxtBtn")?.addEventListener("click", downloadTxt);
  $("printBtn")?.addEventListener("click", () => {
    state.mode = "pdf";
    const radio = document.querySelector("input[name=mode][value=pdf]");
    if (radio) radio.checked = true;
    render().then(() => window.print());
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#langPanel") && !event.target.closest("#langSearch")) {
      const panel = $("langPanel");
      if (panel) panel.hidden = true;
    }
  });
}

function findTranslation(idOrIso) {
  if (!idOrIso || !state.catalog) return null;
  const exact = state.catalog.translations.find((row) => row.id === idOrIso);
  if (exact) return exact;
  const lower = idOrIso.toLowerCase();
  return (
    state.catalog.translations.find((row) => row.id.toLowerCase() === lower) ||
    state.catalog.translations.find((row) => row.iso === lower) ||
    null
  );
}

function parseHash() {
  const raw = location.hash.replace(/^#/, "");
  if (!raw) return;
  const [id, usfm, chapter, mode] = raw.split("/");
  const tx = findTranslation(id);
  if (tx) state.tx = tx;
  if (usfm && state.books.length) {
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

function pickDefaultTx() {
  const savedTx = localStorage.getItem(STORAGE_TX);
  const savedIso = localStorage.getItem(STORAGE_LANG);
  return (
    findTranslation(savedTx) ||
    findTranslation("engwebp") ||
    findTranslation("eng-web") ||
    findTranslation(savedIso) ||
    findTranslation("eng") ||
    state.catalog.translations[0]
  );
}

async function bootReader() {
  applyTheme(preferredTheme());
  startRain();
  bindReader();
  const [catalog, books] = await Promise.all([
    fetchJson("data/translations.json"),
    fetchJson("data/books.json"),
  ]);
  state.catalog = catalog;
  state.allBooks = books;
  state.books = books;
  state.tx = pickDefaultTx();
  parseHash();
  await discoverBooks(state.tx);
  applyBooksFor(state.tx);
  parseHash();
  fillBooks();
  const count = $("txCount");
  if (count) count.textContent = `${catalog.count.toLocaleString()} translations`;
  await render();
}

function printHref(tx) {
  return tx.printPath ? `${GITHUB_PRINT}/${tx.printPath.split("/").map(encodeURIComponent).join("/")}` : GITHUB_PRINT;
}

function renderPrintCatalog(filter = "") {
  const list = $("printList");
  if (!list || !state.catalog) return;
  const q = filter.trim().toLowerCase();
  const rows = state.catalog.translations.filter((tx) => matchesTranslation(tx, q));
  const shown = rows.slice(0, q ? 400 : 200);
  list.innerHTML = shown
    .map((tx) => {
      const book = (tx.coverage === "bible" ? "gen" : "mat");
      return `<article class="print-card">
        <a class="print-open" href="./#${tx.id}/${book}/1/scroll">${tx.native || tx.language}
          <small>${tx.title} · ${tx.language} · ${coverageLabel(tx)}</small>
        </a>
        <a class="ghost" href="${printHref(tx)}" target="_blank" rel="noopener">PDF</a>
      </article>`;
    })
    .join("");
  const status = $("status");
  if (status) {
    status.textContent = `${shown.length} of ${rows.length} · ${state.catalog.count} Matrix Holy Bibles · ${SITE}`;
  }
}

function bindPrintCatalog() {
  $("themeBtn")?.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem(STORAGE_THEME, next);
    applyTheme(next);
  });
  $("printSearch")?.addEventListener("input", (event) => renderPrintCatalog(event.target.value));
}

async function bootPrintCatalog() {
  applyTheme(preferredTheme());
  startRain();
  bindPrintCatalog();
  state.catalog = await fetchJson("data/translations.json");
  const count = $("txCount");
  if (count) count.textContent = `${state.catalog.count.toLocaleString()} translations`;
  renderPrintCatalog();
}

if ($("view-scroll")) {
  bootReader().catch((err) => setStatus(err.message || String(err)));
} else if ($("printCatalog")) {
  bootPrintCatalog().catch((err) => setStatus(err.message || String(err)));
}

const SITE = "ChristSupply.Net";
const TX = "engwebp";
const TOKEN_RE = /(God(?:'s)?|LORD|Jesus Christ|Jesus|Christ|Holy Spirit|Spirit)/g;

const $ = (id) => document.getElementById(id);
const stage = $("stage");
const pageMark = $("pageMark");

const state = {
  books: [],
  cache: new Map(),
};

function hashParts() {
  const raw = decodeURIComponent((location.hash || "#cover").replace(/^#/, ""));
  const [kind, a, b] = raw.split("/");
  return { kind: kind || "cover", a, b };
}

function go(hash) {
  location.hash = hash;
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
      pushText((el.textContent || "").replace(/^\s*\d+\s*/, ""));
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

function markWords(text) {
  return text.replace(TOKEN_RE, (token) => {
    const key = token.toLowerCase().replace("'s", "");
    if (key === "god") return `<a class="god" href="#word/god">${token}</a>`;
    if (key === "jesus" || key === "christ" || key === "jesus christ") {
      return `<a class="jesus" href="#word/jesus">${token}</a>`;
    }
    if (key === "lord") return `<a class="lord" href="#word/lord">${token}</a>`;
    return `<a class="spirit" href="#word/spirit">${token}</a>`;
  });
}

function btn(href, title, sub = "") {
  return `<a class="btn" href="${href}">${title}${sub ? `<small>${sub}</small>` : ""}</a>`;
}

function cover() {
  pageMark.textContent = "Page 1 · ChristSupply.Net";
  return `
    <p class="center">C H R I S T . S U P P L Y</p>
    <div class="cross" aria-hidden="true"></div>
    <h1 class="mint">Holy Bible</h1>
    <p class="mint center">World | English | Bible</p>
    <p class="lede">Offline reading packet. Open Source to fork and change the theme.</p>
    <p class="lede">Don't forget to smile today! Because <a class="jesus" href="#word/jesus">Jesus</a> loves you! (:</p>
    <p class="lede">May this Bible bridge every gap and every nation in Jesus name amen.</p>
    <div class="tiles"><div class="tile"></div><div class="tile web"></div></div>
    <p class="mint center">WEB Protestant Edition - Public Domain</p>
    ${btn("#root", "Open the clickable pages")}
  `;
}

function root() {
  pageMark.textContent = "Root Index · ChristSupply.Net";
  return `
    <h1>Root Index</h1>
    <p class="center">Go to:</p>
    <p class="center">WORD</p>
    ${btn("#word-of-god", "THE WORD OF GOD")}
    ${btn("#ot", "OLD TESTAMENT")}
    ${btn("#nt", "NEW TESTAMENT")}
    ${btn("#rainbow", "RAINBOW LETTERS")}
    ${btn("#library", "FULL LIBRARY", "ALL BOOKS, CHAPTERS, INDEXES")}
  `;
}

function rainbow() {
  pageMark.textContent = "Rainbow · ChristSupply.Net";
  const colors = [
    ["#ff4848", "RED LETTER"],
    ["#ff8c30", "ORANGE LETTER"],
    ["#e6b430", "GOLD LETTER"],
    ["#ffdc40", "YELLOW LETTER"],
    ["#50ff8c", "GREEN LETTER"],
    ["#48e6e6", "CYAN LETTER"],
    ["#5096ff", "BLUE LETTER"],
    ["#b478ff", "PURPLE LETTER"],
    ["#ff78b4", "PINK LETTER"],
  ];
  return `<h2>RAINBOW</h2><div class="rainbow">${colors
    .map(([color, label]) => `<a class="btn" href="#read/JHN/1" style="color:${color}">${label}</a>`)
    .join("")}</div>`;
}

function wordOfGod() {
  pageMark.textContent = "The Word of God · ChristSupply.Net";
  return `
    <h1>The Word of God</h1>
    <p class="lede">"In the beginning"</p>
    ${btn("#book/GEN", "Genesis", "IN THE BEGINNING GOD CREATED")}
    ${btn("#book/JHN", "John", "IN THE BEGINNING WAS THE WORD")}
    ${btn("#library", "Full Library", "ALL BOOKS, CHAPTERS, INDEXES")}
    <a class="back" href="#root">Back to Root Index</a>
  `;
}

function bookList(title, rows) {
  pageMark.textContent = `${title} · ChristSupply.Net`;
  return `<h1>${title}</h1><div class="grid">${rows
    .map((book) => btn(`#book/${book.usfm}`, book.name))
    .join("")}</div><a class="back" href="#root">Root Index</a>`;
}

function bookPage(book) {
  pageMark.textContent = `${book.name} · ChristSupply.Net`;
  const links = Array.from({ length: book.chapters }, (_, i) => i + 1)
    .map((n) => `<a class="btn" href="#read/${book.usfm}/${n}">${n}</a>`)
    .join("");
  return `<h1>${book.name}</h1><p class="center">Click a chapter</p><div class="chapters">${links}</div>
    <a class="back" href="#library">Full Library</a>`;
}

function wordPage(key) {
  const copy = {
    god: ["GOD", "God created. God said. God saw that it was good."],
    jesus: ["JESUS", "Jesus Christ, the Word made flesh."],
    lord: ["THE LORD", "The LORD said. I am the LORD."],
    spirit: ["SPIRIT", "God's Spirit was hovering over the waters."],
  }[key] || ["WORD", "All Users Are Created Equally By God."];
  pageMark.textContent = `${copy[0]} · ChristSupply.Net`;
  return `<h1 class="mint">${copy[0]}</h1><p class="lede">${copy[1]}</p>
    ${btn("#read/GEN/1", "Read Genesis 1")}${btn("#read/JHN/1", "Read John 1")}
    ${btn("#root", "Back to Root Index")}`;
}

async function loadChapter(book, chapter) {
  const key = `${book.usfm}:${chapter}`;
  if (state.cache.has(key)) return state.cache.get(key);
  const file = ebibleFilename(book.usfm, chapter);
  const html = await fetchText(`/api/ebible/${TX}/${file}`);
  const verses = parseEbibleHtml(html);
  state.cache.set(key, verses);
  return verses;
}

async function readPage(book, chapter) {
  pageMark.textContent = `${book.name} ${chapter} · ChristSupply.Net`;
  const prev = chapter > 1 ? `#read/${book.usfm}/${chapter - 1}` : `#book/${book.usfm}`;
  const next = chapter < book.chapters ? `#read/${book.usfm}/${chapter + 1}` : "#library";
  let body = `<p class="status">Loading ${book.name} ${chapter}…</p>`;
  try {
    const verses = await loadChapter(book, chapter);
    body = verses
      .map((v) => `<p class="verse"><b>${v.verse}</b> ${markWords(v.text)}</p>`)
      .join("");
  } catch (err) {
    body = `<p class="status">${err.message}. Serve with scripts/serve.py so eBible can be proxied.</p>`;
  }
  return `
    <h1>${book.name} - Chapter ${chapter}</h1>
    <div class="grid">
      ${btn("#word-of-god", "Word of God")}
      ${btn(`#book/${book.usfm}`, "Chapters")}
      ${btn(prev, chapter > 1 ? "Previous" : "Start")}
      ${btn(next, chapter < book.chapters ? "Next" : "Library")}
    </div>
    ${btn("https://christsupply.net", "Share")}
    ${body}
  `;
}

async function render() {
  if (!state.books.length) return;
  const { kind, a, b } = hashParts();
  const byUsfm = Object.fromEntries(state.books.map((row) => [row.usfm, row]));
  const ot = state.books.filter((row) => row.testament === "OT");
  const nt = state.books.filter((row) => row.testament === "NT");
  if (kind === "root") stage.innerHTML = root();
  else if (kind === "rainbow") stage.innerHTML = rainbow();
  else if (kind === "word-of-god") stage.innerHTML = wordOfGod();
  else if (kind === "ot") stage.innerHTML = bookList("Old Testament", ot);
  else if (kind === "nt") stage.innerHTML = bookList("New Testament", nt);
  else if (kind === "library") stage.innerHTML = bookList("Full Library", state.books);
  else if (kind === "book" && byUsfm[a]) stage.innerHTML = bookPage(byUsfm[a]);
  else if (kind === "word") stage.innerHTML = wordPage(a);
  else if (kind === "read" && byUsfm[a]) stage.innerHTML = await readPage(byUsfm[a], Number(b) || 1);
  else stage.innerHTML = cover();
}

async function boot() {
  state.books = await fetchJson("data/books.json");
  window.addEventListener("hashchange", () => {
    render().catch((err) => {
      stage.innerHTML = `<p class="status">${err.message}</p>`;
    });
  });
  await render();
}

boot().catch((err) => {
  stage.innerHTML = `<p class="status">${err.message}</p>`;
});

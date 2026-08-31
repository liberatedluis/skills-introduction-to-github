const RAINBOW_ORDER = ["red", "orange", "gold", "yellow", "green", "cyan", "blue", "purple", "pink"];
const THEME_GROUPS = [
  {
    label: "WHITE",
    ids: ["iam", "lord-said", "arcs"],
  },
  {
    label: "NOW",
    ids: ["afraid", "help", "mercy"],
  },
  {
    label: "LIFE",
    ids: ["believe", "love", "peace", "sin", "wrath"],
  },
];

const STATIC_LINKS = {
  iam: { title: "I AM THE LORD", blurb: "116 names and titles — tap one to open its Scriptures." },
  arcs: { title: "ARCS OF GOD", blurb: "500 Christ-centered scripture arcs in 10 groups of 50." },
  help: { title: "HELP ME NOW GOD", blurb: "Short hope for this moment — 8 paths." },
};

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function bookMap(books) {
  const map = new Map();
  for (const book of books || []) map.set(book.id, book);
  return map;
}

function bookName(books, id) {
  return bookMap(books).get(Number(id))?.name || `Book ${id}`;
}

function refLabel(books, book, chapter, verse) {
  return `${bookName(books, book)} ${chapter}:${verse}`;
}

function countPacked(versesByBook) {
  return Object.values(versesByBook || {}).reduce((sum, rows) => sum + rows.length, 0);
}

function chrome(data, extra = "") {
  return `
    <p class="idx-equal">${esc(data.equal).replace("God", "<b>God</b>")}</p>
    ${extra}
    <p class="idx-liberate">${esc(data.liberate)}</p>
    <p class="idx-links">
      <a href="${esc(data.sourceUrl)}" target="_blank" rel="noopener">Source</a>
      <span>|</span>
      <button type="button" class="idx-text" data-index="">Contents</button>
      <span>|</span>
      <button type="button" class="idx-text" data-share="1">Share</button>
    </p>`;
}

function backRow(path, label = "Back to Root Index") {
  const parent = path.slice(0, -1);
  const target = parent.length ? parent.join("/") : "";
  return `<button type="button" class="idx-back" data-index="${esc(target)}">${esc(label)}</button>`;
}

function cardButton(path, title, subtitle = "", color = "") {
  const style = color ? ` style="color:${esc(color)}"` : "";
  return `<button type="button" class="idx-card" data-index="${esc(path)}">
    <strong${style}>${esc(title)}</strong>
    ${subtitle ? `<span>${esc(subtitle)}</span>` : ""}
  </button>`;
}

function verseButtons(books, verses) {
  if (!(verses || []).length) return `<p class="idx-empty">No linked verses printed for this entry.</p>`;
  return verses
    .map(([book, chapter, verse]) => {
      const label = refLabel(books, book, chapter, verse);
      return `<button type="button" class="idx-verse" data-go-book="${book}" data-go-chapter="${chapter}" data-go-verse="${verse}">${esc(label)}</button>`;
    })
    .join("");
}

function packedBookList(books, versesByBook, basePath) {
  const ids = Object.keys(versesByBook || {}).map(Number).sort((a, b) => a - b);
  if (!ids.length) return `<p class="idx-empty">No verses in this translation catalog yet.</p>`;
  return ids
    .map((id) => {
      const n = (versesByBook[String(id)] || []).length;
      return cardButton(`${basePath}/${id}`, bookName(books, id), `${n} verse${n === 1 ? "" : "s"}`);
    })
    .join("");
}

function packedVerseList(books, versesByBook, bookId) {
  const rows = versesByBook?.[String(bookId)] || [];
  return rows
    .map(([chapter, verse]) => {
      const label = refLabel(books, bookId, chapter, verse);
      return `<button type="button" class="idx-verse" data-go-book="${bookId}" data-go-chapter="${chapter}" data-go-verse="${verse}">${esc(label)}</button>`;
    })
    .join("");
}

function rootView(data) {
  const rainbow = RAINBOW_ORDER.map((id) => {
    const row = data.rainbow[id];
    return cardButton(id, row.title.replace(/ Index$/i, "").toUpperCase(), `${row.count.toLocaleString()} verses`, row.color);
  }).join("");

  const themeBlocks = THEME_GROUPS.map((group) => {
    const buttons = group.ids
      .map((id) => {
        if (id === "iam") return cardButton("iam", STATIC_LINKS.iam.title, STATIC_LINKS.iam.blurb);
        if (id === "arcs") return cardButton("arcs", STATIC_LINKS.arcs.title, `${data.arcs.length} arcs`);
        if (id === "help") return cardButton("help", STATIC_LINKS.help.title, STATIC_LINKS.help.blurb);
        const row = data.themes[id];
        if (!row) return "";
        return cardButton(id, row.title.replace(/ Index$/i, "").toUpperCase(), row.blurb);
      })
      .join("");
    return `<h3 class="idx-kicker">${esc(group.label)}</h3>${buttons}`;
  }).join("");

  return `
    <header class="idx-hero">
      <p class="idx-brand">C H R I S T . S U P P L Y</p>
      <h1>Root Index</h1>
      <p class="idx-sub">Go to the Word, the rainbow letters, and the clickable study indexes from the offline WEB packet.</p>
    </header>
    <h3 class="idx-kicker">WORD</h3>
    ${cardButton("word", "THE WORD OF GOD", "In the beginning")}
    ${cardButton("ot", "OLD TESTAMENT", "Genesis through Malachi")}
    ${cardButton("nt", "NEW TESTAMENT", "Matthew through Revelation")}
    <h3 class="idx-kicker">RAINBOW</h3>
    ${rainbow}
    ${themeBlocks}
    <h3 class="idx-kicker">PEOPLE</h3>
    ${cardButton("women", "WOMEN OF GOD", `${data.women.length} people`)}
    ${cardButton("men", "MEN OF GOD", `${data.men.length} people`)}
    <h3 class="idx-kicker">WORDS</h3>
    ${cardButton("words", "WORD INDEX", `${data.dictionary.length} words`)}
    ${cardButton("roots", "WORD ROOTS", `${data.roots.length} core words`)}
  `;
}

function wordOfGodView(data) {
  return `
    <h2>The Word of God</h2>
    <p class="idx-sub">“${esc(data.wordOfGod.quote)}”</p>
    ${data.wordOfGod.entries
      .map((row) => {
        if (row.id === "library") return cardButton("library", row.title, row.subtitle);
        return `<button type="button" class="idx-card" data-go-book="${row.book}" data-go-chapter="${row.chapter}" data-go-verse="1">
          <strong>${esc(row.title)}</strong><span>${esc(row.subtitle)}</span>
        </button>`;
      })
      .join("")}
  `;
}

function testamentView(books, testament, title, blurb) {
  const rows = (books || []).filter((book) => book.testament === testament);
  return `
    <h2>${esc(title)}</h2>
    <p class="idx-sub">${esc(blurb)}</p>
    ${rows.map((book) => cardButton(`library/${book.id}`, book.name, `${book.chapters} chapters`)).join("")}
  `;
}

function libraryView(books, bookId) {
  if (!bookId) {
    return `
      <h2>Full Library</h2>
      <p class="idx-sub">All books, chapters, and indexes.</p>
      ${cardButton("ot", "Old Testament", "Genesis through Malachi")}
      ${cardButton("nt", "New Testament", "Matthew through Revelation")}
      ${(books || []).map((book) => cardButton(`library/${book.id}`, book.name, `${book.chapters} chapters`)).join("")}
    `;
  }
  const book = bookMap(books).get(Number(bookId));
  if (!book) return `<p class="idx-empty">That book is not in this translation.</p>`;
  const chapters = Array.from({ length: book.chapters }, (_, i) => i + 1)
    .map(
      (chapter) =>
        `<button type="button" class="idx-chip" data-go-book="${book.id}" data-go-chapter="${chapter}" data-go-verse="1">Chapter ${chapter}</button>`
    )
    .join("");
  return `<h2>${esc(book.name)}</h2><p class="idx-sub">${book.chapters} chapters · tap to open in the Matrix scroller</p><div class="idx-chips">${chapters}</div>`;
}

function packedIndexView(books, row, path, kind) {
  const bookId = path[1];
  if (!bookId) {
    return `
      <h2 style="color:${esc(row.color || "")}">${esc(row.title)}</h2>
      <p class="idx-sub">${esc(row.blurb)} ${countPacked(row.versesByBook).toLocaleString()} linked verses.</p>
      ${packedBookList(books, row.versesByBook, kind)}
    `;
  }
  return `
    <h2>${esc(bookName(books, bookId))}</h2>
    <p class="idx-sub">${esc(row.title)}</p>
    <div class="idx-verse-list">${packedVerseList(books, row.versesByBook, bookId)}</div>
  `;
}

function listCardsView(title, blurb, items, base, books) {
  const sub = items[1];
  if (!sub) {
    return `
      <h2>${esc(title)}</h2>
      <p class="idx-sub">${esc(blurb)}</p>
      ${items[0]
        .map((row) =>
          cardButton(
            `${base}/${row.id}`,
            row.title,
            row.note || row.roots || (row.count ? `${row.count}×` : `${(row.verses || []).length} verses`)
          )
        )
        .join("")}
    `;
  }
  const row = items[0].find((item) => item.id === sub);
  if (!row) return `<p class="idx-empty">Not found.</p>`;
  return `
    <h2>${esc(row.title)}</h2>
    ${row.roots ? `<p class="idx-roots">${esc(row.roots)}</p>` : ""}
    <p class="idx-sub">${esc(row.note || blurb)}</p>
    <div class="idx-verse-list">${verseButtons(books, row.verses)}</div>
  `;
}

function dictionaryView(data, books, path) {
  const letters = [...new Set(data.dictionary.map((row) => row.letter).filter((letter) => /[A-Z]/.test(letter)))];
  const letter = path[1];
  const wordId = path[2];
  if (!letter) {
    return `
      <h2>Word Index</h2>
      <p class="idx-sub">Bible words with meaning notes. See also Word Roots.</p>
      <div class="idx-chips">
        ${letters
          .map((item) => {
            const n = data.dictionary.filter((row) => row.letter === item).length;
            return `<button type="button" class="idx-chip" data-index="words/${item}">${esc(item)} <em>${n}</em></button>`;
          })
          .join("")}
      </div>
    `;
  }
  const rows = data.dictionary.filter((row) => row.letter === letter);
  if (!wordId) {
    return `
      <h2>${esc(letter)} Word Index</h2>
      <p class="idx-sub">${rows.length} words</p>
      ${rows.map((row) => cardButton(`words/${letter}/${row.id}`, row.word, `${row.uses.toLocaleString()} uses`)).join("")}
    `;
  }
  const row = rows.find((item) => item.id === wordId) || data.dictionary.find((item) => item.id === wordId);
  if (!row) return `<p class="idx-empty">Word not found.</p>`;
  return `
    <h2>${esc(row.n.toString().padStart(4, "0"))}. ${esc(row.word)}</h2>
    <p class="idx-sub">${esc(row.note)}</p>
    <p class="idx-sub">Appears ${row.uses.toLocaleString()} times in this WEB edition.${
      (row.verses || []).length ? " Click a verse to jump into the Word." : ""
    }</p>
    <div class="idx-verse-list">${verseButtons(books, row.verses)}</div>
  `;
}

function arcsView(data, books, path) {
  const group = path[1];
  const arcId = path[2];
  if (!group) {
    const blocks = Array.from({ length: 10 }, (_, i) => {
      const start = i * 50 + 1;
      const end = start + 49;
      const first = data.arcs.find((row) => row.n === start);
      const last = data.arcs.find((row) => row.n === end) || data.arcs[data.arcs.length - 1];
      return cardButton(
        `arcs/${start}-${end}`,
        `Arcs ${String(start).padStart(3, "0")}-${String(end).padStart(3, "0")}`,
        `${first?.title || ""} to ${last?.title || ""}`
      );
    }).join("");
    return `<h2>The Arcs of GOD</h2><p class="idx-sub">${esc(STATIC_LINKS.arcs.blurb)}</p>${blocks}`;
  }
  const [start, end] = group.split("-").map(Number);
  const rows = data.arcs.filter((row) => row.n >= start && row.n <= end);
  if (!arcId) {
    return `
      <h2>Arcs ${esc(group)}</h2>
      ${rows.map((row) => cardButton(`arcs/${group}/${row.id}`, `${String(row.n).padStart(3, "0")}. ${row.title}`, row.note)).join("")}
    `;
  }
  const row = data.arcs.find((item) => item.id === arcId);
  if (!row) return `<p class="idx-empty">Arc not found.</p>`;
  return `
    <h2>${String(row.n).padStart(3, "0")}. ${esc(row.title)}</h2>
    <p class="idx-sub">${esc(row.note)}</p>
    <div class="idx-verse-list">${verseButtons(books, row.verses)}</div>
  `;
}

export function renderIndexHTML(data, books, path) {
  const root = path[0] || "";
  let body = "";
  if (!root) body = rootView(data);
  else if (root === "word") body = wordOfGodView(data);
  else if (root === "ot") body = testamentView(books, "OT", "Old Testament", "Genesis through Malachi, linked into each book’s chapter index.");
  else if (root === "nt") body = testamentView(books, "NT", "New Testament", "Matthew through Revelation, linked into each book’s chapter index.");
  else if (root === "library") body = libraryView(books, path[1]);
  else if (data.rainbow[root]) body = packedIndexView(books, data.rainbow[root], path, root);
  else if (data.themes[root]) body = packedIndexView(books, data.themes[root], path, root);
  else if (root === "iam") body = listCardsView("I AM THE LORD", STATIC_LINKS.iam.blurb, [data.iam, path[1]], "iam", books);
  else if (root === "help") body = listCardsView("Help Me Now God", STATIC_LINKS.help.blurb, [data.help, path[1]], "help", books);
  else if (root === "women") body = listCardsView("Women of God", "Courage, faith, and faithfulness.", [data.women, path[1]], "women", books);
  else if (root === "men") body = listCardsView("Men of God", "Faith, repentance, and courage.", [data.men, path[1]], "men", books);
  else if (root === "roots") body = listCardsView("Word Roots", "66 core words with Hebrew / Aramaic / Greek roots.", [data.roots, path[1]], "roots", books);
  else if (root === "words") body = dictionaryView(data, books, path);
  else if (root === "arcs") body = arcsView(data, books, path);
  else body = `<p class="idx-empty">Unknown index.</p>`;

  const showBack = Boolean(root);
  return `
    <article class="idx-sheet">
      ${chrome(data, `${showBack ? backRow(path) : ""}<div class="idx-body">${body}</div>`)}
    </article>
  `;
}

export async function loadIndexes() {
  const res = await fetch("data/indexes.json");
  if (!res.ok) throw new Error("index catalog missing");
  return res.json();
}

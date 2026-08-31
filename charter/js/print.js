import { documents } from "./texts.js";

export function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function page(inner, extraClass = "") {
  return `<section class="sheet ${extraClass}">${inner}</section>`;
}

function marks(left, right, inner) {
  return `
    <header class="mark"><span>Charter</span><span>${escapeHtml(left)}</span></header>
    <div class="body">${inner}</div>
    <footer class="mark"><span>Created by Christ Supply · <a href="https://christ.supply/support-us">Support Here</a></span><span>${escapeHtml(right)}</span></footer>
  `;
}

export function renderPrintPages(docs, theme, options = {}) {
  const heading = options.heading || (docs.length === 1 ? docs[0].title : "Charter");
  const lede = options.lede || (docs.length === 1
    ? `${docs[0].blurb} One thought per page.`
    : "Three founding texts. One thought per page.");
  const title = page(
    marks(
      theme === "dark" ? "Dark edition" : "Light edition",
      "One thought at a time",
      `
      <p class="kicker">${escapeHtml(docs.length > 2 ? "Three founding texts" : "Charter")}</p>
      <h1>${escapeHtml(heading)}</h1>
      <p class="lede">${escapeHtml(lede)}</p>
      <ul class="list">
        ${docs.map((doc) => `<li>${escapeHtml(doc.title)}</li>`).join("")}
      </ul>
      <p class="source">National Archives transcriptions. Labels are not the legal text.</p>
    `
    ),
    "title-page"
  );

  const sections = docs.map((doc) => {
    const start = page(
      marks(
        doc.year,
        doc.short,
        `
        <p class="kicker">${escapeHtml(doc.year)} · ${doc.bites.length} bites</p>
        <h1>${escapeHtml(doc.title)}</h1>
        <p class="lede">${escapeHtml(doc.blurb)}</p>
      `
      ),
      "section-page"
    );
    const bites = doc.bites.map((bite, index) =>
      page(
        marks(
          `${doc.short} · ${bite.group}`,
          `${index + 1} of ${doc.bites.length}`,
          `
          <h1 class="cite">${escapeHtml(bite.cite)}</h1>
          ${bite.label ? `<p class="label">${escapeHtml(bite.label)}</p>` : ""}
          <p class="bite">${escapeHtml(bite.text)}</p>
          ${bite.note ? `<p class="note">${escapeHtml(bite.note)}</p>` : ""}
          <p class="source">Text: ${escapeHtml(doc.sourceLabel)}. Labels are not the legal text.</p>
        `
        )
      )
    );
    return start + bites.join("");
  });

  return title + sections.join("");
}

if (typeof document !== "undefined" && document.body && !globalThis.__CHARTER_PDF__) {
  const params = new URLSearchParams(location.search);
  const theme = params.get("theme") === "dark" ? "dark" : "light";
  const only = params.get("doc");
  const docs = only ? documents.filter((doc) => doc.id === only) : documents;
  document.documentElement.dataset.theme = theme;
  document.title = `Charter · ${theme} PDF`;
  document.body.innerHTML = renderPrintPages(docs, theme);
}

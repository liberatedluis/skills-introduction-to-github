import { catalog, homeDocuments, findBite, hrefFor } from "./texts.js";

const THEME_KEY = "charter-theme";
const root = document.documentElement;
const homeView = document.getElementById("home");
const readerView = document.getElementById("reader");
const crumb = document.getElementById("crumb");
const citeEl = document.getElementById("cite");
const labelEl = document.getElementById("label");
const biteEl = document.getElementById("bite");
const noteEl = document.getElementById("note");
const sourceEl = document.getElementById("source");
const progressMeta = document.getElementById("progressMeta");
const progressBar = document.getElementById("progressBar");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const copyBtn = document.getElementById("copyBtn");
const shareBtn = document.getElementById("shareBtn");
const continueLink = document.getElementById("continueLink");
const themeBtn = document.getElementById("themeBtn");
const contentsBtn = document.getElementById("contentsBtn");
const drawer = document.getElementById("drawer");
const rail = document.getElementById("rail");
const drawerContents = document.getElementById("drawerContents");
const toast = document.getElementById("toast");

let current = null;
let touchStartX = 0;

function preferredTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeBtn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
  themeBtn.textContent = theme === "dark" ? "Light" : "Dark";
  document.querySelector('meta[name="theme-color"]').setAttribute("content", theme === "dark" ? "#161310" : "#f3ead8");
}

function parseHash() {
  const raw = decodeURIComponent(location.hash.replace(/^#\/?/, "")).trim();
  if (!raw) return { page: "home" };
  const [docId, biteId] = raw.split("/");
  if (!docId) return { page: "home" };
  if (!catalog[docId]) return { page: "home" };
  if (!biteId) return { page: "bite", docId, biteId: catalog[docId].bites[0].id };
  return { page: "bite", docId, biteId };
}

function shareUrl() {
  return `${location.origin}${location.pathname}${location.hash}`;
}

function shareText(doc, bite) {
  return `${bite.text}\n\n— ${doc.title}, ${bite.cite}`;
}

function groupBites(doc) {
  const groups = [];
  for (const bite of doc.bites) {
    const last = groups[groups.length - 1];
    if (!last || last.name !== bite.group) groups.push({ name: bite.group, bites: [bite] });
    else last.bites.push(bite);
  }
  return groups;
}

function renderContents(doc, activeId, into) {
  const frag = document.createDocumentFragment();
  const title = document.createElement("h2");
  title.textContent = "Contents";
  frag.appendChild(title);
  for (const group of groupBites(doc)) {
    const section = document.createElement("section");
    section.className = "contents-group";
    const heading = document.createElement("h3");
    heading.textContent = group.name;
    section.appendChild(heading);
    for (const bite of group.bites) {
      const link = document.createElement("a");
      link.href = hrefFor(doc.id, bite.id);
      link.textContent = bite.cite;
      if (bite.id === activeId) link.setAttribute("aria-current", "page");
      section.appendChild(link);
    }
    frag.appendChild(section);
  }
  into.replaceChildren(frag);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 1600);
}

function renderHome() {
  current = null;
  document.title = "Charter · Civic reader";
  homeView.classList.remove("hidden");
  readerView.classList.add("hidden");
  contentsBtn.hidden = true;
  drawer.classList.remove("open");
  rail.replaceChildren();
}

function renderBite(docId, biteId) {
  const found = findBite(docId, biteId);
  if (!found) {
    location.hash = "";
    return;
  }
  const { doc, bite, index } = found;
  current = { doc, bite, index };
  document.title = `${bite.cite} · ${doc.short} · Charter`;
  homeView.classList.add("hidden");
  readerView.classList.remove("hidden");
  contentsBtn.hidden = false;
  crumb.textContent = `${doc.title} · ${bite.group}`;
  citeEl.textContent = bite.cite;
  labelEl.textContent = bite.label || "";
  labelEl.hidden = !bite.label;
  biteEl.textContent = bite.text;
  noteEl.textContent = bite.note || "";
  noteEl.hidden = !bite.note;
  sourceEl.innerHTML = "";
  const sourceLink = document.createElement("a");
  sourceLink.href = doc.source;
  sourceLink.target = "_blank";
  sourceLink.rel = "noopener";
  sourceLink.textContent = doc.sourceLabel;
  sourceEl.append("Text: ", sourceLink, ". Labels are not the legal text.");
  progressMeta.textContent = `${index + 1} of ${doc.bites.length}`;
  progressBar.style.width = `${((index + 1) / doc.bites.length) * 100}%`;
  prevBtn.disabled = index === 0 && !doc.prevDoc;
  nextBtn.disabled = index === doc.bites.length - 1 && !doc.nextDoc;
  if (index === doc.bites.length - 1 && doc.nextDoc) {
    continueLink.hidden = false;
    continueLink.href = hrefFor(doc.nextDoc, catalog[doc.nextDoc].bites[0].id);
    continueLink.textContent = doc.nextLabel;
  } else {
    continueLink.hidden = true;
  }
  renderContents(doc, bite.id, rail);
  renderContents(doc, bite.id, drawerContents);
}

function route() {
  const state = parseHash();
  drawer.classList.remove("open");
  contentsBtn.setAttribute("aria-expanded", "false");
  if (state.page === "home") renderHome();
  else renderBite(state.docId, state.biteId);
  window.scrollTo(0, 0);
}

function goRelative(step) {
  if (!current) return;
  const nextIndex = current.index + step;
  if (nextIndex >= 0 && nextIndex < current.doc.bites.length) {
    location.hash = hrefFor(current.doc.id, current.doc.bites[nextIndex].id).slice(1);
    return;
  }
  if (step > 0 && current.doc.nextDoc) {
    location.hash = hrefFor(current.doc.nextDoc, catalog[current.doc.nextDoc].bites[0].id).slice(1);
  }
  if (step < 0 && current.doc.prevDoc) {
    const prev = catalog[current.doc.prevDoc];
    location.hash = hrefFor(prev.id, prev.bites[prev.bites.length - 1].id).slice(1);
  }
}

async function copyBite() {
  if (!current) return;
  const payload = `${shareText(current.doc, current.bite)}\n${shareUrl()}`;
  try {
    await navigator.clipboard.writeText(payload);
    showToast("Copied");
  } catch {
    showToast("Copy failed");
  }
}

async function shareBite() {
  if (!current) return;
  const data = {
    title: `${current.bite.cite} · Charter`,
    text: shareText(current.doc, current.bite),
    url: shareUrl(),
  };
  if (navigator.share) {
    try {
      await navigator.share(data);
      return;
    } catch (err) {
      if (err && err.name === "AbortError") return;
    }
  }
  await copyBite();
}

function renderHomeCards() {
  const table = document.getElementById("table");
  table.replaceChildren(
    ...homeDocuments.map((doc) => {
      const card = document.createElement("a");
      card.className = "doc-card";
      card.href = hrefFor(doc.id, doc.bites[0].id);
      card.innerHTML = `<small>${doc.year} · ${doc.bites.length} bites</small><h2>${doc.title}</h2><p>${doc.blurb}</p>`;
      return card;
    })
  );
}

themeBtn.addEventListener("click", () => {
  const next = root.dataset.theme === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
});

contentsBtn.addEventListener("click", () => {
  drawer.classList.add("open");
  contentsBtn.setAttribute("aria-expanded", "true");
});

drawer.addEventListener("click", (event) => {
  if (event.target === drawer || event.target.closest("[data-close]")) {
    drawer.classList.remove("open");
    contentsBtn.setAttribute("aria-expanded", "false");
  }
});

prevBtn.addEventListener("click", () => goRelative(-1));
nextBtn.addEventListener("click", () => goRelative(1));
copyBtn.addEventListener("click", copyBite);
shareBtn.addEventListener("click", shareBite);

document.addEventListener("keydown", (event) => {
  if (event.target.matches("input, textarea")) return;
  if (event.key === "ArrowRight") goRelative(1);
  if (event.key === "ArrowLeft") goRelative(-1);
  if (event.key === "Escape") drawer.classList.remove("open");
});

document.addEventListener("touchstart", (event) => {
  touchStartX = event.changedTouches[0].clientX;
}, { passive: true });

document.addEventListener("touchend", (event) => {
  if (!current) return;
  const dx = event.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) < 72) return;
  goRelative(dx < 0 ? 1 : -1);
}, { passive: true });

window.addEventListener("hashchange", route);

applyTheme(preferredTheme());
renderHomeCards();
route();

if ("serviceWorker" in navigator && location.protocol !== "file:") {
  navigator.serviceWorker.register("./sw.js", { scope: "./" });
}

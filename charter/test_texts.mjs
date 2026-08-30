import { documents, homeDocuments, findBite, hrefFor } from "./js/texts.js";

let errors = 0;
const seen = new Set();

for (const doc of documents) {
  if (!doc.id || !doc.title || !doc.bites?.length) {
    console.error("bad document", doc.id);
    errors += 1;
  }
  for (const [index, bite] of doc.bites.entries()) {
    const key = `${doc.id}/${bite.id}`;
    if (seen.has(key)) {
      console.error("duplicate", key);
      errors += 1;
    }
    seen.add(key);
    if (!bite.text?.trim()) {
      console.error("empty text", key);
      errors += 1;
    }
    if (!bite.cite) {
      console.error("missing cite", key);
      errors += 1;
    }
    if (findBite(doc.id, bite.id)?.index !== index) {
      console.error("lookup failed", key);
      errors += 1;
    }
    if (!hrefFor(doc.id, bite.id).endsWith(`/${encodeURIComponent(bite.id)}`)) {
      console.error("href failed", key);
      errors += 1;
    }
  }
  console.log(`${doc.id}: ${doc.bites.length} bites`);
}

if (homeDocuments.map((doc) => doc.id).join(",") !== "declaration,constitution,rights") {
  console.error("home table should be the three founding texts");
  errors += 1;
}

if (errors) {
  console.error(`failed with ${errors} error(s)`);
  process.exit(1);
}

console.log(`ok: ${seen.size} unique bites`);

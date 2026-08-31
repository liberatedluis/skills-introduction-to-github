import { existsSync } from "node:fs";
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

const expectedPdfs = [
  "charter-light.pdf",
  "charter-dark.pdf",
  "declaration-light.pdf",
  "declaration-dark.pdf",
  "constitution-light.pdf",
  "constitution-dark.pdf",
  "rights-light.pdf",
  "rights-dark.pdf",
];
const missing = expectedPdfs.filter((name) => !existsSync(new URL(`./pdfs/${name}`, import.meta.url)));
if (missing.length) {
  console.error("missing PDFs:", missing.join(", "));
  process.exit(1);
}
console.log(`ok: ${expectedPdfs.length} light/dark PDFs`);

if (!findBite("declaration", "signers")?.bite.cite) {
  console.error("declaration/signers alias failed");
  process.exit(1);
}
if (findBite("declaration", "signers-va")?.bite.text.includes("Thomas Jefferson") !== true) {
  console.error("Virginia Declaration signers missing Jefferson");
  process.exit(1);
}
if (findBite("constitution", "signers-washington")?.bite.text.includes("George Washington") !== true) {
  console.error("Washington signer name not expanded");
  process.exit(1);
}
if (/G°\.|Presidt|Jaco:|Gouv |Abr Baldwin|Wil:/.test(JSON.stringify(documents))) {
  console.error("abbreviated signer names remain");
  process.exit(1);
}
console.log("ok: signer names");

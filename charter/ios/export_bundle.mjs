#!/usr/bin/env node
import { copyFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { documents, homeDocuments } from "../js/texts.js";

const root = dirname(fileURLToPath(import.meta.url));
const dest = join(root, "Charter");
mkdirSync(dest, { recursive: true });

const bundle = {
  documents: documents.map((doc) => ({
    id: doc.id,
    title: doc.title,
    short: doc.short,
    year: doc.year,
    blurb: doc.blurb,
    source: doc.source,
    sourceLabel: doc.sourceLabel,
    nextDoc: doc.nextDoc || null,
    nextLabel: doc.nextLabel || null,
    prevDoc: doc.prevDoc || null,
    bites: doc.bites.map((bite) => ({
      id: bite.id,
      kind: bite.kind,
      group: bite.group,
      cite: bite.cite,
      label: bite.label || "",
      text: bite.text,
      note: bite.note || "",
    })),
  })),
  homeIds: homeDocuments.map((doc) => doc.id),
};

writeFileSync(join(dest, "texts.json"), JSON.stringify(bundle, null, 2) + "\n");
let pdfs = 0;
for (const slug of ["charter", "declaration", "constitution", "rights"]) {
  for (const theme of ["light", "dark"]) {
    const name = `${slug}-${theme}.pdf`;
    const from = join(root, "../pdfs", name);
    if (!existsSync(from)) continue;
    copyFileSync(from, join(dest, name));
    pdfs += 1;
  }
}
console.log("exported", bundle.documents.reduce((n, doc) => n + doc.bites.length, 0), "bites and", pdfs, "PDFs");

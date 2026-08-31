#!/usr/bin/env node
import { copyFileSync, mkdirSync, writeFileSync } from "node:fs";
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
copyFileSync(join(root, "../pdfs/charter-light.pdf"), join(dest, "charter-light.pdf"));
copyFileSync(join(root, "../pdfs/charter-dark.pdf"), join(dest, "charter-dark.pdf"));
console.log("exported", bundle.documents.reduce((n, doc) => n + doc.bites.length, 0), "bites");

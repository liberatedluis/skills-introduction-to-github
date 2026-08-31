import { declaration } from "./declaration.js";
import { constitution } from "./constitution.js";
import { rights, later } from "./amendments.js";

export const documents = [declaration, constitution, rights, later];

export const homeDocuments = [declaration, constitution, rights];

export const catalog = Object.fromEntries(documents.map((doc) => [doc.id, doc]));

export function biteCount(doc) {
  return doc.bites.length;
}

export function findBite(docId, biteId) {
  const doc = catalog[docId];
  if (!doc) return null;
  const resolved = biteId === "signers"
    ? doc.bites.find((bite) => bite.kind === "signers")?.id
    : biteId;
  const index = doc.bites.findIndex((bite) => bite.id === resolved);
  if (index < 0) return null;
  return { doc, bite: doc.bites[index], index };
}

export function hrefFor(docId, biteId) {
  return `#/${docId}/${encodeURIComponent(biteId)}`;
}

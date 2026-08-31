#!/usr/bin/env node
import { spawn } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { documents } from "./js/texts.js";
import { renderPrintPages } from "./js/print.js";

const root = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(join(root, "css/print.css"), "utf8");
const outDir = join(root, "pdfs");
mkdirSync(outDir, { recursive: true });

const byId = Object.fromEntries(documents.map((doc) => [doc.id, doc]));
const books = [
  {
    slug: "charter",
    docs: documents,
    heading: "Charter",
    lede: "Three founding texts. One thought per page.",
  },
  {
    slug: "declaration",
    docs: [byId.declaration],
    heading: byId.declaration.title,
    lede: `${byId.declaration.blurb} One thought per page.`,
  },
  {
    slug: "constitution",
    docs: [byId.constitution],
    heading: byId.constitution.title,
    lede: `${byId.constitution.blurb} One thought per page.`,
  },
  {
    slug: "rights",
    docs: [byId.rights, byId.later],
    heading: "The Bill of Rights and later amendments",
    lede: "Amendments I–X, then XI–XXVII, so the Constitution is whole. One thought per page.",
  },
];

function htmlFor(book, theme) {
  return `<!DOCTYPE html>
<html lang="en" data-theme="${theme}">
<head>
<meta charset="utf-8" />
<title>${book.heading} · ${theme} PDF</title>
<style>${css}</style>
</head>
<body>
${renderPrintPages(book.docs, theme, { heading: book.heading, lede: book.lede })}
</body>
</html>`;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function stopTree(child) {
  try {
    child.kill("SIGTERM");
  } catch {
    /* already gone */
  }
}

async function chromePdf(htmlPath, pdfPath, profile) {
  mkdirSync(profile, { recursive: true });
  if (existsSync(pdfPath)) unlinkSync(pdfPath);

  // Call the real binary. /usr/local/bin/google-chrome is a desktop wrapper that
  // always adds --remote-debugging-port=9222 and hangs print-to-pdf.
  // Headless Chrome writes the PDF, then often never exits; treat a stable file as success.
  const child = spawn(
    "/usr/bin/google-chrome-stable",
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--disable-background-networking",
      "--disable-sync",
      "--disable-extensions",
      "--disable-component-update",
      "--no-pdf-header-footer",
      "--no-first-run",
      "--no-default-browser-check",
      "--remote-debugging-port=0",
      `--user-data-dir=${profile}`,
      `--print-to-pdf=${pdfPath}`,
      pathToFileURL(htmlPath).href,
    ],
    { stdio: "ignore" }
  );

  const deadline = Date.now() + 180000;
  let lastSize = -1;
  let stableHits = 0;

  while (Date.now() < deadline) {
    if (existsSync(pdfPath)) {
      const size = statSync(pdfPath).size;
      if (size > 1000 && size === lastSize) {
        stableHits += 1;
        if (stableHits >= 3) {
          stopTree(child);
          await sleep(400);
          try {
            child.kill("SIGKILL");
          } catch {
            /* already gone */
          }
          return;
        }
      } else {
        stableHits = 0;
        lastSize = size;
      }
    }
    if (child.exitCode !== null && !existsSync(pdfPath)) {
      throw new Error(`chrome exited ${child.exitCode} without writing ${pdfPath}`);
    }
    await sleep(400);
  }

  stopTree(child);
  try {
    child.kill("SIGKILL");
  } catch {
    /* already gone */
  }
  if (!existsSync(pdfPath) || statSync(pdfPath).size < 1000) {
    throw new Error(`chrome timed out writing ${pdfPath}`);
  }
}

for (const book of books) {
  for (const theme of ["light", "dark"]) {
    const htmlPath = join(outDir, `${book.slug}-${theme}.html`);
    const pdfPath = join(outDir, `${book.slug}-${theme}.pdf`);
    const profile = join(outDir, `.chrome-${book.slug}-${theme}`);
    writeFileSync(htmlPath, htmlFor(book, theme));
    await chromePdf(htmlPath, pdfPath, profile);
    unlinkSync(htmlPath);
    rmSync(profile, { recursive: true, force: true });
    console.log(pdfPath);
  }
}

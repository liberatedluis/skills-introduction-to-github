#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { documents } from "./js/texts.js";
import { renderPrintPages } from "./js/print.js";

const root = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(join(root, "css/print.css"), "utf8");
const outDir = join(root, "pdfs");
mkdirSync(outDir, { recursive: true });

function htmlFor(theme) {
  return `<!DOCTYPE html>
<html lang="en" data-theme="${theme}">
<head>
<meta charset="utf-8" />
<title>Charter · ${theme} PDF</title>
<style>${css}</style>
</head>
<body>
${renderPrintPages(documents, theme)}
</body>
</html>`;
}

function chromePdf(htmlPath, pdfPath, theme) {
  const profile = join(outDir, `.chrome-${theme}`);
  mkdirSync(profile, { recursive: true });
  const result = spawnSync(
    "google-chrome",
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--no-pdf-header-footer",
      "--no-first-run",
      "--no-default-browser-check",
      `--user-data-dir=${profile}`,
      `--print-to-pdf=${pdfPath}`,
      pathToFileURL(htmlPath).href,
    ],
    { timeout: 180000, encoding: "utf8" }
  );
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || `chrome exited ${result.status}`);
  }
}

for (const theme of ["light", "dark"]) {
  const htmlPath = join(outDir, `charter-${theme}.html`);
  const pdfPath = join(outDir, `charter-${theme}.pdf`);
  writeFileSync(htmlPath, htmlFor(theme));
  chromePdf(htmlPath, pdfPath, theme);
  unlinkSync(htmlPath);
  console.log(pdfPath);
}

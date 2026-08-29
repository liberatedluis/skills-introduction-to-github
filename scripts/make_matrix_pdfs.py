#!/usr/bin/env python3
"""Write 1,300 Matrix-styled Holy Bible PDFs next to the scrollable HTML pages."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from brand import SITE  # noqa: E402
from holy_catalog import build_catalog  # noqa: E402
from make_holy_bible_pdfs import generate_matrix_one  # noqa: E402

OUT = ROOT / "scroll-bibles"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--only")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    catalog = build_catalog()
    jobs = catalog
    if args.only:
        jobs = [row for row in catalog if row["id"] == args.only]
        if not jobs:
            raise SystemExit(f"unknown translation {args.only}")
    if args.limit:
        jobs = jobs[: args.limit]
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                generate_matrix_one,
                meta,
                str(OUT / Path(meta["printPath"])),
                args.force,
            ): meta
            for meta in jobs
        }
        for fut in as_completed(futures):
            result = fut.result()
            results.append(result)
            print(
                f"{result['status']:6} {result['id']} {result.get('bytes', '')} {result.get('error', '')}",
                flush=True,
            )
            if len(results) % 25 == 0:
                (OUT / "pdf-progress.json").write_text(
                    json.dumps(
                        {
                            "done": len(results),
                            "total": len(jobs),
                            "ok": sum(1 for row in results if row["status"] in {"ok", "exists"}),
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
    ok = sum(1 for row in results if row["status"] in {"ok", "exists"})
    (OUT / "pdf-build-log.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"done {ok}/{len(results)} Matrix PDFs -> {OUT} · {SITE}")
    if ok < len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

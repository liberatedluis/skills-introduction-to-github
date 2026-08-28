#!/usr/bin/env python3
This project is a 1,300-translation Matrix Holy Bible reader. Live chapter text loads from eBible (and getBible for a few public-domain extras). The local server proxies those chapter files so the scroller works without CORS issues.

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "ebible"
CACHE.mkdir(parents=True, exist_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/ebible/"):
            self.proxy_ebible()
            return
        super().do_GET()

    def proxy_ebible(self):
        rel = self.path[len("/api/ebible/") :].split("?", 1)[0]
        rel = rel.lstrip("/")
        if ".." in rel or not rel:
            self.send_error(400, "bad path")
            return
        translation, _, rest = rel.partition("/")
        if not translation or not rest:
            self.send_error(400, "need /api/ebible/{id}/{file}")
            return
        filename = rest.split("/")[-1]
        cached = CACHE / translation / filename
        if cached.exists() and cached.stat().st_size > 0:
            data = cached.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        url = f"https://ebible.org/{translation}/{filename}"
        try:
            req = Request(url, headers={"User-Agent": "ChristSupplyBible/1.0"})
            with urlopen(req, timeout=30) as resp:
                data = resp.read()
        except HTTPError as err:
            self.send_error(err.code, err.reason)
            return
        except URLError as err:
            self.send_error(502, str(err.reason))
            return
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys_stdout = __import__("sys").stderr
        sys_stdout.write("%s - %s\n" % (self.address_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Christ Supply Holy Bible at http://{args.host}:{args.port}")
    print("Made by Liberated Luis With Cursor, Claude Opus, and MacBook · ChristSupply.Net")
    server.serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Tiny static server + comments sidecar API for the commentable-html layer.

Run inside a deliverable folder:  python3 serve.py [port]   (default 8777)

  GET  <dir>/__comments__/<docId>   -> returns <dir>/<docId>.comments.json  (or {"threads":[]})
  PUT  <dir>/__comments__/<docId>   -> writes the JSON body to <dir>/<docId>.comments.json
  *                                 -> serves static files from the current directory

<dir> is the folder of the page that asks, so a page one level down (viewer/index.html) keeps its
store beside it.

Static files answer byte-range requests (206 + Content-Range, 416 past the end): Safari will not
play an MP4 without them, and Chrome cannot seek one reliably. Media and data under a data/ folder
may be cached for an hour; everything else, HTML and comment stores included, is sent no-store so
edits show on refresh.

Bind is localhost-only. The comment layer auto-detects this endpoint when the
page is opened over http; otherwise it falls back to localStorage. The AI reads
and writes <docId>.comments.json directly on disk between rounds.
"""
import http.server, socketserver, json, os, re, sys, tempfile, urllib.parse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
ROOT = os.getcwd()
REAL_ROOT = os.path.realpath(ROOT)
MARK = "/__comments__/"
STORE = ".comments.json"  # the sidecar API reads and writes this file beside the page
RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")
CACHEABLE = (".mp4", ".csv", ".png", ".json")


class Handler(http.server.SimpleHTTPRequestHandler):
    _remaining = None  # bytes left to send for a 206; None means a whole file

    def _is_store(self):
        """True when this request is for the comments sidecar rather than an ordinary file."""
        return MARK in urllib.parse.unquote(self.path.split("?")[0])

    def _store_path(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        i = path.find(MARK)
        doc = os.path.basename(path[i + len(MARK):].strip("/")) or "document"
        base = os.path.realpath(self.translate_path(path[:i] + "/"))
        if os.path.commonpath([REAL_ROOT, base]) != REAL_ROOT:
            return None
        return os.path.join(base, doc + STORE)

    def _send_json(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        if self._is_store():
            path = self._store_path()
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    self._send_json(200, f.read())
            else:
                self._send_json(200, b'{"threads":[]}')
            return
        return super().do_GET()

    def do_PUT(self):
        if self._is_store():
            n = int(self.headers.get("Content-Length", 0))
            data = self.rfile.read(n)
            try:
                json.loads(data)
            except Exception:
                self._send_json(400, b'{"error":"invalid json"}')
                return
            path = self._store_path()
            if not path:
                self._send_json(403, b'{"error":"bad path"}')
                return
            # atomic write: temp file + replace, so a concurrent GET never sees a partial file
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
            self._send_json(200, b'{"ok":true}')
            return
        self._send_json(405, b'{"error":"method not allowed"}')

    do_POST = do_PUT

    def send_head(self):
        """Serve one byte range of a file when asked; anything else goes to the stock handler."""
        path = self.translate_path(self.path)
        m = RANGE.match(self.headers.get("Range", "").strip())
        if not m or m.group(1) == m.group(2) == "" or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        if m.group(1) == "":  # bytes=-N asks for the last N bytes
            start, end = max(0, size - int(m.group(2))), size - 1
        else:
            start = int(m.group(1))
            end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
        if start >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        try:
            if self._remaining is None:
                return super().copyfile(source, outputfile)
            n, self._remaining = self._remaining, None
            while n > 0:
                chunk = source.read(min(1 << 16, n))
                if not chunk:
                    break
                outputfile.write(chunk)
                n -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser dropped a range it no longer needs, which every seek does

    def send_response(self, code, message=None):
        self._status = code
        super().send_response(code, message)

    def end_headers(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        sidecar = MARK in path
        if not sidecar:
            self.send_header("Accept-Ranges", "bytes")
        cache = ("/data/" in path and path.endswith(CACHEABLE) and not sidecar
                 and getattr(self, "_status", 200) in (200, 206, 304))  # never cache a 401 or a 404
        self.send_header("Cache-Control", "max-age=3600" if cache else "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


socketserver.ThreadingTCPServer.allow_reuse_address = True
socketserver.ThreadingTCPServer.daemon_threads = True
with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"\n  commentable-html  →  http://127.0.0.1:{PORT}/")
    print(f"  serving {ROOT}")
    print("  Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped.")

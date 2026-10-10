"""Servidor local mínimo: solo sirve lo imprescindible de site/ (lista blanca) y solo en 127.0.0.1."""
import base64
import hashlib
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import paths
HERE = paths.APP
BASE = os.path.join(HERE, "site")            # datos generados
INDEX = os.path.join(paths.RES, "site")       # la página (solo lectura)
try:
    CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
except Exception:
    CFG = {}
PORT = int(os.environ.get("MCDASH_PORT") or CFG.get("port", 8765))

JS = "text/javascript; charset=utf-8"
ALLOWED = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/data.js": ("data.js", JS),
    "/history.js": ("history.js", JS),
    "/terrain.js": ("terrain.js", JS),
}
CSP = ("default-src 'none'; script-src 'self' {SCRIPT_HASHES}; object-src 'none'; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data: https://mc-heads.net https://crafatar.com; connect-src 'self'; "
       "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


# Only these Host names may use the server (blocks DNS-rebinding): this computer, the free Cloudflare tunnels, and any
# extra names listed in config.json -> "allowed_hosts" (for a named tunnel).
EXTRA_HOSTS = {str(h).lower() for h in CFG.get("allowed_hosts", [])}
MAX_CONNECTIONS = 64
_slots = threading.BoundedSemaphore(MAX_CONNECTIONS)


def host_ok(host):
    h = (host or "").lower().strip()
    if h.startswith("["):                                              # [::1]:port
        h = h.split("]")[0] + "]"
    else:
        h = h.split(":")[0]
    return h in ("127.0.0.1", "localhost", "[::1]") or h.endswith(".trycloudflare.com") or h in EXTRA_HOSTS


LANG_FILES = {"/lang/%s.js" % c for c in ("es", "en", "zh", "hi", "ar", "fr", "pt", "ru", "de", "ja")}   # solo estos archivos de idioma


_csp_cache = {}


def csp_for(page):
    """CSP con el hash de cada <script> en línea de la página: así un script inyectado no se ejecuta aunque llegue al HTML."""
    key = hashlib.sha256(page).digest()
    if key not in _csp_cache:
        hashes = []
        for m in re.finditer(rb"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>", page, re.S | re.I):
            src = m.group(1).replace(b"\r\n", b"\n").replace(b"\r", b"\n")      # el navegador normaliza los saltos de línea antes de calcular el hash
            hashes.append("'sha256-%s'" % base64.b64encode(hashlib.sha256(src).digest()).decode())
        _csp_cache.clear()
        _csp_cache[key] = CSP.replace("{SCRIPT_HASHES}", " ".join(hashes))
    return _csp_cache[key]


class Handler(BaseHTTPRequestHandler):
    timeout = 10          # corta conexiones que se quedan colgadas (anti slowloris)
    server_version = "mcdash"
    sys_version = ""
    def do_GET(self):
        # peticiones ambiguas (la base de los ataques de contrabando entre proxy y servidor): se rechazan sin más
        if (len(self.headers.get_all("Host") or []) != 1 or self.headers.get("Transfer-Encoding") is not None
                or (self.headers.get("Content-Length") or "0").strip() not in ("", "0")):
            self.close_connection = True
            self.send_error(400, "Bad request")
            return
        if not host_ok(self.headers.get("Host")):
            self.send_error(421, "Unknown host")
            return
        # another website must not be able to pull the data into its own page (<script src=...> from a different site)
        if (self.headers.get("Sec-Fetch-Site") or "same-origin") not in ("same-origin", "none"):
            self.send_error(403, "Cross-site requests are not allowed")
            return
        if not _slots.acquire(blocking=False):                         # too many simultaneous requests
            self.send_error(503, "Busy")
            return
        try:
            self._serve(head=getattr(self, "_head", False))
        finally:
            _slots.release()

    def _serve(self, head=False):
        path = self.path.split("?", 1)[0]
        item = ALLOWED.get(path) or ((path[1:], JS) if path in LANG_FILES else None)
        if not item:
            self.send_error(404)
            return
        try:
            body = open(os.path.join(INDEX if (item[0] == "index.html" or item[0].startswith("lang/")) else BASE, item[0]), "rb").read()
        except OSError:
            self.send_error(503, "Data not available yet: run the program first")
            return
        self.send_response(200)
        self.send_header("Content-Type", item[1])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        self.send_header("Content-Security-Policy", csp_for(body) if item[0] == "index.html" else "default-src 'none'; frame-ancestors 'none'")
        self.send_header("Strict-Transport-Security", "max-age=31536000")
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def do_HEAD(self):
        self._head = True
        self.do_GET()

    def log_message(self, *a):
        pass


def run(port=None):
    srv = ThreadingHTTPServer(("127.0.0.1", port or PORT), Handler)   # solo este equipo; el túnel entra por aquí
    srv.daemon_threads = True
    srv.serve_forever()


if __name__ == "__main__":
    print(f"Serving site/ at http://127.0.0.1:{PORT}/  (Ctrl+C to stop)")
    run()

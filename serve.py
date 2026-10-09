"""Servidor local mínimo: solo sirve lo imprescindible de site/ (lista blanca) y solo en 127.0.0.1."""
import json
import os
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
CSP = ("default-src 'none'; script-src 'self' 'unsafe-inline'; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data: https://mc-heads.net https://crafatar.com; connect-src 'self'; "
       "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")


class Handler(BaseHTTPRequestHandler):
    timeout = 10          # corta conexiones que se quedan colgadas (anti slowloris)
    server_version = "mcdash"
    sys_version = ""
    def do_GET(self):
        item = ALLOWED.get(self.path.split("?", 1)[0])
        if not item:
            self.send_error(404)
            return
        try:
            body = open(os.path.join(INDEX if item[0] == "index.html" else BASE, item[0]), "rb").read()
        except OSError:
            self.send_error(503, "Datos no disponibles todavia: ejecuta build.py")
            return
        self.send_response(200)
        self.send_header("Content-Type", item[1])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=()")
        self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.do_GET()

    def log_message(self, *a):
        pass


def run(port=None):
    srv = ThreadingHTTPServer(("127.0.0.1", port or PORT), Handler)   # solo este equipo; el túnel entra por aquí
    srv.daemon_threads = True
    srv.serve_forever()


if __name__ == "__main__":
    print(f"Sirviendo site/ en http://127.0.0.1:{PORT}/  (Ctrl+C para parar)")
    run()

"""Genera site/index.min.html: la misma página con el JavaScript minificado y los nombres internos reemplazados.

Herramienta de desarrollo (no forma parte del .exe). Usa Terser, el minificador estándar, ejecutado dentro de
Edge/Chrome headless (no hace falta Node). La versión y el hash de Terser están fijados: si el archivo descargado
no coincide, se aborta.

  python scripts/minify_page.py

serve.py sirve index.min.html en lugar de index.html mientras no esté desfasado respecto al original.
Es ofuscación, no seguridad: dificulta leer la página, pero la protección real es el cifrado de los datos (secure.py).
"""
import json
import hashlib
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _cdp                                                        # noqa: E402

TERSER_URL = "https://cdn.jsdelivr.net/npm/terser@5.31.6/dist/bundle.min.js"
TERSER_SHA256 = "38af5a0fb14c73bc49acc03cb5e1187ff45470b7dec04571aea44525aa063ce8"
SRC = os.path.join(ROOT, "site", "index.html")
OUT = os.path.join(ROOT, "site", "index.min.html")
CACHE = os.path.join(ROOT, "data", "terser-5.31.6.js")


def find_browser():
    cands = [os.environ.get("MCDASH_BROWSER", ""),
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
             "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/microsoft-edge"]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    raise SystemExit("No encuentro Edge/Chrome. Define MCDASH_BROWSER con la ruta del ejecutable.")


def terser_source():
    if os.path.isfile(CACHE):
        data = open(CACHE, "rb").read()
        if hashlib.sha256(data).hexdigest() == TERSER_SHA256:
            return data.decode("utf-8")
    req = urllib.request.Request(TERSER_URL, headers={"User-Agent": "minecraft-world-dashboard"})
    with urllib.request.urlopen(req, timeout=60) as r:             # nosec B310 - https fijo
        data = r.read(5_000_000)
    if hashlib.sha256(data).hexdigest() != TERSER_SHA256:
        raise SystemExit("El Terser descargado no coincide con el hash fijado: abortado.")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE, "wb").write(data)
    return data.decode("utf-8")


def minify_js(code):
    _cdp.EDGE = find_browser()
    b = _cdp.Browser("about:blank", port=9377)
    try:
        b.run_js(terser_source())
        opts = {"ecma": 2020, "compress": {"passes": 2}, "mangle": True, "format": {"comments": False}}
        r = b.run_js("Terser.minify(%s, %s).then(r => r.code)" % (json.dumps(code), json.dumps(opts)))
        if not r or len(r) < len(code) // 5:
            raise SystemExit("Terser no devolvió código válido.")
        return r
    finally:
        b.close()


def main():
    html = open(SRC, encoding="utf-8").read().replace("\r\n", "\n")
    # único <script> en línea (los demás llevan src)
    m = [x for x in re.finditer(r"<script>(.*?)</script>", html, re.S)]
    if len(m) != 1:
        raise SystemExit("Se esperaba exactamente un <script> en línea, hay %d." % len(m))
    js = m[0].group(1)
    mini = minify_js(js)
    out = html[:m[0].start(1)] + mini + html[m[0].end(1):]
    # comentarios HTML y CSS fuera (los de CSS solo dentro de <style>)
    out = re.sub(r"<!--(?!\[).*?-->", "", out, flags=re.S)
    out = re.sub(r"(<style[^>]*>)(.*?)(</style>)",
                 lambda s: s.group(1) + re.sub(r"/\*.*?\*/", "", s.group(2), flags=re.S) + s.group(3), out, flags=re.S)
    out = re.sub(r"\n[ \t]+", "\n", out)                            # sangrías
    out = re.sub(r"\n{2,}", "\n", out)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)
    print("OK  %s  %d -> %d bytes (JS %d -> %d)" % (os.path.relpath(OUT, ROOT), len(html.encode()), len(out.encode()), len(js), len(mini)))


if __name__ == "__main__":
    main()

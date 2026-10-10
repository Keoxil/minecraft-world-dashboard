#!/usr/bin/env python3
"""Un solo paso: arranca la página, la mantiene al día y te da un enlace para compartirla.

    python start.py                 # lo normal: lee tu mundo, abre la página y crea el enlace para tus amigos
    python start.py --sin-enlace    # solo en tu ordenador, sin enlace público
    python start.py --silencioso    # sin mensajes ni navegador (para el arranque automático)
    python start.py --instalar-inicio / --quitar-inicio    # arrancar solo al iniciar sesión (Windows)
"""
import argparse
import hashlib
import io
import json
import os
import platform
import re
import socket
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
import webbrowser

import paths
HERE = paths.APP
SELF = os.path.abspath(__file__)
DATA = os.path.join(HERE, "data")
TOOLS = os.path.join(HERE, "tools")
IS_WIN = sys.platform.startswith("win")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TASK_INICIO = "MinecraftWorldDashboardInicio"
QUIET = False
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def say(*a):
    if not QUIET:
        print(*a, flush=True)
    try:
        os.makedirs(DATA, exist_ok=True)
        with open(os.path.join(DATA, "start.log"), "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + " ".join(str(x) for x in a) + "\n")
    except OSError:
        pass


def load_config():
    try:
        return json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
    except Exception:
        return {}


# ------------------------------------------------------------------ cloudflared (descarga verificada)
def _asset():
    m = platform.machine().lower()
    arch = "arm64" if m in ("arm64", "aarch64") else ("arm" if m.startswith("arm") else ("386" if m in ("i386", "i686", "x86") else "amd64"))
    if IS_WIN:
        return f"cloudflared-windows-{arch if arch != 'arm64' else 'amd64'}.exe", "cloudflared.exe", False
    if sys.platform == "darwin":
        return f"cloudflared-darwin-{arch}.tgz", "cloudflared", True
    return f"cloudflared-linux-{arch}", "cloudflared", False


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "minecraft-world-dashboard", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def ensure_cloudflared():
    asset, fname, is_tgz = _asset()
    dest = os.path.join(TOOLS, fname)
    if os.path.isfile(dest):
        return dest
    found = shutil_which("cloudflared")
    if found:
        return found
    say("Descargando la herramienta de Cloudflare (solo la primera vez, unos 50 MB)...")
    rel = json.loads(_get("https://api.github.com/repos/cloudflare/cloudflared/releases/latest"))
    body = rel.get("body") or ""
    m = re.search(re.escape(asset) + r"[^\n]*?([0-9a-f]{64})", body, re.I)
    if not m:
        raise RuntimeError("no he podido comprobar la firma (hash) oficial de la descarga; por seguridad no la uso")
    expected = m.group(1).lower()
    url = next((a["browser_download_url"] for a in rel.get("assets", []) if a["name"] == asset), None)
    if not url:
        raise RuntimeError(f"no existe la descarga {asset} para este sistema")
    blob = _get(url, timeout=600)
    got = hashlib.sha256(blob).hexdigest()
    if got != expected:
        raise RuntimeError("la descarga no coincide con la firma oficial de Cloudflare; no la uso")
    os.makedirs(TOOLS, exist_ok=True)
    if is_tgz:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            member = next(x for x in tf.getmembers() if os.path.basename(x.name) == "cloudflared")
            open(dest, "wb").write(tf.extractfile(member).read())
    else:
        open(dest, "wb").write(blob)
    if not IS_WIN:
        os.chmod(dest, 0o755)
    say("Herramienta de Cloudflare descargada y verificada.")
    return dest


def shutil_which(name):
    import shutil
    return shutil.which(name)


# ------------------------------------------------------------------ utilidades
def port_in_use(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def copy_to_clipboard(text):
    try:
        if IS_WIN:
            subprocess.run(["clip"], input=text.encode("utf-8"), creationflags=NO_WINDOW, timeout=5)
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), timeout=5)
        else:
            for tool in (["wl-copy"], ["xclip", "-selection", "clipboard"]):
                if shutil_which(tool[0]):
                    subprocess.run(tool, input=text.encode("utf-8"), timeout=5)
                    break
        return True
    except Exception:
        return False


def pid_alive(pid):
    try:
        if IS_WIN:
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True, creationflags=NO_WINDOW).stdout
            return str(pid) in out
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def selfcmd(mode):
    """Comando para volver a lanzarse en un modo interno (--build / --serve), sea .exe o script."""
    return [sys.executable, mode] if paths.FROZEN else [sys.executable, SELF, mode]


def load_prefs():
    try:
        return json.load(open(os.path.join(DATA, "preferencias.json"), encoding="utf-8"))
    except Exception:
        return {}


def save_prefs(**kw):
    p = load_prefs()
    p.update(kw)
    os.makedirs(DATA, exist_ok=True)
    json.dump(p, open(os.path.join(DATA, "preferencias.json"), "w", encoding="utf-8"))


def choose_world(force=False):
    """Menú para elegir el mundo. Solo pregunta si hay más de uno y nunca se ha elegido (o si se pide con --elegir-mundo)."""
    import discover
    prefs = load_prefs()
    if not force and prefs.get("mundo_preguntado"):
        return
    worlds = discover.list_worlds(load_config())
    if len(worlds) < 2 and not force:
        return
    if not worlds:
        return
    if not (sys.stdin and sys.stdin.isatty()):
        return
    def ask(prompt):
        try:
            return input(prompt).strip()
        except EOFError:
            return ""

    # 1) launcher (solo si hay más de uno)
    launchers = []
    for w in worlds:
        if w["launcher"] not in launchers:
            launchers.append(w["launcher"])
    chosen_l = None
    if len(launchers) > 1:
        print("\nHe encontrado Minecraft en estos launchers:")
        print("  0) Todos / automático (recomendado)")
        for n, l in enumerate(launchers, 1):
            print(f"  {n}) {l}")
        a = ask(f"Elige un número [0-{len(launchers)}] (Intro = 0): ")
        if a.isdigit() and 1 <= int(a) <= len(launchers):
            chosen_l = launchers[int(a) - 1]
            worlds = [w for w in worlds if w["launcher"] == chosen_l]
    # 2) mundo
    print("\nMundos encontrados" + (f" en {chosen_l}" if chosen_l else "") + ":")
    print("  0) Automático: el que tengas abierto en cada momento (recomendado)")
    for n, w in enumerate(worlds, 1):
        print(f"  {n}) {w['name']}   [{w['launcher']}: {os.path.basename(w['instance'])}]" + ("   <- abierto ahora" if w["open"] else ""))
    a = ask(f"Elige un número [0-{len(worlds)}] (Intro = 0): ")
    pick = int(a) if a.isdigit() and 0 <= int(a) <= len(worlds) else 0
    if pick:
        save_prefs(mundo_preguntado=True, world=worlds[pick - 1]["world"], launcher=None)
        print(f"  -> Mundo fijado: {worlds[pick - 1]['name']}   (para cambiarlo: --elegir-mundo)\n")
    else:
        save_prefs(mundo_preguntado=True, world=None, launcher=chosen_l)
        print("  -> Modo automático" + (f" solo con {chosen_l}" if chosen_l else "") + "   (para cambiarlo: --elegir-mundo)\n")


def run_build():
    try:
        r = subprocess.run(selfcmd("--build"), cwd=HERE, capture_output=True, text=True,
                           timeout=900, creationflags=NO_WINDOW)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"error: {e}"


def spawn(cmd, **kw):
    return subprocess.Popen(cmd, cwd=HERE, creationflags=NO_WINDOW, **kw)


# ------------------------------------------------------------------ arranque automático (Windows)
def instalar_inicio():
    if not IS_WIN:
        say("En este sistema añade a mano `python3 start.py --silencioso` a tus programas de inicio (o a systemd/cron @reboot).")
        return
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    exe = pyw if os.path.isfile(pyw) else sys.executable
    tr = f'"{sys.executable}" --silencioso' if paths.FROZEN else f'"{exe}" "{SELF}" --silencioso'
    r = subprocess.run(["schtasks", "/Create", "/TN", TASK_INICIO, "/SC", "ONLOGON", "/F", "/TR", tr],
                       capture_output=True, text=True, creationflags=NO_WINDOW)
    say("Listo: se iniciará solo cada vez que inicies sesión." if r.returncode == 0 else "No he podido crearlo: " + r.stdout + r.stderr)


def quitar_inicio():
    if IS_WIN:
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_INICIO, "/F"], capture_output=True, creationflags=NO_WINDOW)
    say("Ya no se iniciará solo.")


def inicio_instalado():
    if not IS_WIN:
        return True
    return subprocess.run(["schtasks", "/Query", "/TN", TASK_INICIO], capture_output=True, creationflags=NO_WINDOW).returncode == 0


# ------------------------------------------------------------------ principal
def main():
    global QUIET
    ap = argparse.ArgumentParser(description="Arranca la página y crea el enlace para compartirla.")
    ap.add_argument("--sin-enlace", action="store_true", help="solo en tu ordenador, sin enlace público")
    ap.add_argument("--silencioso", action="store_true", help="sin mensajes ni navegador")
    ap.add_argument("--sin-navegador", action="store_true", help="no abrir el navegador")
    ap.add_argument("--puerto", type=int, help="puerto local (por defecto 8765)")
    ap.add_argument("--intervalo", type=int, default=60, help="segundos entre actualizaciones (por defecto 60)")
    ap.add_argument("--elegir-mundo", action="store_true", help="elegir de qué mundo se crea la página (o volver al modo automático)")
    ap.add_argument("--instalar-inicio", action="store_true")
    ap.add_argument("--quitar-inicio", action="store_true")
    args = ap.parse_args()
    QUIET = args.silencioso
    if args.silencioso and IS_WIN and paths.FROZEN:
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass
    if args.instalar_inicio:
        return instalar_inicio()
    if args.quitar_inicio:
        return quitar_inicio()

    os.makedirs(DATA, exist_ok=True)
    cfg = load_config()
    port = args.puerto or int(os.environ.get("MCDASH_PORT") or cfg.get("port", 8765))
    local = f"http://127.0.0.1:{port}/"

    # ya hay otra copia en marcha: solo se enseña el enlace
    pidfile = os.path.join(DATA, "start.pid")
    try:
        other = int(open(pidfile).read().strip())
        if other != os.getpid() and pid_alive(other):
            link = open(os.path.join(DATA, "enlace.txt"), encoding="utf-8").read().strip() if os.path.exists(os.path.join(DATA, "enlace.txt")) else local
            say(f"Ya está en marcha.  Enlace: {link}")
            return
    except Exception:
        pass
    open(pidfile, "w").write(str(os.getpid()))

    if not args.silencioso:
        choose_world(force=args.elegir_mundo)
    say("Leyendo tu mundo de Minecraft (la primera vez tarda un poco)...")
    out = run_build()
    say("  " + (out.splitlines()[-1] if out else "sin salida"))
    if "No encuentro ning" in out:
        say("\nNo he encontrado ningún mundo. Abre Minecraft al menos una vez con un mundo y vuelve a ejecutar esto,")
        say("o indica la carpeta de tu instancia en config.json (mira config.example.json).")
        return

    procs = {}
    state = {"url": None}
    env = dict(os.environ, MCDASH_PORT=str(port))

    def start_server():
        if port_in_use(port):
            return None
        return spawn(selfcmd("--serve"), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def start_tunnel():
        try:
            cf = ensure_cloudflared()
        except Exception as e:
            say(f"No he podido preparar el enlace público: {e}")
            return None
        p = spawn([cf, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"], stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT, text=True, bufsize=1)

        def reader():
            try:
                with open(os.path.join(DATA, "tunnel.log"), "a", encoding="utf-8") as lg:
                    for ln in p.stdout:
                        lg.write(ln)
                        m = URL_RE.search(ln)
                        if m and state["url"] != m.group(0):
                            state["url"] = m.group(0)
            except Exception:
                pass
        threading.Thread(target=reader, daemon=True).start()
        return p

    procs["server"] = start_server()
    if not args.sin_enlace:
        state["url"] = None
        procs["tunnel"] = start_tunnel()
    time.sleep(1.5)
    if not port_in_use(port):
        say(f"No he podido arrancar la página en el puerto {port}. ¿Lo está usando otro programa? Prueba: python start.py --puerto 8770")
        return

    link = None
    if procs.get("tunnel"):
        t0 = time.time()
        while time.time() - t0 < 60 and not state["url"] and procs["tunnel"].poll() is None:
            time.sleep(0.5)
        link = state["url"]

    def announce(url):
        with open(os.path.join(DATA, "enlace.txt"), "w", encoding="utf-8") as fh:
            fh.write(url or local)
        if QUIET:
            return
        copied = copy_to_clipboard(url) if url else False
        print("\n" + "=" * 64)
        print("  ¡Tu página ya está lista!")
        print(f"  Para ti:            {local}")
        if url:
            print(f"  Para tus amigos:    {url}" + ("   (copiado)" if copied else ""))
            print("  Pásales ese enlace: no tienen que instalar ni tocar nada.")
            print("  OJO: el enlace cambia cada vez que se reinicia esto, y quien lo tenga puede ver")
            print("  los nombres de los jugadores y sus coordenadas.")
        else:
            print("  (Sin enlace público: solo se ve en este ordenador.)")
        print("  Deja esta ventana abierta; ciérrala para dejar de compartir.")
        print("=" * 64 + "\n")

    announce(link)
    if not args.silencioso and not args.sin_navegador:
        try:
            webbrowser.open(local)
        except Exception:
            pass
    if not args.silencioso and IS_WIN and sys.stdin and sys.stdin.isatty() and not inicio_instalado():
        pref = os.path.join(DATA, "preferencias.json")
        asked = False
        try:
            asked = json.load(open(pref)).get("preguntado", False)
        except Exception:
            pass
        if not asked:
            try:
                ans = input("¿Quieres que esto se inicie solo al encender el ordenador? [s/N] ").strip().lower()
            except EOFError:
                ans = ""
            save_prefs(preguntado=True)
            if ans.startswith("s"):
                instalar_inicio()

    # bucle: actualizar los datos y vigilar que todo siga vivo
    try:
        next_build = time.time() + args.intervalo
        while True:
            time.sleep(2)
            if time.time() >= next_build:
                run_build()
                next_build = time.time() + args.intervalo
            if procs.get("server") is not None and procs["server"].poll() is not None:
                procs["server"] = start_server()
            if "tunnel" in procs and procs["tunnel"] is not None and procs["tunnel"].poll() is not None:
                say("El enlace se ha caído; creo uno nuevo...")
                state["url"] = None
                procs["tunnel"] = start_tunnel()
                t0 = time.time()
                while time.time() - t0 < 60 and not state["url"]:
                    time.sleep(0.5)
                announce(state["url"])
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs.values():
            if p is not None and p.poll() is None:
                p.terminate()
        try:
            os.remove(pidfile)
        except OSError:
            pass
        say("Parado. Hasta la próxima.")


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()          # imprescindible en el .exe: build.py usa procesos
    if "--build" in sys.argv[1:2]:
        import build
        build.main()
    elif "--serve" in sys.argv[1:2]:
        import serve
        serve.run()
    else:
        main()

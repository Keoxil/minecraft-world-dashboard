#!/usr/bin/env python3
"""One step: starts the page, keeps it up to date and gives you a link to share it.

    python start.py                 # the normal way: reads your world, opens the page and creates a link for your friends
    python start.py --no-link       # only on this computer, no public link
    python start.py --silent        # no messages and no browser (for automatic startup)
    python start.py --install-startup / --remove-startup    # start by itself when you log in (Windows)
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


# ------------------------------------------------------------------ cloudflared (verified download)
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
    say("Downloading the Cloudflare tool (first time only, about 50 MB)...")
    rel = json.loads(_get("https://api.github.com/repos/cloudflare/cloudflared/releases/latest"))
    body = rel.get("body") or ""
    m = re.search(re.escape(asset) + r"[^\n]*?([0-9a-f]{64})", body, re.I)
    if not m:
        raise RuntimeError("could not find the official checksum for the download; not using it for safety")
    expected = m.group(1).lower()
    url = next((a["browser_download_url"] for a in rel.get("assets", []) if a["name"] == asset), None)
    if not url:
        raise RuntimeError(f"no download named {asset} exists for this system")
    blob = _get(url, timeout=600)
    got = hashlib.sha256(blob).hexdigest()
    if got != expected:
        raise RuntimeError("the download does not match Cloudflare official checksum; not using it")
    os.makedirs(TOOLS, exist_ok=True)
    if is_tgz:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            member = next(x for x in tf.getmembers() if os.path.basename(x.name) == "cloudflared")
            open(dest, "wb").write(tf.extractfile(member).read())
    else:
        open(dest, "wb").write(blob)
    if not IS_WIN:
        os.chmod(dest, 0o755)
    say("Cloudflare tool downloaded and verified.")
    return dest


def shutil_which(name):
    import shutil
    return shutil.which(name)


# ------------------------------------------------------------------ helpers
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
    """Command to relaunch itself in an internal mode (--build / --serve), whether .exe or script."""
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
    """Menu to choose the world. It only asks if there is more than one and it has never been chosen (or when --choose-world is used)."""
    import discover
    prefs = load_prefs()
    if not force and prefs.get("mundo_preguntado"):
        return
    cfg = dict(load_config())
    cfg["instances"] = list(cfg.get("instances", [])) + list(prefs.get("instances", []))
    worlds = discover.list_worlds(cfg)
    if not (sys.stdin and sys.stdin.isatty()):
        return
    if len(worlds) < 2 and not force and worlds:
        return
    def ask(prompt):
        try:
            return input(prompt).strip()
        except EOFError:
            return ""

    # 1) launcher (only if there is more than one)
    launchers = []
    for w in worlds:
        if w["launcher"] not in launchers:
            launchers.append(w["launcher"])
    chosen_l = None
    if not worlds:
        print("\nNo Minecraft worlds were found automatically.")
        print("  +) Enter the folder manually")
        a = ask("Type + to enter it, or press Enter to continue: ")
        if a == "+":
            folder = ask("Paste the path of your instance folder (the one that contains the 'saves' folder): ").strip('" ')
            folder = os.path.abspath(os.path.expanduser(folder)) if folder else ""
            if os.path.basename(folder).lower() == "saves":
                folder = os.path.dirname(folder)
            if folder and os.path.isdir(os.path.join(folder, "saves")):
                save_prefs(instances=sorted(set(prefs.get("instances", [])) | {folder}))
                return choose_world(force=True)
            print("  Could not find a 'saves' folder there.\n")
        return
    if len(launchers) > 1:
        print("\nMinecraft was found in these launchers:")
        print("  0) All / automatic (recommended)")
        for n, l in enumerate(launchers, 1):
            print(f"  {n}) {l}")
        a = ask(f"Choose a number [0-{len(launchers)}] (Enter = 0): ")
        if a.isdigit() and 1 <= int(a) <= len(launchers):
            chosen_l = launchers[int(a) - 1]
            worlds = [w for w in worlds if w["launcher"] == chosen_l]
    # 2) world
    print("\nWorlds found" + (f" in {chosen_l}" if chosen_l else "") + ":")
    print("  0) Automatic: whichever world you have open at the time (recommended)")
    for n, w in enumerate(worlds, 1):
        print(f"  {n}) {w['name']}   [{w['launcher']}: {os.path.basename(w['instance'])}]" + ("   <- open now" if w["open"] else ""))
    print("  +) My Minecraft is in another folder (enter it manually)")
    a = ask(f"Choose a number [0-{len(worlds)}] or + (Enter = 0): ")
    if a == "+":
        folder = ask("Paste the path of your instance folder (the one that contains the 'saves' folder): ").strip('" ')
        folder = os.path.abspath(os.path.expanduser(folder)) if folder else ""
        if os.path.basename(folder).lower() == "saves":
            folder = os.path.dirname(folder)
        if folder and os.path.isdir(os.path.join(folder, "saves")):
            save_prefs(instances=sorted(set(prefs.get("instances", [])) | {folder}))
            print("  -> Folder added.")
            return choose_world(force=True)
        print("  Could not find a 'saves' folder there; nothing changed.\n")
        return
    pick = int(a) if a.isdigit() and 0 <= int(a) <= len(worlds) else 0
    if pick:
        save_prefs(mundo_preguntado=True, world=worlds[pick - 1]["world"], launcher=None)
        print(f"  -> World set: {worlds[pick - 1]['name']}   (to change it later: --choose-world)\n")
    else:
        save_prefs(mundo_preguntado=True, world=None, launcher=chosen_l)
        print("  -> Automatic mode" + (f" using only {chosen_l}" if chosen_l else "") + "   (to change it later: --choose-world)\n")


def run_build():
    try:
        r = subprocess.run(selfcmd("--build"), cwd=HERE, capture_output=True, text=True,
                           timeout=900, creationflags=NO_WINDOW)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"error: {e}"


def spawn(cmd, **kw):
    return subprocess.Popen(cmd, cwd=HERE, creationflags=NO_WINDOW, **kw)


# ------------------------------------------------------------------ automatic startup (Windows)
def instalar_inicio():
    if not IS_WIN:
        say("On this system, add `python3 start.py --silent` to your startup programs (or to systemd/cron @reboot) yourself.")
        return
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    exe = pyw if os.path.isfile(pyw) else sys.executable
    tr = f'"{sys.executable}" --silent' if paths.FROZEN else f'"{exe}" "{SELF}" --silent'
    r = subprocess.run(["schtasks", "/Create", "/TN", TASK_INICIO, "/SC", "ONLOGON", "/F", "/TR", tr],
                       capture_output=True, text=True, creationflags=NO_WINDOW)
    say("Done: it will start by itself every time you log in." if r.returncode == 0 else "Could not create it: " + r.stdout + r.stderr)


def quitar_inicio():
    if IS_WIN:
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_INICIO, "/F"], capture_output=True, creationflags=NO_WINDOW)
    say("It will no longer start by itself.")


def inicio_instalado():
    if not IS_WIN:
        return True
    return subprocess.run(["schtasks", "/Query", "/TN", TASK_INICIO], capture_output=True, creationflags=NO_WINDOW).returncode == 0


# ------------------------------------------------------------------ main
def main():
    global QUIET
    ap = argparse.ArgumentParser(description="Starts the page and creates a link to share it.")
    ap.add_argument("--no-link", "--sin-enlace", dest="no_link", action="store_true", help="only on this computer, no public link")
    ap.add_argument("--silent", "--silencioso", dest="silent", action="store_true", help="no messages and no browser")
    ap.add_argument("--no-browser", "--sin-navegador", dest="no_browser", action="store_true", help="do not open the browser")
    ap.add_argument("--port", "--puerto", dest="port", type=int, help="local port (default 8765)")
    ap.add_argument("--interval", "--intervalo", dest="interval", type=int, default=60, help="seconds between updates (default 60)")
    ap.add_argument("--choose-world", "--elegir-mundo", dest="choose_world", action="store_true", help="choose which world the page is built from (or go back to automatic mode)")
    ap.add_argument("--install-startup", "--instalar-inicio", dest="install_startup", action="store_true")
    ap.add_argument("--remove-startup", "--quitar-inicio", dest="remove_startup", action="store_true")
    args = ap.parse_args()
    QUIET = args.silent
    if args.silent and IS_WIN and paths.FROZEN:
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass
    if args.install_startup:
        return instalar_inicio()
    if args.remove_startup:
        return quitar_inicio()

    os.makedirs(DATA, exist_ok=True)
    cfg = load_config()
    port = args.port or int(os.environ.get("MCDASH_PORT") or cfg.get("port", 8765))
    local = f"http://127.0.0.1:{port}/"

    # another copy is already running: just show its link
    pidfile = os.path.join(DATA, "start.pid")
    try:
        other = int(open(pidfile).read().strip())
        if other != os.getpid() and pid_alive(other):
            link = open(os.path.join(DATA, "enlace.txt"), encoding="utf-8").read().strip() if os.path.exists(os.path.join(DATA, "enlace.txt")) else local
            say(f"Already running.  Link: {link}")
            return
    except Exception:
        pass
    open(pidfile, "w").write(str(os.getpid()))

    if not args.silent:
        choose_world(force=args.choose_world)
    say("Reading your Minecraft world (the first time takes a little while)...")
    out = run_build()
    say("  " + (out.splitlines()[-1] if out else "no output"))
    if "No Minecraft world found" in out:
        say("\nNo world found. Open Minecraft at least once with a world and run this again,")
        say("or run it with --choose-world to enter your instance folder by hand.")
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
            say(f"Could not set up the public link: {e}")
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
    if not args.no_link:
        state["url"] = None
        procs["tunnel"] = start_tunnel()
    time.sleep(1.5)
    if not port_in_use(port):
        say(f"Could not start the page on port {port}. Is another program using it? Try: --port 8770")
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
        print("  Your page is ready!")
        print(f"  For you:            {local}")
        if url:
            print(f"  For your friends:   {url}" + ("   (copied)" if copied else ""))
            print("  Send them that link: they do not need to install or touch anything.")
            print("  NOTE: the link changes every time this restarts, and anyone who has it can see")
            print("  the players names and their coordinates.")
        else:
            print("  (No public link: it can only be seen on this computer.)")
        print("  Keep this window open; close it to stop sharing.")
        print("=" * 64 + "\n")

    announce(link)
    if not args.silent and not args.no_browser:
        try:
            webbrowser.open(local)
        except Exception:
            pass
    if not args.silent and IS_WIN and sys.stdin and sys.stdin.isatty() and not inicio_instalado():
        pref = os.path.join(DATA, "preferencias.json")
        asked = False
        try:
            asked = json.load(open(pref)).get("preguntado", False)
        except Exception:
            pass
        if not asked:
            try:
                ans = input("Start this automatically when you log in to the computer? [y/N] ").strip().lower()
            except EOFError:
                ans = ""
            save_prefs(preguntado=True)
            if ans.startswith("y"):
                instalar_inicio()

    # loop: refresh the data and make sure everything stays alive
    try:
        next_build = time.time() + args.interval
        while True:
            time.sleep(2)
            if time.time() >= next_build:
                run_build()
                next_build = time.time() + args.interval
            if procs.get("server") is not None and procs["server"].poll() is not None:
                procs["server"] = start_server()
            if "tunnel" in procs and procs["tunnel"] is not None and procs["tunnel"].poll() is not None:
                say("The link went down; creating a new one...")
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
        say("Stopped. See you next time.")


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()          # required in the .exe: build.py uses processes
    if "--build" in sys.argv[1:2]:
        import build
        build.main()
    elif "--serve" in sys.argv[1:2]:
        import serve
        serve.run()
    else:
        main()

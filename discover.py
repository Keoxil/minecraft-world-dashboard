"""Encuentra solo el mundo de Minecraft que está abierto ahora mismo.

Busca instancias de Minecraft en los launchers más habituales (launcher oficial, Modrinth, Prism/MultiMC y
CurseForge), mira cuál de sus mundos tiene el archivo session.lock bloqueado por el juego (= mundo abierto) y, si no
hay ninguno abierto, se queda con el último que se usó. También resuelve las rutas de un mundo en los dos formatos
de carpetas que ha tenido Minecraft (el nuevo, con dimensions/ y players/, y el clásico).
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

IS_WIN = sys.platform.startswith("win")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # que no parpadee una consola al ejecutarse en segundo plano


# ------------------------------------------------------------------ instancias
def _home():
    return os.path.expanduser("~")


def _appdata():
    if IS_WIN:
        return os.environ.get("APPDATA") or os.path.join(_home(), "AppData", "Roaming")
    if sys.platform == "darwin":
        return os.path.join(_home(), "Library", "Application Support")
    return os.environ.get("XDG_DATA_HOME") or os.path.join(_home(), ".local", "share")


def _documents_dirs():
    """Carpetas donde puede estar CurseForge: el perfil, Documentos y Documentos dentro de OneDrive (muy habitual en Windows)."""
    home = _home()
    out = [home, os.path.join(home, "Documents")]
    for var in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        base = os.environ.get(var)
        if base:
            out += [base, os.path.join(base, "Documents"), os.path.join(base, "Documentos")]
    out += [os.path.join(home, "OneDrive", "Documents"), os.path.join(home, "OneDrive", "Documentos"), os.path.join(home, "Documentos")]
    seen, res = set(), []
    for d in out:
        d = os.path.normpath(d)
        if d not in seen:
            seen.add(d)
            res.append(d)
    return res


def instance_roots(extra=()):
    """Carpetas de instancia (las que contienen saves/)."""
    ad, home = _appdata(), _home()
    candidates = [os.path.join(ad, ".minecraft"), os.path.join(ad, "minecraft"), os.path.join(home, ".minecraft")]
    for pattern in (
        os.path.join(ad, "ModrinthApp", "profiles", "*"),
        os.path.join(ad, "com.modrinth.theseus", "profiles", "*"),
        os.path.join(ad, "PrismLauncher", "instances", "*", ".minecraft"),
        os.path.join(ad, "PrismLauncher", "instances", "*", "minecraft"),
        os.path.join(ad, "MultiMC", "instances", "*", ".minecraft"),
        os.path.join(ad, "gdlauncher_next", "instances", "*"),
        os.path.join(ad, "ATLauncher", "instances", "*"),
        os.path.join(ad, "PrismLauncher", "instances", "*", "minecraft"),
    ) + tuple(os.path.join(d, "curseforge", "minecraft", "Instances", "*") for d in _documents_dirs()):
        candidates += glob.glob(pattern)
    for e in list(extra) + [p for p in os.environ.get("MCDASH_INSTANCES", "").split(os.pathsep) if p]:
        candidates.append(os.path.expanduser(e))
    seen, out = set(), []
    for c in candidates:
        c = os.path.normpath(c)
        if c not in seen and os.path.isdir(os.path.join(c, "saves")):
            seen.add(c)
            out.append(c)
    return out


def launcher_of(instance):
    """Nombre del launcher al que pertenece una instancia (por su ruta)."""
    p = instance.replace("\\", "/").lower()
    for key, name in (("modrinthapp", "Modrinth"), ("com.modrinth", "Modrinth"), ("prismlauncher", "Prism Launcher"),
                      ("multimc", "MultiMC"), ("curseforge", "CurseForge"), ("gdlauncher", "GDLauncher"),
                      ("atlauncher", "ATLauncher"), ("/.minecraft", "Official Launcher"), ("/minecraft", "Official Launcher")):
        if key in p:
            return name
    return "Other"


def worlds_of(instance):
    saves = os.path.join(instance, "saves")
    try:
        names = sorted(os.listdir(saves))
    except OSError:
        return []
    return [os.path.join(saves, n) for n in names if os.path.isfile(os.path.join(saves, n, "level.dat"))]


# ------------------------------------------------------------------ mundo abierto
def is_locked(world):
    """Minecraft mantiene bloqueado session.lock mientras el mundo está abierto (en Windows no se puede leer)."""
    lock = os.path.join(world, "session.lock")
    if not os.path.exists(lock):
        return False
    try:
        with open(lock, "rb") as f:
            f.read(1)
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def _game_dirs_running():
    """En Linux/macOS: carpetas --gameDir de los procesos de Java en marcha (el bloqueo no se puede leer ahí)."""
    if IS_WIN:
        return []
    try:
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return []
    dirs = []
    for ln in out.splitlines():
        if "java" in ln and "--gameDir" in ln:
            m = re.search(r"--gameDir\s+(\"[^\"]+\"|\S+)", ln)
            if m:
                dirs.append(os.path.normpath(m.group(1).strip('"')))
    return dirs


def _mtime(world):
    try:
        return os.path.getmtime(os.path.join(world, "level.dat"))
    except OSError:
        return 0


def pick(config, data_dir):
    """Devuelve {'instance', 'world', 'open'} del mundo que toca mostrar."""
    forced = config.get("world")
    if forced:
        w = os.path.normpath(os.path.expanduser(forced))
        inst = os.path.dirname(os.path.dirname(w))
        return {"instance": inst, "world": w, "open": is_locked(w)}
    roots = instance_roots(config.get("instances", []))
    if config.get("launcher"):                 # elegido en el menú de arranque: solo instancias de ese launcher
        roots = [i for i in roots if launcher_of(i) == config["launcher"]] or roots
    allw = [(i, w) for i in roots for w in worlds_of(i)]
    locked = [(i, w) for i, w in allw if is_locked(w)]
    if not locked:
        running = _game_dirs_running()
        locked = [(i, w) for i, w in allw if os.path.normpath(i) in running]
        if locked:
            locked = [max(locked, key=lambda iw: _mtime(iw[1]))]
    state_path = os.path.join(data_dir, "last_world.json")
    if locked:
        i, w = max(locked, key=lambda iw: _mtime(iw[1]))
        _save_last(state_path, i, w)
        return {"instance": i, "world": w, "open": True}
    try:
        last = json.load(open(state_path, encoding="utf-8"))
        if os.path.isfile(os.path.join(last["world"], "level.dat")):
            return {"instance": last["instance"], "world": last["world"], "open": False}
    except Exception:
        pass
    if allw:
        i, w = max(allw, key=lambda iw: _mtime(iw[1]))
        return {"instance": i, "world": w, "open": False}
    return None


def list_worlds(config):
    """Todos los mundos encontrados, el abierto primero y después los más recientes: [{instance, world, name, open}]."""
    out = []
    for i in instance_roots(config.get("instances", [])):
        for w in worlds_of(i):
            out.append({"instance": i, "world": w, "name": os.path.basename(w), "launcher": launcher_of(i), "open": is_locked(w), "mtime": _mtime(w)})
    out.sort(key=lambda x: (not x["open"], -x["mtime"]))
    return out


def _save_last(path, instance, world):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"instance": instance, "world": world}, fh)
    except OSError:
        pass


def slug(instance, world):
    inst = os.path.basename(instance)
    if inst.lower() in (".minecraft", "minecraft"):
        inst = os.path.basename(os.path.dirname(instance))
    return re.sub(r"[^A-Za-z0-9._-]+", "_", f"{inst}__{os.path.basename(world)}")[:120]


# ------------------------------------------------------------------ rutas dentro de un mundo (nuevo y clásico)
def region_dir(world, dim):
    new = os.path.join(world, "dimensions", "minecraft", dim, "region")
    if os.path.isdir(new):
        return new
    legacy = {"overworld": "region", "the_nether": os.path.join("DIM-1", "region"), "the_end": os.path.join("DIM1", "region")}
    return os.path.join(world, legacy[dim])


def _first_dir(world, *rels):
    for r in rels:
        p = os.path.join(world, r)
        if os.path.isdir(p):
            return p
    return os.path.join(world, rels[0])


def stat_files(world):
    return sorted(glob.glob(os.path.join(_first_dir(world, os.path.join("players", "stats"), "stats"), "*.json")))


def adv_file(world, uuid):
    return os.path.join(_first_dir(world, os.path.join("players", "advancements"), "advancements"), uuid + ".json")


def player_file(world, uuid):
    return os.path.join(_first_dir(world, os.path.join("players", "data"), "playerdata"), uuid + ".dat")


# ------------------------------------------------------------------ nombres de jugador
def read_names(instance, world):
    """UUID -> nombre, de usercache.json y, si falta alguno, de las líneas «UUID of player X is …» del registro."""
    names = {}
    for p in (os.path.join(instance, "usercache.json"), os.path.join(os.path.dirname(os.path.dirname(world)), "usercache.json")):
        try:
            for e in json.load(open(p, encoding="utf-8")):
                names.setdefault(e["uuid"], e["name"])
        except Exception:
            pass
    logs = sorted(glob.glob(os.path.join(instance, "logs", "*.log")))
    for lg in logs[-3:]:
        try:
            for ln in open(lg, encoding="utf-8", errors="replace"):
                m = re.search(r"UUID of player (\S+) is ([0-9a-fA-F-]{36})", ln)
                if m:
                    names.setdefault(m.group(2).lower(), m.group(1))
        except OSError:
            pass
    return names


# ------------------------------------------------------------------ varios
def assets_dirs(instance):
    """Carpetas de assets del juego (para leer los nombres oficiales de los logros)."""
    ad, home = _appdata(), _home()
    cands = [os.path.join(ad, "ModrinthApp", "meta", "assets"), os.path.join(ad, "com.modrinth.theseus", "meta", "assets"),
             os.path.join(ad, ".minecraft", "assets"), os.path.join(home, ".minecraft", "assets"),
             os.path.join(ad, "PrismLauncher", "assets"), os.path.join(ad, "MultiMC", "assets"),
             os.path.join(instance, "assets")]
    return [c for c in cands if os.path.isdir(os.path.join(c, "indexes"))]


def java_running():
    """¿Hay algún Minecraft (Java) en marcha?"""
    try:
        if IS_WIN:
            out = subprocess.run([os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "tasklist.exe"), "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=10,
                                 creationflags=NO_WINDOW).stdout.lower()
            return "javaw.exe" in out or "java.exe" in out
        return subprocess.run(["pgrep", "-f", "java"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return True

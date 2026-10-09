"""Rutas comunes. RES = recursos de solo lectura (site/index.html); APP = datos del usuario (config, data/, site/*.js)."""
import os
import sys

FROZEN = bool(getattr(sys, "frozen", False))
RES = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def _app():
    if os.environ.get("MCDASH_HOME"):
        return os.path.abspath(os.environ["MCDASH_HOME"])
    if FROZEN:
        base = os.environ.get("LOCALAPPDATA") if sys.platform.startswith("win") else os.path.join(os.path.expanduser("~"), ".local", "share")
        return os.path.join(base or os.path.expanduser("~"), "MinecraftWorldDashboard")
    return os.path.dirname(os.path.abspath(__file__))


APP = _app()
os.makedirs(APP, exist_ok=True)

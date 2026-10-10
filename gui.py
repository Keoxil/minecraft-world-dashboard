"""Desktop app window: pick the world, copy the public link, open the page. No console needed.

Run with `python gui.py`, or just open the installed "Minecraft World Dashboard" app.
"""
import os
import re
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox

import customtkinter as ctk

import paths
import start

APP_NAME = "Minecraft World Dashboard"
AUTO_LABEL = "Automatic (follow the world I have open)"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "MinecraftWorldDashboard"
LOCK_PORT = 47831            # only one copy of the app at a time (a free local port acts as the lock)
URL_RE = start.URL_RE


def free_port(first):
    for p in range(first, first + 40):
        if not start.port_in_use(p):
            return p
    return first


# ------------------------------------------------------------------ background work
class Service:
    """Builds the data every minute, serves the page and (optionally) keeps a Cloudflare tunnel alive."""

    def __init__(self):
        cfg = start.load_config()
        self.port = free_port(int(os.environ.get("MCDASH_PORT") or cfg.get("port", 8765)))
        self.state = {"status": "Starting...", "world": "", "link": None, "tool": "", "error": "", "last_ok": None}
        self.share = True
        self.stop_ev = threading.Event()
        self.kick = threading.Event()
        self.tunnel = None
        self.tunnel_gen = 0
        self.lock = threading.Lock()

    def set(self, **kw):
        with self.lock:
            self.state.update(kw)

    def get(self):
        with self.lock:
            return dict(self.state)

    # --- local server
    def start_server(self):
        import serve

        def run():
            try:
                serve.run(self.port)
            except Exception as e:
                self.set(error=f"Could not start the local page: {e}")
        threading.Thread(target=run, daemon=True).start()

    # --- data builder
    def build_loop(self):
        while not self.stop_ev.is_set():
            self.set(status="Reading your world...")
            out = start.run_build()
            lines = [l for l in out.splitlines() if l.strip()]
            world = next((l for l in lines if l.startswith("World:")), "")
            if any("No Minecraft world found" in l for l in lines):
                self.set(status="No Minecraft world found yet", world="", error="Open Minecraft once with a world, or use 'Add folder...' below.")
            elif lines and lines[-1].startswith("OK"):
                m = re.match(r"World:\s*(.*?)\s{2}\((.*?)\)", world)
                self.set(status="Running", world=(f"{m.group(1)}  ({m.group(2)})" if m else world), error="", last_ok=time.time())
            else:
                self.set(status="Something went wrong while reading the world", error=(lines[-1] if lines else "no output")[:200])
            self.kick.wait(60)
            self.kick.clear()

    # --- public link
    def tunnel_loop(self):
        gen = self.tunnel_gen
        while not self.stop_ev.is_set() and gen == self.tunnel_gen and self.share:
            try:
                start.say = lambda *a: self.set(tool=" ".join(str(x) for x in a))     # shows download progress in the window
                cf = start.ensure_cloudflared()
            except Exception as e:
                self.set(tool=f"Could not prepare the public link: {e}")
                self.stop_ev.wait(30)
                continue
            self.set(tool="Creating your link...", link=None)
            proc = start.spawn([cf, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{self.port}"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            self.tunnel = proc
            for ln in proc.stdout:
                m = URL_RE.search(ln)
                if m:
                    self.set(link=m.group(0), tool="")
                if self.stop_ev.is_set() or gen != self.tunnel_gen or not self.share:
                    break
            try:
                proc.terminate()
            except Exception:
                pass
            if self.share and gen == self.tunnel_gen and not self.stop_ev.is_set():
                self.set(link=None, tool="The link went down; creating a new one...")
                self.stop_ev.wait(3)
        self.set(link=None, tool="" if not self.share else self.get()["tool"])

    def set_share(self, on):
        self.share = on
        self.tunnel_gen += 1
        if self.tunnel and self.tunnel.poll() is None:
            try:
                self.tunnel.terminate()
            except Exception:
                pass
        if on:
            threading.Thread(target=self.tunnel_loop, daemon=True).start()
        else:
            self.set(link=None, tool="")

    def run(self):
        self.start_server()
        threading.Thread(target=self.build_loop, daemon=True).start()
        if self.share:
            threading.Thread(target=self.tunnel_loop, daemon=True).start()

    def stop(self):
        self.stop_ev.set()
        self.share = False
        self.tunnel_gen += 1
        if self.tunnel and self.tunnel.poll() is None:
            try:
                self.tunnel.terminate()
            except Exception:
                pass


# ------------------------------------------------------------------ start with Windows
def autostart_enabled():
    if not start.IS_WIN:
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, RUN_VALUE)
            return True
    except OSError:
        return False


def set_autostart(on):
    if not start.IS_WIN:
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            cmd = f'"{sys.executable}" --minimized' if paths.FROZEN else f'"{sys.executable}" "{os.path.abspath(__file__)}" --minimized'
            winreg.SetValueEx(k, RUN_VALUE, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(k, RUN_VALUE)
            except OSError:
                pass


# ------------------------------------------------------------------ window
BG, CARD, CARD2 = "#0b1118", "#141d28", "#1b2736"
INK, MUT, ACC, ACC_HI, BAD = "#e8f1f5", "#8fa3b3", "#4fd6c8", "#7fe8dc", "#ff8a7a"
FONT = "Segoe UI"


def res(name):
    """Bundled resource path: next to the app when frozen, inside assets/ when running from source."""
    for d in (paths.RES, os.path.join(paths.RES, "assets")):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return ""


def app_version():
    p = res("version.txt")
    try:
        return open(p, encoding="utf-8").read().strip() if p else ""
    except OSError:
        return ""


class App:
    def __init__(self, root, svc, minimized):
        self.root, self.svc = root, svc
        self.worlds = []
        root.title(APP_NAME)
        root.geometry("640x700")
        root.minsize(600, 660)
        root.configure(fg_color=BG)
        ico = res("app.ico")
        if ico:
            try:
                root.after(250, lambda: root.iconbitmap(ico))       # customtkinter resets the icon at start-up; set it after
            except tk.TclError:
                pass
        self.build_ui()
        self.refresh_worlds()
        self.tick()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        if minimized:
            root.iconify()

    # ---- building blocks
    def card(self, parent, title, pady=(0, 14)):
        f = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16)
        f.pack(fill="x", padx=24, pady=pady)
        ctk.CTkLabel(f, text=title, text_color=MUT, font=(FONT, 11, "bold"), anchor="w").pack(fill="x", padx=18, pady=(14, 0))
        return f

    def build_ui(self):
        r = self.root

        # header
        head = ctk.CTkFrame(r, fg_color="transparent")
        head.pack(fill="x", padx=24, pady=(22, 16))
        png = res("app_icon.png")
        if png:
            try:
                self.logo = tk.PhotoImage(file=png)
                tk.Label(head, image=self.logo, bg=BG, bd=0).pack(side="left", padx=(0, 14))
            except tk.TclError:
                pass
        box = ctk.CTkFrame(head, fg_color="transparent")
        box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(box, text="World Dashboard", font=(FONT, 26, "bold"), text_color=INK, anchor="w").pack(fill="x")
        ctk.CTkLabel(box, text="Your Minecraft world, live on the web", font=(FONT, 12), text_color=MUT, anchor="w").pack(fill="x")
        self.pill = ctk.CTkFrame(head, fg_color=CARD, corner_radius=20)
        self.pill.pack(side="right")
        self.dot = ctk.CTkLabel(self.pill, text="●", text_color=MUT, font=(FONT, 12), width=16)
        self.dot.pack(side="left", padx=(12, 0), pady=6)
        self.status = ctk.CTkLabel(self.pill, text="Starting...", text_color=INK, font=(FONT, 12))
        self.status.pack(side="left", padx=(2, 14), pady=6)

        # world
        w = self.card(r, "WORLD")
        self.var_world = ctk.StringVar(value=AUTO_LABEL)
        self.menu = ctk.CTkOptionMenu(w, variable=self.var_world, values=[AUTO_LABEL], command=self.on_world, height=38, corner_radius=10,
                                      fg_color=CARD2, button_color="#243449", button_hover_color="#2d4259", dropdown_fg_color=CARD2,
                                      dropdown_hover_color="#2d4259", text_color=INK, dropdown_text_color=INK, font=(FONT, 13),
                                      dropdown_font=(FONT, 12), anchor="w", dynamic_resizing=False)
        self.menu.pack(fill="x", padx=18, pady=(8, 8))
        row = ctk.CTkFrame(w, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(0, 14))
        self.showing = ctk.CTkLabel(row, text="", text_color=MUT, font=(FONT, 12), anchor="w")
        self.showing.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Add folder", width=96, height=30, corner_radius=8, fg_color="transparent", border_width=1, border_color="#2d4259",
                      text_color=INK, hover_color=CARD2, font=(FONT, 12), command=self.add_folder).pack(side="right")

        # open page (hero button)
        hero = ctk.CTkFrame(r, fg_color="transparent")
        hero.pack(fill="x", padx=24, pady=(0, 14))
        ctk.CTkButton(hero, text="Open my page", height=52, corner_radius=14, fg_color=ACC, hover_color=ACC_HI, text_color="#06201d",
                      font=(FONT, 16, "bold"), command=self.open_local).pack(fill="x")
        self.local_lbl = ctk.CTkLabel(hero, text="", text_color=MUT, font=(FONT, 11))
        self.local_lbl.pack(pady=(6, 0))

        # share
        s = self.card(r, "SHARE WITH FRIENDS", pady=(0, 10))
        top = ctk.CTkFrame(s, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(6, 0))
        ctk.CTkLabel(top, text="Public link", text_color=INK, font=(FONT, 14, "bold"), anchor="w").pack(side="left")
        self.share_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(top, text="", variable=self.share_var, command=self.on_share, width=44, progress_color=ACC, button_color=INK,
                      button_hover_color="#ffffff", fg_color="#2d4259").pack(side="right")
        row = ctk.CTkFrame(s, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(10, 0))
        self.link_var = ctk.StringVar(value="")
        self.link_entry = ctk.CTkEntry(row, textvariable=self.link_var, state="readonly", height=38, corner_radius=10, fg_color=BG, border_color="#2d4259",
                                       text_color=INK, font=("Consolas", 12))
        self.link_entry.pack(side="left", fill="x", expand=True)
        self.copy_btn = ctk.CTkButton(row, text="Copy", width=84, height=38, corner_radius=10, fg_color=ACC, hover_color=ACC_HI, text_color="#06201d",
                                      font=(FONT, 13, "bold"), command=self.copy_link)
        self.copy_btn.pack(side="right", padx=(8, 0))
        self.tool_lbl = ctk.CTkLabel(s, text="", text_color=MUT, font=(FONT, 11), anchor="w")
        self.tool_lbl.pack(fill="x", padx=18, pady=(6, 0))
        ctk.CTkLabel(s, text="Anyone with the link can see player names and coordinates. The link changes every time the app restarts.",
                     text_color=MUT, font=(FONT, 11), wraplength=540, justify="left", anchor="w").pack(fill="x", padx=18, pady=(2, 14))

        # footer
        foot = ctk.CTkFrame(r, fg_color="transparent")
        foot.pack(fill="x", padx=26, pady=(4, 0))
        self.auto_var = ctk.BooleanVar(value=autostart_enabled())
        if start.IS_WIN:
            ctk.CTkSwitch(foot, text="Start with Windows", variable=self.auto_var, command=self.on_auto, progress_color=ACC, button_color=INK,
                          fg_color="#2d4259", text_color=INK, font=(FONT, 13)).pack(side="left")
        ver = app_version()
        ctk.CTkLabel(foot, text=("v" + ver) if ver else "", text_color=MUT, font=(FONT, 11)).pack(side="right")
        self.err = ctk.CTkLabel(r, text="", text_color=BAD, font=(FONT, 12), wraplength=580, justify="left", anchor="w")
        self.err.pack(fill="x", padx=26, pady=(8, 0))
        ctk.CTkLabel(r, text="Closing this window stops sharing. Minimize it to keep the page online.", text_color=MUT, font=(FONT, 11),
                     anchor="w").pack(fill="x", padx=26, pady=(2, 12))

    # ---- worlds
    def refresh_worlds(self):
        cfg = dict(start.load_config())
        prefs = start.load_prefs()
        cfg["instances"] = list(cfg.get("instances", [])) + list(prefs.get("instances", []))
        try:
            import discover
            self.worlds = discover.list_worlds(cfg)
        except Exception:
            self.worlds = []
        self.labels = [AUTO_LABEL]
        for w in self.worlds:
            self.labels.append(f"{w['name']}   -   {w['launcher']}: {os.path.basename(w['instance'])}" + ("   (open now)" if w["open"] else ""))
        self.menu.configure(values=self.labels)
        cur = prefs.get("world")
        idx = 0
        for i, w in enumerate(self.worlds, 1):
            if cur and os.path.normpath(w["world"]) == os.path.normpath(cur):
                idx = i
        self.var_world.set(self.labels[idx])

    def on_world(self, choice):
        i = self.labels.index(choice) if choice in self.labels else 0
        if i <= 0:
            start.save_prefs(mundo_preguntado=True, world=None, launcher=None)
        else:
            start.save_prefs(mundo_preguntado=True, world=self.worlds[i - 1]["world"], launcher=None)
        self.svc.set(status="Reading your world...")
        self.svc.kick.set()

    def add_folder(self):
        folder = filedialog.askdirectory(title="Choose your Minecraft instance folder (the one that contains 'saves')")
        if not folder:
            return
        folder = os.path.abspath(folder)
        if os.path.basename(folder).lower() == "saves":
            folder = os.path.dirname(folder)
        if not os.path.isdir(os.path.join(folder, "saves")):
            messagebox.showwarning(APP_NAME, "I could not find a 'saves' folder there. Pick the folder that contains 'saves'.")
            return
        prefs = start.load_prefs()
        start.save_prefs(instances=sorted(set(prefs.get("instances", [])) | {folder}))
        self.refresh_worlds()
        self.svc.kick.set()

    # ---- actions
    def open_local(self):
        webbrowser.open(f"http://127.0.0.1:{self.svc.port}/")

    def copy_link(self):
        link = self.svc.get()["link"]
        if link:
            self.root.clipboard_clear()
            self.root.clipboard_append(link)
            self.copy_btn.configure(text="Copied!")
            self.root.after(1500, lambda: self.copy_btn.configure(text="Copy"))

    def on_share(self):
        self.svc.set_share(self.share_var.get())

    def on_auto(self):
        try:
            set_autostart(self.auto_var.get())
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Could not change the startup setting: {e}")
            self.auto_var.set(autostart_enabled())

    def quit(self):
        self.svc.stop()
        self.root.destroy()

    # ---- periodic refresh
    def tick(self):
        st = self.svc.get()
        ok = st["status"] == "Running"
        self.status.configure(text=st["status"])
        self.dot.configure(text_color=ACC if ok else (BAD if st["error"] else "#e5b94d"))
        self.showing.configure(text=("Showing: " + st["world"]) if st["world"] else "")
        self.local_lbl.configure(text=f"http://127.0.0.1:{self.svc.port}")
        self.link_var.set(st["link"] or ("" if self.share_var.get() else "Public link is off"))
        self.tool_lbl.configure(text=st["tool"] if not st["link"] else "")
        self.copy_btn.configure(state="normal" if st["link"] else "disabled")
        self.err.configure(text=st["error"])
        self.root.after(700, self.tick)


def main():
    minimized = "--minimized" in sys.argv
    lock = socket.socket()
    try:
        lock.bind(("127.0.0.1", LOCK_PORT))
    except OSError:
        r = tk.Tk()
        r.withdraw()
        messagebox.showinfo(APP_NAME, "Minecraft World Dashboard is already running. Look for it in your taskbar.")
        return
    svc = Service()
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    App(root, svc, minimized)
    svc.run()
    root.mainloop()
    svc.stop()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    if "--build" in sys.argv[1:2]:
        import build
        build.main()
    elif "--serve" in sys.argv[1:2]:
        import serve
        serve.run()
    else:
        main()

"""Cliente CDP mínimo (solo biblioteca estándar) para controlar Edge/Chrome headless."""
import base64, json, os, shutil, socket, struct, subprocess, time, urllib.request

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


class WS:
    def __init__(self, url):
        assert url.startswith("ws://")
        host, rest = url[5:].split("/", 1)
        h, p = host.split(":")
        self.s = socket.create_connection((h, int(p)), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{rest} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(1)
        self.buf = b""

    def send(self, obj):
        d = json.dumps(obj).encode()
        hdr = bytearray([0x81])
        n = len(d)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126); hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127); hdr += struct.pack(">Q", n)
        mask = os.urandom(4)
        self.s.sendall(bytes(hdr) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(d)))

    def _read(self, n):
        while len(self.buf) < n:
            c = self.s.recv(65536)
            if not c:
                raise EOFError
            self.buf += c
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        msg = b""
        while True:
            b1, b2 = self._read(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            payload = self._read(n)
            msg += payload
            if b1 & 0x80:
                return json.loads(msg.decode("utf-8", "replace"))


class Browser:
    def __init__(self, url, port=9333, prof=None, extra=()):
        self.prof = prof or os.path.join(os.environ["TEMP"], "cdp_prof_%d" % port)
        shutil.rmtree(self.prof, ignore_errors=True)
        self.p = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--remote-debugging-port={port}",
                                   f"--user-data-dir={self.prof}", "--no-first-run", *extra, "about:blank"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2))
                page = [t for t in tabs if t.get("type") == "page"][0]
                break
            except Exception:
                time.sleep(0.5)
        self.ws = WS(page["webSocketDebuggerUrl"])
        self.i = 0
        self.logs = []
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            self.call(m)
        self.call("Page.navigate", url=url)

    def call(self, method, **params):
        self.i += 1
        my = self.i
        self.ws.send({"id": my, "method": method, "params": params})
        while True:
            m = self.ws.recv()
            if m.get("id") == my:
                return m.get("result", {})
            self._note(m)

    def _note(self, m):
        k = m.get("method")
        if k == "Runtime.consoleAPICalled":
            self.logs.append(("console." + m["params"]["type"], " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])[:300]))
        elif k == "Runtime.exceptionThrown":
            d = m["params"]["exceptionDetails"]
            self.logs.append(("EXCEPTION", (d.get("exception", {}).get("description") or d.get("text", ""))[:400]))
        elif k == "Log.entryAdded":
            e = m["params"]["entry"]
            self.logs.append(("log." + e["level"], e["text"][:300]))

    def run_js(self, js):  # solo pruebas: evalua JS en un Edge de prueba sobre nuestra pagina local
        r = self.call("Runtime.evaluate", expression=js, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")

    def wait(self, js, timeout=40, every=0.5):
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                v = self.run_js(js)
                if v:
                    return v
            except Exception:
                pass
            time.sleep(every)
        return None

    def close(self):
        try:
            self.call("Browser.close")
        except Exception:
            pass
        self.p.kill()

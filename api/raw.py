from http.server import BaseHTTPRequestHandler
import os
import re
import urllib.parse
import urllib.request

KNOWN_HOSTS = ["sqe5t8mtibvai8ge"]


def candidate_hosts():
    hosts = []
    s = (os.environ.get("BLOB_STORE_ID") or "").strip()
    if s.startswith("store_"):
        s = s[len("store_"):]
    if s:
        hosts.append(s.lower())
    for h in KNOWN_HOSTS:
        if h not in hosts:
            hosts.append(h)
    return hosts


def is_browser(headers) -> bool:
    ua = (headers.get("User-Agent") or "").lower()
    if "roblox" in ua:
        return False
    dest = (headers.get("Sec-Fetch-Dest") or "").lower()
    mode = (headers.get("Sec-Fetch-Mode") or "").lower()
    if dest == "document" or mode == "navigate":
        return True
    accept = (headers.get("Accept") or "").lower()
    if accept.startswith("text/html") and "mozilla" in ua:
        return True
    return False


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "NovaProtector/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>NovaProtector</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#000;color:#fff;font-family:system-ui,sans-serif}
.wrap{min-height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;gap:14px}
.shield{font-size:64px}
h1{font-size:1.45rem}
p{color:#aaa;max-width:420px;line-height:1.5}
a{color:#5865F2;text-decoration:none;font-weight:600;border:1px solid #5865F2;padding:10px 18px;border-radius:8px}
a:hover{background:#5865F2;color:#fff}
.links{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.id{color:#555;font-size:.75rem;margin-top:16px;word-break:break-all}
</style>
</head>
<body>
<div class="wrap">
  <div class="shield">&#128737;&#65039;</div>
  <h1>Este codigo ha sido protegido por NovaProtector</h1>
  <p>Ofuscado en <strong style="color:#fff">https://novaprotector.vercel.app/</strong></p>
  <div class="links">
    <a href="https://novaprotector.vercel.app/" target="_blank" rel="noopener">NovaProtector</a>
    <a href="https://discord.gg/9kqrTp2NM" target="_blank" rel="noopener">Discord</a>
  </div>
  <div class="id">id: {file_id}</div>
</div>
</body>
</html>
"""


class handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        return

    def _send(self, status, body, ctype="text/plain; charset=utf-8"):
        if not isinstance(body, (bytes, bytearray)):
            body = str(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Disposition", "inline")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, b"ok")

    def do_GET(self):
        try:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_id = (qs.get("id") or [None])[0]
            blob_url = (qs.get("url") or [None])[0]

            if not file_id or not re.fullmatch(r"[a-zA-Z0-9_-]{8,64}", file_id):
                self._send(400, b"Identificador no valido.")
                return

            if is_browser(self.headers):
                self._send(200, HTML.replace("{file_id}", file_id).encode("utf-8"), "text/html; charset=utf-8")
                return

            candidates = []
            if blob_url:
                decoded = urllib.parse.unquote(blob_url)
                if decoded.startswith("https://") and "blob.vercel-storage.com" in decoded:
                    candidates.append(decoded)

            for host in candidate_hosts():
                candidates.append("https://%s.public.blob.vercel-storage.com/%s.lua" % (host, file_id))
                candidates.append("https://%s.public.blob.vercel-storage.com/%s" % (host, file_id))

            last = None
            for url in candidates:
                try:
                    data = fetch_bytes(url)
                    # Evitar devolver JSON de error accidental
                    if data.lstrip().startswith(b"{") and b"obfuscationReady" in data[:200]:
                        last = "respuesta API invalida"
                        continue
                    self._send(200, data, "text/plain; charset=utf-8")
                    return
                except Exception as e:
                    last = e
                    continue

            self._send(404, ("Script no encontrado: " + str(last)).encode("utf-8"))
        except Exception as e:
            self._send(500, str(e).encode("utf-8"))


app = handler

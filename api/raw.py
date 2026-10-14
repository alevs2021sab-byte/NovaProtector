from http.server import BaseHTTPRequestHandler
import os
import re
import urllib.parse
import urllib.request
import urllib.error

STORE_FALLBACK = ""  # opcional: store_xxx si no hay env


def store_host():
    s = (os.environ.get("BLOB_STORE_ID") or STORE_FALLBACK or "").strip()
    if s.startswith("store_"):
        s = s[len("store_"):]
    return s.lower()


def is_browser(headers) -> bool:
    ua = (headers.get("User-Agent") or "").lower()
    accept = (headers.get("Accept") or "").lower()
    if "roblox" in ua:
        return False
    if "mozilla" in ua or "chrome" in ua or "safari" in ua or "firefox" in ua:
        return True
    if "text/html" in accept:
        return True
    return False


HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>NovaProtector</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:#000;color:#fff;font-family:system-ui,sans-serif}}
.wrap{{min-height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;gap:14px}}
.shield{{font-size:64px}}
h1{{font-size:1.5rem}}
p{{color:#aaa;max-width:420px;line-height:1.45}}
a{{color:#5865F2;text-decoration:none;font-weight:600;border:1px solid #5865F2;padding:10px 18px;border-radius:8px}}
a:hover{{background:#5865F2;color:#fff}}
.id{{color:#555;font-size:.75rem;margin-top:20px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="shield">🛡️</div>
  <h1>Este código ha sido protegido por NovaProtector</h1>
  <p>Ofuscado en <strong style="color:#fff">https://novaprotector.vercel.app/</strong></p>
  <a href="https://novaprotector.vercel.app/" target="_blank" rel="noopener">NovaProtector</a>
  <a href="https://discord.gg/9kqrTp2NM" target="_blank" rel="noopener">Discord</a>
  <div class="id">id: {file_id}</div>
</div>
</body>
</html>
"""


class handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, status, body: bytes, ctype="text/plain; charset=utf-8"):
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
            if not file_id or not re.fullmatch(r"[a-zA-Z0-9_-]{6,64}", file_id):
                self._send(400, b"invalid id")
                return

            if is_browser(self.headers):
                html = HTML.format(file_id=file_id)
                self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
                return

            host = store_host()
            if not host:
                self._send(500, b"BLOB_STORE_ID not configured")
                return
            url = f"https://{host}.public.blob.vercel-storage.com/{file_id}.lua"
            req = urllib.request.Request(url, headers={"User-Agent": "NovaProtector/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
            except Exception as e:
                self._send(404, f"not found: {e}".encode())
                return
            self._send(200, data, "text/plain; charset=utf-8")
        except Exception as e:
            self._send(500, str
                       (e).encode())

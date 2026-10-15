
from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.parse
import urllib.request
import urllib.error

MAX_BYTES = 200_000
ALLOWED_HOST_SUFFIX = ".public.blob.vercel-storage.com"


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_text(self, status, text):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header(
            "Content-Type", "text/plain; charset=utf-8"
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        params = urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query
        )

        file_id = params.get("id", [""])[0]
        blob_url = params.get("url", [""])[0]

        if not re.fullmatch(r"[a-f0-9]{32}", file_id):
            self.send_text(400, "Identificador no válido.")
            return

        parsed = urllib.parse.urlparse(blob_url)
        hostname = (parsed.hostname or "").lower()

        if (
            parsed.scheme != "https"
            or not hostname.endswith(ALLOWED_HOST_SUFFIX)
            or parsed.username
            or parsed.password
            or parsed.port not in (None, 443)
            or parsed.query
            or parsed.fragment
            or not parsed.path.endswith("/" + file_id + ".lua")
        ):
            self.send_text(400, "URL de archivo no válida.")
            return

        request = urllib.request.Request(
            blob_url,
            headers={"Accept": "text/plain"},
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read(MAX_BYTES + 1)

            if len(data) > MAX_BYTES:
                self.send_text(413, "El archivo supera los 200 KB.")
                return

            content = data.decode("utf-8")
            self.send_text(200, content)

        except urllib.error.HTTPError as exc:
            self.send_text(
                502, f"No se pudo recuperar el archivo ({exc.code})."
            )
        except (urllib.error.URLError, UnicodeDecodeError, OSError):
            self.send_text(502, "No se pudo recuperar el archivo.")



app = handler

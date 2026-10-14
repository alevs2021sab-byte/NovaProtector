
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import urllib.parse
import urllib.request
import urllib.error

MAX_BYTES = 200_000
BLOB_SUFFIX = ".public.blob.vercel-storage.com"


def send_text(handler, status, message):
    body = message.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_json(handler, status, data):
    body = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def validate_blob_url(url, file_id):
    try:
        parsed = urllib.parse.urlparse(url)

        if parsed.scheme != "https":
            return False

        host = (parsed.hostname or "").lower()

        if not host.endswith(BLOB_SUFFIX):
            return False

        if parsed.username or parsed.password or parsed.port:
            return False

        if parsed.query or parsed.fragment:
            return False

        filename = parsed.path.rsplit("/", 1)[-1]
        return filename == f"{file_id}.lua"

    except (ValueError, AttributeError):
        return False


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        query = urllib.parse.parse_qs(
            urllib.parse.urlparse(self.path).query
        )

        file_id = (query.get("id") or [""])[0]
        blob_url = (query.get("url") or [""])[0]

        if not re.fullmatch(r"[a-f0-9]{16}", file_id):
            send_json(self, 400, {
                "success": False,
                "error": "ID inválido"
            })
            return

        if not validate_blob_url(blob_url, file_id):
            send_json(self, 400, {
                "success": False,
                "error": "URL de Blob inválida"
            })
            return

        request = urllib.request.Request(
            blob_url,
            headers={"User-Agent": "NovaProtector/1.0"}
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                final_url = response.geturl()

                if not validate_blob_url(final_url, file_id):
                    send_json(self, 502, {
                        "success": False,
                        "error": "Redirección de Blob no permitida"
                    })
                    return

                content = response.read(MAX_BYTES + 1)

            if len(content) > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El archivo supera el tamaño permitido"
                })
                return

            self.send_response(200)
            self.send_header(
                "Content-Type", "text/plain; charset=utf-8"
            )
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        except urllib.error.HTTPError as error:
            send_json(self, 502, {
                "success": False,
                "error": f"Vercel Blob respondió HTTP {error.code}"
            })
        except Exception:
            send_json(self, 502, {
                "success": False,
                "error": "No se pudo recuperar el archivo de Blob"
            })


app = handler


from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, build_opener, HTTPHandler
from urllib.error import HTTPError, URLError
import json
import re
import posixpath

MAX_BYTES = 200_000
BLOB_SUFFIX = ".public.blob.vercel-storage.com"


def send_json(handler, status, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header(
        "Content-Type", "application/json; charset=utf-8"
    )
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_text(handler, status, body):
    data = body.encode("utf-8")
    handler.send_response(status)
    handler.send_header(
        "Content-Type", "text/plain; charset=utf-8"
    )
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class NoRedirectHandler(HTTPHandler):
    pass


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        request_url = urlparse(self.path)
        params = parse_qs(
            request_url.query,
            keep_blank_values=True
        )

        file_ids = params.get("id", [])
        blob_urls = params.get("url", [])

        if len(file_ids) != 1 or len(blob_urls) != 1:
            send_json(self, 400, {
                "success": False,
                "error": "ID inválido"
            })
            return

        file_id = file_ids[0]
        blob_url = blob_urls[0]

        if not re.fullmatch(r"[0-9a-f]{16}", file_id):
            send_json(self, 400, {
                "success": False,
                "error": "ID inválido"
            })
            return

        parsed = urlparse(blob_url)

        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or not parsed.hostname.endswith(BLOB_SUFFIX)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.query
            or parsed.fragment
            or posixpath.basename(parsed.path) != file_id + ".lua"
        ):
            send_json(self, 400, {
                "success": False,
                "error": "URL de archivo inválida"
            })
            return

        try:
            request = Request(
                blob_url,
                headers={
                    "User-Agent": "NovaProtector/1.0",
                    "Accept": "text/plain"
                },
                method="GET"
            )

            with build_opener().open(request, timeout=15) as response:
                content = response.read(MAX_BYTES + 1)

            if len(content) > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El archivo supera los 200 KB"
                })
                return

            send_text(
                self,
                200,
                content.decode("utf-8", errors="strict")
            )

        except HTTPError as exc:
            send_json(self, 502, {
                "success": False,
                "error": "No se pudo recuperar el archivo de Blob",
                "upstreamStatus": exc.code
            })
        except (URLError, TimeoutError):
            send_json(self, 502, {
                "success": False,
                "error": "No se pudo conectar con Blob"
            })
        except UnicodeDecodeError:
            send_json(self, 502, {
                "success": False,
                "error": "El archivo no contiene texto UTF-8 válido"
            })
        except Exception:
            send_json(self, 500, {
                "success": False,
                "error": "Error interno al recuperar el archivo"
            })
            

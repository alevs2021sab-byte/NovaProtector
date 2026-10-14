
from http.server import BaseHTTPRequestHandler
import json
import os
import secrets
import urllib.parse
import urllib.request
import urllib.error


MAX_BYTES = 200_000


def send_json(handler, status, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def upload_blob(file_id, content):
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BLOB_READ_WRITE_TOKEN no está configurado.")

    pathname = f"{file_id}.lua"
    url = "https://blob.vercel-storage.com/" + urllib.parse.quote(pathname)

    request = urllib.request.Request(
        url,
        data=content.encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "x-api-version": "7",
            "x-content-type": "text/plain; charset=utf-8",
            "x-add-random-suffix": "0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Vercel Blob respondió HTTP {error.code}: {detail}"
        ) from error

    blob_url = result.get("url")
    if not blob_url:
        raise RuntimeError("Vercel Blob no devolvió una URL.")

    return blob_url


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        send_json(self, 200, {
            "success": True,
            "service": "NovaProtector",
            "blobConfigured": bool(
                os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
            ),
        })

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Allow", "GET, POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "Solicitud vacía o demasiado grande."
                })
                return

            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            code = payload.get("code")

            if not isinstance(code, str) or not code.strip():
                send_json(self, 400, {
                    "success": False,
                    "error": "Introduce código LuaU válido como texto."
                })
                return

            file_id = secrets.token_hex(8)
            blob_url = upload_blob(file_id, code)

            raw_url = (
                "https://novaprotector.vercel.app/api/raw?"
                + urllib.parse.urlencode({
                    "id": file_id,
                    "url": blob_url,
                })
            )

            send_json(self, 200, {
                "success": True,
                "fileId": file_id,
                "blobUrl": blob_url,
                "fileUrl": raw_url,
            })

        except (ValueError, UnicodeDecodeError):
            send_json(self, 400, {
                "success": False,
                "error": "El cuerpo debe ser JSON válido."
            })
        except Exception as error:
            send_json(self, 500, {
                "success": False,
                "error": str(error),
            })


app = handler

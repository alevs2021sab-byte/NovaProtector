
from http.server import BaseHTTPRequestHandler
import json
import os
import secrets
import urllib.parse
import urllib.request
import urllib.error

MAX_BYTES = 200_000
BASE_URL = "https://novaprotector.vercel.app"


def send_json(handler, status, data):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def upload_to_blob(file_id, code):
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Falta BLOB_READ_WRITE_TOKEN en las variables de Vercel."
        )

    pathname = f"{file_id}.lua"
    upload_url = (
        "https://blob.vercel-storage.com/"
        + urllib.parse.quote(pathname, safe="")
    )

    request = urllib.request.Request(
        upload_url,
        data=code.encode("utf-8"),
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
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"Vercel Blob devolvió HTTP {exc.code}: {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "No se pudo conectar con Vercel Blob."
        ) from exc

    blob_url = result.get("url")
    if not isinstance(blob_url, str) or not blob_url.startswith("https://"):
        raise RuntimeError("Blob no devolvió una URL válida.")

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

    def do_POST(self):
        try:
            length_text = self.headers.get("Content-Length", "0")

            try:
                length = int(length_text)
            except ValueError:
                send_json(self, 400, {
                    "success": False,
                    "error": "Longitud de solicitud inválida."
                })
                return

            if length <= 0:
                send_json(self, 400, {
                    "success": False,
                    "error": "La solicitud está vacía."
                })
                return

            if length > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El código supera el límite de 200 KB."
                })
                return

            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
            code = payload.get("code")

            if not isinstance(code, str) or not code.strip():
                send_json(self, 400, {
                    "success": False,
                    "error": "Introduce código LuaU como texto."
                })
                return

            if len(code.encode("utf-8")) > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El código supera el tamaño permitido."
                })
                return

            # Por ahora se conserva el código original.
            # No se afirma que esté ofuscado.
            file_id = secrets.token_hex(8)
            blob_url = upload_to_blob(file_id, code)

            raw_url = (
                f"{BASE_URL}/api/raw?"
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
                "transformed": False,
                "message": (
                    "Archivo guardado correctamente. "
                    "La transformación LuaU aún no está implementada."
                ),
            })

        except (json.JSONDecodeError, UnicodeDecodeError):
            send_json(self, 400, {
                "success": False,
                "error": "El cuerpo debe ser JSON válido en UTF-8."
            })
        except Exception as exc:
            send_json(self, 500, {
                "success": False,
                "error": str(exc),
            })


app = handler

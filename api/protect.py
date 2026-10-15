
from http.server import BaseHTTPRequestHandler
import json
import os
import secrets
import urllib.parse
import urllib.request
import urllib.error

MAX_BYTES = 200_000
BASE_URL = "https://novaprotector.vercel.app"
BLOB_UPLOAD_URL = "https://blob.vercel-storage.com/"


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


def process_luau(source):
    if not source or not source.strip():
        raise ValueError("Introduce código Luau.")

    if "\x00" in source:
        raise ValueError("El código contiene caracteres no válidos.")

    # No afirmar que el código está ofuscado sin un motor real.
    return source


def upload_to_blob(file_id, code):
    token = (
        os.environ.get("BLOB_READ_WRITE_TOKEN")
        or os.environ.get("VERCEL_BLOB_READ_WRITE_TOKEN")
        or ""
    ).strip()

    if not token:
        raise RuntimeError(
            "Falta BLOB_READ_WRITE_TOKEN en las variables de Vercel."
        )

    url = BLOB_UPLOAD_URL + urllib.parse.quote(
        file_id + ".lua", safe=""
    )

    request = urllib.request.Request(
        url,
        data=code.encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": "Bearer " + token,
            "x-api-version": "7",
            "x-content-type": "text/plain; charset=utf-8",
            "x-add-random-suffix": "0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(
            "utf-8", errors="replace"
        )[:250]
        raise RuntimeError(
            f"Error de Vercel Blob ({exc.code}): {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "No se pudo conectar con Vercel Blob."
        ) from exc

    blob_url = result.get("url", "")
    parsed = urllib.parse.urlparse(blob_url)

    if (
        parsed.scheme != "https"
        or not (parsed.hostname or "").endswith(
            ".public.blob.vercel-storage.com"
        )
        or parsed.username
        or parsed.password
    ):
        raise RuntimeError("Vercel Blob devolvió una URL no válida.")

    return blob_url


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        configured = bool(
            (
                os.environ.get("BLOB_READ_WRITE_TOKEN")
                or os.environ.get("VERCEL_BLOB_READ_WRITE_TOKEN")
                or ""
            ).strip()
        )

        send_json(self, 200, {
            "success": True,
            "service": "NovaProtector",
            "blobConfigured": configured,
            "mode": "safe-storage",
            "obfuscationReady": False,
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0:
                send_json(self, 400, {
                    "success": False,
                    "error": "La solicitud está vacía.",
                })
                return

            if length > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El límite es de 200 KB.",
                })
                return

            body = self.rfile.read(length)
            payload = json.loads(body.decode("utf-8"))

            if not isinstance(payload, dict):
                send_json(self, 400, {
                    "success": False,
                    "error": "El cuerpo debe ser un objeto JSON.",
                })
                return

            code = payload.get("code")

            if not isinstance(code, str) or not code.strip():
                send_json(self, 400, {
                    "success": False,
                    "error": "Introduce código Luau.",
                })
                return

            if len(code.encode("utf-8")) > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El código supera los 200 KB.",
                })
                return

            processed = process_luau(code)
            file_id = secrets.token_hex(16)
            blob_url = upload_to_blob(file_id, processed)

            file_url = BASE_URL + "/api/raw?" + (
                urllib.parse.urlencode({
                    "id": file_id,
                    "url": blob_url,
                })
            )

            send_json(self, 200, {
                "success": True,
                "fileId": file_id,
                "blobUrl": blob_url,
                "fileUrl": file_url,
                "transformed": False,
                "mode": "safe-storage",
                "message": (
                    "Archivo guardado. La ofuscación todavía "
                    "no está implementada."
                ),
            })

        except (ValueError, UnicodeDecodeError):
            send_json(self, 400, {
                "success": False,
                "error": "JSON inválido o código incorrecto.",
            })
        except Exception:
            send_json(self, 500, {
                "success": False,
                "error": (
                    "No se pudo procesar la solicitud. "
                    "Revisa los registros de Vercel."
                ),
            })


app = handler

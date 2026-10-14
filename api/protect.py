
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
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def compact_luau(source):
    """
    Elimina comentarios Lua/Luau sin quitar espacios del código.
    Es conservador: no renombra variables ni pretende validar toda
    la sintaxis de Luau.
    """
    output = []
    i = 0
    n = len(source)

    while i < n:
        # Strings normales.
        if source[i] in ("'", '"'):
            quote = source[i]
            start = i
            i += 1

            while i < n:
                if source[i] == "\\":
                    i += 2
                elif source[i] == quote:
                    i += 1
                    break
                else:
                    i += 1

            output.append(source[start:i])
            continue

        # Comentarios que comienzan con --.
        if source.startswith("--", i):
            start = i + 2
            j = start

            if j < n and source[j] == "[":
                j += 1
                while j < n and source[j] == "=":
                    j += 1

                if j < n and source[j] == "[":
                    level = j - start
                    closing = "]" + ("=" * level) + "]"
                    end = source.find(closing, j + 1)

                    if end == -1:
                        output.append(source[i:])
                        break

                    comment = source[i:end + len(closing)]
                    output.append(
                        "".join(ch for ch in comment if ch == "\n")
                    )
                    i = end + len(closing)
                    continue

            end = source.find("\n", i + 2)
            if end == -1:
                break

            output.append("\n")
            i = end + 1
            continue

        # Strings largos: [[...]], [=[...]=], etc.
        if source[i] == "[":
            j = i + 1
            while j < n and source[j] == "=":
                j += 1

            if j < n and source[j] == "[":
                level = j - i - 1
                closing = "]" + ("=" * level) + "]"
                end = source.find(closing, j + 1)

                if end == -1:
                    output.append(source[i:])
                    break

                end += len(closing)
                output.append(source[i:end])
                i = end
                continue

        output.append(source[i])
        i += 1

    return "".join(output).strip()


def upload_to_blob(file_id, code):
    token = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()

    if not token:
        raise RuntimeError(
            "Falta BLOB_READ_WRITE_TOKEN en las variables de Vercel."
        )

    request = urllib.request.Request(
        BLOB_UPLOAD_URL + urllib.parse.quote(file_id + ".lua", safe=""),
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
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"Vercel Blob respondió HTTP {exc.code}: {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "No se pudo conectar con Vercel Blob."
        ) from exc

    blob_url = result.get("url")
    if not isinstance(blob_url, str):
        raise RuntimeError("Blob no devolvió una URL válida.")

    parsed = urllib.parse.urlparse(blob_url)
    if (
        parsed.scheme != "https"
        or not (parsed.hostname or "").endswith(
            ".public.blob.vercel-storage.com"
        )
    ):
        raise RuntimeError("La URL devuelta por Blob no es válida.")

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
            "transformation": "comment-removal",
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
                    "error": "El código supera el límite de 200 KB.",
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
                    "error": "Introduce código LuaU.",
                })
                return

            if len(code.encode("utf-8")) > MAX_BYTES:
                send_json(self, 413, {
                    "success": False,
                    "error": "El código supera el tamaño permitido.",
                })
                return

            processed = compact_luau(code)
            if not processed:
                send_json(self, 400, {
                    "success": False,
                    "error": "No hay código para procesar.",
                })
                return

            file_id = secrets.token_hex(8)
            blob_url = upload_to_blob(file_id, processed)

            raw_url = BASE_URL + "/api/raw?" + urllib.parse.urlencode({
                "id": file_id,
                "url": blob_url,
            })

            send_json(self, 200, {
                "success": True,
                "fileId": file_id,
                "blobUrl": blob_url,
                "fileUrl": raw_url,
                "transformed": processed != code,
                "mode": "comment-removal",
                "message": (
                    "Código procesado y guardado. "
                    "Esta versión elimina comentarios, pero todavía "
                    "no renombra variables ni realiza ofuscación avanzada."
                ),
            })

        except (ValueError, UnicodeDecodeError):
            send_json(self, 400, {
                "success": False,
                "error": "JSON inválido o codificación UTF-8 incorrecta.",
            })
        except Exception as exc:
            send_json(self, 500, {
                "success": False,
                "error": str(exc),
            })


# Punto de entrada requerido por Vercel.
app = handler

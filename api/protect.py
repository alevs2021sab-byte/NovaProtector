
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


def minify_lua(source):
    """Reduce comentarios y espacios sin modificar el contenido de strings."""
    out = []
    i = 0
    n = len(source)
    pending_space = False
    previous = ""

    def long_bracket(pos):
        if pos >= n or source[pos] != "[":
            return None
        j = pos + 1
        while j < n and source[j] == "=":
            j += 1
        if j < n and source[j] == "[":
            return j - pos - 1
        return None

    def needs_space(a, b):
        if not a or not b:
            return False
        word = lambda c: c.isalnum() or c == "_"
        if word(a[-1]) and word(b[0]):
            return True
        if a[-1] == "." and b[0] == ".":
            return True
        if a[-1] == "-" and b[0] == "-":
            return True
        if a[-1] in "+-*/%=<>~:" and b[0] in "+-*/%=<>~:":
            return True
        if a[-1] == "[" and b[0] == "[":
            return True
        return False

    while i < n:
        c = source[i]

        if c.isspace():
            pending_space = True
            i += 1
            continue

        # Comentarios Lua/LuaU: --texto o --[[bloque]]
        if source.startswith("--", i):
            level = long_bracket(i + 2)
            if level is not None:
                start = i + 2 + level + 1
                closing = "]" + ("=" * level) + "]"
                end = source.find(closing, start)
                i = n if end == -1 else end + len(closing)
            else:
                end = source.find("\n", i + 2)
                i = n if end == -1 else end
            pending_space = True
            continue

        # Strings entre comillas: conservar exactamente su contenido.
        if c in ("'", '"'):
            quote = c
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
            token = source[start:i]

        # Strings largos: [[...]], [=[...]=], etc.
        elif c == "[" and long_bracket(i) is not None:
            level = long_bracket(i)
            opening_len = level + 2
            closing = "]" + ("=" * level) + "]"
            start = i
            content_start = i + opening_len
            end = source.find(closing, content_start)
            i = n if end == -1 else end + len(closing)
            token = source[start:i]

        # Identificadores y números.
        elif c.isalnum() or c == "_":
            start = i
            i += 1
            while i < n and (
                source[i].isalnum() or source[i] == "_"
            ):
                i += 1
            token = source[start:i]

        else:
            # Operadores de varios caracteres.
            operators = (
                "...", "..=", "//=", "==", "~=", "<=", ">=",
                "::", "//", "..", "+=", "-=", "*=", "/=",
                "%=", "^=", "->"
            )
            token = next(
                (op for op in operators if source.startswith(op, i)),
                c
            )
            i += len(token)

        if pending_space and needs_space(previous, token):
            out.append(" ")

        out.append(token)
        previous = token
        pending_space = False

    return "".join(out).strip()


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
        raise RuntimeError("No se pudo conectar con Vercel Blob.") from exc

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
            length = int(self.headers.get("Content-Length", "0"))
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

            transformed = minify_lua(code)
            if not transformed:
                send_json(self, 400, {
                    "success": False,
                    "error": "No hay código válido para procesar."
                })
                return

            file_id = secrets.token_hex(8)
            blob_url = upload_to_blob(file_id, transformed)
            raw_url = (
                f"{BASE_URL}/api/raw?"
                + urllib.parse.urlencode({
                    "id": file_id,
                    "url": blob_url
                })
            )

            send_json(self, 200, {
                "success": True,
                "fileId": file_id,
                "blobUrl": blob_url,
                "fileUrl": raw_url,
                "transformed": transformed != code,
                "message": (
                    "Código procesado y guardado. "
                    "Esta versión compacta el código y elimina comentarios; "
                    "todavía no renombra variables."
                )
            })

        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            send_json(self, 400, {
                "success": False,
                "error": "La solicitud debe contener JSON válido en UTF-8."
            })
        except Exception as exc:
            send_json(self, 500, {
                "success": False,
                "error": str(exc)
            })


app = handler

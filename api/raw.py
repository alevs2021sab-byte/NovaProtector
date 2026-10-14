
from http.server import BaseHTTPRequestHandler
import re
import urllib.parse
import urllib.request
import urllib.error


BLOB_SUFFIX = ".public.blob.vercel-storage.com"


def valid_blob_url(value, file_id):
    try:
        parsed = urllib.parse.urlparse(value)

        if parsed.scheme != "https":
            return False

        if not parsed.hostname:
            return False

        if not parsed.hostname.endswith(BLOB_SUFFIX):
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

    def send_text(self, status, text):
        body = text.encode("utf-8", errors="replace")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Allow", "GET, OPTIONS")
        self.end_headers()

    def do_GET(self):
        try:
            query = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )

            file_id = (query.get("id") or [""])[0]
            blob_url = (query.get("url") or [""])[0]

            if not re.fullmatch(r"[a-f0-9]{16}", file_id):
                self.send_text(400, "Invalid file ID")
                return

            if not valid_blob_url(blob_url, file_id):
                self.send_text(400, "Invalid Blob URL")
                return

            request = urllib.request.Request(
                blob_url,
                headers={"User-Agent": "NovaProtector/1.0"},
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                final_url = response.geturl()

                if not valid_blob_url(final_url, file_id):
                    self.send_text(502, "Unexpected Blob redirect")
                    return

                content = response.read(200_001)

            if len(content) > 200_000:
                self.send_text(413, "File too large")
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
            self.send_text(502, f"Blob returned HTTP {error.code}")
        except Exception:
            self.send_text(502, "Could not retrieve the 
            Blob file")


app = handler

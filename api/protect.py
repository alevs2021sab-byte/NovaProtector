from http.server import BaseHTTPRequestHandler
import json
import re
import os
import random
import string
import base64
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

DOMAIN = "https://novaprotector.vercel.app"

RESERVED = {
    "self", "script", "game", "workspace", "print", "warn", "error",
    "typeof", "type", "pairs", "ipairs", "next", "select", "unpack",
    "table", "string", "math", "task", "wait", "spawn", "delay", "shared",
    "bit32", "utf8", "coroutine", "debug", "os", "tick", "time",
    "loadstring", "load", "pcall", "xpcall", "tostring", "tonumber",
    "Instance", "Enum", "Color3", "UDim2", "Vector3", "CFrame", "UDim",
    "Players", "PlayerGui", "LocalPlayer", "ReplicatedStorage", "ServerStorage",
    "ServerScriptService", "StarterGui", "StarterPack", "StarterPlayer",
    "Lighting", "Terrain", "RunService", "UserInputService", "TweenService",
    "HttpService", "TeleportService", "MarketplaceService", "DataStoreService",
    "CollectionService", "PhysicsService", "PathfindingService", "SoundService",
    "TextService", "ContextActionService", "GuiService", "GroupService",
    "Teams", "Chat", "VoiceChatService", "ProximityPromptService",
    "Debris", "InsertService", "ContentProvider", "Stats", "TestService",
    "VirtualUser", "CoreGui", "CorePackages", "RobloxReplicatedStorage",
    "GetService", "FindFirstChild", "WaitForChild", "IsA", "Clone", "Destroy",
    "Connect", "Once", "Fire", "Invoke", "Parent", "Name", "Value",
}


def random_name(n=8):
    return "".join(random.choices(string.ascii_letters, k=n))


def strip_comments(code: str) -> str:
    code = re.sub(r"--\[\[[\s\S]*?\]\]", "", code)
    code = re.sub(r"--[^\r\n]*", "", code)
    lines = [ln.rstrip() for ln in code.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def protect_strings(code: str):
    """Saca strings del codigo para no renombrar dentro de ellas."""
    strings = []

    def save(m):
        strings.append(m.group(0))
        return "__NPSTR%d__" % (len(strings) - 1)

    # "..." y '...' con escapes basicos
    protected = re.sub(r'"(?:\\.|[^"\\])*"', save, code)
    protected = re.sub(r"'(?:\\.|[^'\\])*'", save, protected)
    return protected, strings


def restore_strings(code: str, strings):
    def restore(m):
        return strings[int(m.group(1))]

    return re.sub(r"__NPSTR(\d+)__", restore, code)


def rename_locals(code: str) -> str:
    protected, strings = protect_strings(code)
    found = re.findall(r"\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)", protected)
    mapping = {}
    for name in set(found):
        if name not in RESERVED and not name.startswith("__NPSTR"):
            mapping[name] = "_" + random_name(7)
    for old, new in mapping.items():
        protected = re.sub(r"\b" + re.escape(old) + r"\b", new, protected)
    return restore_strings(protected, strings)


def add_junk(code: str) -> str:
    junk = [
        "local %s=%d;" % (random_name(), random.randint(1, 999)),
        "if false then local %s=nil end;" % random_name(),
    ]
    out = []
    for line in code.splitlines():
        out.append(line)
        if line.strip() and random.random() > 0.85:
            out.append(random.choice(junk))
    return "\n".join(out)


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def obfuscate(code: str) -> str:
    src = strip_comments(code)
    src = rename_locals(src)
    src = add_junk(src)

    key = bytes(random.randint(1, 255) for _ in range(12))
    enc = xor_bytes(src.encode("utf-8"), key)
    b64 = base64.b64encode(enc).decode("ascii")
    kb64 = base64.b64encode(key).decode("ascii")

    chunks = [b64[i : i + 90] for i in range(0, len(b64), 90)]
    lines = []
    lines.append("-- NovaProtector | protected")
    lines.append("-- " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))

    names = []
    for c in chunks:
        nm = "_" + random_name(9)
        names.append(nm)
        lines.append('local %s="%s"' % (nm, c))
    cat = "_" + random_name(8)
    lines.append("local %s=%s" % (cat, "..".join(names)))
    kn = "_" + random_name(7)
    lines.append('local %s="%s"' % (kn, kb64))

    lines.append("local function _D(data)")
    lines.append("local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'")
    lines.append("data=string.gsub(data,'[^'..b..'=]','')")
    lines.append("return (data:gsub('.',function(x)")
    lines.append("if x=='=' then return '' end")
    lines.append("local r,f='',(b:find(x)-1)")
    lines.append("for i=6,1,-1 do r=r..(f%2^i-f%2^(i-1)>0 and '1' or '0') end")
    lines.append("return r")
    lines.append("end):gsub('%d%d%d?%d?%d?%d?%d?%d?',function(x)")
    lines.append("if #x~=8 then return '' end")
    lines.append("local c=0")
    lines.append("for i=1,8 do c=c+(x:sub(i,i)=='1' and 2^(8-i) or 0) end")
    lines.append("return string.char(c)")
    lines.append("end))")
    lines.append("end")
    lines.append("local function _X(s,k)")
    lines.append("local o={}")
    lines.append("for i=1,#s do")
    lines.append("local a=string.byte(s,i)")
    lines.append("local bb=string.byte(k,((i-1)%#k)+1)")
    lines.append("o[i]=string.char(bit32.bxor(a,bb))")
    lines.append("end")
    lines.append("return table.concat(o)")
    lines.append("end")
    lines.append("local _src=_X(_D(%s),_D(%s))" % (cat, kn))
    lines.append("local _fn,_err=loadstring(_src)")
    lines.append('if not _fn then error("NovaProtector: "..tostring(_err)) end')
    lines.append("_fn()")
    return "\n".join(lines)


def upload_to_blob(pathname: str, content: str) -> str:
    token = (os.environ.get("BLOB_READ_WRITE_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("Falta BLOB_READ_WRITE_TOKEN")
    safe = re.sub(r"[^a-zA-Z0-9._-]", "", pathname)
    if not safe.endswith(".lua"):
        safe += ".lua"
    body = content.encode("utf-8")
    url = "https://blob.vercel-storage.com/" + urllib.parse.quote(safe)
    headers = {
        "Authorization": "Bearer " + token,
        "x-api-version": "7",
        "x-content-type": "text/plain; charset=utf-8",
        "x-add-random-suffix": "0",
    }
    req = urllib.request.Request(url, data=body, method="PUT", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError("HTTP %s: %s" % (e.code, err)) from e
    return data.get("url") or data.get("downloadUrl")


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_GET(self):
        self.send_json(200, {
            "success": True,
            "service": "NovaProtector",
            "blobConfigured": bool(os.environ.get("BLOB_READ_WRITE_TOKEN")),
            "mode": "obfuscate",
            "obfuscationReady": True,
        })

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            data = json.loads(raw.decode("utf-8"))
            code = data.get("code", "")
            if not isinstance(code, str) or not code.strip():
                self.send_json(400, {"success": False, "error": "Codigo vacio"})
                return

            protected = obfuscate(code)
            file_id = hashlib.md5((protected + str(random.random())).encode()).hexdigest()[:16]
            blob_url = None
            blob_error = None
            file_url = None
            try:
                blob_url = upload_to_blob(file_id + ".lua", protected)
                q = urllib.parse.urlencode({"id": file_id, "url": blob_url})
                file_url = DOMAIN + "/api/raw?" + q
            except Exception as e:
                blob_error = str(e)

            self.send_json(200, {
                "success": True,
                "fileId": file_id,
                "blobUrl": blob_url,
                "fileUrl": file_url,
                "transformed": True,
                "mode": "obfuscate",
                "message": "Codigo ofuscado y guardado.",
                "blobError": blob_error,
            })
        except Exception as e:
            self.send_json(500, {"success": False, "error": str(e)})


app = handler

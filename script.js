const codeEl = document.getElementById("code");
const btn = document.getElementById("btn");
const outBox = document.getElementById("outBox");
const out = document.getElementById("out");
const copy = document.getElementById("copy");
const msg = document.getElementById("msg");

btn.addEventListener("click", async () => {
  const code = codeEl.value.trim();
  if (!code) {
    alert("Pega un script primero.");
    return;
  }
  btn.disabled = true;
  btn.textContent = "Ofuscando...";
  msg.textContent = "";
  msg.className = "msg";

  try {
    const res = await fetch("/api/protect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Error desconocido");
    if (!data.fileUrl) throw new Error(data.blobError || "No se pudo guardar el script");

    const ls = `loadstring(game:HttpGet("${data.fileUrl}"))()`;
    out.value = ls;
    outBox.classList.remove("hidden");
    msg.textContent = "Listo. Copia el loadstring.";
  } catch (e) {
    outBox.classList.remove("hidden");
    out.value = "";
    msg.textContent = String(e.message || e);
    msg.className = "msg err";
  } finally {
    btn.disabled = false;
    btn.textContent = "Obfuscar código";
  }
});

copy.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(out.value);
    msg.textContent = "Copiado.";
    msg.className = "msg";
  } catch {
    out.select();
    document.execCommand("copy");
    msg.textContent = "Copiado.";
  }
});

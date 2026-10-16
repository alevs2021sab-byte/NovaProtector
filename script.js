const codeInput = document.getElementById("codeInput");
const processButton = document.getElementById("processButton");
const processLabel = document.getElementById("processLabel");
const clearButton = document.getElementById("clearButton");
const charCount = document.getElementById("charCount");
const notice = document.getElementById("notice");
const resultPanel = document.getElementById("resultPanel");
const resultUrl = document.getElementById("resultUrl");
const copyButton = document.getElementById("copyButton");
const openButton = document.getElementById("openButton");
const serviceLabel = document.getElementById("serviceLabel");
const statusDot = document.getElementById("statusDot");
const yearEl = document.getElementById("year");

if (yearEl) yearEl.textContent = new Date().getFullYear();

function updateCount() {
  const n = codeInput.value.length;
  charCount.textContent = n.toLocaleString("es") + " chars";
}

function showNotice(msg, type = "") {
  notice.textContent = msg || "";
  notice.className = "notice" + (type ? " " + type : "");
}

async function checkService() {
  try {
    const res = await fetch("/api/protect");
    const data = await res.json();
    if (data.success) {
      serviceLabel.textContent = data.obfuscationReady ? "Online · Obfuscation ready" : "Online";
      statusDot.className = "pulse ok";
    } else {
      throw new Error("offline");
    }
  } catch {
    serviceLabel.textContent = "Offline";
    statusDot.className = "pulse bad";
  }
}

async function processCode() {
  const code = codeInput.value.trim();
  if (!code) {
    showNotice("Pega un script para continuar.", "err");
    return;
  }

  processButton.disabled = true;
  processLabel.textContent = "Procesando…";
  showNotice("Ofuscando y guardando…");

  try {
    const res = await fetch("/api/protect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Error del servidor");
    if (!data.fileUrl && !data.blobUrl) {
      throw new Error(data.blobError || "No se pudo guardar en Blob");
    }

    const raw = data.fileUrl || data.blobUrl;
    const ls = 'loadstring(game:HttpGet("' + raw + '"))()';
    resultUrl.value = ls;
    openButton.href = raw;
    resultPanel.classList.remove("hidden");
    resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    showNotice(data.message || "Listo. Copia el loadstring.", "ok");
  } catch (e) {
    resultPanel.classList.add("hidden");
    showNotice(String(e.message || e), "err");
  } finally {
    processButton.disabled = false;
    processLabel.textContent = "Ofuscar código";
  }
}

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(resultUrl.value);
    showNotice("Loadstring copiado al portapapeles.", "ok");
  } catch {
    resultUrl.select();
    document.execCommand("copy");
    showNotice("Loadstring copiado.", "ok");
  }
});

clearButton.addEventListener("click", () => {
  codeInput.value = "";
  updateCount();
  resultPanel.classList.add("hidden");
  showNotice("");
  codeInput.focus();
});

processButton.addEventListener("click", processCode);
codeInput.addEventListener("input", updateCount);
codeInput.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") processCode();
});

updateCount();
che
  ckService();

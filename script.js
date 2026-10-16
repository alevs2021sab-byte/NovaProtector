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

let lastRawUrl = "";

function updateCount() {
  charCount.textContent = `${codeInput.value.length.toLocaleString("es")} caracteres`;
}

function showNotice(msg, type = "") {
  notice.textContent = msg || "";
  notice.className = "notice" + (type ? " " + type : "");
}

async function checkService() {
  try {
    const res = await fetch("/api/protect");
    const data = await res.json();
    if (data.success && data.obfuscationReady) {
      serviceLabel.textContent = "Ofuscación lista";
      statusDot.className = "status-dot ok";
    } else if (data.success) {
      serviceLabel.textContent = "API conectada";
      statusDot.className = "status-dot ok";
    } else {
      throw new Error("API no lista");
    }
  } catch {
    serviceLabel.textContent = "API no disponible";
    statusDot.className = "status-dot bad";
  }
}

async function processCode() {
  const code = codeInput.value.trim();
  if (!code) {
    showNotice("Pega un script primero.", "err");
    return;
  }

  processButton.disabled = true;
  processLabel.textContent = "Ofuscando…";
  showNotice("Procesando…");

  try {
    const res = await fetch("/api/protect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || "Error desconocido");
    if (!data.fileUrl && !data.blobUrl) {
      throw new Error(data.blobError || "No se pudo guardar el script");
    }

    // Preferir dominio; si raw falla en el futuro, el usuario aún tiene blob
    lastRawUrl = data.fileUrl || data.blobUrl;
    const loadstring = `loadstring(game:HttpGet("${lastRawUrl}"))()`;

    resultUrl.value = loadstring;
    openButton.href = lastRawUrl;
    resultPanel.classList.remove("hidden");
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
    showNotice("Loadstring copiado.", "ok");
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
});

processButton.addEventListener("click", processCode);
codeInput.addEventListener("input", updateCount);
updateCount();
checkService();

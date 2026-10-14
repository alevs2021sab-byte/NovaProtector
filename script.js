
const codeInput = document.getElementById("codeInput");
const processButton = document.getElementById("processButton");
const processLabel = document.getElementById("processLabel");
const processIcon = document.getElementById("processIcon");
const clearButton = document.getElementById("clearButton");
const charCount = document.getElementById("charCount");
const lineNumbers = document.getElementById("lineNumbers");
const notice = document.getElementById("notice");
const resultPanel = document.getElementById("resultPanel");
const resultUrl = document.getElementById("resultUrl");
const resultDescription = document.getElementById("resultDescription");
const copyButton = document.getElementById("copyButton");
const openButton = document.getElementById("openButton");
const downloadButton = document.getElementById("downloadButton");
const serviceLabel = document.getElementById("serviceLabel");

let lastResultUrl = "";
let lastFileName = "novaprotector.lua";

document.getElementById("year").textContent = new Date().getFullYear();

function updateEditorInfo() {
  const text = codeInput.value;
  const lines = Math.max(1, text.split("\n").length);

  charCount.textContent =
    `${text.length.toLocaleString("es-PE")} caracteres`;

  lineNumbers.textContent = Array.from(
    { length: lines },
    (_, index) => index + 1
  ).join("\n");
}

function showNotice(message, type = "") {
  notice.textContent = message;
  notice.className = "notice";

  if (type) {
    notice.classList.add(type);
  }

  notice.hidden = false;
}

function hideNotice() {
  notice.hidden = true;
  notice.textContent = "";
  notice.className = "notice";
}

function resetResult() {
  resultPanel.hidden = true;
  lastResultUrl = "";
  resultUrl.value = "";
}

async function checkService() {
  try {
    const response = await fetch("/api/protect", {
      method: "GET",
      cache: "no-store"
    });

    const data = await response.json();

    if (response.ok && data.success) {
      serviceLabel.textContent = data.blobConfigured
        ? "Servicio conectado"
        : "Falta configurar Blob";
    } else {
      serviceLabel.textContent = "Servicio no disponible";
    }
  } catch {
    serviceLabel.textContent = "Servicio sin conexión";
  }
}

async function processCode() {
  const code = codeInput.value;

  if (!code.trim()) {
    showNotice("Introduce tu código LuaU antes de continuar.", "error");
    codeInput.focus();
    return;
  }

  if (new TextEncoder().encode(code).length > 200000) {
    showNotice("El código supera el límite permitido de 200 KB.", "error");
    return;
  }

  hideNotice();
  resetResult();

  processButton.disabled = true;
  clearButton.disabled = true;
  processIcon.textContent = "◌";
  processLabel.textContent = "Procesando…";

  try {
    const response = await fetch("/api/protect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ code })
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.success) {
      throw new Error(
        data.error || `No se pudo procesar el código (HTTP ${response.status}).`
      );
    }

    if (
      typeof data.fileUrl !== "string" ||
      !data.fileUrl.startsWith(window.location.origin + "/api/raw?")
    ) {
      throw new Error("El servidor no devolvió un enlace RAW válido.");
    }

    lastResultUrl = data.fileUrl;
    lastFileName = `novaprotector-${data.fileId || "result"}.lua`;

    resultUrl.value = lastResultUrl;
    openButton.href = lastResultUrl;
    resultDescription.textContent =
      data.message || "El archivo se guardó correctamente.";

    resultPanel.hidden = false;
    showNotice("El servidor terminó de procesar tu solicitud.", "success");

    resultPanel.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  } catch (error) {
    showNotice(
      error.message || "No se pudo conectar con NovaProtector.",
      "error"
    );
  } finally {
    processButton.disabled = false;
    clearButton.disabled = false;
    processIcon.textContent = "✳";
    processLabel.textContent = "Procesar código";
  }
}

async function copyResultUrl() {
  if (!lastResultUrl) return;

  try {
    await navigator.clipboard.writeText(lastResultUrl);
    copyButton.textContent = "Copiado ✓";
  } catch {
    resultUrl.focus();
    resultUrl.select();

    const copied = document.execCommand("copy");
    copyButton.textContent = copied ? "Copiado ✓" : "Selecciona y copia";

    if (!copied) {
      showNotice("Selecciona el enlace y cópialo manualmente.", "error");
    }
  }

  window.setTimeout(() => {
    copyButton.textContent = "Copiar";
  }, 1800);
}

async function downloadResult() {
  if (!lastResultUrl) return;

  downloadButton.disabled = true;
  downloadButton.textContent = "Descargando…";

  try {
    const response = await fetch(lastResultUrl, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error("No se pudo recuperar el archivo RAW.");
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = lastFileName;
    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(objectUrl);
  } catch (error) {
    showNotice(error.message || "Error al descargar el archivo.", "error");
  } finally {
    downloadButton.disabled = false;
    downloadButton.textContent = "Descargar .lua ↓";
  }
}

processButton.addEventListener("click", processCode);

clearButton.addEventListener("click", () => {
  codeInput.value = "";
  updateEditorInfo();
  hideNotice();
  resetResult();
  codeInput.focus();
});

copyButton.addEventListener("click", copyResultUrl);
downloadButton.addEventListener("click", downloadResult);

codeInput.addEventListener("input", () => {
  updateEditorInfo();
  hideNotice();
});

codeInput.addEventListener("keydown", event => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
    event.preventDefault();
    processCode();
  }

  // Inserta una tabulación en el editor sin perder el texto.
  if (event.key === "Tab") {
    event.preventDefault();

    const start = codeInput.selectionStart;
    const end = codeInput.selectionEnd;

    codeInput.setRangeText("    ", start, end, "end");
    updateEditorInfo();
  }
});

updateEditorInfo();
checkService();

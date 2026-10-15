
const JavaScriptObfuscator = require("javascript-obfuscator");

const MAX_BYTES = 200_000;

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");

  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({
      success: false,
      error: "Usa el método POST."
    });
  }

  try {
    const body = req.body;
    const code = body && body.code;

    if (typeof code !== "string" || !code.trim()) {
      return res.status(400).json({
        success: false,
        error: "Introduce código JavaScript."
      });
    }

    if (Buffer.byteLength(code, "utf8") > MAX_BYTES) {
      return res.status(413).json({
        success: false,
        error: "El código supera los 200 KB."
      });
    }

    const result = JavaScriptObfuscator.obfuscate(code, {
      compact: true,
      simplify: true,
      identifierNamesGenerator: "hexadecimal",
      stringArray: true,
      stringArrayThreshold: 0.5,
      renameGlobals: false,
      selfDefending: false
    }).getObfuscatedCode();

    return res.status(200).json({
      success: true,
      transformed: true,
      language: "javascript",
      code: result,
      message: "JavaScript transformado correctamente."
    });
  } catch {
    return res.status(400).json({
      success: false,
      error: "No se pudo procesar el JavaScript."
    }
      );
  }
};

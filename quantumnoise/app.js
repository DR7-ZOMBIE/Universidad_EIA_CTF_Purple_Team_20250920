// app.js
import fs from "fs";
import path from "path";
import crypto from "crypto";
import express from "express";
import cookieParser from "cookie-parser";

const __dirname = path.resolve();
const app = express();
const PORT = process.env.PORT || 80;

app.set("view engine", "ejs"); // (no usamos vistas EJS: servimos HTML estático, pero queda listo)
app.use(express.urlencoded({ extended: true, limit: "1mb" }));
app.use(express.json({ limit: "1mb" }));
app.use(cookieParser());
app.use("/static", express.static(path.join(__dirname, "public")));

const FLAG = "EIAPT{d90d519c28c6a8c4ef5387221ccd6abd24c5c6b9625f9beb489c0e346c19ceb2}";
const N = 262144; // nº de bits del dataset (~256k)
const SEED = 0xBADC0DE; // semilla determinística para reproducibilidad

// -------- PRNG simple (xorshift32) ----------
function xorshift32(seedObj) {
  // guardamos el estado dentro de un objeto para mutarlo
  let x = seedObj.x >>> 0;
  x ^= (x << 13) >>> 0;
  x ^= (x >>> 17) >>> 0;
  x ^= (x << 5) >>> 0;
  seedObj.x = x >>> 0;
  return x >>> 0;
}
function randu(seedObj) {
  return xorshift32(seedObj) / 0xffffffff; // [0,1)
}

// -------- Generación de QRNG sesgado ----------
function generateQRNGBits(nbits) {
  const seedObj = { x: SEED >>> 0 };
  const b0 = 0.012; // sesgo DC pequeño
  const A1 = 0.06, f1 = 0.01357, phi1 = 1.1;
  const A2 = 0.028, f2 = 0.03141, phi2 = 2.2;
  const noiseAmp = 0.01;

  const bits = new Uint8Array(nbits);
  for (let n = 0; n < nbits; n++) {
    const p =
      0.5 + b0
      + A1 * Math.sin(2 * Math.PI * f1 * n + phi1)
      + A2 * Math.cos(2 * Math.PI * f2 * n + phi2)
      + (randu(seedObj) - 0.5) * 2 * noiseAmp;
    const u = randu(seedObj);
    bits[n] = u < Math.max(0, Math.min(1, p)) ? 1 : 0;
  }
  return bits;
}

// Empaquetar bits (LSB-first por byte)
function packBitsToBuffer(bits) {
  const len = Math.ceil(bits.length / 8);
  const buf = Buffer.alloc(len);
  for (let i = 0; i < bits.length; i++) {
    if (bits[i]) buf[Math.floor(i / 8)] |= (1 << (i % 8));
  }
  return buf;
}

// Derivar 128 bits por “Fourier-like” (signo de seno correlado)
function derive128BitsFourier(bits) {
  // x[n] = ±1
  const x = new Float64Array(bits.length);
  for (let i = 0; i < bits.length; i++) x[i] = bits[i] ? 1 : -1;

  // para k=1..128, sk = sum_n x[n]*sin(2πkn/N)
  const out = new Uint8Array(128);
  for (let k = 1; k <= 128; k++) {
    let s = 0;
    const w = (2 * Math.PI * k) / bits.length;
    // stride para acelerar (downsample correlación sin afectar signo global)
    const stride = 4; // reduce coste 4x; al ser sesgo suave, conserva signo robusto
    for (let n = 0; n < bits.length; n += stride) {
      s += x[n] * Math.sin(w * n);
    }
    out[k - 1] = s > 0 ? 1 : 0;
  }
  return out; // 128 bits
}

function bitsToKey16(bytes128) {
  // empaqueta 128 bits en 16 bytes (LSB-first)
  const buf = Buffer.alloc(16);
  for (let i = 0; i < 128; i++) {
    if (bytes128[i]) buf[Math.floor(i / 8)] |= (1 << (i % 8));
  }
  return buf;
}

function hamming(a, b) {
  // cuenta bits distintos entre dos buffers del mismo tamaño
  let d = 0;
  for (let i = 0; i < a.length; i++) {
    let v = a[i] ^ b[i];
    // Kernighan
    while (v) { v &= v - 1; d++; }
  }
  return d;
}

// Generar dataset y clave de referencia en arranque (determinístico)
const QRNG_BITS = generateQRNGBits(N);
const QRNG_BUF = packBitsToBuffer(QRNG_BITS);
const KEY_BITS = derive128BitsFourier(QRNG_BITS);
const KEY = bitsToKey16(KEY_BITS);

// Cifrar flag con AES-128-CTR
const IV = Buffer.from("a1b2c3d4e5f60718293a4b5c6d7e8f90", "hex");
const CIPHER = crypto.createCipheriv("aes-128-ctr", KEY, IV);
const CIPHERTEXT = Buffer.concat([CIPHER.update(FLAG, "utf8"), CIPHER.final()]);

// ------------------- RUTAS -------------------
app.get("/", (req, res) => {
  // servimos el index.html directamente
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.get("/download/qrng.bin", (_req, res) => {
  res.setHeader("Content-Type", "application/octet-stream");
  res.setHeader("Content-Disposition", "attachment; filename=qrng.bin");
  res.end(QRNG_BUF);
});

app.get("/api/metadata", (_req, res) => {
  res.json({
    n_bits: N,
    description: "Raw QRNG bitstream (biased). Intended approach: statistics + Fourier.",
    hint: "Map bits to ±1, compute correlations against sin(2πk n / N) for k=1..128, take sign for each k to form 128-bit key.",
    iv_hex: IV.toString("hex"),
    cipher_len: CIPHERTEXT.length,
    ui: "Enter 128 predicted bits or a 32-hex AES-128 key."
  });
});

app.post("/api/submit", (req, res) => {
  try {
    let key = null;
    if (typeof req.body.key_hex === "string") {
      const kh = req.body.key_hex.trim().toLowerCase();
      if (!/^[0-9a-f]{32}$/.test(kh)) {
        return res.status(400).json({ ok: false, error: "key_hex debe ser 32 hex chars (16 bytes)" });
      }
      key = Buffer.from(kh, "hex");
    } else if (typeof req.body.bits === "string") {
      const b = req.body.bits.trim().replace(/\s+/g, "");
      if (!/^[01]{128}$/.test(b)) {
        return res.status(400).json({ ok: false, error: "bits debe ser una cadena de 128 caracteres 0/1" });
      }
      const arr = new Uint8Array(128);
      for (let i = 0; i < 128; i++) arr[i] = b[i] === "1" ? 1 : 0;
      key = bitsToKey16(arr);
    } else {
      return res.status(400).json({ ok: false, error: "Provee key_hex o bits" });
    }

    const dist = hamming(key, KEY);
    if (dist === 0) {
      const dec = crypto.createDecipheriv("aes-128-ctr", key, IV);
      const plain = Buffer.concat([dec.update(CIPHERTEXT), dec.final()]).toString("utf8");
      return res.json({ ok: true, flag: plain, distance: 0 });
    } else {
      return res.json({ ok: false, distance: dist, hint: "Reduce la distancia de Hamming a 0. Fourier ayuda 😉" });
    }
  } catch (e) {
    return res.status(500).json({ ok: false, error: "Internal error" });
  }
});

app.listen(PORT, () => console.log(`QuantumNoise listening on :${PORT}`));

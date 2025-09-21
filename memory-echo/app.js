import express from "express";
import path from "path";
import cookieParser from "cookie-parser";
import fs from "fs";

const __dirname = path.resolve();
const app = express();
const PORT = process.env.PORT || 80;

app.use(cookieParser());
app.use(express.urlencoded({extended:true}));
app.use(express.json());
app.use("/static", express.static(path.join(__dirname, "public")));

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Descarga del dump
app.get("/download/mem.raw", (_req, res) => {
  const p = path.join(__dirname, "artifacts", "mem.raw");
  if (!fs.existsSync(p)) return res.status(404).send("mem.raw no disponible");
  res.setHeader("Content-Type", "application/octet-stream");
  res.setHeader("Content-Disposition", "attachment; filename=mem.raw");
  fs.createReadStream(p).pipe(res);
});

// Herramientas opcionales (para el jugador)
app.get("/tools/viewer.py", (_req, res) => {
  res.sendFile(path.join(__dirname, "tools", "viewer.py"));
});
app.get("/tools/trap_ransom.py", (_req, res) => {
  res.sendFile(path.join(__dirname, "tools", "trap_ransom.py"));
});

app.listen(PORT, () => {
  console.log(`Memory Echo listening on :${PORT}`);
});

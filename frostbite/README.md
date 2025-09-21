# Frostbite: Threshold Misbinding in MPC Signatures

> *“Even frozen thresholds crack when resynced.”*

**Categoría:** Cryptography

**Dificultad:** Alto

**Puntos:** 500

**Autor:** Dennis Juilland

**Host:** `172.30.255.144`

**Puerto:** `8101`

---

## 🎯 Objetivo

Este servicio implementa una firma multiparte tipo **FROST/Schnorr (t=2 de N=3)** con un **bug de re-sincronización (threshold misbinding)** que provoca **reutilización de nonces** entre firmas.

Tu meta es obtener **dos firmas** sobre **mensajes distintos** que compartan  **el mismo RR**R**** , recuperar la **clave privada global xx**x**** y construir una **firma válida** sobre el mensaje administrativo `authorize:admin-panel`.

---

## 🧠 Resumen cripto (Schnorr simplificado)

* Parámetros:
  * p=p =**p**= `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F`
  * q=q =**q**= `0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141`
  * g=5g = 5**g**=**5**
* Clave pública global: Y=gx mod pY = g^{x} \bmod p**Y**=**g**x**mod**p, con x=xA+xB+xC mod qx = x_A + x_B + x_C \bmod q**x**=**x**A****+**x**B****+**x**C****mod**q**.
* Firma de mm**m**:
  * e=H(R∥m) mod qe = H(R \parallel m) \bmod q**e**=**H**(**R**∥**m**)**mod**q (SHA-256)
  * **Para firmar offline:** s=(k+e⋅x) mod (p−1)s = (k + e\cdot x) \bmod (p-1)**s**=**(**k**+**e**⋅**x**)**mod**(**p**−**1**)**
  * Verificación del servicio: gs=?R⋅Ye ( mod  p)g^s \stackrel{?}{=} R \cdot Y^e \ (\bmod\ p)**g**s**=**?**R**⋅**Y**e** **(**mod** **p**)

**Ataque clásico (nonce reuse):** con dos firmas (R,s1,e1)(R, s_1, e_1)**(**R**,**s**1****,**e**1)**, (R,s2,e2)(R, s_2, e_2)**(**R**,**s**2,**e**2)** y  **el mismo RR**R**** :

x≡(s1−s2)⋅(e1−e2)−1(modq)x \equiv (s_1 - s_2)\cdot (e_1 - e_2)^ \pmod q**x**≡**(**s**1****−**s**2)**⋅**(**e**1−**e**2)**−**1**(**mod**q**)**
--------------------------------------------------------------------------------------------------------------

## 🐛 El bug (threshold misbinding / re-sync)

El servidor **no liga** los *commitments* Ri=gkiR_i=g^{k_i}**R**i****=**g**k**i** a la  **sesión/ronda/mensaje** , por lo que los nonces de los participantes **A, B y C** pueden  **reutilizarse** . Repitiendo el flujo se consigue el **mismo RR**R**** agregado en firmas distintas.

> El servicio valida firmas contra **YY**Y**** (clave pública  **global** ). Para tener éxito, trabaja con los  **tres participantes** : `["A","B","C"]`.

---

## 🌐 API

Base: `http://172.30.255.144:8101`

* `GET /` → información del servicio
* `GET /pub` → devuelve `g` y `Y`
* `POST /session/start`

  <pre class="overflow-visible!" data-start="2127" data-end="2173"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>"participants"</span><span>:</span><span>[</span><span>"A"</span><span>,</span><span>"B"</span><span>,</span><span>"C"</span><span>]</span><span>}</span><span>
  </span></span></code></div></div></pre>

  → `{"session_id":"...","R_agg":<int>}`
* `POST /sign/round1`

  <pre class="overflow-visible!" data-start="2240" data-end="2307"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>"session_id"</span><span>:</span><span>"<sid>"</span><span>,</span><span>"participants"</span><span>:</span><span>[</span><span>"A"</span><span>,</span><span>"B"</span><span>,</span><span>"C"</span><span>]</span><span>}</span><span>
  </span></span></code></div></div></pre>

  → `{"session_id":"<sid>","R_agg":<int>}`
* `POST /sign/round2`

  <pre class="overflow-visible!" data-start="2376" data-end="2430"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>"session_id"</span><span>:</span><span>"<sid>"</span><span>,</span><span>"message"</span><span>:</span><span>"..."</span><span>}</span><span>
  </span></span></code></div></div></pre>

  → `{"session_id":"<sid>","R":<int>,"s":<int>,"e":<int>}`
* `POST /verify`

  <pre class="overflow-visible!" data-start="2510" data-end="2563"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-json"><span><span>{</span><span>"R"</span><span>:</span><span><int></span><span>,</span><span>"s"</span><span>:</span><span><int></span><span>,</span><span>"message"</span><span>:</span><span>"..."</span><span>}</span><span>
  </span></span></code></div></div></pre>

  → `{"ok": true|false}`

> Nota: existe un **endpoint administrativo** que acepta una firma válida sobre `authorize:admin-panel`. No se documenta su salida.

---

## 🧪 Guía de explotación (manual)

1. **Crear sesión** con `["A","B","C"]`

   `POST /session/start`
2. **Fijar nonces (bug)**

   `POST /sign/round1` con los mismos participantes
3. **Obtener firma 1** sobre `m1`

   `POST /sign/round2` → guarda R,s1,e1R, s_1, e_1**R**,**s**1,**e**1
4. **Reforzar reuse (opcional)**

   `POST /sign/round1` de nuevo con `["A","B","C"]`
5. **Obtener firma 2** sobre `m2`

   `POST /sign/round2` → guarda R,s2,e2R, s_2, e_2**R**,**s**2,**e**2

   **Comprueba:** el RR**R** debe ser **idéntico** al de la firma 1.
6. **Recuperar xx**x****

   x=(s1−s2)⋅(e1−e2)−1 mod qx = (s_1 - s_2) \cdot (e_1 - e_2)^{-1} \bmod q**x**=**(**s**1****−**s**2)**⋅**(**e**1−**e**2)**−**1**mod**q**
7. **Firmar offline** `authorize:admin-panel`

   * Elige kk**k**
   * R=gk mod pR = g^k \bmod p**R**=**g**k**mod**p
   * e=H(R∥"authorize:admin-panel") mod qe = H(R \parallel \text{"authorize:admin-panel"}) \bmod q**e**=**H**(**R**∥**"authorize:admin-panel"**)**mod**q
   * **s=(k+e⋅x) mod (p−1)s = (k + e\cdot x) \bmod (p-1)**s**=**(**k**+**e**⋅**x**)**mod**(**p**−**1**)****
   * Verifica con `POST /verify`
8. **Usa la firma administrativa** cuando la verificación sea `ok:true`.

---

## 🤖 Script de ayuda

Se incluye un `solve.sh` que automatiza el flujo anterior (recupera xx**x** con `["A","B","C"]`, firma administrativa **mod (p-1)** y valida con `/verify`).

Uso:

<pre class="overflow-visible!" data-start="3828" data-end="3880"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>HOST=172.30.255.144 PORT=8101 ./solve.sh
</span></span></code></div></div></pre>

---

## 🧩 Pistas opcionales

* Si tus dos firmas **no** comparten RR**R**, repite `round1` y vuelve a firmar: el bug es de **re-sync** y a veces requiere repetir.
* Usa **los tres** participantes para que la verificación coincida con la clave  **global** .
* Al forjar la firma final, recuerda que el exponente trabaja **mod (p−1)(p-1)**(**p**−**1**)**** en Zp\*\mathbb{Z}_p^\***Z**p**\***.

---

## ⚙️ Para organizadores (operación)

* `./run.sh up` — construir y lanzar el contenedor (puerto host `8101`)
* `./run.sh connect` — shell dentro del contenedor
* `./run.sh reset` — reinicia el proceso (reinicia estado en memoria)
* `./run.sh clean` — detener y eliminar contenedor/imagen

**Seguridad mínima recomendada:** limitar puertos en firewall, añadir `/health` para scorebot, y opcionalmente rate-limit a los endpoints de firma.

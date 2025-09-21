# 🧠👻 Memory Echo: Ghost Threads of a Hypervisor

**Categoría:** Forensics

**Dificultad:** 🔺 Alto

**Puertos:** `8105 : 80`

**Formato de entrega:** `flag` en forma `EIAPT{...}`

**Lema:** *“In echoes of memory, hypervisors leave ghosts.”* 🪞🕳️

---

## 📜 Historia

Un equipo de IaaS detectó un comportamiento anómalo en una VM con virtualización asistida por hardware. Antes de apagarse, el hipervisor alcanzó a guardar un **snapshot parcial** de memoria. Tu misión: seguir las **huellas fantasmas** (EPT/NPT, restos de hypercalls y patrones de TLB) para **descubrir el canal encubierto** y recuperar la flag. 🕵️‍♀️

> 🛡️ El dump es sintético y seguro para CTF. Nada cifra tu máquina ni escribe en disco fuera de la carpeta del reto.

---

## 🎯 Objetivo

Analiza el **dump de memoria** y  **recupera la flag** . El reto está pensado para resolverse con herramientas de **forense de memoria** y  **reversing** . No se requiere acceso a Internet para resolverlo.

---

## 🗂️ Estructura del repositorio

<pre class="overflow-visible!" data-start="1011" data-end="1455"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>memory-echo/
├── app.js                  </span><span># servidor web (descarga del dump) 🌐</span><span>
├── artifacts/
│   └── mem_gen.py          </span><span># generador del dump sintético 🧪</span><span>
├── Dockerfile
├── package.json
├── </span><span>public</span><span>/
│   ├── index.html
│   └── styles.css
├── run.sh                  </span><span># up | reset | connect ▶️</span><span>
└── tools/
    ├── viewer.py           </span><span># visor simple (opcional) 👀</span><span>
    └── trap_ransom.py      </span><span># pantalla completa "troll"</span><span> segura (opcional) 😈
</span></span></code></div></div></pre>

---

## 🚀 Puesta en marcha

### 1) Levantar el entorno (Docker)

<pre class="overflow-visible!" data-start="1522" data-end="1575"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh up
</span><span># Abre: http://127.0.0.1:8105</span><span>
</span></span></code></div></div></pre>

### 2) Descargar el dump

<pre class="overflow-visible!" data-start="1602" data-end="1668"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl -o mem.raw http://127.0.0.1:8105/download/mem.raw
</span></span></code></div></div></pre>

> Alternativa:
>
> <pre class="overflow-visible!" data-start="1689" data-end="1759"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker </span><span>cp</span><span> memory-echo:/app/artifacts/mem.raw ./mem.raw
> </span></span></code></div></div></pre>

### 3) Verificación rápida

<pre class="overflow-visible!" data-start="1788" data-end="1890"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>file mem.raw
xxd -l 8 mem.raw    </span><span># debería mostrar una cabecera identificable del snapshot</span><span>
</span></span></code></div></div></pre>

---

## 🧰 Herramientas sugeridas

* 🐁 **radare2** o **rizin**
* 🔍 **Volatility/Volatility3** (módulos/plug-ins de tu preferencia)
* 🔧 Utilidades Unix: `strings`, `xxd/hexdump`, `grep`, `awk`, etc.
* 🧠 Tu editor/IDE favorito para notas y diagramas

> Puedes usar cualquier herramienta; no está limitada a las anteriores.

---

## 🧩 Contexto técnico (alto nivel, sin spoilers)

* El dump contiene artefactos inspirados en  **virtualización KVM** :
  * Pistas de **tablas de segundo nivel** (EPT/NPT) y metadatos asociados.
  * Restos de invocaciones a  **hypercalls** .
  * Un **registro ligero** vinculado a traducciones de memoria (TLB) que compone un  **canal encubierto** .
* La **flag** se encuentra embebida en la imagen a través de una **representación de datos** que **no** está en claro.
* Reconstruir el **flujo lógico** (no necesariamente toda la VM) te permitirá **extraer** la información relevante.

> Esto **no** es un reto de “adivinar offsets”: interpreta señales, sigue relaciones y valida hipótesis.

---

## 🧪 Reglas y consideraciones

* ✅ Se permite cualquier herramienta local (CLI/GUI) y scripting.
* 🚫 No ataques la infraestructura del CTF. La explotación es contra el  **dump** , no contra el servidor web.
* 📝 Documenta  **pasos clave** : cómo localizaste evidencia, cómo la interpretaste y por qué concluiste lo que concluiste.
* 🕒 No hay límite de tiempo fuera del de la competencia.

---

## 🧾 Entrega

Remite **solo la flag** en tu plataforma de envío con el formato exacto:

<pre class="overflow-visible!" data-start="3419" data-end="3437"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>EIAPT{...}
</span></span></code></div></div></pre>

> Si tu writeup es requerido por la organización: comparte capturas y metodología, **sin publicar spoilers** durante el evento.

---

## 💡 Consejos (sin guiar la solución)

* Construye un  **mapa mental** : zonas de interés, referencias cruzadas entre artefactos y “huellas” coherentes entre sí.
* Valida  **consistencia temporal** : pistas que parezcan logs/eventos pueden delatar **orden** o **cercanía** en ejecución.
* No todo el dump es oro: diferencia **ruido** de  **señales** .
* Si usas frameworks forenses, prioriza **módulos de memoria** y  **traducción de direcciones** .
* La **decodificación** final existe, pero primero debes  **llegar a los datos correctos** . 😉

---

## 🧯 FAQ

**¿Necesito Internet para resolverlo?**

No. Todo lo necesario está en el dump y las herramientas locales.

**¿Puedo usar Windows/macOS/Linux?**

Sí. Docker y las herramientas sugeridas funcionan en los tres (puede variar la instalación).

**¿El “trap” visual apaga mi PC?**

No. Es un efecto visual opcional del entorno para ambientación; no realiza acciones peligrosas. Si te molesta, cierra el proceso desde fuera.

**¿Puedo compartir la flag?**

No compartas soluciones ni flags durante el evento. Respeta a otros jugadores.

---



# 🔎 Guía de **resolución manual con radare2** (explicada paso a paso)

> Objetivo: **extraer la flag** escondida en el dump `mem.raw` a partir del área “TLB log”, que está **XOReada con 0x37** y delimitada por la etiqueta ASCII `TLBLOG\0`.
>
> La idea es **no modificar el archivo en disco** y trabajar sólo en memoria.

---

## 0) Por qué cada opción de arranque

<pre class="overflow-visible!" data-start="366" data-end="411"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>r2 -n -e io.cache=</span><span>true</span><span> -w mem.raw
</span></span></code></div></div></pre>

* `-n` → No ejecuta análisis automático (rápido y cero ruido; no necesitamos desensamblados aquí).
* `-e io.cache=true` → Todas las “escrituras” (como el XOR) se hacen  **en caché** , no en el archivo real.
* `-w` → Permite comandos de escritura (p. ej., `wox`); sin `-w`, radare2 no te deja aplicar XOR.

  **Tranquilo** : con `io.cache=true` no se persiste al disco a menos que guardes explícitamente.

---

## 1) Localizar el área de interés (TLBLOG)

En el dump se insertan **marcadores ASCII** (pistas didácticas), entre ellos `TLBLOG\0` que precede a la secuencia ofuscada.

Dos formas:

**A. strings internas de r2**

<pre class="overflow-visible!" data-start="1035" data-end="1067"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>izz | grep TLBLOG
</span></code></div></div></pre>

* `izz` lista strings encontradas; `grep` filtra la etiqueta.
* Copia el **offset** que te muestre (ej.: `0x00500000`).

**B. búsqueda directa de texto**

<pre class="overflow-visible!" data-start="1224" data-end="1247"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>/ TLBLOG
</span></code></div></div></pre>

* Esto crea flags `hit…` en la sesión actual (p. ej., `hit0_0`).
* Puedes saltar con `s hit0_0` **sólo si acabas de hacer `/ TLBLOG`** (si no, el flag no existe).
* Alternativamente, usa el **offset** en hex que viste con `izz`.

👉 **¿Por qué?** Porque sabemos (por diseño del reto) que justo después de `TLBLOG\0` comienza la **zona XOReada** que contiene la flag. Encontrar esta etiqueta nos ubica exactamente en el inicio de esa estructura.

---

## 2) Saltar a la etiqueta y verificar

Supongamos que `izz` te dijo `0x00500000`:

<pre class="overflow-visible!" data-start="1787" data-end="1932"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>s 0x00500000   ; situarse en el offset
px 16          ; mirar 16 bytes: deberías ver 54 4c 42 4c 4f 47 00 ...  => "T L B L O G \0"
</span></code></div></div></pre>

👉 **¿Por qué?** `px` confirma que realmente estás en la etiqueta y que el siguiente byte es `\0` (terminador).

El **buffer XOReado** empieza **inmediatamente después** de ese `\0`.

---

## 3) Posicionarse al comienzo del buffer XOReado

<pre class="overflow-visible!" data-start="2175" data-end="2200"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>s+ 7
px 64
</span></code></div></div></pre>

* **`s+ 7`** : avanzamos 7 bytes (6 letras `T L B L O G` + el `\0`).
* **`px 64`** : ahora deberías ver bytes *“aleatorios”* (no ASCII legible), porque están  **XOReados** .

👉 **¿Por qué?** Este es el **punto exacto** donde comienza la cadena ofuscada que, una vez decodificada, contendrá la flag (terminada en `\0`).

---

## 4) Decodificar en memoria (XOR 0x37) y leer como cadena

<pre class="overflow-visible!" data-start="2586" data-end="2829"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>b 192         ; fija el tamaño del bloque de trabajo (ajústalo si hace falta)
wox 0x37      ; XORear el bloque actual con 0x37 (sólo en cache, no en disco)
psz @ $$      ; imprimir la cadena C-terminated desde la posición actual
</span></code></div></div></pre>

* `b 192` → define **cuántos bytes** afectará `wox` desde el cursor.

  Si no aparece la flag, prueba `b 256` o `b 384` y repite `wox 0x37; psz @ $$`.
* `wox 0x37` → aplica **XOR 0x37** sobre el bloque actual.

  *XOR es involutivo* : si lo ejecutas  **dos veces seguidas** , vuelves a ofuscar.
* `psz @ $$` → imprime string **hasta el primer `\0`** partiendo de **la dirección actual** (`$$`).

👉 **¿Por qué?** Sabemos por el diseño del dump que:

* La cadena está  **XOReada con 0x37** .
* Termina en **byte NUL** (`\0`), así que `psz` es la forma más limpia de extraerla una vez decodificada.
* Hacerlo en caché (`io.cache=true`) garantiza que  **no tocas el archivo real** .

**Salida esperada:** una línea con la flag tipo: EIAPT{SHA-256}

---

## 5) Salir sin persistir cambios

<pre class="overflow-visible!" data-start="3682" data-end="3699"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>q!
</span></code></div></div></pre>

👉 **¿Por qué?** Aun cuando todo fue en caché, es buena práctica salir sin guardar (y evitar cualquier sobrescritura accidental).

---

## (Opcional) Ver otros artefactos para contextualizar

* **Marcas EPT/NPT** :

<pre class="overflow-visible!" data-start="3917" data-end="3971"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>izz | egrep 'EPTP|PML4|PDPT|PDT|PT'
  </span></code></div></div></pre>

  Te da una idea de que el dump incluye *pistas* sobre tablas de segundo nivel.

* **Hypercalls** (inspiración KVM/VMX):

  <pre class="overflow-visible!" data-start="4095" data-end="4160"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-radare2"><span>/x 0f01c1    ; VMCALL
  /x 0f01d9    ; VMMCALL
  </span></code></div></div></pre>

  Refuerzan la narrativa de “trazas del hipervisor”.

👉 **¿Por qué?** No son necesarios para extraer la flag, pero explican el **porqué** del `TLBLOG`: es un *log* mínimo y plausible de traducciones/buffer, del cual se deriva un **canal encubierto** que “transporta” la flag.

---

## Errores típicos y cómo evitarlos

* **“`s hit0` no funciona”** → Debes **ejecutar antes** `/ TLBLOG` en esta sesión; si no, el flag `hit0` no existe. O usa el **offset** que te dio `izz`.
* **`psz` no muestra nada** → Probablemente XOReaste pocos bytes.
  * Sube el bloque: `b 256` o `b 384`.
  * Vuelve a XORear: `wox 0x37` (si lo aplicaste dos veces, vuelve a aplicar una tercera vez).
  * Repite: `psz @ $$`.
* **“No quiero tocar el archivo”** → Ya lo cubre `-e io.cache=true`. No guardes (`q!`).
* **“`strings` no ve la flag”** → Correcto, está XOReada adrede. Debes  **decodificar** .

---

## Resumen conceptual

1. **Ubicar** la etiqueta `TLBLOG\0`: es la “cabecera” de la zona que nos interesa.
2. **Saltar** justo después del `\0`: allí empieza el  **payload ofuscado** .
3. **XORear con 0x37** en memoria: decodifica los bytes.
4. **Imprimir** como cadena hasta `\0`: aparece la  **flag** .
5. **Salir** sin guardar.

Con esto **compruebas** cómo, en un contexto de hipervisor, un **canal encubierto** (aquí, un “log TLB” figurado) puede **transportar** datos sensibles (la flag) y cómo una simple **ofuscación reversible** (XOR) es suficiente para esconderla de herramientas triviales como `strings`.

## 🏁 Créditos

**Autor:** Dennis Juilland

**Título:** *Memory Echo: Ghost Threads of a Hypervisor*

**Lema:** *“In echoes of memory, hypervisors leave ghosts.”*

---

## 🔐 Ética y fair play

Este reto busca mejorar tus habilidades de análisis forense y reversing en entornos virtualizados. Sé responsable, respeta el tiempo de otros y **no publiques spoilers** mientras el evento esté en curso. 🫶

---

¡Suerte cazando 👻 del hipervisor! 🛰️🧩

# SpecterJIT: Ghosts in the Optimizer 👻⚙️

> **Categoría:** Reversing
>
> **Dificultad:** Media-Alta 🔧
>
> **Autor:** Dennis Juilland
>
> **Stack:** x86-64 ELF, FastAPI, Docker 🐳

---

## Descripción 🕵️‍♂️

Un binario x86-64 “inocente” esconde un **mini-JIT** que genera código nativo **en caliente** con `mmap/mprotect`. La API valida un **token** de 64 bits que debes producir aplicando el algoritmo real del binario.

El optimizador esconde “fantasmas” entre especulaciones del branch predictor:  **antidebug** , **rutas condicionales** y mezclas dependientes del  **tiempo** .

Tu misión: **entender el flujo** y **reimplementar** el cálculo del token (sin brute force ni atajos) para canjear la  **FLAG** . 🏁

> ⚠️  **Sin spoilers** : no publiques la solución ni el token en write-ups públicos hasta que el reto termine.

---

## Objetivos de aprendizaje 🎯

* Detectar y analizar **JITs mínimos** que ensamblan gadgets en runtime.
* Identificar **antidebug** comunes (`ptrace`, `prctl`, …). 🚫🐞
* Seguir datos desde  **entrada → JIT → salida** .
* Reproducir **rotaciones** y **mezclas** (tipo splitmix/murmur) dependientes del tiempo ⏱️.
* Crear un **solver determinista** robusto ante  **desfase de reloj** .

---

## Estructura del repo 📁

<pre class="overflow-visible!" data-start="1254" data-end="1539"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>specterjit/
├── app/                 </span><span># API FastAPI</span><span>
├── </span><span>bin</span><span>-src/             </span><span># Código fuente del binario (se compila en build)</span><span>
├── Dockerfile           </span><span># Imagen de la API + toolchain</span><span>
├── run.sh               </span><span># Helper build/run/reset/clean</span><span>
└── README.md            </span><span># Este archivo</span><span>
</span></span></code></div></div></pre>

---

## Requisitos 🧰

* Docker 🐳 y red local.
* Linux (recomendado) o WSL2.
* Herramientas sugeridas: `ghidra` / `radare2` / `gdb` / `strace`.
* (Opcional) Python 3.10+ para tu solver.

---

## Puesta en marcha 🚀

1. **Levantar la API**

<pre class="overflow-visible!" data-start="1787" data-end="1810"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh up
</span></span></code></div></div></pre>

2. **Endpoints**

* **Docs:** `http://<IP>:8102/docs` 📚
* **Binario:** `GET /download/specterjit` ⬇️
* **Redención:** `POST /redeem` con `{"token":"<hex64>"}` 💌

3. **Gestión**

<pre class="overflow-visible!" data-start="1994" data-end="2084"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh reset   </span><span># 🔄 reinicia</span><span>
./run.sh clean   </span><span># 🧹 borra contenedor e imagen</span><span>
</span></span></code></div></div></pre>

> Puerto por defecto: **8102** (host) → **8001** (contenedor).

---

## Reglas del juego 🧭

* No modificar la API para revelar la flag. 🙅‍♂️
* No brute force ni abuso de la API (rate razonable). 🧪
* El reto exige **reconstruir el algoritmo** del binario y reproducirlo.
* Se permite reversing, emulación y scripting propio. 🧑‍💻

---

## Pistas (sin spoilers) 🔍

* Ajuste de **buffering** y **antidebug** al inicio.
* La entrada de **5 bytes** decide la **ruta** del JIT. 🔀
* Verás `mmap` (RW) → `mprotect` (RX) y escritura de **máquina** antes de llamar. 🧱➡️⚡
* El **tiempo** influye (latencia y skew importan). ⏲️
* Tras el JIT hay un **post-mix** antes del `printf`.
* Si todo “casi” funciona pero falla, revisa **rotaciones** (cantidad y dirección). 🔁
* Un **solo bit** mal rotado rompe el token. 🧨

---

## Qué entregar 📦

1. **Write-up** breve con:
   * Detección del JIT y evidencia de ejecución en caliente.
   * Antidebug encontrados y cómo los sorteaste.
   * Diagrama del **flujo de datos** (entrada → JIT → salida).
   * Tests/validaciones intermedias.
   * Manejo de **skew** de reloj.
2. **Solver propio** que:
   * Genere el token **sin ejecutar** el binario.
   * Pruebe una ventana de ±N segundos.
   * Llame a `POST /redeem` y muestre la respuesta.
   * **No** revele la solución en el README. 🤫

---

## Self-check ✅

* Verifica el binario:
  <pre class="overflow-visible!" data-start="3496" data-end="3619"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>curl http://<IP>:8102/download/specterjit -o specterjit
  file specterjit    </span><span># Debe ser ELF 64-bit dinámico</span><span>
  </span></span></code></div></div></pre>
* Si recibes  **403** :
  * Revisa **reloj** y prueba ± segundos. ⏳
  * ¿Antidebug alterando semilla/rama?
  * ¿Rotaciones correctas (bits/dirección)?
  * ¿Ruta correcta para los 5 bytes? 🧩

---

## Buenas prácticas 🌱

* Usa **timeouts** cortos para no colgar scripts. ⏱️
* Evita depurar mientras generas tokens (altera resultados). 🧯
* Documenta **suposiciones** y  **checks** .
* Mantén bajo el **rate** de requests. 🌊

---

## FAQ 💬

**¿Se puede sólo con análisis estático?**

Sí, pero combina **estático + dinámico** para confirmar offsets y rutas.

**¿El token es aleatorio?**

No: depende de **entradas deterministas** (incluido el tiempo actual) y del **camino** ejecutado.

**¿Puedo usar el binario para obtener el token?**

El espíritu es **reimplementar** el algoritmo. Puedes validar hipótesis con el binario, pero tu entrega debe ser un  **solver independiente** .

**¿WSL/VM me falla?**

Cuida **NTP** y latencias. El antidebug puede cambiar la semilla si depuras. 🛰️

---

## Créditos 🙌

* Reto y binario:  **Dennis Juilland** .
* Inspirado en JITs minimalistas y defensas antidebug de CTFs.

---

## Términos 📜

Material educativo. No apliques estas técnicas fuera del ámbito del reto o sin autorización. Los organizadores pueden ajustar parámetros o apagar el servicio sin aviso.

---

¡Suerte cazando fantasmas en el optimizador! 👻🧠💥

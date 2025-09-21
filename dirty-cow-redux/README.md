# Dirty Cow Redux: CoW Race Resurrection 🐄⚡

> **Categoría:** Binary Exploitation
>
> **Dificultad:** Media–Alta
>
> **Autor:** Dennis Juilland
>
> **Lema:** *Every cow leaves footprints, even in patched pastures.*
>
> **Puertos:** `8103 : 8002`

---

## 🎯 Objetivo

Ganar privilegios suficientes para leer la **flag** ubicada en `root/.flag.txt` aprovechando una condición de carrera de escritura por `mmap` inspirada en  **Dirty COW (CVE-2016-5195)** , con un giro moderno.

Tu punto de entrada práctico es un pequeño “gatekeeper” de texto plano en el contenedor: **debes lograr que su contenido esté en el estado correcto** y luego ejecutar un binario de verificación que,  **si todo está bien** , revelará la flag.

> **Importante:** Este README **no** contiene la solución. Tu reto es idear la sincronización y la técnica de escritura sin romper el sistema. 😉

---

## 🧱 Lo que trae el entorno

Dentro del contenedor se despliegan:

* `cowtool` — utilidad SUID de laboratorio que **escribe sobre un archivo mapeado** bajo una ventana de tiempo “caprichosa”.
* `flagger` — binario SUID que **verifica el estado del gate** y, si es correcto,  **imprime la flag** .
* `http_server.py` — expone descargas HTTP de los binarios.
* `tcp_banner.sh` — sirve un banner con instrucciones por TCP (para `nc`).

Archivos interesantes:

* `/srv/cow_gate.conf` — **puerta** (archivo de control).
* `/root/.flag.txt` — **flag** (solo lectura por root).

---

## 🚀 Puesta en marcha

1. Construye/lanza el servicio:

   <pre class="overflow-visible!" data-start="1505" data-end="1534"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh up
   </span></span></code></div></div></pre>

   Verás algo como:

   <pre class="overflow-visible!" data-start="1558" data-end="1688"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>HTTP:</span><span></span><span>http://127.0.0.1:8103/</span><span>
   </span><span>Descargas:</span><span></span><span>/download/cowtool</span><span></span><span>/download/flagger</span><span>
   </span><span>Banner TCP:</span><span></span><span>nc</span><span></span><span>127.0</span><span>.0</span><span>.1</span><span></span><span>8103</span><span>
   </span></span></code></div></div></pre>
2. (Opcional) Conéctate al contenedor:

   <pre class="overflow-visible!" data-start="1732" data-end="1800"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh connect
   </span><span># prompt dentro del contenedor</span><span>
   </span></span></code></div></div></pre>
3. Resetea o limpia si hace falta:

   <pre class="overflow-visible!" data-start="1840" data-end="1984"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh reset     </span><span># reinicia el contenedor</span><span>
   ./run.sh clean     </span><span># borra contenedor + imagen (reconstruye en el próximo 'up')</span><span>
   </span></span></code></div></div></pre>

---

## 🔗 Interacción y artefactos

* **HTTP (descargas):**

  * `GET http://127.0.0.1:8103/download/cowtool`
  * `GET http://127.0.0.1:8103/download/flagger`
* **Banner por TCP:**

  <pre class="overflow-visible!" data-start="2170" data-end="2203"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>nc 127.0.0.1 8103
  </span></span></code></div></div></pre>

  Muestra instrucciones del reto y pistas generales.

---

## 📌 Enunciado técnico (alto nivel)

* Existe una **condición de carrera** entre:
  * una **escritura a través de memoria mapeada** sobre un archivo que normalmente no deberías poder modificar, y
  * un **ciclo de invalidación/consejo de memoria** que provoca ventanas breves de oportunidad (y ruido de sincronización).
* La herramienta de práctica (`cowtool`) no te “resuelve” el reto: te da **un medio imperfecto** para intentar la escritura bajo  **una ventana temporal** . Deberás **sincronizar el write** y  **cuidar alineación / tamaño / persistencia** .
* El verificador (`flagger`) **no eleva privilegios** por sí mismo; **únicamente valida** que el **archivo de control** quedó exactamente en el estado esperado antes de revelar la flag.

---

## ✅ Criterio de éxito

* Lograr que el archivo de control pase la verificación del verificador.
* Ejecutar:
  <pre class="overflow-visible!" data-start="3126" data-end="3164"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>/usr/local/bin/flagger
  </span></span></code></div></div></pre>
* Si la verificación es correcta, imprimirá la flag (que vive en `root/.flag.txt`).

> **Nota:** Limítate al  **control file** . El reto no requiere escribir directamente sobre `/root/.flag.txt` ni modificar credenciales del sistema.

---

## 🧭 Pistas (sin spoilers)

* **Sincronización:** No intentes una sola escritura. Piensa en  **ráfagas** , micro-pausas y **observabilidad** (por ejemplo, leer el archivo entre intentos).
* **Exactitud:** El verificador es **estricto** con el  **contenido y tamaño** . Evita caracteres extra o basura residual.
* **Persistencia:** Asegúrate de **forzar el contenido** al disco/archivo (recuerda que estás jugando con `mmap`).
* **Ruido temporal:** La ventana no es estable; el **timing** cambia. Experimenta con  **intensidad y duración de ráfagas** .
* **Alineación y longitudes:** Ajusta cuidadosamente **offsets** y **longitud** de lo que escribes.

---

## 🛠️ Consejos de debugging

* Observa el estado del **gate** entre intentos:

  <pre class="overflow-visible!" data-start="4137" data-end="4180"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>head</span><span> -n1 /srv/cow_gate.conf
  </span></span></code></div></div></pre>

  o en hex para ver bytes exactos:

  <pre class="overflow-visible!" data-start="4218" data-end="4267"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>xxd -g 1 -l 16 /srv/cow_gate.conf
  </span></span></code></div></div></pre>
* Si “parece correcto” pero falla el verificador, sospecha de:

  * **Saltos de línea extra** , `\0` faltantes o  **sobras** .
  * **Alineación** : puede que estés “pegando” en la dirección equivocada.
  * **Persistencia** : escribe y  **sincroniza** .
* ¿Se te “rompió” el entorno?

  `./run.sh reset` restaura el estado del contenedor.

---

## 🧪 Reglas del juego

* No cambies permisos globales del sistema ni montes cosas externas.
* No toques `/root/.flag.txt` directamente.
* No uses exploits fuera del ámbito del reto (kernel, contenedor) que no estén relacionados con la mecánica del ejercicio.
* El reto está diseñado para  **practicar timings de race y escritura vía mmap** , no para brute-forzar el host.

---

## 🧩 Entregables sugeridos

* Un **script de explotación** (p. ej., Bash/C/Python) que demuestre tu enfoque.
* Un **informe breve** con:
  * Cómo sincronizas la ventana de escritura.
  * Cómo garantizas tamaño/alineación persistentes.
  * Medidas para lidiar con el jitter temporal.

---

## 🧹 Reset rápido

Si algo quedó en mal estado, puedes  **recrear todo** :

<pre class="overflow-visible!" data-start="5349" data-end="5387"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>./run.sh clean
./run.sh up
</span></span></code></div></div></pre>

---

## ❓FAQ

**Q:** ¿Necesito un kernel vulnerable real?

**A:** No. Es un laboratorio **contenido** que emula la mecánica de Dirty COW para fines didácticos.

**Q:** ¿Puedo modificar el binario verificador?

**A:** No. La gracia es **hacer que el gate quede perfecto** y luego usar `flagger` sin alterarlo.

**Q:** ¿Puedo compilar mis propias pruebas dentro del contenedor?

**A:** Sí, hay toolchain básico. Pero evita instalaciones extrañas. Mantén el entorno limpio.

---

¡Buena cacería, vaquera/o del kernel! 🐄💥

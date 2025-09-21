# QuantumNoise: Entropy Betrayed — README

> **Categoría:** Miscellaneous
>
> **Dificultad:** Alto
>
> **Puertos:** `8106 : 80`
>
> **Resumen:** Te damos muestras crudas de un “QRNG perfecto” (generador cuántico de números aleatorios). En realidad tiene un **sesgo físico** (ruido de láser) que se filtra como  **componentes periódicas** . Con estadística + análisis de **Fourier** puedes **predecir bits suficientes** para reconstruir una **clave AES-128** y así  **descifrar la flag** .
>
> *Even true randomness hides a biased whisper.*

---

## 🧩 Objetivo del reto

1. Descargar el **bitstream crudo** (`qrng.bin`).
2. Detectar el **sesgo** y las **componentes periódicas** (armónicos de muy baja frecuencia).
3. Reconstruir una **clave AES-128** a partir de ese sesgo,  **sin romper criptografía** , solo explotando la  **falta de entropía verdadera** .
4. Usar la clave para **descifrar la flag** desde la propia web (o vía API).

> La **UI** del reto trae un “verificador/generador” con estética “PC cuántico”. Si introduces tus **128 bits** o el **key_hex** correcto, la web te muestra la flag.

---

## 🏗️ Puesta en marcha

<pre class="overflow-visible!" data-start="1133" data-end="1216"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Desde la carpeta del reto:</span><span>
./run.sh up
</span><span># → abre http://127.0.0.1:8106</span><span>
</span></span></code></div></div></pre>

Estructura relevante:

<pre class="overflow-visible!" data-start="1241" data-end="1441"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>quantumnoise/
├── </span><span>public</span><span>/
│   ├── index.html     # UI cuá</span><span>ntica</span><span> (verificador/generador)
│   └── styles.css
├── app.js             </span><span># servidor (Express)</span><span>
├── Dockerfile
├── package.json
└── run.sh
</span></span></code></div></div></pre>

---

## 🌐 Endpoints útiles

* `GET /` → UI cuántica y verificador.
* `GET /download/qrng.bin` → **dataset** binario (bits empaquetados).
* `GET /api/metadata` → metadatos (número de bits, IV de AES-CTR, longitud del ciphertext, etc.).
* `POST /api/submit` → verificación:
  * cuerpo JSON con **uno** de:
    * `{ "bits": "128 caracteres 0/1" }`, o
    * `{ "key_hex": "32 hex (16 bytes AES-128)" }`
  * respuesta: `{ ok: true, flag: "..." }` si atinaste, o `{ ok:false, distance: <hamming> }` para ayudarte a converger.

Ejemplos:

<pre class="overflow-visible!" data-start="1978" data-end="2151"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Descargar dataset</span><span>
curl -o qrng.bin http://127.0.0.1:8106/download/qrng.bin

</span><span># Ver metadatos (iv_hex, n_bits, etc.)</span><span>
curl http://127.0.0.1:8106/api/metadata | jq
</span></span></code></div></div></pre>

> La **flag no aparece** en ningún endpoint de forma directa; la devuelve solo si tu clave es  **exacta** .

---

## 🧪 ¿Qué hay dentro del dataset?

* `qrng.bin` contiene **N bits** (por defecto ~262K).
* **Empaquetado LSB-first por byte** : el **bit 0** va en el **LSB** del primer byte, el bit 1 en el siguiente, etc.
* Origen simulado con:
  * **Sesgo DC** pequeño ( **p(1) ≠ 0.5** ),
  * **Modulación senoidal** de muy baja frecuencia (ruido periódico de fuente/láser),
  * Ruido aleatorio pequeño.

Este tipo de “imperfecciones” ocurre en QRNG reales si el **pipe físico** no está perfectamente calibrado/compensado.

---

## 🧭 Camino de ataque (manual, paso a paso)

> El truco:  **no rompes AES** ; solo **predices** 128 bits **derivados** de correlaciones periódicas presentes en el bitstream.

### 1) Desempaquetar `qrng.bin` a bits

* Recuerda: **LSB-first** por byte.
* Si vas a trabajar con FFT/DFT, te conviene un array `x[n] ∈ {+1, −1}`:

x[n]={+1si bit = 1−1si bit = 0x[n] =
\begin{cases}
+1 & \text{si bit = 1} \\
-1 & \text{si bit = 0}
\end{cases}**x**[**n**]**=**{**+**1**−**1****si bit = 1**si bit = 0**
 **Por qué** : muchas pruebas estadísticas y correlaciones asumen variables centradas alrededor de 0; con ±1, un **sesgo DC** aparece como  **media positiva o negativa** .

### 2) Comprobar sesgo básico

* **Frecuencia de 1s** vs 0.5 (prueba de frecuencia / χ²).
* **Media** de x[n]x[n]**x**[**n**] (si hay sesgo DC, será ≠ 0).

> No te dará la clave aún, pero confirma que  **no es aleatorio perfecto** .

### 3) Buscar componentes periódicas (Fourier)

El backend expone **armónicos de baja frecuencia** (senos/cosenos) por la física de la fuente.

Una manera manual y estable:

* Para cada k=1..128k = 1..128**k**=**1..128** (solo necesitas 128 “medidas”):

  Sk=∑n=0N−1x[n]⋅sin⁡ ⁣(2πknN)S_k = \sum_{n=0}^{N-1} x[n]\cdot \sin\!\left(\frac{2\pi k n}{N}\right)**S**k****=**n**=**0**∑**N**−**1****x**[**n**]**⋅**sin**(**N**2**πkn****)
* Toma el **signo** de SkS_k**S**k como **bit k** de la clave:

bitk={1si Sk>00si Sk≤0\text{bit}_k =
\begin{cases}
1 & \text{si } S_k > 0 \\
0 & \text{si } S_k \le 0
\end{cases}**bit**k=**{**1**0****si **S**k****>**0**si **S**k≤**0****

> **Por qué funciona:** si la señal incluye una modulación baja ∼sin⁡(ωn)\sim \sin(\omega n)**∼**sin**(**ωn**)**, la correlación con ese seno será **positiva o negativa** de forma consistente. Con buena SNR, el **signo** es estable aunque la magnitud varíe.

**Tips prácticos**

* Puedes “submuestrear” (usar cada 2, 4, … muestras) al correlacionar: el **signo** suele mantenerse para componentes muy bajas, y ahorra tiempo.
* Si usas  **FFT** , la **parte imaginaria** del bin kk**k** (o la fase) te da esencialmente la misma información de signo.

### 4) Construir la clave AES-128

* Concatenas los 128 bits bit1,…,bit128\text{bit}_1, \dots, \text{bit}_{128}**bit**1,**…**,**bit**128.
* Empaquétalos **LSB-first por byte** → 16 bytes.
* O conviértelos a `key_hex` (32 hex).

### 5) Verificar en la web

* Opción A: pegar los **128 bits** en el verificador.
* Opción B: pegar el **key_hex** (32 hex).
* Si tu clave es correcta → la web te devuelve la  **flag** .
* Si no, te muestra una **Hamming distance** para indicar qué tan cerca estás (ideal <— 0).

---

## 🧪 Comprobaciones y sanity checks

* Tu espectro/ correlación debería mostrar **picos** a frecuencias muy bajas (k pequeños).
* Si cambias el **signo** de algunos SkS_k**S**k, verás que la **Hamming distance** disminuye/aumenta de forma predecible.
* La **IV** de AES-CTR viene en `/api/metadata` (no necesitas adivinarla).

---

## ❗ Errores frecuentes

* **Desempaquetado incorrecto** : recuerda  **LSB-first** . Si lo inviertes, la clave no coincide.
* **Usar coseno en lugar de seno** sin entender la fase: puedes perder el signo. Si vas con FFT, fíjate en **fase** (o usa seno explícito).
* **Esperar que “strings” o “grep” den la flag** : aquí **no hay** “texto escondido” en claro; la flag está cifrada con AES-CTR.
* **Conformarte con una clave “parecida”** : el verificador exige **exactitud total** (Hamming 0).

---

## 🖥️ Interfaz cuántica (UI)

* Lado izquierdo: **Dataset & Metadata** + botón de  **hint Fourier** .
* Lado derecho: **Verificador** (acepta 128 bits o 32-hex).
* Fondo animado con un **“qubit orb”** para el mood ☺️.

---

## 🔐 Por qué este ataque es realista

Aunque el QRNG sea “cuántico”, la **capa analógica** (láseres, detectores, osciladores) puede **filtrar patrones** (periodicidad, drift térmico, resonancias). Si la **post-processing chain** no “aplasta” correctamente esos artefactos (extractores de entropía, debiasers robustos), la salida  **no es uniforme** , y puedes **predecir** bits ⇒ **baja entropía efectiva** ⇒  **claves débiles** .

---

## 📦 Entregables que produce la plataforma

* `qrng.bin` — stream crudo (bits empaquetados).
* `/api/metadata` — info para **reproducibilidad** (N, IV de AES-CTR, longitud del cipher).
* Verificador con **métrica de Hamming** para ayudarte a converger.

---

## 🧰 Troubleshooting

* **“Hamming no baja”** → Revisa  **LSB-first** , el signo de tu seno y que estés sumando sobre **todo N** (o submuestreo consistente).
* **“Mi FFT no marca picos”** → Recuerda convertir a  **±1** ; con 0/1 el DC te contamina la lectura. Resta la media si persiste.
* **“¿Stride seguro?”** → El signo es robusto para armónicos muy bajos; reducir a n, n+4, n+8 suele conservarlo y acelera.

---

## 📜 Reglas del juego

* Se permite usar librerías de análisis (NumPy, SciPy, etc.).
* **No** se necesita romper AES ni vulnerar el servidor.
* La solución debe **reconstruir la clave** a partir del **sesgo/frecuencia** del dataset.

---

¡Que la **ruido-cuántico** te sea leve! 🌌🧪🌀

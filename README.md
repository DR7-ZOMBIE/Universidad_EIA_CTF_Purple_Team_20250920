# 🛡️ CTF Purple Team – Pack de Retos

> **Powered by la Academia de Ciberseguridad**
>
> Infraestructura “one-click” desplegada vía Docker/Compose por la Academia: Portal + SMB + Guacamole + XRDP + Postgres, más servicios por reto. Tú solo juegas. 😎

> ⚠️  **Aviso** : No compartas credenciales internas ni detalles de infraestructura fuera de entornos de laboratorio. Todo está pensado para uso formativo, controlado y responsable.

---

## 📚 Catálogo de retos (sin flags)

| Categoría          | Nombre del reto                                             | Descripción                                                                                                                                            | Aforismo                                                   | Responsable     | Puertos (host→servicio)                                            | Estado    | Dificultad | Puntuaje |
| ------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | --------------- | ------------------------------------------------------------------- | --------- | ---------- | -------- |
| Cryptography        | **Frostbite: Threshold Misbinding in MPC Signatures** | Servicio MPC (ECDSA/FROST) que filtra*shares*bajo ciertas reconexiones; explota resincronización de rondas para reconstruir la clave y firmar.       | *Even frozen thresholds crack when resynced*             | Dennis Juilland | **8101 : 8000**                                               | Completed | Alto       | 500      |
| Reversing           | **SpecterJIT: Ghosts in the Optimizer**               | Binario con JIT que emite*gadgets*en caliente; reversing dinámico + trampas de*branch predictor*para recomponer el cálculo final.                 | *The optimizer hides ghosts in every speculation.*       | Dennis Juilland | **8102 : 8001**                                               | Completed | Alto       | 500      |
| Binary Exploitation | **Dirty Cow Redux: CoW Race Resurrection**            | Race en `mmap`(inspirado en CVE-2016-5195) con twist moderno; sincroniza*writes*y sortea SMEP/SMAP para root.                                       | *Every cow leaves footprints, even in patched pastures.* | Dennis Juilland | **8103 : 8002**                                               | Completed | Alto       | 500      |
| Web                 | **SAML Hydra: Assertion of Many Heads**               | SAML mal configurado con parsers múltiples (XML→JSON→JWT). XSW +*JWT alg confusion*para admin impersonation.                                       | *Many heads sign, but only one truth escapes*            | Dennis Juilland | **8104 : 80**                                                 | Completed | Alto       | 500      |
| Forensics           | **Memory Echo: Ghost Threads of a Hypervisor**        | Dump parcial de VM (KVM). Reconstruye EPT/NPT, localiza restos de*hypercall*y usa Volatility + TLB analysis para descubrir el covert channel.         | *In echoes of memory, hypervisors leave ghosts.*         | Dennis Juilland | **8105 : 80**                                                 | Completed | Alto       | 500      |
| Misc                | **QuantumNoise: Entropy Betrayed**                    | RNG “cuántico” con sesgo físico (ruido láser). Estadística + Fourier para predecir bits y recuperar la clave AES.                                 | *Even true randomness hides a biased whisper*            | Dennis Juilland | **8106 : 80**                                                 | Completed | Alto       | 500      |
| Pwned               | **ARCSlid: Hidden Files, Hidden Lies**                | Escenario integrado: Portal/SMB/Guacamole/XRDP/Postgres. Descarga un ZIP “inocente”, conéctate por RDP y progresa hasta la flag en el host objetivo. | *Even archives bleed secrets when paths are twisted.*    | Dennis Juilland | **8080 · 8081 · 137 · 139 · 138 · 3389 · 5432 · 4822** | Completed | Alto       | 500      |

> **Nota** : “Puertos (host→servicio)” muestra el puerto publicado en el **host** y, tras “:”, el puerto del **servicio interno** cuando aplique.

---

## 🧩 Estructura del repo

<pre class="overflow-visible!" data-start="3140" data-end="3899"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>/
├─ arcslid/                 </span><span># escenario integrado (Portal + SMB + Guac + XRDP + PG)</span><span>
│  ├─ docker-compose.yml
│  ├─ run.sh               </span><span># orquesta payload, DB y conexión Guac</span><span>
│  ├─ quicheck.sh          </span><span># verificación E2E express</span><span>
│  ├─ portal/              </span><span># Node/Express (sirve /payload/*.zip)</span><span>
│  ├─ smb/                 </span><span># share [drop] → /share/drop (RO)</span><span>
│  ├─ xrdp/                </span><span># XRDP + XFCE + supervisord</span><span>
│  ├─ guac/initdb.sql      </span><span># se autogenera si falta</span><span>
│  └─ payload/             </span><span># genera ARCSlid-photos.zip</span><span>
├─ frostbite/              </span><span># (crypto)</span><span>
├─ specterjit/             </span><span># (reversing)</span><span>
├─ dirty-cow-redux/        </span><span># (pwn/binexp)</span><span>
├─ saml-hydra/             </span><span># (web)</span><span>
├─ memory-echo/            </span><span># (forensics)</span><span>
└─ quantum-noise/          </span><span># (misc)</span><span>
</span></span></code></div></div></pre>

Cada reto (excepto ARCSlid) tiene su propio `docker-compose.yml` y README local con objetivos, requisitos y cómo validar (sin flag en claro).

---

## 🚀 ARCSlid – Arranque rápido

**La Academia despliega la infra por ti.** Si corres local:

<pre class="overflow-visible!" data-start="4143" data-end="4282"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>cd</span><span> arcslid
./run.sh up          </span><span># build + despliegue + preparación de DB Guacamole</span><span>
./quicheck.sh        </span><span># smoke test end-to-end</span><span>
</span></span></code></div></div></pre>

**Accesos:**

* **Portal** → [http://127.0.0.1:8080](http://127.0.0.1:8080)
* **Guacamole** → [http://127.0.0.1:8081/guacamole](http://127.0.0.1:8081/guacamole)
  * Usuario jugador por defecto: `ctf` / `ctf`
  * Conexión: `ARCSlid-RDP` (host `arcslid-xrdp`, usuario `player`)

> ¿Tu target es una VM distinta? Actualiza la IP de la conexión RDP:
>
> `./run.sh sql-set-ip 192.168.56.101`

---

## 🧪 Snippets útiles

 **SMB (ARCSlid)** :

<pre class="overflow-visible!" data-start="4664" data-end="4781"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>smbclient -p 8107 -N -L //127.0.0.1
smbclient -p 8107 -N //127.0.0.1/drop -c </span><span>'ls; get ARCSlid-photos.zip'</span><span>
</span></span></code></div></div></pre>

 **Conectividad Guacamole → XRDP** :

<pre class="overflow-visible!" data-start="4818" data-end="4927"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker </span><span>exec</span><span> -it arcslid-guac bash -lc </span><span>'echo > /dev/tcp/arcslid-xrdp/3389 && echo OK || echo FAIL'</span><span>
</span></span></code></div></div></pre>

 **Esquema Guacamole en Postgres** :

<pre class="overflow-visible!" data-start="4964" data-end="5169"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker </span><span>exec</span><span> -it arcslid-pg psql -U postgres -d guacdb -c </span><span>"\dt guacamole_*"</span><span>
docker </span><span>exec</span><span> -it arcslid-pg psql -U postgres -d guacdb -c </span><span>"SELECT connection_name, protocol FROM guacamole_connection;"</span><span>
</span></span></code></div></div></pre>

---

## 🛠️ Despliegue del resto de retos

Para cada carpeta (`frostbite/`, `specterjit/`, etc.):

<pre class="overflow-visible!" data-start="5270" data-end="5381"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>cd</span><span> <carpeta-del-reto>
docker compose up -d --build
</span><span># verifica el puerto indicado en la tabla global</span><span>
</span></span></code></div></div></pre>

Incluye en cada README local:

* 🎯 Objetivo
* 🚦 Arranque / Puertos
* 🧑‍💻 Requisitos del jugador
* ✅ Criterio de validación (sin flag en claro)

---

## 🩺 Troubleshooting

* **Healthchecks “unhealthy” pero todo OK** : suele faltar `ss`/`nc` en imágenes base; es cosmético.
* **Guacamole no conecta por RDP** :
* Revisa XRDP:
  <pre class="overflow-visible!" data-start="5721" data-end="5811"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker </span><span>exec</span><span> -it arcslid-xrdp bash -lc </span><span>'tail -n 200 /var/log/xrdp*.log'</span><span>
  </span></span></code></div></div></pre>
* Confirma que la conexión apunta a `arcslid-xrdp` (o la IP que fijaste con `sql-set-ip`).
* **Reset limpio** :

<pre class="overflow-visible!" data-start="5927" data-end="5979"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker compose down -v
  ./run.sh up
  </span></span></code></div></div></pre>

---

## 🤝 Créditos & Reconocimientos

* **Coordinación/Diseño** : Dennis Juilland
* **Aforismos & narrativa** : equipo creativo
* **Infra** : **Academia de Ciberseguridad** — despliegue automatizado de todos los servicios del escenario ARCSlid y soporte a los retos satélite.

> ¿Quieres que lo partamos en un `README.md` raíz y sub-README por reto con plantillas listas para rellenar? Te los dejo en un toque.
>

FROM debian:stable-slim

ENV DEBIAN_FRONTEND=noninteractive

# Paquetes base + toolchain + venv + setcap + coreutils (timeout) + getcap
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-dev python3-pip \
    gcc make libc6-dev libffi-dev \
    file binutils ca-certificates \
    libcap2-bin coreutils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

# --- Crear venv y activar en PATH ---
RUN python3 -m venv /venv
ENV PATH="/venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

# App Python
COPY app/ /srv/app/
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic==2.9.2

# Binario (se compila en build)
COPY bin-src/ /srv/bin-src/
WORKDIR /srv/bin-src
RUN make clean && make \
 && strip -s ./specterjit \
 && setcap cap_sys_ptrace+ep /srv/bin-src/specterjit \
 && file ./specterjit

# Volver a la app
WORKDIR /srv

# Usuario no root
RUN useradd -m ctf && chown -R ctf:ctf /srv
USER ctf

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

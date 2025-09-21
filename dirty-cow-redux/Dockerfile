# Dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential gcc make socat \
    python3 python3-pip curl vim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Usuario de juego
RUN useradd -m -s /bin/bash player
RUN mkdir -p /home/player/uploads && chown -R player:player /home/player

# Carpeta de control del reto y flag
RUN mkdir -p /etc/cow && \
    echo "NO" > /etc/cow/permit && \
    chown root:root /etc/cow/permit && chmod 600 /etc/cow/permit

# Flag (cámbiala si quieres rotarla)
RUN echo "EIAPT{4d03140c60e43b2d3b69509201dfef00bda2b9874ba9dbbe20415b134e3e7f9a}" > /root/flag.txt && \
    chown root:root /root/flag.txt && chmod 400 /root/flag.txt

# Binario vulnerable
WORKDIR /opt/challenge
COPY cowrace.c /opt/challenge/cowrace.c
RUN gcc -O2 -Wall cowrace.c -o /usr/local/bin/cowrace -pthread && \
    chown root:root /usr/local/bin/cowrace && chmod 4755 /usr/local/bin/cowrace

# Servicio TCP que ejecuta el binario por conexión
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8002
CMD ["/entrypoint.sh"]

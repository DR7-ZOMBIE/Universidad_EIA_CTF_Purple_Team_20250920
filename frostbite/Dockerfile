FROM python:3.11-slim

WORKDIR /app

# Dependencias mínimas
RUN pip install --no-cache-dir fastapi uvicorn pydantic==2.9.2

# Copiamos código
COPY app/ /app/

# Usuario no-root (endurecimiento básico)
RUN useradd -m ctf && chown -R ctf:ctf /app
USER ctf

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

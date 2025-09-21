#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, time, signal

# ⚠️ Sigue siendo solo visual. Nada se cifra, nada se toca.

TOTAL_SECONDS = 120  # 2 minutos

def fallback_text():
    # Modo consola si no hay pygame o display. Ignora Ctrl+C hasta que termine.
    def handler(_sig, _frm):
        # Ignora Ctrl+C durante el conteo
        pass
    old = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handler)
    try:
        for i in range(TOTAL_SECONDS, -1, -1):
            print(f"[ALERTA SIMULADA] 'Ransom' CTF. Explota en: {i:03d}s ...   ", end="\r", flush=True)
            time.sleep(1)
        print("\n(Fin de simulación)")
    finally:
        signal.signal(signal.SIGINT, old)

try:
    import pygame
except Exception:
    fallback_text()
    sys.exit(0)

def center(surface, text, font, color, y):
    s = font.render(text, True, color)
    r = s.get_rect(center=(surface.get_width()//2, y))
    surface.blit(s, r)

def main():
    # Pantalla completa
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    try:
        pygame.init()
        # FULLSCREEN a resolución nativa
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    except Exception:
        fallback_text()
        return

    W, H = screen.get_size()
    pygame.display.set_caption("ALERTA — Simulación CTF")
    pygame.mouse.set_visible(False)  # Oculta el cursor
    clock = pygame.time.Clock()

    # Fuentes (con fallback)
    try:
        big  = pygame.font.SysFont("Arial", 68, bold=True)
        mid  = pygame.font.SysFont("Arial", 36, bold=True)
        small= pygame.font.SysFont("Arial", 22)
    except Exception:
        big = mid = small = pygame.font.Font(None, 36)

    t0 = time.time()
    end_at = t0 + TOTAL_SECONDS
    running = True
    finished = False

    # Para bloquear cierre dentro de la ventana, ignoramos QUIT/teclas hasta que termine
    while running:
        now = time.time()
        left = max(0, int(end_at - now))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                # Ignorar cierre hasta que termine
                if left > 0:
                    pass
                else:
                    running = False
            elif ev.type == pygame.KEYDOWN:
                # Ignorar ESC, Q, ALT+F4 (señalizado como QUIT), etc., hasta el final
                if left > 0:
                    pass

        # Render
        screen.fill((12, 0, 0))
        pygame.draw.rect(screen, (160, 0, 0), (0, 0, W, H), 24)

        center(screen, "Has sido 'infectado' (simulado)", big, (255, 80, 80), H//2 - 140)
        center(screen, "Analizaste una imagen con formato erróneo.", mid, (255, 180, 180), H//2 - 70)
        center(screen, f"El sistema 'explotará' en: {left:03d}s", big, (255, 255, 0), H//2 + 10)
        center(screen, "Tranquilo: es SOLO la temática del reto. No cifra nada.", small, (220, 220, 220), H//2 + 70)
        center(screen, "No puedes cerrar esta ventana hasta que termine el conteo.", small, (180, 180, 180), H//2 + 100)

        pygame.display.flip()
        clock.tick(30)

        if left <= 0 and not finished:
            finished = True
            # Pequeña pausa final y permitir cerrar
            time.sleep(2.0)
            running = False

    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    main()

// cowrace.c — servicio remoto vulnerable (TOCTOU + mmap) + WALL chat
// Versión CTF remoto: sin realpath(), carrera entre lstat() -> usleep() -> open().
// Protocolo:
//   HELP
//   SHOW
//   PUT <name>         (lee 1 línea de datos y escribe en uploads/<name>)
//   LINK <name> <target>
//   EDIT <name>        (lee 1 línea y la copia vía mmap)
//   NICK <alias>
//   SAY <texto>        (o WALL <texto>)
//   WALL ON | OFF | TAIL
//
// Objetivo: lograr que EDIT escriba "OK" en /etc/cow/permit y luego SHOW muestre la FLAG.

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define UPLOAD_DIR "/home/player/uploads/"
#define PERMIT     "/etc/cow/permit"
#define FLAG       "/root/flag.txt"
#define WALL_PATH  "/var/tmp/cow_wall.log"

static bool starts_with(const char *s, const char *p) {
    size_t ls = strlen(s), lp = strlen(p);
    return ls >= lp && strncmp(s, p, lp) == 0;
}

static void print_banner(void) {
    puts("=== Dirty Cow Redux: CoW Race Resurrection ===");
    puts("Every cow leaves footprints, even in patched pastures.");
    puts("Comandos: HELP | SHOW | PUT <name> | LINK <name> <target> | EDIT <name>");
    puts("Extras: NICK <alias> | SAY <texto> | WALL <texto> | WALL ON | WALL OFF | WALL TAIL");
    puts("Notas:");
    puts(" - PUT lee una linea y la escribe en uploads/<name> (sin '/').");
    puts(" - LINK convierte uploads/<name> en symlink hacia <target>.");
    puts(" - EDIT valida y mapea uploads/<name>; si ganas la carrera, escribes fuera.");
    puts(" - WALL permite chatear entre conexiones (nc) en vivo.");
    puts("");
    fflush(stdout);
}

static void try_print_flag(void) {
    int fd = open(PERMIT, O_RDONLY);
    if (fd >= 0) {
        char buf[8] = {0};
        ssize_t n = read(fd, buf, sizeof(buf)-1);
        close(fd);
        if (n > 0 && strncmp(buf, "OK", 2) == 0) {
            int ff = open(FLAG, O_RDONLY);
            if (ff >= 0) {
                char fbuf[4096];
                ssize_t r = read(ff, fbuf, sizeof(fbuf));
                close(ff);
                if (r > 0) {
                    write(STDOUT_FILENO, "FLAG: ", 6);
                    write(STDOUT_FILENO, fbuf, r);
                    return;
                }
            }
            puts("No pude leer la flag. Contacta al organizador.");
        } else {
            puts("Aun no hay huellas en el establo. (SHOW luego de activar puede revelar la flag)");
        }
    } else {
        puts("No se pudo abrir el establo.");
    }
    fflush(stdout);
}

static int read_line(char *buf, size_t sz) {
    if (!fgets(buf, sz, stdin)) return -1;
    buf[strcspn(buf, "\r\n")] = 0;
    return 0;
}

static int join_path(const char *name, char *out, size_t outsz) {
    if (strchr(name, '/')) return -1; // nombres simples, sin '/'
    int n = snprintf(out, outsz, "%s%s", UPLOAD_DIR, name);
    return (n < 0 || (size_t)n >= outsz) ? -1 : 0;
}

/* ---------------- WALL: utilidades ---------------- */

static void wall_ensure(void) {
    int fd = open(WALL_PATH, O_CREAT | O_WRONLY, 0666);
    if (fd >= 0) close(fd);
}

static void sanitize_line(char *s) {
    for (; *s; ++s) {
        if (*s == '\n' || *s == '\r') *s = ' ';
    }
}

static void wall_post(const char *nick, const char *text) {
    wall_ensure();
    int fd = open(WALL_PATH, O_WRONLY | O_APPEND);
    if (fd < 0) return;
    time_t t = time(NULL);
    struct tm tm;
    localtime_r(&t, &tm);
    char ts[32];
    strftime(ts, sizeof(ts), "%H:%M:%S", &tm);

    char line[2048];
    char txtcpy[1500];
    strncpy(txtcpy, text, sizeof(txtcpy)-1);
    txtcpy[sizeof(txtcpy)-1] = 0;
    sanitize_line(txtcpy);
    int n = snprintf(line, sizeof(line), "[WALL %s] %s: %s\n", ts, nick, txtcpy);
    if (n > 0) write(fd, line, (size_t)n);
    close(fd);
}

static void wall_tail_last(int nlines) {
    wall_ensure();
    FILE *f = fopen(WALL_PATH, "r");
    if (!f) { puts("[WALL] no disponible"); return; }
    // lee todo y muestra las ultimas n líneas (simple y suficiente)
    char *buf = NULL; size_t cap = 0; ssize_t r;
    // carga todo
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    if (sz < 0) { fclose(f); return; }
    fseek(f, 0, SEEK_SET);
    buf = (char*)malloc((size_t)sz + 1);
    if (!buf) { fclose(f); return; }
    size_t rd = fread(buf, 1, (size_t)sz, f);
    buf[rd] = 0;
    fclose(f);

    // encuentra ultimas n líneas
    int count = 0;
    long i;
    for (i = (long)rd - 1; i >= 0; --i) {
        if (buf[i] == '\n') {
            if (++count == nlines) { i++; break; }
        }
    }
    if (i < 0) i = 0;
    write(STDOUT_FILENO, buf + i, rd - (size_t)i);
    free(buf);
    fflush(stdout);
}

static volatile int wall_running = 0;
static pthread_t wall_thr;

static void *wall_follow_thread(void *arg) {
    (void)arg;
    wall_ensure();
    int fd = open(WALL_PATH, O_RDONLY);
    if (fd < 0) return NULL;
    off_t off = lseek(fd, 0, SEEK_END);
    if (off < 0) off = 0;

    char buf[2048];
    while (wall_running) {
        struct stat st;
        if (fstat(fd, &st) == 0 && st.st_size > off) {
            off_t toread = st.st_size - off;
            if (toread > (off_t)sizeof(buf)) toread = sizeof(buf);
            ssize_t n = pread(fd, buf, (size_t)toread, off);
            if (n > 0) {
                write(STDOUT_FILENO, buf, (size_t)n);
                fflush(stdout);
                off += n;
            }
        }
        usleep(200000); // 200 ms
    }
    close(fd);
    return NULL;
}

static void wall_on(void) {
    if (wall_running) { puts("[WALL] ya activo."); return; }
    wall_running = 1;
    if (pthread_create(&wall_thr, NULL, wall_follow_thread, NULL) == 0) {
        puts("[WALL] follow ON.");
    } else {
        wall_running = 0;
        puts("[WALL] no se pudo activar.");
    }
    fflush(stdout);
}

static void wall_off(void) {
    if (!wall_running) { puts("[WALL] ya apagado."); return; }
    wall_running = 0;
    pthread_join(wall_thr, NULL);
    puts("[WALL] follow OFF.");
    fflush(stdout);
}

/* -------------- Comandos base del reto -------------- */

static void cmd_put(char *name) {
    char path[PATH_MAX];
    if (join_path(name, path, sizeof(path)) != 0) { puts("Nombre invalido."); return; }
    puts("Datos (1 linea):"); fflush(stdout);
    char data[4096]; if (read_line(data, sizeof(data)) != 0) { puts("Entrada vacia."); return; }
    int fd = open(path, O_WRONLY|O_CREAT|O_TRUNC, 0644);
    if (fd < 0) { perror("open"); return; }
    write(fd, data, strlen(data));
    close(fd);
    puts("OK: escrito."); fflush(stdout);
}

static void cmd_link(char *name, char *target) {
    char path[PATH_MAX];
    if (join_path(name, path, sizeof(path)) != 0) { puts("Nombre invalido."); return; }
    unlink(path);
    if (symlink(target, path) != 0) { perror("symlink"); return; }
    puts("OK: symlink creado."); fflush(stdout);
}

static void cmd_edit(char *name) {
    // Validación mínima (join_path ya obliga prefijo), sin realpath() para que la carrera sea viable.
    char path[PATH_MAX];
    if (join_path(name, path, sizeof(path)) != 0) { puts("Nombre invalido."); return; }

    struct stat st;
    if (lstat(path, &st) != 0) { perror("lstat"); return; }
    // Ventana de carrera entre lstat() y open() (ajusta 3000–8000 us para dificultad)
    usleep(5000); // 5 ms

    int fd = open(path, O_RDWR);
    if (fd < 0) { perror("open"); return; }

    off_t len = st.st_size;
    if (len < 128) { if (ftruncate(fd, 128) != 0) { perror("ftruncate"); close(fd); return; } len = 128; }

    void *map = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) { perror("mmap"); close(fd); return; }

    puts("Datos a escribir (1 linea, se copia a mmap):"); fflush(stdout);
    char data[256]; if (read_line(data, sizeof(data)) != 0) { munmap(map, len); close(fd); puts("Entrada vacia."); return; }
    size_t dlen = strnlen(data, sizeof(data));
    memcpy(map, data, dlen);
    msync(map, len, MS_SYNC);
    munmap(map, len); close(fd);
    puts("Actualizacion completada."); fflush(stdout);
}

static void gen_default_nick(char *nick, size_t nsz) {
    unsigned int r = (unsigned int)getpid();
    snprintf(nick, nsz, "cow%04x", r & 0xFFFF);
}

static void set_nick(char *nick, size_t nsz, const char *newn) {
    char tmp[64]; size_t j=0;
    for (size_t i=0; newn[i] && j< (sizeof(tmp)-1); ++i) {
        char c = newn[i];
        if ((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='_'||c=='-')
            tmp[j++]=c;
    }
    tmp[j]=0;
    if (j==0) { puts("Alias invalido."); return; }
    if (j>=nsz) tmp[nsz-1]=0;
    strncpy(nick, tmp, nsz-1);
    nick[nsz-1]=0;
    printf("[WALL] alias cambiado a: %s\n", nick); fflush(stdout);
}

int main(void) {
    // SUID: privilegios efectivos root (para el reto)
    seteuid(0); setegid(0);

    char nick[32]; gen_default_nick(nick, sizeof(nick));

    print_banner();
    try_print_flag();

    char line[1024];
    while (1) {
        fputs("\n> ", stdout); fflush(stdout);
        if (read_line(line, sizeof(line)) != 0) break;
        if (!*line) continue;

        if (!strncmp(line, "HELP", 4)) {
            print_banner();
        } else if (!strncmp(line, "SHOW", 4)) {
            try_print_flag();
        } else if (!strncmp(line, "PUT ", 4)) {
            char name[256]; if (sscanf(line+4, "%255s", name) == 1) cmd_put(name); else puts("Uso: PUT <name>");
        } else if (!strncmp(line, "LINK ", 5)) {
            char name[256], target[512];
            if (sscanf(line+5, "%255s %511s", name, target) == 2) cmd_link(name, target);
            else puts("Uso: LINK <name> <target>");
        } else if (!strncmp(line, "EDIT ", 5)) {
            char name[256]; if (sscanf(line+5, "%255s", name) == 1) cmd_edit(name); else puts("Uso: EDIT <name>");
        } else if (!strncmp(line, "NICK ", 5)) {
            char nn[64]; if (sscanf(line+5, "%63s", nn) == 1) set_nick(nick, sizeof(nick), nn); else puts("Uso: NICK <alias>");
        } else if (!strncmp(line, "SAY ", 4)) {
            wall_post(nick, line+4);
        } else if (!strncmp(line, "WALL ON", 7)) {
            wall_on();
        } else if (!strncmp(line, "WALL OFF", 8)) {
            wall_off();
        } else if (!strncmp(line, "WALL TAIL", 9)) {
            wall_tail_last(10);
        } else if (!strncmp(line, "WALL ", 5)) {
            wall_post(nick, line+5);
        } else if (!strncmp(line, "QUIT", 4)) {
            puts("Bye."); break;
        } else {
            puts("Comando desconocido. Escribe HELP.");
        }
    }

    if (wall_running) { wall_off(); }
    return 0;
}

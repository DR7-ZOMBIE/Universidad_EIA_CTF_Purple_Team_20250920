#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>     // <-- necesario para srand
#include <sys/mman.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>

// --- Ligeras defensas (no bloquean al analista serio) ---
static void light_antis() {
    prctl(PR_SET_DUMPABLE, 0, 0, 0, 0);
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) == -1 && errno) {
        // si estamos traceados, variamos un poco la semilla
        srand((unsigned)time(NULL) ^ 0x9e3779b1);
    } else {
        srand((unsigned)time(NULL));
    }
}

// Rutinita para "entrenar" rama (patrón esperado: 'L','R','L','L','R')
// si el patrón no coincide, cambiamos la máscara de decodificación
static uint64_t predictor_training_mask() {
    char buf[8] = {0};
    // Lee hasta 5 chars, ignorando newline
    ssize_t n = read(0, buf, 5);
    const char want[6] = {'L','R','L','L','R','\0'};
    if (n >= 5 && !memcmp(buf, want, 5)) {
        return 0xa5a5a5a5a5a5a5a5ULL; // máscara "correcta"
    }
    return 0x5a5a5a5a5a5a5a5aULL; // máscara alternativa
}

// JIT: genera una función que devuelve un uint64 obfuscado
typedef uint64_t (*jit_func_t)(uint64_t seed);

static jit_func_t build_jit(uint64_t k1, uint64_t k2, uint64_t k3) {
    // Código máquina x86_64 (SysV) equivalente a:
    // uint64_t f(uint64_t seed) {
    //   rax = seed
    //   rax ^= k1
    //   ror rax, 13
    //   rax += k2
    //   rax *= k3
    //   ror rax, 29
    //   return rax;
    // }
    // Ensamblado aproximado (hex):
    // mov rax, rdi                48 89 f8
    // movabs rbx, k1              48 bb <k1 8bytes>
    // xor rax, rbx                48 31 d8
    // ror rax, 0x0d               48 c1 c8 0d
    // movabs rcx, k2              48 b9 <k2 8bytes>
    // add rax, rcx                48 01 c8
    // movabs rdx, k3              48 ba <k3 8bytes>
    // imul rax, rdx               48 0f af c2
    // ror rax, 0x1d               48 c1 c8 1d
    // ret                          c3

    unsigned char code[] = {
        0x48,0x89,0xF8,
        0x48,0xBB,0,0,0,0,0,0,0,0,
        0x48,0x31,0xD8,
        0x48,0xC1,0xC8,0x0D,
        0x48,0xB9,0,0,0,0,0,0,0,0,
        0x48,0x01,0xC8,
        0x48,0xBA,0,0,0,0,0,0,0,0,
        0x48,0x0F,0xAF,0xC2,
        0x48,0xC1,0xC8,0x1D,
        0xC3
    };

    // Pachar k1,k2,k3 little-endian
    memcpy(&code[5],  &k1, 8);
    memcpy(&code[23], &k2, 8);
    memcpy(&code[35], &k3, 8);

    void *buf = mmap(NULL, sizeof(code),
                     PROT_READ|PROT_WRITE,
                     MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (buf == MAP_FAILED) return NULL;

    memcpy(buf, code, sizeof(code));
    mprotect(buf, sizeof(code), PROT_READ|PROT_EXEC);
    return (jit_func_t)buf;
}

// Pequeña ofuscación de constantes (se decodifican con máscara dinámica)
static void decode_consts(uint64_t mask, uint64_t *k1, uint64_t *k2, uint64_t *k3) {
    uint64_t e1 = 0xB5E2D4C7A19F8871ULL;
    uint64_t e2 = 0x7C8A11F0D3B42955ULL;
    uint64_t e3 = 0xA1C3E5F7092B4D6FULL;
    *k1 = e1 ^ ((mask << 7) | (mask >> 5));
    *k2 = e2 ^ ((mask << 13) | (mask >> 11));
    *k3 = e3 ^ ((mask << 29) | (mask >> 19));
}

static uint64_t weak_hash64(uint64_t x) {
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33; return x;
}

int main(int argc, char **argv) {
    (void)argc; (void)argv;

    // salida sin buffer: importantísimo para docker exec / pipes
    setvbuf(stdout, NULL, _IONBF, 0);

    light_antis();

    uint64_t mask = predictor_training_mask();

    uint64_t seed = (uint64_t)time(NULL);
    seed = weak_hash64(seed ^ 0x9e3779b97f4a7c15ULL);

    uint64_t k1,k2,k3;
    decode_consts(mask, &k1, &k2, &k3);

    jit_func_t F = build_jit(k1, k2, k3);
    if (!F) { puts("jit_err"); return 1; }

    uint64_t out = F(seed);
    uint64_t token64 = weak_hash64(out ^ 0xC6A4A7935BD1E995ULL) ^ 0x27d4eb2f165667c5ULL;

    // 16 hex + newline (para asegurar flush en cualquier caso)
    printf("%016llx\n", (unsigned long long)token64);
    return 0;
}


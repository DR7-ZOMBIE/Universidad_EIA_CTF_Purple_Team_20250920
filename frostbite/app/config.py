import os

# Parámetros "Schnorr" toy (mod prime q, generador g mod p). Para CTF es suficiente.
# p es seguro para mod mult., pero trabajamos en subgrupo de orden q.
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F  # secp256k1 prime (solo para mod)
g = 5
q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # orden de secp256k1 (toy)

# Mensaje admin y FLAG
ADMIN_MSG = os.getenv("ADMIN_MSG", "authorize:admin-panel")
FLAG = os.getenv("FLAG", "EIAPT{a16005a6d088406f4e6337aa7c74c0cbc5421a0d646f0763386abd05074c1116}")

# IP/host para mensajes
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "127.0.0.1")

# Shares fijos de A, B, C (no revelados por API)
xA = 0x1337_aaaabbbbccccddddeeeeffff1111222233334444555566667777888899 % q
xB = 0x1337_deadbeefcafebabef00df00df00dba5eba11c0ffeec0ffee123456789 % q
xC = 0x1337_0102030405060708090a0b0c0d0e0f1112131415161718191a1b1c1d1e % q

# Clave global (suma de shares) y pubkey Y = g^x mod p
x_total = (xA + xB + xC) % q
def powmod(a, e, m): return pow(a, e, m)
Y = powmod(g, x_total, p)

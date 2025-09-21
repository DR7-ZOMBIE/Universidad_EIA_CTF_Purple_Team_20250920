import hashlib
import secrets
from typing import List, Tuple
from config import p, q, g, Y
from storage import GLOBAL_NONCE, GLOBAL_Ri

def H_int(*ints_or_bytes) -> int:
    h = hashlib.sha256()
    for obj in ints_or_bytes:
        if isinstance(obj, int):
            h.update(obj.to_bytes(64, 'big'))
        elif isinstance(obj, bytes):
            h.update(obj)
        elif isinstance(obj, str):
            h.update(obj.encode())
        else:
            raise TypeError("Unsupported type in hash input")
    return int.from_bytes(h.digest(), 'big') % q

# Mapea id de participante a share secreto (fijado en config)
from config import xA, xB, xC
def share_of(pid: str) -> int:
    return {"A": xA, "B": xB, "C": xC}[pid]

def ensure_commitments(participants: List[str]) -> List[int]:
    """
    **BUG**: Si ya existe GLOBAL_NONCE[pid], NO se genera uno nuevo por sesión/mensaje.
    Esto hace que al orquestar dos firmas con mismos participants, puedas forzar mismo R (producto).
    """
    Ri = []
    for pid in participants:
        if pid not in GLOBAL_NONCE:
            k_i = secrets.randbelow(q-1) + 1
            GLOBAL_NONCE[pid] = k_i
            GLOBAL_Ri[pid] = pow(g, k_i, p)
        Ri.append(GLOBAL_Ri[pid])
    return Ri

def aggregate_R(Ri_list: List[int]) -> int:
    R = 1
    for Ri in Ri_list:
        R = (R * Ri) % p
    return R

def sign_aggregated(participants: List[str], message: str) -> Tuple[int,int,int]:
    """
    Devuelve (R, s, e) para un conjunto de participantes.
    s = sum_i (k_i) + e * sum_i (x_i)  (mod q)
    """
    Ri_list = ensure_commitments(participants)        # BUG: reusa k_i antiguos
    R = aggregate_R(Ri_list)
    e = H_int(R, message)
    k_sum = sum(GLOBAL_NONCE[pid] for pid in participants) % q
    x_sum = sum(share_of(pid)   for pid in participants) % q
    s = (k_sum + (e * x_sum) % q) % q
    return R, s, e

def verify(R: int, s: int, message: str) -> bool:
    e = H_int(R, message)
    left = pow(g, s, p)
    right = (R * pow(Y, e, p)) % p
    return left == right

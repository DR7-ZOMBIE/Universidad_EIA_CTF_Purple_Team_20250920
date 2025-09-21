# app/main.py (fragmento del POST /redeem)
import os, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Req(BaseModel):
    token: str

app = FastAPI()

def u64(x): return x & 0xFFFFFFFFFFFFFFFF
def ror(x,n): n &= 63; return u64((x >> n) | (x << (64-n)))
def rol(x,n): n &= 63; return u64((x << n) | (x >> (64-n)))

def mix1(t):
    C  = 0x9e3779b97f4a7c15
    M1 = 0xF51C3F3D558FCCD3
    M2 = 0xC4CEB9FE1A85EC53
    x = u64(((t ^ C) >> 33) ^ t ^ C)
    x = u64(x * M1)
    x = u64((x ^ (x >> 33)) * M2)
    return x

def mix2(x):
    C  = 0xC6A4A7935BD1E995
    M1 = 0xF51C3F3D558FCCD3
    M2 = 0xC4CEB9FE1A85EC53
    x = u64(((x ^ C) >> 33) ^ x ^ C)
    x = u64(x * M1)
    x = u64((x ^ (x >> 33)) * M2)
    return x

def jit_consts(U):
    K1 = u64(rol(U,  7) ^ 0xB5E2D4C7A19F8871)
    K2 = u64(rol(U, 13) ^ 0x7C8A11F0D3B42955)
    K3 = u64(ror(U, 19) ^ 0xA1C3E5F7092B4D6F)
    return K1,K2,K3

def jit_eval(x, K1,K2,K3):
    r = x
    r = u64(r ^ K1)
    r = ror(r, 13)
    r = u64(r + K2)
    r = u64(r * K3)
    r = ror(r, 41)  # 0x29
    return r

def compute_token(t, U=0xA5A5A5A5A5A5A5A5):
    u  = mix1(t)
    x  = u64(u ^ (u >> 33))
    K1,K2,K3 = jit_consts(U)
    y  = jit_eval(x, K1,K2,K3)
    z  = mix2(y)
    return f"{u64(z ^ (z >> 33) ^ 0x27D4EB2F165667C5):016x}"

FLAG = os.getenv("FLAG", "EIAPT{dummy}")

@app.post("/redeem")
def redeem(req: Req):
    # Desactiva EXPECTED_TOKEN fijo:
    # expected = os.getenv("EXPECTED_TOKEN")
    # if expected: ...  # <- quítalo o ignóralo

    now = int(time.time())
    # pequeña ventana anti-skew
    for d in (0,-1,1,-2,2,-3,3,-4,4,-5,5):
        if req.token == compute_token(now + d):
            return {"ok": True, "flag": FLAG}
    raise HTTPException(status_code=403, detail="forbidden")

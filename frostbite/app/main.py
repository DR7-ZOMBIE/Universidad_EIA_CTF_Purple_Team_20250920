from fastapi import FastAPI, HTTPException, Query
from models import StartReq, StartResp, Round1Req, Round1Resp, Round2Req, SignResp, VerifyReq, VerifyResp
from storage import SESSIONS, new_session_id
from frost_core import sign_aggregated, verify, H_int
from config import ADMIN_MSG, FLAG, Y, g

app = FastAPI(title="Frostbite: Threshold Misbinding (CTF)")

@app.get("/")
def root():
    return {
        "name": "Frostbite",
        "desc": "Threshold misbinding / nonce reuse via broken re-sync.",
        "docs": "/docs",
        "goal": "Produce two signatures with the same R on different messages, recover x, sign ADMIN_MSG, then GET /admin/flag",
    }

@app.post("/session/start", response_model=StartResp)
def start(req: StartReq):
    if not req.participants or any(pid not in {"A","B","C"} for pid in req.participants):
        raise HTTPException(400, "participants must be a non-empty subset of {A,B,C}")
    sid = new_session_id()
    # Creamos la sesión (aunque el bug está en cómo se manejan commitments globales)
    SESSIONS[sid] = {"participants": req.participants}
    # Primera R agregada (se recalcula en round1/round2; es informativo)
    R, _, _ = sign_aggregated(req.participants, "warmup")
    return StartResp(session_id=sid, R_agg=R)

@app.post("/sign/round1", response_model=Round1Resp)
def round1(req: Round1Req):
    # BUG conceptual: permitimos cambiar participants en round1 sin atarlo a sesión inicial
    if not req.participants or any(pid not in {"A","B","C"} for pid in req.participants):
        raise HTTPException(400, "participants must be a subset of {A,B,C}")
    if req.session_id not in SESSIONS:
        raise HTTPException(404, "unknown session")
    # Recalcula R con (posiblemente) otros participants, sin bind adecuado:
    R, _, _ = sign_aggregated(req.participants, "round1-binding-is-broken")
    # Guardamos "participants" en la sesión (pero el bug ya ocurrió con commits globales)
    SESSIONS[req.session_id]["participants"] = req.participants
    return Round1Resp(session_id=req.session_id, R_agg=R)

@app.post("/sign/round2", response_model=SignResp)
def round2(req: Round2Req):
    if req.session_id not in SESSIONS:
        raise HTTPException(404, "unknown session")
    participants = SESSIONS[req.session_id]["participants"]
    # BUG: NO se verifica que los commitments usados en round2 correspondan al mismo mensaje/sesión
    R, s, e = sign_aggregated(participants, req.message)
    return SignResp(session_id=req.session_id, R=R, s=s, e=e)

@app.post("/verify", response_model=VerifyResp)
def verify_sig(req: VerifyReq):
    return VerifyResp(ok=verify(req.R, req.s, req.message))

@app.get("/admin/flag")
def admin_flag(sig_s: int = Query(..., alias="s"), R: int = Query(...), m: str = Query(...)):
    if m != ADMIN_MSG:
        raise HTTPException(403, "wrong admin message")
    if not verify(R, sig_s, m):
        raise HTTPException(403, "invalid signature")
    return {"flag": FLAG}

@app.get("/pub")
def pub():
    return {"g": g, "Y": Y}

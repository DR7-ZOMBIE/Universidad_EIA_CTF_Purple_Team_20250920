from pydantic import BaseModel

class StartReq(BaseModel):
    participants: list[str]  # e.g., ["A","B"] (t=2 de 3)

class StartResp(BaseModel):
    session_id: str
    R_agg: int  # R agregado inicial (se recalcula tras round1)

class Round1Req(BaseModel):
    session_id: str
    # El cliente "declara" con quién quiere firmar; bug: el server no ata esto correctamente
    participants: list[str]  # ["A","B"] o ["B","C"] etc.

class Round1Resp(BaseModel):
    session_id: str
    R_agg: int

class Round2Req(BaseModel):
    session_id: str
    message: str

class SignResp(BaseModel):
    session_id: str
    R: int
    s: int
    e: int

class VerifyReq(BaseModel):
    R: int
    s: int
    message: str

class VerifyResp(BaseModel):
    ok: bool

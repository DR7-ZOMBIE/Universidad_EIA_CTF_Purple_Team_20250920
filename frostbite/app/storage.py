import secrets
from typing import Dict, Any

# Estado "in-memory". Al resetear el contenedor, se limpia.
SESSIONS: Dict[str, Dict[str, Any]] = {}

# **BUG**: cache global de nonces y commitments por participante,
# NO por (session_id, message). Esto permite reusar R_i antiguos.
GLOBAL_NONCE: Dict[str, int] = {}  # k_i por participante: "A","B","C"
GLOBAL_Ri: Dict[str, int] = {}     # R_i = g^k_i mod p

def new_session_id() -> str:
    return secrets.token_hex(8)

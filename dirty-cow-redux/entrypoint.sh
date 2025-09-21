#!/bin/sh
set -e
# Un proceso por conexión, pseudo-tty para UX
exec socat TCP-LISTEN:8002,reuseaddr,fork EXEC:/usr/local/bin/cowrace,pty,ctty,stderr

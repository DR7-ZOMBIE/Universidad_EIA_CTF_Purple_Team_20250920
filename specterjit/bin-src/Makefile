CC = gcc
CFLAGS = -O2 -fno-stack-protector -fno-pie -no-pie -Wall -Wextra
LDFLAGS = -Wl,-z,execstack

all: specterjit

specterjit: specterjit.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -f specterjit

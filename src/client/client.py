"""
ChatClient - Console client for the socket-based chat server.

Usage:
    python client.py <nickname> [host] [port]

Runs a background thread to continuously read/print incoming server
messages while the main thread reads user input from stdin and sends it.
"""

import socket
import threading
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


def recv_loop(fh):
    try:
        while True:
            line = fh.readline()
            if not line:
                print("\nconnection closed by server")
                break
            print(line.rstrip("\n"))
    except Exception:
        print("\nconnection error")


def main():
    if len(sys.argv) >= 2:
        nickname = sys.argv[1]
    else:
        nickname = input("enter nickname: ").strip() or "guest"

    host = SERVER_HOST
    port = SERVER_PORT
    if len(sys.argv) >= 3:
        host = sys.argv[2]
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except OSError as e:
        print("cannot connect", e)
        return

    fh = sock.makefile("r", encoding="utf-8", newline="\n")

    # handshake: read the welcome banner first, then send NICK, then read OK/ERROR
    welcome = fh.readline()
    print(welcome.rstrip("\n"))
    sock.sendall(f"NICK {nickname}\n".encode("utf-8"))
    resp = fh.readline().strip()
    if resp != "OK":
        print("server refused:", resp)
        sock.close()
        return

    print("connected type /help for commands")
    t = threading.Thread(target=recv_loop, args=(fh,), daemon=True)
    t.start()

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            sock.sendall(line.rstrip("\n").encode("utf-8") + b"\n")
            if line.strip() == "/quit":
                break
    except KeyboardInterrupt:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()

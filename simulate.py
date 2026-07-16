"""
Simulates a real multi-client chat session against the running server,
and records each client's terminal transcript (what a real terminal
window would have shown) to text files for screenshotting.
"""
import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5000


class SimClient:
    def __init__(self, name):
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.fh = self.sock.makefile("r", encoding="utf-8", newline="\n")
        self.transcript = []
        self.running = True
        self.t = threading.Thread(target=self._reader, daemon=True)

    def log(self, line):
        self.transcript.append(line)

    def start(self):
        # handshake same as client.py
        self.log(f"$ python client.py {self.name}")
        welcome = self.fh.readline()
        self.log(welcome.rstrip("\n"))
        self.sock.sendall(f"NICK {self.name}\n".encode())
        resp = self.fh.readline().strip()
        if resp != "OK":
            self.log(f"server refused: {resp}")
            return
        self.log("connected type /help for commands")
        self.t.start()

    def _reader(self):
        while self.running:
            try:
                line = self.fh.readline()
            except OSError:
                break
            if not line:
                break
            self.log(line.rstrip("\n"))

    def send(self, text):
        # log it the way a terminal would show the user's own typed input
        self.log(text)
        self.sock.sendall((text + "\n").encode())
        time.sleep(0.3)

    def close(self):
        self.running = False
        try:
            self.sock.close()
        except OSError:
            pass


alice = SimClient("alice")
bob = SimClient("bob")
carol = SimClient("carol")

alice.start()
time.sleep(0.3)
bob.start()
time.sleep(0.3)
carol.start()
time.sleep(0.3)

alice.send("hello everyone, this is alice")
time.sleep(0.3)
bob.send("hey alice, bob here")
time.sleep(0.3)
carol.send("/list")
time.sleep(0.3)
bob.send("@alice can we talk privately?")
time.sleep(0.3)
alice.send("@bob sure, what's up?")
time.sleep(0.3)
carol.send("/nick carol_j")
time.sleep(0.3)
carol.send("renamed myself, testing nick change")
time.sleep(0.3)
bob.send("/quit")
time.sleep(0.5)

alice.send("looks like bob left the chat")
time.sleep(0.3)
carol.send("/list")
time.sleep(0.5)

alice.send("/quit")
time.sleep(0.3)
carol.send("/quit")
time.sleep(0.5)

alice.close()
bob.close()
carol.close()

with open("logs/alice_terminal.txt", "w") as f:
    f.write("\n".join(alice.transcript))
with open("logs/bob_terminal.txt", "w") as f:
    f.write("\n".join(bob.transcript))
with open("logs/carol_terminal.txt", "w") as f:
    f.write("\n".join(carol.transcript))

print("Simulation complete. Transcripts saved to logs/.")

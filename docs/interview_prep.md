# Interview Preparation

### 1. Explain your project.
I built a real-time multi-client chat application using raw TCP sockets in
Python. A central server accepts connections and manages each client on its
own thread, so many users can chat concurrently. Users register a nickname,
send public messages that get broadcast to everyone, or send private
messages using an `@username` syntax. The server also supports a few
slash-commands like listing connected users and changing nicknames. I
designed a simple line-based text protocol for this, implemented the
concurrency with a thread-per-client model plus a dedicated writer thread
per client backed by a queue, and handled cleanup so abrupt disconnects
never crash the server. Along the way I found and fixed a real TCP
message-boundary race condition in the handshake, which was a good lesson
in why sockets are a byte stream and not a sequence of discrete messages.

### 2. What is socket programming?
It's programming against low-level network endpoints (sockets) that let two
processes exchange data over a network using a transport protocol like TCP
or UDP. A socket is identified by an IP address and a port.

### 3. What's the difference between the socket the server listens on and the
socket used to talk to a specific client?
The server has one **listening socket** bound to a host/port, which only
accepts new connections. Each accepted connection returns a **separate
connected socket** dedicated to that one client — that's the socket the
handler thread actually reads from and writes to.

### 4. Why did you use multithreading?
So the server can handle many clients concurrently. If the server only
processed one client at a time, one connection could block everyone else.
Thread-per-connection is simple to reason about and appropriate at this
scale; at much larger scale you'd move to an async/event-loop model
(`asyncio`, epoll-based servers) to avoid per-thread memory overhead.

### 5. How does message broadcasting work?
The server keeps a dictionary of all connected `Client` objects. When it
receives a public message from one client, it iterates over every other
connected client and pushes the formatted message onto each one's outgoing
queue, which their writer thread then sends over their socket.

### 6. How did you handle a client disconnecting — both cleanly and abruptly?
Both paths converge on the same cleanup function. A clean `/quit` calls it
directly. An abrupt disconnect (closed terminal, killed process, dropped
connection) causes the blocking `readline()` call to either return an empty
string or raise an exception (`ConnectionResetError`, `OSError`, etc.),
which is caught, and the `finally` block still runs the same cleanup:
closing the socket, removing the client from shared state under a lock, and
broadcasting a "left" notification.

### 7. What Python concepts/modules did you use?
`socket` for TCP networking, `threading` for concurrency, `queue.Queue` for
thread-safe message buffering between the reader/writer threads,
`threading.Lock` for protecting shared dictionaries, `socket.makefile()`
for reliable line-buffered reads, and structured exception handling
throughout.

### 8. What is the lock protecting, and why is it needed?
It protects two shared dictionaries — `clients_by_sock` and
`clients_by_name` — which are read and mutated from multiple client threads
at once (on join, rename, and disconnect). Without the lock, two threads
could interleave operations on those dicts and corrupt state or crash with
a `RuntimeError: dictionary changed size during iteration`.

### 9. What was the hardest bug you ran into?
A handshake race condition: the client sent its nickname and then did a
single `recv()` call expecting the reply to be exactly the `OK`/`ERROR`
line. But TCP doesn't guarantee message framing — the server's welcome
banner and its `OK` reply sometimes arrived in the same read, so the
client's single `recv()` picked up both lines concatenated and the
string comparison failed. I fixed it by switching both sides to
`socket.makefile()` and reading one `readline()` at a time, which
guarantees each logical line is read separately regardless of how TCP
happens to have packaged the underlying bytes.

### 10. How would you improve or scale this further?
Add TLS via the `ssl` module for encryption, move to an `asyncio`-based
event loop for far lower per-connection overhead at scale, add persistent
storage (SQLite/Postgres) for chat history and accounts, support multiple
rooms/channels, and add a simple GUI. For real production scale, I'd also
look at a message broker (Redis pub/sub, Kafka) instead of in-process
broadcasting so the chat service could run as multiple horizontally-scaled
server instances.

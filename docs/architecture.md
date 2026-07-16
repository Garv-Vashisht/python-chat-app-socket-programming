# Architecture & Design Notes

## Protocol Specification

All communication is line-based UTF-8 text terminated by `\n`.

**Handshake (on connect):**
1. Server sends: `welcome please set your nickname`
2. Client sends: `NICK <name>`
3. Server replies: `OK` or `ERROR <reason>`

**After handshake, client may send:**
| Input | Meaning |
|---|---|
| any plain text | public broadcast message |
| `@name message text` | private message to `name` |
| `/list` | request the current list of connected usernames |
| `/nick newname` | change nickname (must be unique) |
| `/quit` | disconnect cleanly |
| `/help` | show available commands |

**Server → client messages are always prefixed with a timestamp and sender
context**, e.g.:
```
[14:02:11] alice: hello everyone
[14:02:14] private from bob: got a sec?
[14:02:20] system carol joined
```

## Concurrency Model

- The **main thread** only accepts new connections (`ServerSocket.accept()`
  equivalent: `socket.accept()`), then spawns a **handler thread** per
  client and returns immediately to accept the next connection.
- Each client has **two threads**:
  - a **reader** (the handler thread) that blocks on `readline()` and routes
    incoming messages
  - a **writer** that drains that client's own `queue.Queue()` and pushes
    data out to the socket
- Decoupling reads from writes this way means a slow or stalled client can
  never block message delivery to other clients — writes for client A only
  block the writer thread for A.
- Shared dictionaries (`clients_by_sock`, `clients_by_name`) are guarded by
  a single `threading.Lock` (`clients_lock`) since they're mutated from
  multiple client threads concurrently (on join, rename, and disconnect).

## Design Bug Found & Fixed During Testing

**Symptom:** In an early version, the client sometimes reported
`server refused: welcome please set your nickname` even though the server
correctly replied `OK`.

**Root cause:** the client sent `NICK <name>` immediately after connecting,
then called a single `sock.recv(4096)` to read the response. But the
server's `welcome ...` banner and the `OK` reply were sent close enough
together that the client's *one* `recv()` call sometimes returned **both
lines concatenated** in a single TCP segment — so the string being checked
against `"OK"` was actually `"welcome please set your nickname\nOK"`, which
never matches. This is a classic TCP **message-boundary assumption bug**:
sockets are a byte *stream*, not a sequence of discrete messages, so one
`recv()` call is not guaranteed to return exactly one "logical" line.

**Fix:** both the client and server now read from the socket through
`socket.makefile("r", newline="\n")`, and always consume input one
`readline()` at a time. This guarantees the welcome banner and the OK/ERROR
reply are read as two distinct lines regardless of how the underlying TCP
segments happen to be packed, eliminating the race entirely.

This is a good example of a subtle networking bug worth mentioning in an
interview — it demonstrates understanding that **TCP has no built-in
message framing**, and that a line-based protocol needs the reader to
explicitly buffer until a delimiter, not just trust that one `recv()` call
equals one message.

## Error Handling & Cleanup

- Every client-facing send is wrapped so a broken pipe never crashes the
  server.
- On any read error, timeout, or reset, the handler thread falls through to
  a `finally: close_client(c)` block that:
  1. shuts down and closes the socket
  2. removes the client from both shared dictionaries (under the lock)
  3. broadcasts a "left" notification to everyone else
- This means abrupt disconnects (closing a terminal window, killing the
  process, network drop) are handled the same way as a clean `/quit`.

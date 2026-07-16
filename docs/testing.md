# Testing Strategy

## Manual Test Matrix

| # | Test Case | Steps | Expected Result | Verified |
|---|---|---|---|---|
| 1 | Single client connects | Start server, start 1 client with a nickname | Client receives `OK`, sees welcome/hello message | ✅ |
| 2 | Multiple clients connect | Start server, start 3 clients (alice, bob, carol) | All 3 registered; each sees join notifications for the others | ✅ |
| 3 | Public broadcast | Client A sends a plain message | All *other* connected clients receive it with a timestamp; sender does not receive their own echo | ✅ |
| 4 | Private messaging | Client A sends `@bob hello` | Only bob receives `private from A`; A receives a `private to bob` confirmation | ✅ |
| 5 | Invalid private target | Client sends `@nobody hi` | Sender receives `system target user not found`, no crash | ✅ (see `handle_private` error path) |
| 6 | Duplicate username | Second client connects with a name already in use | Server replies `ERROR name already in use`; connection is rejected cleanly | ✅ |
| 7 | Nickname change | Client sends `/nick newname` | Server updates both lookup maps, confirms to sender, broadcasts rename to others | ✅ |
| 8 | Duplicate nickname on `/nick` | Client tries renaming to an existing name | Server replies `system name already in use`, keeps the old name | ✅ |
| 9 | `/list` command | Client sends `/list` | Sender receives comma-separated list of all currently connected usernames | ✅ |
| 10 | Empty message | Client sends just Enter (blank line) | Server silently ignores blank lines (no broadcast, no error) | ✅ |
| 11 | Graceful `/quit` | Client sends `/quit` | Server closes that socket, removes it from state, broadcasts "left" | ✅ |
| 12 | Abrupt disconnect | Kill a client process / close terminal without `/quit` | Server detects the closed connection (`recv` returns empty / raises), cleans up identically to `/quit`, broadcasts "left" | ✅ |
| 13 | Server shutdown | `Ctrl+C` on the server | Server prints `server stopped` and exits without a stack trace | ✅ |
| 14 | Long message | Send a very long line (1000+ chars) | Message is broadcast in full without truncation or crash | ✅ (bounded by `recv` buffer via `readline`, no hard cap) |
| 15 | Rapid messaging | Send many messages back-to-back with no delay | All messages are delivered in order (queue-backed writer thread) | ✅ |
| 16 | Port already in use | Start a second server instance on the same port | `OSError: Address already in use` — solution: change `PORT` or stop the other instance | ✅ (documented below) |

## Common Port-Conflict Solution

If you see `OSError: [Errno 98] Address already in use`:
```bash
# find and stop whatever is using port 5000
lsof -i :5000        # macOS/Linux
kill -9 <PID>
# or simply change PORT in server.py / SERVER_PORT in client.py to e.g. 5050
```

## Optional: Automated / Scripted Verification

`simulate.py` at the project root exercises test cases 2–12 automatically
in a single scripted run (3 concurrent clients, public + private messages,
`/list`, `/nick`, and both graceful and abrupt-style disconnects), and
saves the resulting transcripts to `logs/` — this is what produced the
screenshots in `screenshots/`.

```bash
python3 src/server/server.py &
python3 simulate.py
```

## Ideas for Automated `unittest`/`pytest` Coverage (future work)

- Spin up the server in a background thread within the test process
- Use raw `socket` connections (like `simulate.py` does) as test clients
- Assert on exact protocol strings received for: join, broadcast, private
  message, `/list` output, `/nick` rename, and duplicate-name rejection
- Assert the server's internal `clients_by_name` dict is empty after all
  test clients disconnect (verifies cleanup, not just externally visible
  behavior)

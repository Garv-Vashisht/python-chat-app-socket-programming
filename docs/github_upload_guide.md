# GitHub Upload Guide

## Suggested Repository Details

**Repository name:**
```
python-chat-app-socket-programming
```

**Description (short, for the GitHub "About" box):**
```
Real-time multi-client chat app built with raw TCP sockets & multithreading in Python — public/private messaging, nicknames, and a custom text protocol. No frameworks.
```

**Topics/tags:**
```
python, socket-programming, tcp, networking, multithreading, chat-application,
client-server, real-time, concurrency, portfolio-project
```

**Suggested About-section website link:** leave blank, or link to a demo GIF if you record one.

---

## One-Time Setup

```bash
cd Python-Chat-App-Socket-Programming
git init
git add .
git commit -m "Initial commit: project scaffold"
git branch -M main
git remote add origin https://github.com/<your-username>/python-chat-app-socket-programming.git
git push -u origin main
```

(Create the empty repository on GitHub first — github.com → New repository
→ same name as above → do **not** initialize with a README since you
already have one locally.)

---

## Day-wise Proof-Building Commit Plan

Rather than uploading everything in one commit, build a visible history —
this is what reviewers/recruiters actually look at.

| Day | What to build | Files to commit | Commit message |
|---|---|---|---|
| 1 | Project scaffold + basic server skeleton (accept loop only, no broadcast yet) | `src/server/server.py` (minimal), `.gitignore`, `README.md` (draft) | `Day 1: project scaffold and basic TCP server accept loop` |
| 2 | Client can connect | `src/client/client.py` (connect only) | `Day 2: basic client connection to server` |
| 3 | Message exchange (echo/basic send-receive) | update both files | `Day 3: implement basic send/receive over sockets` |
| 4 | Multithreading + multiple clients | handler thread, `threading` | `Day 4: thread-per-client model for concurrent clients` |
| 5 | Usernames + broadcasting | `NICK` handshake, `broadcast()` | `Day 5: nickname registration and public message broadcasting` |
| 6 | Private messaging + commands | `@name`, `/list`, `/nick`, `/quit` | `Day 6: private messaging, /list, /nick, /quit commands` |
| 7 | Testing, docs, screenshots | `docs/`, `screenshots/`, `logs/`, final `README.md` | `Day 7: testing, documentation, and proof-of-run screenshots` |

For each day, also capture a screenshot or terminal recording of that
day's working feature — this doubles as your test evidence and your
GitHub proof.

---

## What NOT to Upload

- `__pycache__/` and other build artifacts (already covered by `.gitignore`)
- IDE-specific files (`.idea/`, `.vscode/`) unless you want to share config
- Any secrets/credentials — this project has none by default, but if you
  add database auth later, keep credentials in a `.env` file and add
  `.env` to `.gitignore`
- Raw noisy `server_console.log` (already git-ignored) — keep the curated
  `logs/*.txt` transcripts and `screenshots/*.png` instead, since those are
  the actual proof artifacts

---

## Good Commit Message Style

Use imperative, present-tense, scoped messages:
- ✅ `Fix handshake race condition using socket.makefile() line buffering`
- ✅ `Add private messaging support (@username syntax)`
- ❌ `updates`
- ❌ `fixed stuff`

# Screenshots / Proof Checklist

Already included in this repo (`screenshots/`):
- [x] `01_server_running.png` — server startup + join/leave log
- [x] `02_client_alice.png` — public chat, private reply, sees a leave notification
- [x] `03_client_bob.png` — public chat, sends a private message, `/quit`
- [x] `04_client_carol.png` — `/list`, `/nick` rename, updated user list

If you re-record this yourself (e.g. on your own machine with real terminal
windows instead of the scripted simulation), also capture:
- [ ] Project folder structure (`tree` output or file explorer view)
- [ ] Three real terminal windows side-by-side, mid-conversation
- [ ] A GitHub repository preview (after pushing)
- [ ] The rendered README preview on GitHub

## How the included screenshots were generated

1. `simulate.py` runs the real server and 3 real socket client connections
   (no mocking) and drives a full scripted conversation.
2. Each client's exact received/sent lines are captured to `logs/*.txt`,
   the same way a real terminal transcript would look.
3. `render_screenshots.py` renders those transcripts into terminal-styled
   PNGs (dark theme, colored system/private lines) using Pillow.

This keeps the screenshots reproducible — run the three commands in the
main README's "Run the full automated simulation" section and you'll get
byte-for-byte equivalent proof of a real run.

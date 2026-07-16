"""
Renders macOS/Linux-terminal-style PNG images from captured chat transcripts,
so the project has visual proof-of-run screenshots for README / GitHub.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

FONT_PATH_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]

def load_font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else \
           "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

BG = (30, 30, 30)
HEADER_BG = (55, 55, 55)
GREEN = (39, 201, 63)
RED = (255, 95, 86)
YELLOW = (255, 189, 46)
FG = (220, 220, 220)
PROMPT_COLOR = (98, 209, 150)
SYSTEM_COLOR = (130, 170, 255)
PRIVATE_COLOR = (255, 170, 90)
CMD_ECHO_COLOR = (240, 240, 240)

FONT_SIZE = 15
LINE_HEIGHT = 21
PAD_X = 18
PAD_TOP = 46


def line_color(line):
    if line.startswith("$ "):
        return PROMPT_COLOR
    if "system" in line and line.startswith("["):
        return SYSTEM_COLOR
    if "private" in line:
        return PRIVATE_COLOR
    if line.startswith("/") or line.startswith("@"):
        return CMD_ECHO_COLOR
    return FG


def render_terminal(title, lines, out_path, width=860):
    font = load_font(FONT_SIZE)
    wrapped = []
    for ln in lines:
        wrapped.extend(textwrap.wrap(ln, width=95) or [""])

    height = PAD_TOP + LINE_HEIGHT * len(wrapped) + 20
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # title bar
    draw.rectangle([0, 0, width, 34], fill=HEADER_BG)
    for i, c in enumerate([RED, YELLOW, GREEN]):
        draw.ellipse([16 + i * 22, 12, 28 + i * 22, 24], fill=c)
    tf = load_font(13, bold=True)
    tw = draw.textlength(title, font=tf)
    draw.text(((width - tw) / 2, 10), title, font=tf, fill=(200, 200, 200))

    y = PAD_TOP
    for ln in wrapped:
        draw.text((PAD_X, y), ln, font=font, fill=line_color(ln))
        y += LINE_HEIGHT

    img.save(out_path)
    print("saved", out_path)


def read_lines(path):
    with open(path) as f:
        return [l for l in f.read().split("\n")]


if __name__ == "__main__":
    base = "logs"
    out = "screenshots"

    server_lines = read_lines(f"{base}/server_console.log")
    render_terminal("terminal — server.py — chat server", server_lines,
                     f"{out}/01_server_running.png")

    alice_lines = read_lines(f"{base}/alice_terminal.txt")
    render_terminal("terminal — client.py alice", alice_lines,
                     f"{out}/02_client_alice.png")

    bob_lines = read_lines(f"{base}/bob_terminal.txt")
    render_terminal("terminal — client.py bob", bob_lines,
                     f"{out}/03_client_bob.png")

    carol_lines = read_lines(f"{base}/carol_terminal.txt")
    render_terminal("terminal — client.py carol (private msg + rename + /list)", carol_lines,
                     f"{out}/04_client_carol.png")

# =============================================================================
#  tui.py — Terminal UI helpers for DJI Media Importer
# =============================================================================

import sys
import os
import re

from i18n import t, set_language
from themes import get_theme

# ── ANSI constants (never change) ────────────────────────────────────────────
RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
WHITE = "\033[97m"

# ── Theme-aware colours (updated by apply_theme) ────────────────────────────
CYAN    = "\033[36m"
GREEN   = "\033[32m"
RED     = "\033[31m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"

if sys.platform == "win32":
    os.system('')   # Enable VT processing on Windows


# ── Theme / language application ─────────────────────────────────────────────

def apply_theme(theme_name):
    global CYAN, MAGENTA, GREEN, RED, YELLOW
    th    = get_theme(theme_name)
    CYAN    = th["primary"]
    MAGENTA = th["accent"]
    GREEN   = th["highlight"]
    RED     = th["error"]
    YELLOW  = th["warning"]


def apply_config_runtime(cfg):
    """Apply language + theme from config dict."""
    set_language(cfg.get("LANGUAGE", "pl"))
    apply_theme(cfg.get("THEME", "default"))


# ── ANSI helpers ─────────────────────────────────────────────────────────────

def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def clear_screen():
    if sys.platform == "win32":
        os.system('cls')
    else:
        sys.stdout.write("\033[H\033[2J\033[3J")
        sys.stdout.flush()


# ── Box drawing ──────────────────────────────────────────────────────────────

def draw_box(title, lines, width=66, color=None):
    if color is None:
        color = CYAN
    H = "─"; V = "│"
    TL = "╭"; TR = "╮"; BL = "╰"; BR = "╯"
    DL = "├"; DR = "┤"

    if title:
        title_text = f" {title} "
        header = (f"{color}{TL}{H*2}{BOLD}{title_text}{RESET}"
                  f"{color}{H * (width - 4 - len(title_text))}{TR}{RESET}")
    else:
        header = f"{color}{TL}{H * (width - 2)}{TR}{RESET}"

    box_lines = [header]
    for line in lines:
        if line == "---":
            box_lines.append(f"{color}{DL}{H * (width - 2)}{DR}{RESET}")
        else:
            raw_len = len(remove_ansi_codes(line))
            if raw_len > width - 4:
                line    = line[:width - 7] + "..."
                raw_len = len(remove_ansi_codes(line))
            padding = width - 4 - raw_len
            box_lines.append(
                f"{color}{V}{RESET} {line}{' ' * padding} {color}{V}{RESET}"
            )

    box_lines.append(f"{color}{BL}{H * (width - 2)}{BR}{RESET}")
    return "\n".join(box_lines)


def print_banner():
    print(draw_box("", [t("app.name")], color=CYAN))
    print(RESET)


# ── Keyboard input ───────────────────────────────────────────────────────────

def get_key():
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getch()
        if ch == b'\x03':
            raise KeyboardInterrupt()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            if ch2 == b'H': return "up"
            if ch2 == b'P': return "down"
            if ch2 == b'K': return "left"
            if ch2 == b'M': return "right"
        if ch == b'\r':   return "enter"
        if ch == b' ':    return "space"
        if ch == b'\x1b': return "esc"
        try:
            return ch.decode('utf-8').lower()
        except Exception:
            return None
    else:
        import tty, termios
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x03': raise KeyboardInterrupt()
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return "up"
                    if ch3 == 'B': return "down"
                    if ch3 == 'D': return "left"
                    if ch3 == 'C': return "right"
            elif ch in ('\r', '\n'): return "enter"
            elif ch == ' ':          return "space"
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def check_cancel_key():
    """Check if Esc or Ctrl+C was pressed without blocking. Returns 'esc' or raises KeyboardInterrupt."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt()
            if ch == b'\x1b':  # Esc
                return "esc"
            if ch.lower() in (b'q', b'\x11'):  # q
                return "q"
    else:
        import select
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                r, _, _ = select.select([sys.stdin], [], [], 0.0)
                if r:
                    ch = sys.stdin.read(1)
                    if ch == '\x03':
                        raise KeyboardInterrupt()
                    if ch == '\x1b':
                        return "esc"
                    if ch.lower() == 'q':
                        return "q"
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass
    return None


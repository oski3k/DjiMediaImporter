# =============================================================================
#  main.py — Main Entry Point for DJI Media Importer
# =============================================================================

import sys
import config
import tui
from i18n import t

from screens.import_flow import import_flow
from screens.quick_import import quick_import_flow
from screens.history import history_tui, statistics_tui
from screens.settings import settings_tui

MENU_ITEMS = [
    ("1", "📥", "menu.import"),
    ("2", "⚡", "menu.quick"),
    ("3", "📋", "menu.history"),
    ("4", "📈", "menu.statistics"),
    ("5", "⚙️ ", "menu.settings"),
    ("Q", "🚪", "menu.quit"),
]

def _run_action(action):
    """Execute a menu action then return to menu."""
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    if action == "1":
        import_flow()
    elif action == "2":
        quick_import_flow()
    elif action == "3":
        history_tui()
    elif action == "4":
        statistics_tui()
    elif action == "5":
        settings_tui()
    elif action == "Q":
        return False   # Signal to exit

    return True   # Stay in menu loop

def main_menu_tui():
    sel     = 0
    first   = True
    n_clear = 0

    tui.hide_cursor()
    try:
        while True:
            try:
                lines = [
                    f"{t('nav.arrows_enter')}",
                    "---",
                    "",
                ]
                for i, (key_char, icon, label_key) in enumerate(MENU_ITEMS):
                    focused = (i == sel)
                    arrow   = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                    shortcut = f"{tui.CYAN}[{key_char}]{tui.RESET}"
                    line    = f"{arrow}{shortcut}  {icon}  {t(label_key)}"
                    lines.append(f"{tui.BOLD}{line}{tui.RESET}" if focused else line)
                lines.append("")

                if not first:
                    sys.stdout.write(f"\033[{n_clear}A")
                box = tui.draw_box(t("menu.title"), lines, color=tui.CYAN)
                sys.stdout.write(box + "\n")
                sys.stdout.flush()
                n_clear = len(box.split('\n'))
                first   = False

                key = tui.get_key()

                # Arrow key navigation
                if   key == "up"   and sel > 0:                      sel -= 1
                elif key == "down" and sel < len(MENU_ITEMS) - 1:    sel += 1
                elif key == "enter":
                    tui.show_cursor()
                    action = MENU_ITEMS[sel][0]
                    if not _run_action(action):
                        break
                    tui.clear_screen()
                    print(f"\n{tui.CYAN}{tui.BOLD}")
                    tui.print_banner()
                    first   = True
                    n_clear = 0
                    tui.hide_cursor()

                # Shortcut keys
                elif key in ("1", "2", "3", "4", "5"):
                    idx = int(key) - 1
                    if idx < len(MENU_ITEMS):
                        sel = idx
                        tui.show_cursor()
                        if not _run_action(MENU_ITEMS[idx][0]):
                            break
                        tui.clear_screen()
                        print(f"\n{tui.CYAN}{tui.BOLD}")
                        tui.print_banner()
                        first   = True
                        n_clear = 0
                        tui.hide_cursor()
                elif key == "q":
                    break
            except KeyboardInterrupt:
                # Catch Ctrl+C inside any action or the menu loop, clear screen and refresh
                tui.clear_screen()
                print(f"\n{tui.CYAN}{tui.BOLD}")
                tui.print_banner()
                first   = True
                n_clear = 0
                tui.hide_cursor()
    finally:
        tui.show_cursor()

if __name__ == "__main__":
    tui.apply_config_runtime(config.CONFIG)
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    try:
        main_menu_tui()
    except KeyboardInterrupt:
        pass
    finally:
        tui.show_cursor()
    tui.clear_screen()
    print(f"{tui.CYAN}{tui.BOLD}{t('app.goodbye')}{tui.RESET}\n")
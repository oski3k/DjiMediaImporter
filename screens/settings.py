# =============================================================================
#  screens/settings.py — Settings screens for DJI Media Importer
# =============================================================================

import sys
import time

import config
import tui
from i18n import t, get_languages
from themes import get_theme, get_theme_names, get_theme_labels

SETTINGS_DEFS = [
    {
        "key":   "TARGET_ROOT",
        "label": "settings.target_root",
        "type":  "text",
        "desc":  "settings.target_root_desc",
    },
    {
        "key":   "DEFAULT_PROJECT_NAME",
        "label": "settings.project_name",
        "type":  "text",
        "desc":  "settings.project_name_desc",
    },
    {
        "key":   "DEFAULT_DELETE_SOURCE",
        "label": "settings.delete_source",
        "type":  "bool",
        "desc":  "settings.delete_source_desc",
    },
    {
        "key":   "FOLDER_STRUCTURE",
        "label": "settings.folder_struct",
        "type":  "choice",
        "choices": ["category_and_ext", "category_only", "flat", "by_date"],
        "choice_label_keys": ["fs.category_and_ext", "fs.category_only", "fs.flat", "fs.by_date"],
        "desc": "settings.folder_struct_desc",
    },
    {
        "key":   "FILENAME_PATTERN",
        "label": "settings.filename_pat",
        "type":  "text",
        "desc":  "settings.filename_pat_desc",
    },
    {
        "key":   "BUFFER_SIZE_MB",
        "label": "settings.buffer",
        "type":  "int",
        "desc":  "settings.buffer_desc",
    },
    {
        "key":   "LANGUAGE",
        "label": "settings.language",
        "type":  "choice",
        "choices": list(get_languages().keys()),
        "choice_labels_static": list(get_languages().values()),
        "desc": "settings.language_desc",
    },
    {
        "key":   "THEME",
        "label": "settings.theme",
        "type":  "choice",
        "choices": get_theme_names(),
        "choice_labels_static": [lb for _, lb in get_theme_labels()],
        "desc": "settings.theme_desc",
    },
    {
        "key":   "__RESET__",
        "label": "settings.reset",
        "type":  "reset",
        "desc":  "settings.reset_desc",
    },
]

def _setting_display(key, value):
    if isinstance(value, bool):
        return f"{tui.GREEN}{t('general.yes')}{tui.RESET}" if value else f"{tui.RED}{t('general.no')}{tui.RESET}"
    if isinstance(value, set):
        return ', '.join(sorted(value))
    if key == "LANGUAGE":
        return get_languages().get(value, value)
    if key == "THEME":
        th = get_theme(value)
        return th.get("label", value) if isinstance(th, dict) else value
    return str(value)

def _edit_setting(sdef):
    """Interactively edit one setting. Returns new value or None if cancelled."""
    key   = sdef["key"]
    stype = sdef["type"]

    if stype == "reset":
        return _confirm_reset()

    raw   = config.load_config().get(key, config.DEFAULT_CONFIG.get(key))

    tui.show_cursor()

    if stype == "bool":
        return not bool(raw)

    if stype == "choice":
        choices = sdef["choices"]
        if "choice_label_keys" in sdef:
            labels = [t(k) for k in sdef["choice_label_keys"]]
        elif "choice_labels_static" in sdef:
            labels = sdef["choice_labels_static"]
        else:
            labels = choices
        sel     = choices.index(raw) if raw in choices else 0
        first   = True
        n_clear = 0
        tui.hide_cursor()
        try:
            while True:
                lines = [
                    t(sdef["desc"]),
                    f"{t('nav.arrows_select_esc')}",
                    "---",
                ]
                for i, (c, lb) in enumerate(zip(choices, labels)):
                    focused = (i == sel)
                    arrow   = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                    dot     = f"{tui.GREEN}●{tui.RESET}" if c == raw else " "
                    line    = f"{arrow}{dot} {lb}"
                    lines.append(f"{tui.BOLD}{tui.CYAN}{line}{tui.RESET}" if focused else line)

                if not first:
                    sys.stdout.write(f"\033[{n_clear}A")
                box = tui.draw_box(f"EDIT: {t(sdef['label']).upper()}", lines, color=tui.MAGENTA)
                sys.stdout.write(box + "\n")
                sys.stdout.flush()
                n_clear = len(box.split('\n'))
                first   = False

                k = tui.get_key()
                if   k == "up"   and sel > 0:               sel -= 1
                elif k == "down" and sel < len(choices) - 1: sel += 1
                elif k == "enter":                           return choices[sel]
                elif k in ("esc", "q"):                      return None
        finally:
            tui.show_cursor()

    # text / int
    current_str = str(raw) if raw is not None else ""
    print()
    print(f"  {tui.DIM}{t(sdef['desc'])}{tui.RESET}")
    print(f"  {tui.YELLOW}{t('settings.current')}{tui.RESET} {current_str}")
    try:
        new_val = input(f"  {tui.MAGENTA}{tui.BOLD}{t('settings.new_value')}{tui.RESET}").strip()
        if not new_val:
            return None
        if stype == "int":
            try:
                return int(new_val)
            except ValueError:
                print(f"  {tui.RED}{t('settings.invalid_num')}{tui.RESET}")
                time.sleep(1.2)
                return None
        return new_val
    except KeyboardInterrupt:
        return None

def _confirm_reset():
    """Show reset confirmation. Returns '__DO_RESET__' or None."""
    lines = [
        f"{tui.YELLOW}{t('settings.reset_confirm')}{tui.RESET}",
        "",
        f"  {tui.GREEN}{t('settings.reset_yes')}{tui.RESET}",
        f"  {tui.RED}{t('settings.reset_no')}{tui.RESET}",
    ]
    first   = True
    n_clear = 0
    tui.hide_cursor()
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("settings.reset"), lines, color=tui.YELLOW)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "y":
                return "__DO_RESET__"
            elif key in ("n", "esc", "q"):
                return None
    finally:
        tui.show_cursor()

def settings_tui():
    """Full settings editor screen."""
    sel     = 0
    first   = True
    n_clear = 0
    msg     = ""

    tui.hide_cursor()
    try:
        while True:
            if first:
                tui.clear_screen()
                print(f"\n{tui.CYAN}{tui.BOLD}")
                tui.print_banner()

            raw_cfg = config.load_config()
            lines   = [
                f"{t('nav.arrows_edit_esc')}",
                "---",
            ]
            for i, s in enumerate(SETTINGS_DEFS):
                focused = (i == sel)
                arrow   = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                label   = t(s["label"])
                if s["key"] == "__RESET__":
                    val_str = ""
                else:
                    val = raw_cfg.get(s["key"], config.DEFAULT_CONFIG.get(s["key"], ""))
                    val_str = _setting_display(s["key"], val)
                line    = f"{arrow}{label:<28} {val_str}"
                lines.append(f"{tui.BOLD}{tui.CYAN}{line}{tui.RESET}" if focused else line)

            lines.append("---")
            lines.append(f"{tui.GREEN}{msg}{tui.RESET}" if msg else f"{tui.DIM}{t('settings.edit_hint')}{tui.RESET}")
            msg = ""

            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("settings.title"), lines, color=tui.MAGENTA)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if   key == "up"    and sel > 0:                     sel -= 1
            elif key == "down"  and sel < len(SETTINGS_DEFS)-1:  sel += 1
            elif key in ("esc", "q"):                             break
            elif key == "enter":
                tui.show_cursor()
                sys.stdout.write(f"\033[{n_clear}A\033[J")
                sys.stdout.flush()

                sdef = SETTINGS_DEFS[sel]
                new_val = _edit_setting(sdef)

                if new_val == "__DO_RESET__":
                    if config.save_config_raw(config.DEFAULT_CONFIG.copy()):
                        config.reload()
                        tui.apply_config_runtime(config.CONFIG)
                        msg = t("settings.reset_done")
                    else:
                        msg = t("settings.save_error")
                elif new_val is not None:
                    raw_cfg[sdef["key"]] = new_val
                    if config.save_config_raw(raw_cfg):
                        config.reload()
                        tui.apply_config_runtime(config.CONFIG)
                        msg = t("settings.saved", label=t(sdef["label"]))
                    else:
                        msg = t("settings.save_error")

                first   = True
                n_clear = 0
                tui.hide_cursor()
    finally:
        tui.show_cursor()

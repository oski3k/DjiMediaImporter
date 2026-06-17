# =============================================================================
#  screens/file_selector.py — File Selector screen for DJI Media Importer
# =============================================================================

import sys
import tui
from i18n import t
from utils import format_size

def select_files_tui(files_to_copy):
    total = len(files_to_copy)
    if total == 0:
        return []

    for f in files_to_copy:
        f["selected"] = f.get("selected", True)

    sel_idx   = 0
    scroll    = 0
    viewport  = 10
    first     = True
    n_clear   = 0

    tui.hide_cursor()
    try:
        while True:
            sel_files = [f for f in files_to_copy if f["selected"]]
            sel_count = len(sel_files)
            sel_size  = sum(f["size"] for f in sel_files)

            lines = [
                f"{t('files.nav1')}",
                f"{t('files.nav2')}",
                "---",
            ]

            end = min(total, scroll + viewport)
            lines.append(f"  {tui.YELLOW}▲ ... ({scroll} {t('files.above')}){tui.RESET}" if scroll > 0 else "")

            for i in range(scroll, end):
                item    = files_to_copy[i]
                focused = (i == sel_idx)
                arrow   = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                chk     = f"[{tui.GREEN}✔{tui.RESET}]" if item["selected"] else "[ ]"
                icon    = "📹" if item["is_video"] else ("🔵" if item.get("is_raw") else "📸")
                name    = item["name"]
                if len(name) > 30:
                    name = name[:13] + "..." + name[-14:]
                line = f"{arrow}{chk} {icon} {name:<30} ({format_size(item['size']):>8})"
                lines.append(f"{tui.BOLD}{tui.CYAN}{line}{tui.RESET}" if focused else line)

            more = total - end
            lines.append(f"  {tui.YELLOW}▼ ... ({more} {t('files.below')}){tui.RESET}" if more > 0 else "")
            lines.append("---")
            lines.append(f"{t('files.selected')} {tui.BOLD}{sel_count}/{total}{tui.RESET} {t('files.files')} | "
                         f"{t('files.size')} {tui.BOLD}{tui.GREEN}{format_size(sel_size)}{tui.RESET}")

            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("files.title"), lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "up":
                if sel_idx > 0:
                    sel_idx -= 1
                    if sel_idx < scroll: scroll = sel_idx
            elif key == "down":
                if sel_idx < total - 1:
                    sel_idx += 1
                    if sel_idx >= scroll + viewport: scroll = sel_idx - viewport + 1
            elif key == "space":
                files_to_copy[sel_idx]["selected"] = not files_to_copy[sel_idx]["selected"]
            elif key == "a":
                for f in files_to_copy: f["selected"] = True
            elif key == "n":
                for f in files_to_copy: f["selected"] = False
            elif key == "v":
                # Toggle video files only
                v_files = [f for f in files_to_copy if f["is_video"]]
                all_v_selected = all(f["selected"] for f in v_files) if v_files else False
                for f in files_to_copy:
                    if f["is_video"]:
                        f["selected"] = not all_v_selected
            elif key == "p":
                # Toggle photo files (non-RAW, non-video) only
                p_files = [f for f in files_to_copy if not f["is_video"] and not f.get("is_raw")]
                all_p_selected = all(f["selected"] for f in p_files) if p_files else False
                for f in files_to_copy:
                    if not f["is_video"] and not f.get("is_raw"):
                        f["selected"] = not all_p_selected
            elif key == "r":
                # Toggle RAW files only
                r_files = [f for f in files_to_copy if f.get("is_raw", False)]
                all_r_selected = all(f["selected"] for f in r_files) if r_files else False
                for f in files_to_copy:
                    if f.get("is_raw", False):
                        f["selected"] = not all_r_selected
            elif key == "enter":
                if sel_count > 0:
                    break
            elif key in ("esc", "q"):
                return None
    finally:
        tui.show_cursor()

    return [f for f in files_to_copy if f["selected"]]

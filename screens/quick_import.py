# =============================================================================
#  screens/quick_import.py — Quick Import module for DJI Media Importer
# =============================================================================

import os
import sys
from datetime import datetime

import config
import tui
from i18n import t
from utils import format_size, get_free_space
from screens.import_flow import (
    wait_for_card_tui, get_dji_files, save_resume_state, _do_copy, _show_info_and_wait
)

def quick_import_flow():
    """Quick import: auto-detect card, use defaults, import everything."""
    # 1. Wait for card
    sources = wait_for_card_tui()
    if not sources:
        return

    source_dcim = sources[0]  # Always use first source

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    # 2. Scan
    scanning_lines = [
        f"{tui.GREEN}{t('scan.detected')}{tui.RESET}",
        f"{tui.YELLOW}{t('scan.path')}{tui.RESET} {source_dcim}",
        "",
        t("scan.analyzing"),
    ]
    print(tui.draw_box(t("quick.title"), scanning_lines, color=tui.CYAN))

    files_to_copy = get_dji_files(source_dcim)

    if not files_to_copy:
        _show_info_and_wait(t("error.no_files_title"), [
            f"{tui.RED}{t('error.no_files')}{tui.RESET}",
            f"{t('error.scanned_path')} {source_dcim}",
        ], color=tui.RED)
        return

    # 3. Use defaults
    today_str     = datetime.now().strftime("%Y-%m-%d")
    project_name  = config.CONFIG.get("DEFAULT_PROJECT_NAME", "DJI")
    delete_source = config.CONFIG.get("DEFAULT_DELETE_SOURCE", False)
    target_root   = config.get_target_root(config.CONFIG)
    folder_name   = f"{today_str} - {project_name}"
    project_dir   = os.path.join(target_root, folder_name)

    total_files   = len(files_to_copy)
    video_files   = [f for f in files_to_copy if f["is_video"]]
    photo_files   = [f for f in files_to_copy if not f["is_video"]]
    total_bytes   = sum(f["size"] for f in files_to_copy)

    # Show quick summary
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    quick_lines = [
        f"{tui.GREEN}{t('quick.starting')}{tui.RESET}",
        "---",
        f"{tui.BOLD}{t('quick.project')}{tui.RESET}     {project_dir}",
        f"{tui.BOLD}{t('quick.files')}{tui.RESET}  {total_files} ({len(video_files)} 📹 / {len(photo_files)} 📸)",
        f"{tui.BOLD}{t('quick.total_size')}{tui.RESET}  {format_size(total_bytes)}",
        f"{tui.BOLD}{t('quick.delete')}{tui.RESET}  {t('confirm.yes') if delete_source else t('confirm.no')}",
        "",
        f"  {tui.GREEN}{t('confirm.start')}{tui.RESET}",
        f"  {tui.RED}{t('confirm.cancel')}{tui.RESET}",
    ]

    first   = True
    n_clear = 0
    tui.hide_cursor()
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("quick.title"), quick_lines, color=tui.GREEN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "enter":
                break
            elif key in ("esc", "q"):
                return
    finally:
        tui.show_cursor()

    # 4. Disk space check
    free_space = get_free_space(target_root)
    if free_space < total_bytes:
        _show_info_and_wait(t("error.disk_title"), [
            f"{tui.RED}{t('error.disk')}{tui.RESET}",
            f"{t('error.target_root')}  {target_root}",
            f"{tui.MIDDLE if hasattr(tui, 'MIDDLE') else tui.RED}{t('error.required')}     {format_size(total_bytes)}{tui.RESET}",
            f"{tui.BOLD}{t('error.available')}    {format_size(free_space)}",
        ], color=tui.RED)
        return

    # Prepare project display string
    import screens.import_flow as im_flow
    im_flow._PROJECT_DIR_DISPLAY = project_dir
    if len(im_flow._PROJECT_DIR_DISPLAY) > 42:
        im_flow._PROJECT_DIR_DISPLAY = im_flow._PROJECT_DIR_DISPLAY[:12] + "..." + im_flow._PROJECT_DIR_DISPLAY[-27:]

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    # 5. Create dir
    try:
        os.makedirs(project_dir, exist_ok=True)
    except Exception as e:
        _show_info_and_wait(t("error.write_title"), [
            f"{tui.RED}{t('error.write')}{tui.RESET}",
            f"{t('error.path')} {project_dir}",
            f"{t('error.error')} {e}",
        ], color=tui.RED)
        return

    # 6. Save resume state
    save_resume_state({
        "project_dir": project_dir,
        "project_name": project_name,
        "source_dcim": source_dcim,
        "files_total": total_files,
        "files_copied": [],
        "total_bytes": total_bytes,
        "delete_source": delete_source,
        "tags": [],
        "notes": "",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    # 7. Copy
    _do_copy(files_to_copy, total_files, total_bytes, project_dir, project_name,
             source_dcim, delete_source, False, [], "", today_str)

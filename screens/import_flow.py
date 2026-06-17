# =============================================================================
#  screens/import_flow.py — Import Flow module for DJI Media Importer
# =============================================================================

import os
import sys
import time
import shutil
import hashlib
import string
import json
from datetime import datetime
from collections import defaultdict

import config
import tui
from i18n import t
from utils import format_size, get_free_space, get_file_md5
from screens.file_selector import select_files_tui
from screens.history import add_history_entry

_PROJECT_DIR_DISPLAY = ""

# =============================================================================
#  RESUME STATE
# =============================================================================

def save_resume_state(state):
    try:
        with open(config.RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_resume_state():
    if os.path.exists(config.RESUME_FILE):
        try:
            with open(config.RESUME_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None

def clear_resume_state():
    try:
        if os.path.exists(config.RESUME_FILE):
            os.remove(config.RESUME_FILE)
    except Exception:
        pass

# =============================================================================
#  FILE DISCOVERY
# =============================================================================

def find_dji_sources():
    """Return a list of all DCIM paths found on connected drives."""
    found = []
    if sys.platform == "win32":
        drives = [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
        for drive in drives:
            dcim = os.path.join(drive, "DCIM")
            if os.path.exists(dcim):
                found.append(dcim)
    else:
        for base in ["/Volumes", "/media"]:
            if os.path.exists(base):
                for folder in os.listdir(base):
                    full = os.path.join(base, folder, "DCIM")
                    if os.path.exists(full):
                        found.append(full)
    return found

def get_subfolder_name(file_ext, is_video):
    ext = file_ext.lstrip('.').lower()
    if is_video:
        return ext.upper() if ext in {'mp4', 'mov', 'mkv'} else 'VIDEO'
    if ext in {'jpg', 'jpeg'}: return 'JPG'
    if ext == 'png':           return 'PNG'
    if ext in {'dng', 'raw'}:  return 'RAW'
    return 'PHOTOS'

def get_dji_files(source_dcim):
    all_files = []
    for root, _, files in os.walk(source_dcim):
        for file in files:
            ext  = os.path.splitext(file)[1].lower()
            path = os.path.join(root, file)
            is_video = ext in config.VIDEO_EXTENSIONS
            is_photo = ext in config.PHOTO_EXTENSIONS
            if is_video or is_photo:
                try:
                    stat = os.stat(path)
                    is_raw = ext in {'.dng', '.raw'}
                    all_files.append({
                        "name":     file,
                        "path":     path,
                        "size":     stat.st_size,
                        "ext":      ext,
                        "is_video": is_video,
                        "is_raw":   is_raw,
                    })
                except Exception:
                    pass
    all_files.sort(key=lambda x: x["name"])
    return all_files

# =============================================================================
#  FILE OPERATIONS
# =============================================================================

def get_dest_filename(file_info, project_name):
    pattern      = config.CONFIG.get("FILENAME_PATTERN", "{original}")
    original_base = os.path.splitext(file_info["name"])[0]
    try:
        mtime     = os.path.getmtime(file_info["path"])
        file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        file_date = datetime.now().strftime("%Y-%m-%d")

    for key, val in {"file_date": file_date, "project_name": project_name, "original": original_base}.items():
        pattern = pattern.replace(f"{{{key}}}", val)

    ext = file_info["ext"]
    return pattern + ext if not pattern.endswith(ext) else pattern

def resolve_dest_path(src_path, target_sub_dir, dest_filename, file_size):
    target = os.path.join(target_sub_dir, dest_filename)
    if not os.path.exists(target):
        return target, False

    if os.path.getsize(target) == file_size:
        if get_file_md5(src_path) == get_file_md5(target):
            return target, True   # Exact duplicate — skip

    base, ext = os.path.splitext(dest_filename)
    counter = 1
    while True:
        new_path = os.path.join(target_sub_dir, f"{base}_{counter}{ext}")
        if not os.path.exists(new_path):
            return new_path, False
        counter += 1

def copy_file_chunked(src, dst, file_idx, total_files,
                      overall_copied_ref, total_size, start_time, current_file_name):
    buf       = config.CONFIG.get("BUFFER_SIZE_MB", 4) * 1024 * 1024
    file_size = os.path.getsize(src)
    copied    = 0
    src_hasher = hashlib.md5()

    _draw_progress(file_idx, total_files, current_file_name,
                   copied, file_size, overall_copied_ref[0], total_size, start_time,
                   label=t("progress.copying"))

    if file_size > 0:
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                chunk = fsrc.read(buf)
                if not chunk:
                    break
                fdst.write(chunk)
                src_hasher.update(chunk)
                copied                  += len(chunk)
                overall_copied_ref[0]   += len(chunk)
                _draw_progress(file_idx, total_files, current_file_name,
                               copied, file_size, overall_copied_ref[0], total_size, start_time,
                               label=t("progress.copying"))
    else:
        open(dst, 'wb').close()

    shutil.copystat(src, dst)

    if file_size > 0:
        _draw_progress(file_idx, total_files, current_file_name,
                       copied, file_size, overall_copied_ref[0], total_size, start_time,
                       label=t("progress.verifying"))
        dst_hasher = hashlib.md5()
        with open(dst, 'rb') as fdst:
            while True:
                chunk = fdst.read(buf)
                if not chunk:
                    break
                dst_hasher.update(chunk)
        if src_hasher.hexdigest() != dst_hasher.hexdigest():
            raise IOError(f"MD5 verification failed: {current_file_name}")

def write_import_log(project_dir, log_entries, project_name, source_path,
                     total_bytes, duration, delete_source, dry_run=False):
    log_path = os.path.join(project_dir, "import_log.txt")
    mode_str = "[DRY RUN — no files were copied]" if dry_run else "[IMPORT COMPLETED]"
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("DJI Media Importer — Import Log\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project:      {project_name}\n")
            f.write(f"Source:       {source_path}\n")
            f.write(f"Destination:  {project_dir}\n")
            f.write(f"Total size:   {format_size(total_bytes)}\n")
            f.write(f"Duration:     {int(duration)} seconds\n")
            f.write(f"Delete src:   {'Yes' if delete_source else 'No'}\n")
            f.write(f"Status:       {mode_str}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Files ({len(log_entries)}):\n")
            f.write("-" * 60 + "\n")
            for e in log_entries:
                f.write(f"[{e.get('status','COPIED'):<14}]  {e['name']:<35}  "
                        f"{format_size(e.get('size',0)):>10}  →  {e.get('dest','')}\n")
    except Exception:
        pass

# =============================================================================
#  PROGRESS DASHBOARD
# =============================================================================

def _draw_progress(file_idx, total_files, file_name, file_copied, file_size,
                   overall_copied, total_size, start_time,
                   label=None, dry_run=False):
    global _PROJECT_DIR_DISPLAY

    if label is None:
        label = t("progress.copying")

    overall_pct = (overall_copied / total_size * 100) if total_size > 0 else 0
    elapsed     = time.time() - start_time
    speed       = overall_copied / elapsed if elapsed > 0 else 0

    remaining   = total_size - overall_copied
    if speed > 0:
        eta_s   = remaining / speed
        eta_str = f"{int(eta_s // 60)}m {int(eta_s % 60)}s" if eta_s > 60 else f"{int(eta_s)}s"
    else:
        eta_str = "--"

    if   speed > 1024 * 1024: speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
    elif speed > 1024:         speed_str = f"{speed / 1024:.1f} KB/s"
    else:                      speed_str = f"{speed:.1f} B/s"

    bar_w  = 30
    filled = int(bar_w * overall_pct // 100)
    bar    = '█' * filled + '░' * (bar_w - filled)

    display_name = (file_name[:14] + "..." + file_name[-16:]) if len(file_name) > 33 else file_name
    label_padded = f"{label:<13}"
    title_str    = t("progress.title_dry") if dry_run else t("progress.title")
    color        = tui.YELLOW if dry_run else tui.CYAN

    lines = [
        f"{tui.BOLD}{t('progress.dest')}{tui.RESET}  {_PROJECT_DIR_DISPLAY}",
        "---",
        f"{tui.BOLD}{t('progress.overall')}{tui.RESET} [{color}{bar}{tui.RESET}] {tui.BOLD}{overall_pct:.1f}%{tui.RESET}",
        f"{tui.BOLD}{label_padded}{tui.RESET} [{file_idx}/{total_files}] {display_name}",
        f"{tui.BOLD}{t('progress.file_size')}{tui.RESET}        {format_size(file_copied)} / {format_size(file_size)}",
        f"{tui.BOLD}{t('progress.total')}{tui.RESET}   {format_size(overall_copied)} / {format_size(total_size)}",
        f"{tui.BOLD}{t('progress.speed')}{tui.RESET}   {tui.GREEN}{speed_str}{tui.RESET} | {tui.BOLD}{t('progress.remaining')}{tui.RESET} {tui.YELLOW}{eta_str}{tui.RESET}",
    ]
    sys.stdout.write("\033[10A")
    sys.stdout.write(tui.draw_box(title_str, lines, color=color) + "\n")
    sys.stdout.flush()

# =============================================================================
#  TUI SCREENS — WAIT FOR CARD
# =============================================================================

def wait_for_card_tui():
    """Spin until at least one DCIM source is found. Returns list of DCIM paths or None if cancelled."""
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    tui.hide_cursor()
    print("\n" * 6)
    try:
        while True:
            sources = find_dji_sources()
            if sources:
                return sources

            # Check if user pressed cancel
            cancel = tui.check_cancel_key()
            if cancel in ("esc", "q"):
                return None

            lines = [
                f"{tui.YELLOW}{t('wait.status')}{tui.RESET}",
                f"{tui.YELLOW}{t('wait.info')}{tui.RESET}",
                "",
                f"  {tui.CYAN}{spinner[idx % len(spinner)]}{tui.RESET} {t('wait.scanning')}",
            ]
            sys.stdout.write("\033[7A")
            sys.stdout.write(tui.draw_box(t("wait.title"), lines, color=tui.YELLOW) + "\n")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
    finally:
        tui.show_cursor()

# =============================================================================
#  TUI SCREENS — SOURCE SELECTOR
# =============================================================================

def select_source_tui(sources):
    """When multiple DCIM sources detected, let user pick one. Returns path or None."""
    selected_index = 0
    first_draw     = True
    n_clear        = 0

    tui.hide_cursor()
    try:
        while True:
            lines = [
                f"{tui.YELLOW}{t('source.multiple')}{tui.RESET}",
                f"{t('nav.arrows_enter_esc')}",
                "---",
            ]
            for i, src in enumerate(sources):
                focused = (i == selected_index)
                arrow   = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                try:
                    usage    = shutil.disk_usage(src)
                    size_inf = f"{format_size(usage.free)} {t('source.free')} / {format_size(usage.total)}"
                except Exception:
                    size_inf = t("source.unknown")
                display = src if len(src) <= 40 else src[:17] + "..." + src[-20:]
                line    = f"{arrow}💾 {display:<42} ({size_inf})"
                lines.append(f"{tui.BOLD}{tui.CYAN}{line}{tui.RESET}" if focused else line)

            if not first_draw:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("source.title"), lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear    = len(box.split('\n'))
            first_draw = False

            key = tui.get_key()
            if   key == "up"    and selected_index > 0:                  selected_index -= 1
            elif key == "down"  and selected_index < len(sources) - 1:   selected_index += 1
            elif key == "enter":                                          return sources[selected_index]
            elif key in ("esc", "q"):                                     return None
    finally:
        tui.show_cursor()

# =============================================================================
#  TUI SCREENS — CARD OVERVIEW
# =============================================================================

def card_overview_tui(source_dcim, files):
    """Show card overview with breakdown before file selection. Returns True to continue, False to cancel."""
    video_files = [f for f in files if f["is_video"]]
    photo_files = [f for f in files if not f["is_video"] and not f.get("is_raw")]
    raw_files   = [f for f in files if f.get("is_raw")]

    video_size = sum(f["size"] for f in video_files)
    photo_size = sum(f["size"] for f in photo_files)
    raw_size   = sum(f["size"] for f in raw_files)
    total_size = video_size + photo_size + raw_size

    try:
        usage = shutil.disk_usage(source_dcim)
        capacity_str = format_size(usage.total)
        used_str     = format_size(usage.used)
        free_str     = format_size(usage.free)
    except Exception:
        capacity_str = used_str = free_str = "N/A"

    def make_bar(size, total, width=20):
        if total == 0:
            return '░' * width
        filled = int(width * size / total)
        return '█' * filled + '░' * (width - filled)

    pct_video = (video_size / total_size * 100) if total_size > 0 else 0
    pct_photo = (photo_size / total_size * 100) if total_size > 0 else 0
    pct_raw   = (raw_size / total_size * 100) if total_size > 0 else 0

    lines = [
        f"{tui.BOLD}{t('overview.device')}{tui.RESET}      {source_dcim}",
        f"{tui.BOLD}{t('overview.capacity')}{tui.RESET}  {capacity_str}  |  "
        f"{t('overview.used')} {used_str}  |  {t('overview.free')} {free_str}",
        "---",
        f"  {tui.BOLD}{t('overview.breakdown')}{tui.RESET}",
        "",
        f"  📹 {t('overview.video'):<8} {len(video_files):>4} {t('overview.files')}  "
        f"({format_size(video_size):>9})  {tui.CYAN}{make_bar(video_size, total_size)}{tui.RESET} {pct_video:.0f}%",
        f"  📸 {t('overview.photos'):<8} {len(photo_files):>4} {t('overview.files')}  "
        f"({format_size(photo_size):>9})  {tui.GREEN}{make_bar(photo_size, total_size)}{tui.RESET} {pct_photo:.0f}%",
        f"  🔵 {t('overview.raw'):<8} {len(raw_files):>4} {t('overview.files')}  "
        f"({format_size(raw_size):>9})  {tui.YELLOW}{make_bar(raw_size, total_size)}{tui.RESET} {pct_raw:.0f}%",
        "---",
        f"  {tui.GREEN}{t('nav.enter_continue')}{tui.RESET}",
        f"  {tui.RED}{t('nav.esc_back')}{tui.RESET}",
    ]

    first   = True
    n_clear = 0
    tui.hide_cursor()
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("overview.title"), lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "enter":
                return True
            elif key in ("esc", "q"):
                return False
    finally:
        tui.show_cursor()

# =============================================================================
#  TUI SCREENS — FOLDER PREVIEW
# =============================================================================

def folder_preview_tui(files, project_dir, project_name):
    """Show a tree preview of the folder structure that will be created."""
    structure = config.CONFIG.get("FOLDER_STRUCTURE", "category_and_ext")
    today_str = datetime.now().strftime("%Y-%m-%d")

    tree = defaultdict(lambda: {"count": 0, "size": 0})

    for fi in files:
        ext      = fi["ext"]
        is_video = fi["is_video"]
        media_dir = t("folder.video") if is_video else t("folder.photos")
        ext_sub   = get_subfolder_name(ext, is_video)

        if structure == "flat":
            path = ""
        elif structure == "category_only":
            path = media_dir
        elif structure == "by_date":
            try:
                file_date = datetime.fromtimestamp(os.path.getmtime(fi["path"])).strftime("%Y-%m-%d")
            except Exception:
                file_date = today_str
            path = f"{file_date}/{media_dir}/{ext_sub}"
        else:  # category_and_ext
            path = f"{media_dir}/{ext_sub}"

        tree[path]["count"] += 1
        tree[path]["size"]  += fi["size"]

    total_files = sum(v["count"] for v in tree.values())
    total_size  = sum(v["size"] for v in tree.values())

    proj_display = project_dir
    if len(proj_display) > 55:
        proj_display = proj_display[:20] + "..." + proj_display[-30:]

    lines = [f"{tui.BOLD}{proj_display}{tui.RESET}", ""]

    sorted_paths = sorted(tree.keys())
    for i, path in enumerate(sorted_paths):
        info   = tree[path]
        is_last = (i == len(sorted_paths) - 1)
        branch  = "└── " if is_last else "├── "

        if path == "":
            display_path = f"({t('folder.project')})"
        else:
            parts = path.split("/")
            display_path = "/".join(parts) + "/"

        size_str = format_size(info["size"])
        line = f"  {tui.DIM}{branch}{tui.RESET}{tui.CYAN}{display_path}{tui.RESET}  ({info['count']} {t('general.files')}, {size_str})"
        lines.append(line)

    lines.append("")
    lines.append(f"  {tui.BOLD}{t('preview.total')}{tui.RESET} {total_files} {t('general.files')}  |  {format_size(total_size)}")
    lines.append("")
    lines.append(f"  {tui.GREEN}{t('nav.enter_continue')}{tui.RESET}")
    lines.append(f"  {tui.RED}{t('nav.esc_back')}{tui.RESET}")

    first   = True
    n_clear = 0
    tui.hide_cursor()
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("preview.title"), lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "enter":
                return True
            elif key in ("esc", "q"):
                return False
    finally:
        tui.show_cursor()

# =============================================================================
#  TUI SCREENS — CONFIRM / DRY-RUN CHOICE
# =============================================================================

def confirm_import_tui(files_to_copy, source_dcim, video_files, photo_files, total_bytes):
    today_str           = datetime.now().strftime("%Y-%m-%d")
    default_project     = config.CONFIG.get("DEFAULT_PROJECT_NAME", "DJI")
    default_delete      = config.CONFIG.get("DEFAULT_DELETE_SOURCE", False)
    target_root         = config.get_target_root(config.CONFIG)
    free                = get_free_space(target_root)
    delete_prompt_sfx   = "[Y/n]" if default_delete else "[y/N]"

    summary_lines = [
        f"{tui.GREEN}{t('confirm.ready')}{tui.RESET}",
        "---",
        f"{tui.BOLD}{t('confirm.source_path')}{tui.RESET}      {source_dcim}",
        f"{tui.BOLD}{t('confirm.video_files')}{tui.RESET}      {len(video_files)} {t('general.files')} ({sum(f['size'] for f in video_files)/1024**3:.2f} GB)",
        f"{tui.BOLD}{t('confirm.photo_files')}{tui.RESET}      {len(photo_files)} {t('general.files')} ({sum(f['size'] for f in photo_files)/1024**3:.2f} GB)",
        f"{tui.BOLD}{t('confirm.total_files')}{tui.RESET}      {len(files_to_copy)} {t('general.files')}",
        f"{tui.BOLD}{t('confirm.total_size')}{tui.RESET}       {format_size(total_bytes)}",
        f"{tui.BOLD}{t('confirm.free_target')}{tui.RESET}   {format_size(free)}",
    ]
    print(tui.draw_box(t("confirm.summary_title"), summary_lines, color=tui.GREEN))
    print()

    try:
        project_name = input(f"{tui.MAGENTA}{tui.BOLD}{t('confirm.project_name', name=default_project)}{tui.RESET}").strip()
        del_inp      = input(f"{tui.MAGENTA}{tui.BOLD}{t('confirm.delete_source')} {delete_prompt_sfx}: {tui.RESET}").strip().lower()
        tags_inp     = input(f"{tui.MAGENTA}{tui.BOLD}{t('confirm.tags')}{tui.RESET}").strip()
        notes_inp    = input(f"{tui.MAGENTA}{tui.BOLD}{t('confirm.notes')}{tui.RESET}").strip()
    except KeyboardInterrupt:
        return None, None, None, None, [], ""

    if not project_name:
        project_name = default_project
    delete_source = (default_delete if not del_inp else del_inp in ('y', 'yes', 't', 'tak'))

    tags  = [tg.strip() for tg in tags_inp.split(",") if tg.strip()] if tags_inp else []
    notes = notes_inp

    folder_name = f"{today_str} - {project_name}"
    project_dir = os.path.join(target_root, folder_name)

    confirm_lines = [
        f"{tui.BOLD}{t('confirm.folder')}{tui.RESET}  {project_dir}",
        f"{tui.BOLD}{t('confirm.delete')}{tui.RESET}  {t('confirm.yes') if delete_source else t('confirm.no')}",
        "",
        f"  {tui.GREEN}{t('confirm.start')}{tui.RESET}",
        f"  {tui.YELLOW}{t('confirm.dry')}{tui.RESET}",
        f"  {tui.RED}{t('confirm.cancel')}{tui.RESET}",
    ]

    first   = True
    n_clear = 0
    tui.hide_cursor()
    dry_run = None
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("confirm.title"), confirm_lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "enter":
                dry_run = False; break
            elif key == "d":
                dry_run = True;  break
            elif key in ("esc", "q"):
                return None, None, None, None, [], ""
    finally:
        tui.show_cursor()

    return project_name, project_dir, delete_source, dry_run, tags, notes

# =============================================================================
#  IMPORT FLOW CONTROLLER
# =============================================================================

def import_flow():
    """Full import flow: detect → overview → select files → preview → confirm → copy → report."""
    global _PROJECT_DIR_DISPLAY

    # 0. Check for resume state
    resume_state = load_resume_state()
    if resume_state:
        resume_result = _resume_prompt_tui(resume_state)
        if resume_result == "resume":
            _resume_import(resume_state)
            return
        elif resume_result == "cancel":
            return
        clear_resume_state()

    # 1. Wait for card
    sources = wait_for_card_tui()
    if not sources:
        return

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    # 2. Choose source if multiple
    if len(sources) > 1:
        source_dcim = select_source_tui(sources)
        if source_dcim is None:
            return
        tui.clear_screen()
        print(f"\n{tui.CYAN}{tui.BOLD}")
        tui.print_banner()
    else:
        source_dcim = sources[0]

    # 3. Scan
    scanning_lines = [
        f"{tui.GREEN}{t('scan.detected')}{tui.RESET}",
        f"{tui.YELLOW}{t('scan.path')}{tui.RESET} {source_dcim}",
        "",
        t("scan.analyzing"),
    ]
    print(tui.draw_box(t("scan.title"), scanning_lines, color=tui.CYAN))

    files_to_copy = get_dji_files(source_dcim)

    if not files_to_copy:
        _show_info_and_wait(t("error.no_files_title"), [
            f"{tui.RED}{t('error.no_files')}{tui.RESET}",
            f"{t('error.scanned_path')} {source_dcim}",
            "",
            t("error.ensure_files"),
        ], color=tui.RED)
        return

    # 4. Card overview
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    if not card_overview_tui(source_dcim, files_to_copy):
        return

    # 5. File selector
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    selected_files = select_files_tui(files_to_copy)

    if selected_files is None:
        return

    files_to_copy = selected_files
    total_files   = len(files_to_copy)
    video_files   = [f for f in files_to_copy if f["is_video"]]
    photo_files   = [f for f in files_to_copy if not f["is_video"]]
    total_bytes   = sum(f["size"] for f in files_to_copy)

    # 6. Disk space check
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    free_space  = get_free_space(config.get_target_root(config.CONFIG))
    if free_space < total_bytes:
        _show_info_and_wait(t("error.disk_title"), [
            f"{tui.RED}{t('error.disk')}{tui.RESET}",
            f"{t('error.target_root')}  {config.get_target_root(config.CONFIG)}",
            f"{t('error.required')}     {format_size(total_bytes)}",
            f"{t('error.available')}    {format_size(free_space)}",
            "",
            t("error.free_space"),
        ], color=tui.RED)
        return

    # 7. Confirm / project name / tags / dry-run
    # CRITICAL FIX: Clear screen and draw banner before confirm inputs to avoid overlap with file selector!
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    tui.show_cursor()
    result = confirm_import_tui(
        files_to_copy, source_dcim, video_files, photo_files, total_bytes
    )
    project_name, project_dir, delete_source, dry_run, tags, notes = result

    if project_name is None:
        return

    # 8. Folder preview
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    if not folder_preview_tui(files_to_copy, project_dir, project_name):
        return

    today_str = datetime.now().strftime("%Y-%m-%d")

    _PROJECT_DIR_DISPLAY = project_dir
    if len(_PROJECT_DIR_DISPLAY) > 42:
        _PROJECT_DIR_DISPLAY = _PROJECT_DIR_DISPLAY[:12] + "..." + _PROJECT_DIR_DISPLAY[-27:]

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    # 9. Create project dir (skip for dry-run)
    if not dry_run:
        try:
            os.makedirs(project_dir, exist_ok=True)
        except Exception as e:
            _show_info_and_wait(t("error.write_title"), [
                f"{tui.RED}{t('error.write')}{tui.RESET}",
                f"{t('error.path')} {project_dir}",
                f"{t('error.error')} {e}",
            ], color=tui.RED)
            return

    # 10. Save resume state
    if not dry_run:
        save_resume_state({
            "project_dir": project_dir,
            "project_name": project_name,
            "source_dcim": source_dcim,
            "files_total": total_files,
            "files_copied": [],
            "total_bytes": total_bytes,
            "delete_source": delete_source,
            "tags": tags,
            "notes": notes,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    # 11. Copy / simulate
    _do_copy(files_to_copy, total_files, total_bytes, project_dir, project_name,
             source_dcim, delete_source, dry_run, tags, notes, today_str)

def _do_copy(files_to_copy, total_files, total_bytes, project_dir, project_name,
             source_dcim, delete_source, dry_run, tags, notes, today_str):
    """Execute the copy/simulate operation and show results."""
    global _PROJECT_DIR_DISPLAY

    print("\n" * 9)
    overall_ref  = [0]
    start_time   = time.time()
    copied_counts = {}
    log_entries  = []
    success      = False
    resume_state = load_resume_state()

    tui.hide_cursor()
    try:
        for idx, fi in enumerate(files_to_copy, 1):
            src_path  = fi["path"]
            ext       = fi["ext"]
            is_video  = fi["is_video"]

            media_dir    = t("folder.video") if is_video else t("folder.photos")
            ext_sub      = get_subfolder_name(ext, is_video)
            structure    = config.CONFIG.get("FOLDER_STRUCTURE", "category_and_ext")

            if structure == "flat":
                target_sub = project_dir
                sub_name   = t("folder.project")
            elif structure == "category_only":
                target_sub = os.path.join(project_dir, media_dir)
                sub_name   = media_dir
            elif structure == "by_date":
                try:
                    file_date = datetime.fromtimestamp(os.path.getmtime(src_path)).strftime("%Y-%m-%d")
                except Exception:
                    file_date = today_str
                target_sub = os.path.join(project_dir, file_date, media_dir, ext_sub)
                sub_name   = f"{file_date}/{media_dir}/{ext_sub}"
            else:
                target_sub = os.path.join(project_dir, media_dir, ext_sub)
                sub_name   = ext_sub

            dest_filename = get_dest_filename(fi, project_name)
            dest_path     = os.path.join(target_sub, dest_filename)

            if dry_run:
                overall_ref[0] += fi["size"]
                _draw_progress(idx, total_files, dest_filename,
                               fi["size"], fi["size"],
                               overall_ref[0], total_bytes, start_time,
                               label=t("progress.simulating"), dry_run=True)
                time.sleep(0.02)
                log_entries.append({"name": fi["name"], "dest": dest_path,
                                    "size": fi["size"], "status": "DRY RUN"})
                copied_counts[sub_name] = copied_counts.get(sub_name, 0) + 1
                continue

            # Real copy
            os.makedirs(target_sub, exist_ok=True)
            dest_path, is_dup = resolve_dest_path(src_path, target_sub, dest_filename, fi["size"])
            resolved_name     = os.path.basename(dest_path)

            if is_dup:
                overall_ref[0] += fi["size"]
                _draw_progress(idx, total_files, resolved_name,
                               fi["size"], fi["size"],
                               overall_ref[0], total_bytes, start_time,
                               label=t("progress.skipped"))
                time.sleep(0.05)
                copied_counts[sub_name] = copied_counts.get(sub_name, 0) + 1
                log_entries.append({"name": fi["name"], "dest": dest_path,
                                    "size": fi["size"], "status": "SKIPPED (DUP)"})
                # Update resume state
                if resume_state:
                    resume_state["files_copied"].append(fi["name"])
                    save_resume_state(resume_state)
                continue

            copy_file_chunked(src_path, dest_path, idx, total_files,
                              overall_ref, total_bytes, start_time, resolved_name)
            copied_counts[sub_name] = copied_counts.get(sub_name, 0) + 1
            log_entries.append({"name": fi["name"], "dest": dest_path,
                                "size": fi["size"], "status": "COPIED"})

            # Update resume state
            if resume_state:
                resume_state["files_copied"].append(fi["name"])
                save_resume_state(resume_state)

        success = True

    except KeyboardInterrupt:
        sys.stdout.write("\n" * 2)
        _show_info_and_wait(t("error.aborted_title"), [
            f"{tui.RED}{t('error.aborted')}{tui.RESET}",
            t("error.aborted_hint"),
        ], color=tui.RED)
        return
    except Exception as e:
        sys.stdout.write("\n" * 2)
        _show_info_and_wait(t("error.import_title"), [
            f"{tui.RED}{t('error.import')}{tui.RESET}",
            t("error.import_hint"),
            str(e),
            "",
            t("error.src_safe"),
        ], color=tui.RED)
        return
    finally:
        tui.show_cursor()

    if not success:
        return

    # Clear resume state on success
    clear_resume_state()

    duration = time.time() - start_time

    # Post-copy cleanup
    if not dry_run and delete_source:
        for fi in files_to_copy:
            try:
                os.remove(fi["path"])
            except Exception:
                pass

    # Write log file
    if not dry_run:
        write_import_log(project_dir, log_entries, project_name, source_dcim,
                         total_bytes, duration, delete_source, dry_run=False)

    # Save to history
    add_history_entry({
        "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project_name":     project_name,
        "project_dir":      project_dir,
        "source_path":      source_dcim,
        "total_files":      total_files,
        "total_bytes":      total_bytes,
        "duration_seconds": int(duration),
        "delete_source":    delete_source,
        "dry_run":          dry_run,
        "tags":             tags,
        "notes":            notes,
    })

    # Final report
    sys.stdout.write("\n")
    stat_lines = [f"   ▪ {cat}: {tui.BOLD}{cnt}{tui.RESET} {t('general.files')}"
                  for cat, cnt in sorted(copied_counts.items())]

    delete_status = t("success.deleted_yes") if delete_source else t("success.deleted_no")
    dry_note      = (f"{tui.YELLOW}{t('success.dry_note')}{tui.RESET}"
                     if dry_run else f"{tui.GREEN}{t('success.folder_opened')}{tui.RESET}")

    success_lines = [
        f"{tui.GREEN}{t('success.completed_dry') if dry_run else t('success.completed')}{tui.RESET}",
        "---",
        f"{tui.BOLD}{t('success.saved_to')}{tui.RESET}      {project_dir}",
        f"{tui.BOLD}{t('success.copied_files')}{tui.RESET}",
    ] + stat_lines + [
        "---",
        f"{tui.BOLD}{t('success.source_files')}{tui.RESET}  {delete_status}",
        f"{tui.BOLD}{t('success.total_size')}{tui.RESET}    {format_size(total_bytes)}",
        f"{tui.BOLD}{t('success.op_time')}{tui.RESET} {int(duration)}s",
        "",
        dry_note,
    ]

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    title_str = t("success.title_dry") if dry_run else t("success.title")
    color_str = tui.YELLOW if dry_run else tui.GREEN
    print(tui.draw_box(title_str, success_lines, color=color_str))

    if not dry_run:
        try:
            if sys.platform == "win32":
                os.startfile(project_dir)
            else:
                import subprocess
                subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", project_dir])
        except Exception:
            pass

    input(f"\n{t('nav.enter_to_menu')}")

# =============================================================================
#  RESUME PROMPT SCREEN
# =============================================================================

def _resume_prompt_tui(state):
    """Show resume prompt. Returns 'resume', 'fresh', or 'cancel'."""
    proj      = state.get("project_name", "N/A")
    proj_dir  = state.get("project_dir", "N/A")
    total     = state.get("files_total", 0)
    copied    = len(state.get("files_copied", []))
    remaining = total - copied
    pct       = (copied / total * 100) if total > 0 else 0

    lines = [
        f"{tui.YELLOW}{t('resume.interrupted')}{tui.RESET}",
        "---",
        f"{tui.BOLD}{t('resume.project')}{tui.RESET}    {proj}",
        f"{tui.BOLD}{t('resume.progress')}{tui.RESET}   {copied}/{total} {t('resume.copied')} ({pct:.0f}%)",
        f"{tui.BOLD}{t('resume.remaining')}{tui.RESET}  {remaining} {t('general.files')}",
        "",
        f"  {tui.GREEN}{t('resume.resume')}{tui.RESET}",
        f"  {tui.CYAN}{t('resume.fresh')}{tui.RESET}",
        f"  {tui.RED}{t('resume.cancel')}{tui.RESET}",
    ]

    first   = True
    n_clear = 0
    tui.clear_screen()  # CRITICAL FIX: Clear screen on resume prompt startup!
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    tui.hide_cursor()
    try:
        while True:
            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("resume.title"), lines, color=tui.YELLOW)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if key == "r":
                return "resume"
            elif key == "s":
                return "fresh"
            elif key in ("esc", "q"):
                return "cancel"
    finally:
        tui.show_cursor()

def _resume_import(state):
    """Resume an interrupted import."""
    global _PROJECT_DIR_DISPLAY

    source_dcim  = state.get("source_dcim", "")
    project_dir  = state.get("project_dir", "")
    project_name = state.get("project_name", "DJI")
    delete_source = state.get("delete_source", False)
    tags         = state.get("tags", [])
    notes        = state.get("notes", "")
    already_copied = set(state.get("files_copied", []))

    if not os.path.exists(source_dcim):
        _show_info_and_wait(t("error.write_title"), [
            f"{tui.RED}{t('error.no_files')}{tui.RESET}",
            f"{t('error.scanned_path')} {source_dcim}",
        ], color=tui.RED)
        clear_resume_state()
        return

    all_files = get_dji_files(source_dcim)
    files_to_copy = [f for f in all_files if f["name"] not in already_copied]

    if not files_to_copy:
        clear_resume_state()
        _show_info_and_wait(t("success.title"), [
            f"{tui.GREEN}{t('success.completed')}{tui.RESET}",
            "",
            f"{t('history.files')} {len(already_copied)} {t('general.files')}",
        ], color=tui.GREEN)
        return

    total_files = len(files_to_copy)
    total_bytes = sum(f["size"] for f in files_to_copy)
    today_str   = datetime.now().strftime("%Y-%m-%d")

    _PROJECT_DIR_DISPLAY = project_dir
    if len(_PROJECT_DIR_DISPLAY) > 42:
        _PROJECT_DIR_DISPLAY = _PROJECT_DIR_DISPLAY[:12] + "..." + _PROJECT_DIR_DISPLAY[-27:]

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()

    os.makedirs(project_dir, exist_ok=True)

    _do_copy(files_to_copy, total_files, total_bytes, project_dir, project_name,
             source_dcim, delete_source, False, tags, notes, today_str)

# =============================================================================
#  HELPERS
# =============================================================================

def _show_info_and_wait(title, lines, color=None):
    """Print an info box and wait for Enter to return to menu."""
    if color is None:
        color = tui.RED
    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    print(tui.draw_box(title, lines, color=color))
    input(f"\n{t('nav.enter_to_menu')}")

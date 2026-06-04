import os
import shutil
import string
import sys
import re
import time
import json
import hashlib
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "TARGET_ROOT": r"E:\Dron",
    "VIDEO_EXTENSIONS": [".mp4", ".mov", ".mkv"],
    "PHOTO_EXTENSIONS": [".jpg", ".jpeg", ".dng", ".raw", ".png"],
    "BUFFER_SIZE_MB": 4,
    "DEFAULT_PROJECT_NAME": "DJI",
    "DEFAULT_DELETE_SOURCE": False,
    "FOLDER_STRUCTURE": "category_and_ext",
    "FILENAME_PATTERN": "{original}",
    "DUPLICATE_ACTION": "skip_if_same_otherwise_rename"
}

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception as e:
            print(f"Warning: Failed to load config.json ({e}). Using defaults.")
    else:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        except Exception:
            pass
            
    # Fallback dla TARGET_ROOT
    target_root = config["TARGET_ROOT"]
    if not os.path.exists(target_root):
        target_root = os.path.join(os.path.expanduser("~"), "Pictures", "Drone_Imports")
    config["TARGET_ROOT"] = target_root
    
    # Zamiana list rozszerzeń na zbiory (sets) z małymi literami
    config["VIDEO_EXTENSIONS"] = {ext.lower() for ext in config["VIDEO_EXTENSIONS"]}
    config["PHOTO_EXTENSIONS"] = {ext.lower() for ext in config["PHOTO_EXTENSIONS"]}
    
    return config

CONFIG = load_config()

TARGET_ROOT = CONFIG["TARGET_ROOT"]
VIDEO_EXTENSIONS = CONFIG["VIDEO_EXTENSIONS"]
PHOTO_EXTENSIONS = CONFIG["PHOTO_EXTENSIONS"]

def get_free_space(path):
    temp_path = path
    while temp_path and not os.path.exists(temp_path):
        parent = os.path.dirname(temp_path)
        if parent == temp_path:
            break
        temp_path = parent
    try:
        return shutil.disk_usage(temp_path).free
    except Exception:
        return float('inf')

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
        if ch == b'\r': return "enter"
        if ch == b' ': return "space"
        if ch == b'\x1b': return "esc"
        try:
            return ch.decode('utf-8').lower()
        except Exception:
            return None
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x03':
                raise KeyboardInterrupt()
            if ch == '\x1b':
                # Check for arrow keys
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return "up"
                    if ch3 == 'B': return "down"
                    if ch3 == 'D': return "left"
                    if ch3 == 'C': return "right"
            elif ch == '\r' or ch == '\n':
                return "enter"
            elif ch == ' ':
                return "space"
            return ch.lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_file_md5(filepath):
    hasher = hashlib.md5()
    buffer_size = CONFIG.get("BUFFER_SIZE_MB", 4) * 1024 * 1024
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def get_dest_filename(file_info, project_name):
    pattern = CONFIG.get("FILENAME_PATTERN", "{file_date}_{project_name}_{original}")
    original_base = os.path.splitext(file_info["name"])[0]
    
    try:
        mtime = os.path.getmtime(file_info["path"])
        file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        file_date = datetime.now().strftime("%Y-%m-%d")
        
    replacements = {
        "file_date": file_date,
        "project_name": project_name,
        "original": original_base
    }
    
    formatted = pattern
    for key, val in replacements.items():
        formatted = formatted.replace(f"{{{key}}}", val)
        
    ext = file_info["ext"]
    if not formatted.endswith(ext):
        formatted = formatted + ext
    return formatted

def resolve_dest_path(src_path, target_sub_dir, dest_filename, file_size):
    target_file_path = os.path.join(target_sub_dir, dest_filename)
    if not os.path.exists(target_file_path):
        return target_file_path, False

    if os.path.getsize(target_file_path) == file_size:
        src_md5 = get_file_md5(src_path)
        dst_md5 = get_file_md5(target_file_path)
        if src_md5 and dst_md5 and src_md5 == dst_md5:
            return target_file_path, True
            
    base, ext = os.path.splitext(dest_filename)
    counter = 1
    while True:
        new_filename = f"{base}_{counter}{ext}"
        new_path = os.path.join(target_sub_dir, new_filename)
        if not os.path.exists(new_path):
            return new_path, False
        counter += 1

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
RED = "\033[31m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"

PROJECT_DIR_DISPLAY = ""

if sys.platform == "win32":
    os.system('')

def find_dji_source():
    if sys.platform == "win32":
        drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]
        for drive in drives:
            dcim_path = os.path.join(drive, "DCIM")
            if os.path.exists(dcim_path):
                return dcim_path
    else:
        mount_points = ["/Volumes", "/media"]
        for base in mount_points:
            if os.path.exists(base):
                for folder in os.listdir(base):
                    full_path = os.path.join(base, folder, "DCIM")
                    if os.path.exists(full_path):
                        return full_path
    return None

def get_subfolder_name(file_ext, is_video):
    ext = file_ext.lstrip('.').lower()
    if is_video:
        if ext in {'mp4', 'mov', 'mkv'}:
            return ext.upper()
        return 'VIDEO'
    else:
        if ext in {'jpg', 'jpeg'}:
            return 'JPG'
        elif ext == 'png':
            return 'PNG'
        elif ext in {'dng', 'raw'}:
            return 'RAW'
        return 'PHOTOS'

def get_dji_files(source_dcim):
    all_files = []
    for root, _, files in os.walk(source_dcim):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            source_file_path = os.path.join(root, file)
            is_video = file_ext in VIDEO_EXTENSIONS
            is_photo = file_ext in PHOTO_EXTENSIONS
            if is_video or is_photo:
                try:
                    stat = os.stat(source_file_path)
                    all_files.append({
                        "name": file,
                        "path": source_file_path,
                        "size": stat.st_size,
                        "ext": file_ext,
                        "is_video": is_video
                    })
                except Exception:
                    pass
    all_files.sort(key=lambda x: x["name"])
    return all_files

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def draw_box(title, lines, width=66, color=CYAN):
    top_left = "╭"
    top_right = "╮"
    bottom_left = "╰"
    bottom_right = "╯"
    horizontal = "─"
    vertical = "│"
    divider_left = "├"
    divider_right = "┤"
    
    if title:
        title_text = f" {title} "
        header_line = f"{color}{top_left}{horizontal * 2}{BOLD}{title_text}{RESET}{color}{horizontal * (width - 4 - len(title_text))}{top_right}{RESET}"
    else:
        header_line = f"{color}{top_left}{horizontal * (width - 2)}{top_right}{RESET}"
        
    box_lines = [header_line]
    
    for line in lines:
        if line == "---":
            box_lines.append(f"{color}{divider_left}{horizontal * (width - 2)}{divider_right}{RESET}")
        else:
            raw_len = len(remove_ansi_codes(line))
            if raw_len > width - 4:
                line = line[:width - 7] + "..."
                raw_len = len(remove_ansi_codes(line))
                
            padding = width - 4 - raw_len
            box_lines.append(f"{color}{vertical}{RESET} {line}{' ' * padding} {color}{vertical}{RESET}")
            
    box_lines.append(f"{color}{bottom_left}{horizontal * (width - 2)}{bottom_right}{RESET}")
    return "\n".join(box_lines)

def select_files_tui(files_to_copy):
    total = len(files_to_copy)
    if total == 0:
        return []
        
    for f in files_to_copy:
        f["selected"] = f.get("selected", True)
        
    selected_index = 0
    scroll_top = 0
    viewport_height = 10
    
    first_draw = True
    num_lines_to_clear = 0
    
    hide_cursor()
    try:
        while True:
            selected_files = [f for f in files_to_copy if f["selected"]]
            selected_count = len(selected_files)
            selected_size = sum(f["size"] for f in selected_files)
            
            lines = [
                f"Use {CYAN}↑/↓{RESET} to navigate | {CYAN}[Space]{RESET} to toggle | {CYAN}[Enter]{RESET} to confirm",
                f"Press {CYAN}[A]{RESET} to select all | {CYAN}[N]{RESET} to clear selection",
                "---"
            ]
            
            end_idx = min(total, scroll_top + viewport_height)
            
            if scroll_top > 0:
                lines.append(f"  {YELLOW}▲ ... ({scroll_top} more above){RESET}")
            else:
                lines.append("")
                
            for i in range(scroll_top, end_idx):
                item = files_to_copy[i]
                is_focused = (i == selected_index)
                is_selected = item["selected"]
                
                focus_indicator = f"{GREEN}→{RESET} " if is_focused else "  "
                chk = f"[{GREEN}✔{RESET}]" if is_selected else "[ ]"
                icon = "📹" if item["is_video"] else "📸"
                
                name = item["name"]
                if len(name) > 30:
                    name = name[:13] + "..." + name[-14:]
                    
                size_str = format_size(item["size"])
                
                line_content = f"{focus_indicator}{chk} {icon} {name:<30} ({size_str:>8})"
                if is_focused:
                    lines.append(f"{BOLD}{CYAN}{line_content}{RESET}")
                else:
                    lines.append(line_content)
                    
            more_below = total - end_idx
            if more_below > 0:
                lines.append(f"  {YELLOW}▼ ... ({more_below} more below){RESET}")
            else:
                lines.append("")
                
            lines.append("---")
            lines.append(f"Selected: {BOLD}{selected_count}/{total}{RESET} files | Size: {BOLD}{GREEN}{format_size(selected_size)}{RESET}")
            
            if not first_draw:
                sys.stdout.write(f"\033[{num_lines_to_clear}A")
                
            box = draw_box("SELECT FILES TO IMPORT", lines, color=CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            
            num_lines_to_clear = len(box.split('\n'))
            first_draw = False
            
            key = get_key()
            if key == "up":
                if selected_index > 0:
                    selected_index -= 1
                    if selected_index < scroll_top:
                        scroll_top = selected_index
            elif key == "down":
                if selected_index < total - 1:
                    selected_index += 1
                    if selected_index >= scroll_top + viewport_height:
                        scroll_top = selected_index - viewport_height + 1
            elif key == "space":
                files_to_copy[selected_index]["selected"] = not files_to_copy[selected_index]["selected"]
            elif key == "a":
                for f in files_to_copy:
                    f["selected"] = True
            elif key == "n":
                for f in files_to_copy:
                    f["selected"] = False
            elif key == "enter":
                if selected_count > 0:
                    break
            elif key in ("esc", "q"):
                return None
    finally:
        show_cursor()
        
    return [f for f in files_to_copy if f["selected"]]

def wait_for_card_tui():
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    hide_cursor()
    print("\n" * 6)
    try:
        while True:
            dcim_path = find_dji_source()
            if dcim_path:
                return dcim_path
            
            lines = [
                f"{YELLOW}Status:  {RESET}Waiting for device connection...",
                f"{YELLOW}Info:    {RESET}Insert SD card or connect drone via USB.",
                "",
                f"  {CYAN}{spinner[idx % len(spinner)]}{RESET} Scanning drives (searching for DCIM)..."
            ]
            sys.stdout.write("\033[7A")
            box = draw_box("DEVICE STATUS", lines, color=YELLOW)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.1)
    finally:
        show_cursor()

def draw_progress_dashboard(file_idx, total_files, file_name, file_copied, file_size, overall_copied, total_size, start_time, status_label="Copying file:"):
    global PROJECT_DIR_DISPLAY
    overall_pct = (overall_copied / total_size) * 100 if total_size > 0 else 0
    elapsed = time.time() - start_time
    speed = overall_copied / elapsed if elapsed > 0 else 0
    
    remaining_bytes = total_size - overall_copied
    if speed > 0:
        eta_seconds = remaining_bytes / speed
        if eta_seconds > 60:
            eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
        else:
            eta_str = f"{int(eta_seconds)}s"
    else:
        eta_str = "--"
        
    if speed > 1024 * 1024:
        speed_str = f"{speed / (1024 * 1024):.1f} MB/s"
    elif speed > 1024:
        speed_str = f"{speed / 1024:.1f} KB/s"
    else:
        speed_str = f"{speed:.1f} B/s"
        
    bar_width = 30
    filled_width = int(bar_width * overall_pct // 100)
    bar = '█' * filled_width + '░' * (bar_width - filled_width)
    
    file_size_str = f"{format_size(file_copied)} / {format_size(file_size)}"
    total_size_str = f"{format_size(overall_copied)} / {format_size(total_size)}"
    
    if len(file_name) > 33:
        display_name = file_name[:14] + "..." + file_name[-16:]
    else:
        display_name = file_name
        
    # status_label dopasowujemy szerokością do 13 znaków, aby ramka była równa
    status_label_padded = f"{status_label:<13}"
    lines = [
        f"{BOLD}Destination:{RESET}  {PROJECT_DIR_DISPLAY}",
        "---",
        f"{BOLD}Overall progress:{RESET} [{CYAN}{bar}{RESET}] {BOLD}{overall_pct:.1f}%{RESET}",
        f"{BOLD}{status_label_padded}{RESET} [{file_idx}/{total_files}] {display_name}",
        f"{BOLD}File size:{RESET}        {file_size_str}",
        f"{BOLD}Total progress:{RESET}   {total_size_str}",
        f"{BOLD}Transfer speed:{RESET}   {GREEN}{speed_str}{RESET} | {BOLD}Remaining:{RESET} {YELLOW}{eta_str}{RESET}"
    ]
    sys.stdout.write("\033[10A")
    box = draw_box("COPYING MEDIA", lines, color=CYAN)
    sys.stdout.write(box + "\n")
    sys.stdout.flush()

def copy_file_chunked(src, dst, file_idx, total_files, overall_copied_ref, total_size, start_time, current_file_name):
    buffer_size = CONFIG.get("BUFFER_SIZE_MB", 4) * 1024 * 1024
    file_size = os.path.getsize(src)
    file_copied = 0
    
    src_hasher = hashlib.md5()
    
    draw_progress_dashboard(
        file_idx, 
        total_files, 
        current_file_name, 
        file_copied, 
        file_size, 
        overall_copied_ref[0], 
        total_size, 
        start_time,
        status_label="Copying file:"
    )
    
    if file_size > 0:
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    src_hasher.update(chunk)
                    file_copied += len(chunk)
                    overall_copied_ref[0] += len(chunk)
                    draw_progress_dashboard(
                        file_idx, 
                        total_files, 
                        current_file_name, 
                        file_copied, 
                        file_size, 
                        overall_copied_ref[0], 
                        total_size, 
                        start_time,
                        status_label="Copying file:"
                    )
    else:
        with open(dst, 'wb') as fdst:
            pass
    shutil.copystat(src, dst)
    
    # Weryfikacja sumy kontrolnej zapisanego pliku
    if file_size > 0:
        draw_progress_dashboard(
            file_idx, 
            total_files, 
            current_file_name, 
            file_copied, 
            file_size, 
            overall_copied_ref[0], 
            total_size, 
            start_time,
            status_label="Verifying..."
        )
        dst_hasher = hashlib.md5()
        with open(dst, 'rb') as fdst:
            while True:
                chunk = fdst.read(buffer_size)
                if not chunk:
                    break
                dst_hasher.update(chunk)
        
        if src_hasher.hexdigest() != dst_hasher.hexdigest():
            raise IOError(f"MD5 verification failed for file: {current_file_name}")


def import_media_tui():
    global PROJECT_DIR_DISPLAY
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    banner = [
        "DJI MEDIA IMPORTER"
    ]
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    source_dcim = wait_for_card_tui()
    
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    scanning_lines = [
        f"{GREEN}✔ Device detected!{RESET}",
        f"{YELLOW}Path: {RESET}{source_dcim}",
        "",
        "🔍 Analyzing card contents..."
    ]
    print(draw_box("SCANNING DEVICE", scanning_lines, color=CYAN))
    
    files_to_copy = get_dji_files(source_dcim)
    if len(files_to_copy) == 0:
        sys.stdout.write("\033[H\033[2J")
        print(f"\n{CYAN}{BOLD}")
        print(draw_box("", banner, color=CYAN))
        print(RESET)
        empty_lines = [
            f"{RED}❌ No compatible media found to copy.{RESET}",
            f"Scanned path: {source_dcim}",
            "",
            "Ensure the card contains video files (.mp4, .mov, .mkv)",
            "or photo files (.jpg, .jpeg, .dng, .raw, .png)."
        ]
        print(draw_box("NO COMPATIBLE FILES", empty_lines, color=RED))
        input(f"\nPress {BOLD}Enter{RESET} to exit...")
        return

    # Uruchomienie interaktywnego wyboru plików
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    selected_files = select_files_tui(files_to_copy)
    if selected_files is None:
        sys.stdout.write("\033[H\033[2J")
        print(f"\n{RED}{BOLD}")
        cancel_lines = [
            f"{RED}⚠ IMPORT CANCELLED BY USER!{RESET}",
            "File selection was cancelled.",
            "No files have been copied."
        ]
        print(draw_box("CANCELLED", cancel_lines, color=RED))
        input(f"\nPress {BOLD}Enter{RESET} to exit...")
        return
        
    files_to_copy = selected_files
    total_files = len(files_to_copy)
    video_files = [f for f in files_to_copy if f["is_video"]]
    photo_files = [f for f in files_to_copy if not f["is_video"]]
    total_bytes = sum(f["size"] for f in files_to_copy)
    
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    free_space = get_free_space(TARGET_ROOT)
    if free_space < total_bytes:
        sys.stdout.write("\033[H\033[2J")
        print(f"\n{RED}{BOLD}")
        space_err_lines = [
            f"{RED}❌ INSUFFICIENT DISK SPACE!{RESET}",
            f"Target Root:  {TARGET_ROOT}",
            f"Required:     {format_size(total_bytes)}",
            f"Available:    {format_size(free_space)}",
            "",
            "Please free up some space and try again."
        ]
        print(draw_box("DISK SPACE ERROR", space_err_lines, color=RED))
        input(f"\nPress {BOLD}Enter{RESET} to exit...")
        return

        
    summary_lines = [
        f"{GREEN}✔ Device ready for import{RESET}",
        "---",
        f"{BOLD}Source Path:{RESET}      {source_dcim}",
        f"{BOLD}Video files:{RESET}      {len(video_files)} files ({sum(f['size'] for f in video_files) / (1024*1024*1024):.2f} GB)",
        f"{BOLD}Photo files:{RESET}      {len(photo_files)} files ({sum(f['size'] for f in photo_files) / (1024*1024*1024):.2f} GB)",
        f"{BOLD}Total files:{RESET}      {total_files} files",
        f"{BOLD}Total size:{RESET}       {format_size(total_bytes)}"
    ]
    print(draw_box("MEDIA SUMMARY", summary_lines, color=GREEN))
    print()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    default_project_name = CONFIG.get("DEFAULT_PROJECT_NAME", "DJI")
    default_delete = CONFIG.get("DEFAULT_DELETE_SOURCE", False)
    delete_prompt_suffix = "[Y/n]" if default_delete else "[y/N]"
    
    try:
        project_name = input(f"{MAGENTA}{BOLD}❓ Project name [default: {default_project_name}]: {RESET}").strip()
        delete_input = input(f"{MAGENTA}{BOLD}❓ Delete source files after import? {delete_prompt_suffix}: {RESET}").strip().lower()
        if not delete_input:
            delete_source = default_delete
        else:
            delete_source = delete_input in ('y', 'yes')
    except KeyboardInterrupt:
        print(f"\n{RED}Import cancelled.{RESET}")
        return
        
    if not project_name:
        project_name = default_project_name
        
    folder_name = f"{today_str} - {project_name}"
    project_dir = os.path.join(TARGET_ROOT, folder_name)
    
    PROJECT_DIR_DISPLAY = project_dir
    if len(PROJECT_DIR_DISPLAY) > 42:
        PROJECT_DIR_DISPLAY = PROJECT_DIR_DISPLAY[:12] + "..." + PROJECT_DIR_DISPLAY[-27:]
        
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    try:
        os.makedirs(project_dir, exist_ok=True)
    except Exception as e:
        err_lines = [
            f"{RED}❌ Error creating target directory!{RESET}",
            f"Path: {project_dir}",
            f"Error: {e}"
        ]
        print(draw_box("WRITE ERROR", err_lines, color=RED))
        input(f"\nPress {BOLD}Enter{RESET} to exit...")
        return
        
    print("\n" * 9)
    overall_copied_ref = [0]
    start_time = time.time()
    copied_counts = {}
    
    hide_cursor()
    success = False
    hide_cursor()
    try:
        for idx, file_info in enumerate(files_to_copy, 1):
            source_path = file_info["path"]
            filename = file_info["name"]
            ext = file_info["ext"]
            is_video = file_info["is_video"]
            
            media_type_dir = "Wideo" if is_video else "Zdjecia"
            ext_subfolder = get_subfolder_name(ext, is_video)
            
            structure = CONFIG.get("FOLDER_STRUCTURE", "category_and_ext")
            if structure == "flat":
                target_sub_dir = project_dir
                sub_dir_name = "Projekt"
            elif structure == "category_only":
                target_sub_dir = os.path.join(project_dir, media_type_dir)
                sub_dir_name = media_type_dir
            elif structure == "by_date":
                try:
                    mtime = os.path.getmtime(source_path)
                    file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                except Exception:
                    file_date = today_str
                target_sub_dir = os.path.join(project_dir, file_date, media_type_dir, ext_subfolder)
                sub_dir_name = f"{file_date}/{media_type_dir}/{ext_subfolder}"
            else: # category_and_ext or default
                target_sub_dir = os.path.join(project_dir, media_type_dir, ext_subfolder)
                sub_dir_name = ext_subfolder
                
            dest_filename = get_dest_filename(file_info, project_name)
            
            os.makedirs(target_sub_dir, exist_ok=True)
            dest_path, is_duplicate = resolve_dest_path(source_path, target_sub_dir, dest_filename, file_info["size"])
            
            resolved_filename = os.path.basename(dest_path)
            
            if is_duplicate:
                overall_copied_ref[0] += file_info["size"]
                draw_progress_dashboard(
                    idx,
                    total_files,
                    resolved_filename,
                    file_info["size"],
                    file_info["size"],
                    overall_copied_ref[0],
                    total_bytes,
                    start_time,
                    status_label="Skipped (Dup)"
                )
                time.sleep(0.05) # Tiny pause for UX
                copied_counts[sub_dir_name] = copied_counts.get(sub_dir_name, 0) + 1
                continue
                
            copy_file_chunked(
                source_path, 
                dest_path, 
                idx, 
                total_files, 
                overall_copied_ref, 
                total_bytes, 
                start_time, 
                resolved_filename
            )
            copied_counts[sub_dir_name] = copied_counts.get(sub_dir_name, 0) + 1
        success = True
    except KeyboardInterrupt:
        sys.stdout.write("\n" * 2)
        cancel_lines = [
            f"{RED}⚠ IMPORT CANCELLED BY USER!{RESET}",
            "Copying process has stopped.",
            "Some files may not have been copied."
        ]
        print(draw_box("ABORTED", cancel_lines, color=RED))
        return
    except Exception as e:
        sys.stdout.write("\n" * 2)
        err_lines = [
            f"{RED}❌ IMPORT ERROR!{RESET}",
            "An error occurred during copy or verification:",
            f"{e}",
            "",
            "Source files have NOT been deleted."
        ]
        print(draw_box("ERROR", err_lines, color=RED))
        input(f"\nPress {BOLD}Enter{RESET} to exit...")
        return
    finally:
        show_cursor()
        
    if success and delete_source:
        for file_info in files_to_copy:
            try:
                os.remove(file_info["path"])
            except Exception:
                pass
                
    sys.stdout.write("\n")
    
    stat_lines = []
    for cat, count in sorted(copied_counts.items()):
        stat_lines.append(f"   ▪ {cat}: {BOLD}{count}{RESET} files")
        
    delete_status = "Yes, deleted from device" if delete_source else "No, kept on device"
    success_lines = [
        f"{GREEN}🎉 IMPORT COMPLETED SUCCESSFULLY!{RESET}",
        "---",
        f"{BOLD}Saved to:{RESET}      {project_dir}",
        f"{BOLD}Copied files:{RESET}"
    ] + stat_lines + [
        "---",
        f"{BOLD}Source files:{RESET}  {delete_status}",
        f"{BOLD}Total size:{RESET}    {format_size(total_bytes)}",
        f"{BOLD}Operation time:{RESET} {int(time.time() - start_time)} seconds",
        "",
        f"{GREEN}📂 Target folder was automatically opened.{RESET}"
    ]
    
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    print(draw_box("SUCCESS", success_lines, color=GREEN))
    
    try:
        if sys.platform == "win32":
            os.startfile(project_dir)
        else:
            import subprocess
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", project_dir])
    except Exception:
        pass
        
    print()
    for i in range(3, 0, -1):
        sys.stdout.write(f"\rClosing program in {BOLD}{i}{RESET} seconds... ")
        sys.stdout.flush()
        time.sleep(1)

if __name__ == "__main__":
    import_media_tui()
import os
import shutil
import string
import sys
import re
import time
from datetime import datetime

TARGET_ROOT = r"E:\Dron"
if not os.path.exists(TARGET_ROOT):
    TARGET_ROOT = os.path.join(os.path.expanduser("~"), "Pictures", "Drone_Imports")
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv'}
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.dng', '.raw', '.png'}

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

def draw_progress_dashboard(file_idx, total_files, file_name, file_copied, file_size, overall_copied, total_size, start_time):
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
        
    lines = [
        f"{BOLD}Destination:{RESET}  {PROJECT_DIR_DISPLAY}",
        "---",
        f"{BOLD}Overall progress:{RESET} [{CYAN}{bar}{RESET}] {BOLD}{overall_pct:.1f}%{RESET}",
        f"{BOLD}Copying file:{RESET}     [{file_idx}/{total_files}] {display_name}",
        f"{BOLD}File size:{RESET}        {file_size_str}",
        f"{BOLD}Total progress:{RESET}   {total_size_str}",
        f"{BOLD}Transfer speed:{RESET}   {GREEN}{speed_str}{RESET} | {BOLD}Remaining:{RESET} {YELLOW}{eta_str}{RESET}"
    ]
    sys.stdout.write("\033[10A")
    box = draw_box("COPYING MEDIA", lines, color=CYAN)
    sys.stdout.write(box + "\n")
    sys.stdout.flush()

def copy_file_chunked(src, dst, file_idx, total_files, overall_copied_ref, total_size, start_time, current_file_name):
    buffer_size = 4 * 1024 * 1024
    file_size = os.path.getsize(src)
    file_copied = 0
    
    draw_progress_dashboard(
        file_idx, 
        total_files, 
        current_file_name, 
        file_copied, 
        file_size, 
        overall_copied_ref[0], 
        total_size, 
        start_time
    )
    
    if file_size > 0:
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
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
                        start_time
                    )
    else:
        with open(dst, 'wb') as fdst:
            pass
    shutil.copystat(src, dst)

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
    total_files = len(files_to_copy)
    video_files = [f for f in files_to_copy if f["is_video"]]
    photo_files = [f for f in files_to_copy if not f["is_video"]]
    total_bytes = sum(f["size"] for f in files_to_copy)
    
    sys.stdout.write("\033[H\033[2J")
    print(f"\n{CYAN}{BOLD}")
    print(draw_box("", banner, color=CYAN))
    print(RESET)
    
    if total_files == 0:
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
    default_project_name = f"DJI"
    
    try:
        project_name = input(f"{MAGENTA}{BOLD}❓ Project name [default: {default_project_name}]: {RESET}").strip()
        delete_input = input(f"{MAGENTA}{BOLD}❓ Delete source files after import? [y/N]: {RESET}").strip().lower()
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
    try:
        for idx, file_info in enumerate(files_to_copy, 1):
            source_path = file_info["path"]
            filename = file_info["name"]
            ext = file_info["ext"]
            is_video = file_info["is_video"]
            
            media_type_dir = "Wideo" if is_video else "Zdjecia"
            sub_dir_name = get_subfolder_name(ext, is_video)
            
            target_sub_dir = os.path.join(project_dir, media_type_dir, sub_dir_name)
            os.makedirs(target_sub_dir, exist_ok=True)
            dest_path = os.path.join(target_sub_dir, filename)
            
            copy_file_chunked(
                source_path, 
                dest_path, 
                idx, 
                total_files, 
                overall_copied_ref, 
                total_bytes, 
                start_time, 
                filename
            )
            copied_counts[sub_dir_name] = copied_counts.get(sub_dir_name, 0) + 1
    except KeyboardInterrupt:
        sys.stdout.write("\n" * 2)
        cancel_lines = [
            f"{RED}⚠ IMPORT CANCELLED BY USER!{RESET}",
            "Copying process has stopped.",
            "Some files may not have been copied."
        ]
        print(draw_box("ABORTED", cancel_lines, color=RED))
        return
    finally:
        show_cursor()
        
    if delete_source:
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
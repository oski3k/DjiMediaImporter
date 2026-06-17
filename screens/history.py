# =============================================================================
#  screens/history.py — History and Statistics screens for DJI Media Importer
# =============================================================================

import os
import json
import sys
import time
from datetime import datetime
from collections import defaultdict

import config
import tui
from i18n import t
from utils import format_size

def load_history():
    """Load history from import_history.json."""
    if os.path.exists(config.HISTORY_FILE):
        try:
            with open(config.HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    """Save history to import_history.json."""
    try:
        with open(config.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def add_history_entry(entry):
    """Add a new history entry, keeping the last 50."""
    history = load_history()
    history.insert(0, entry)
    save_history(history[:50])

def history_tui():
    """Browse import history screen."""
    history = load_history()

    if not history:
        lines = [
            f"{tui.YELLOW}{t('history.empty')}{tui.RESET}",
            "",
            t("history.empty_hint"),
            "",
            f"{t('nav.esc_q_back')}",
        ]
        tui.clear_screen()
        print(f"\n{tui.CYAN}{tui.BOLD}")
        tui.print_banner()
        print(tui.draw_box(t("history.title"), lines, color=tui.CYAN))
        while tui.get_key() not in ("esc", "q", "enter"):
            pass
        return

    tag_filter = ""
    sel      = 0
    scroll   = 0
    viewport = 8
    first    = True
    n_clear  = 0

    tui.hide_cursor()
    try:
        while True:
            # Apply tag filter
            if tag_filter:
                filtered = [e for e in history if tag_filter.lower() in
                            [tg.lower() for tg in e.get("tags", [])]]
            else:
                filtered = history

            total = len(filtered)

            if first:
                tui.clear_screen()
                print(f"\n{tui.CYAN}{tui.BOLD}")
                tui.print_banner()

            lines = [
                f"{t('nav.arrows_enter_details')}",
                f"{t('history.nav_extra')}",
                "---",
            ]

            if tag_filter:
                lines.append(f"  {tui.YELLOW}{t('history.filtered', tag=tag_filter)}{tui.RESET}")
                lines.append("---")

            if total == 0:
                lines.append(f"  {tui.DIM}{t('history.empty')}{tui.RESET}")
            else:
                end = min(total, scroll + viewport)
                lines.append(f"  {tui.YELLOW}▲ ... ({scroll} {t('files.above')}){tui.RESET}" if scroll > 0 else "")

                for i in range(scroll, end):
                    e        = filtered[i]
                    focused  = (i == sel)
                    arrow    = f"{tui.GREEN}→{tui.RESET} " if focused else "  "
                    ts       = e.get("timestamp", "N/A")[:16]
                    proj     = e.get("project_name", "N/A")
                    n_files  = e.get("total_files", 0)
                    size_str = format_size(e.get("total_bytes", 0))
                    dur      = e.get("duration_seconds", 0)
                    dry_tag  = f" {tui.YELLOW}[DRY]{tui.RESET}" if e.get("dry_run") else ""
                    line     = f"{arrow}{ts}  {proj:<15} {n_files:>4} {t('general.files')}  {size_str:>9}  {dur:>4}s{dry_tag}"
                    lines.append(f"{tui.BOLD}{tui.CYAN}{line}{tui.RESET}" if focused else line)

                more = total - end
                lines.append(f"  {tui.YELLOW}▼ ... ({more} {t('files.below')}){tui.RESET}" if more > 0 else "")

            lines.append("---")
            lines.append(f"{tui.DIM}{t('history.total', count=total)}{tui.RESET}")

            if not first:
                sys.stdout.write(f"\033[{n_clear}A")
            box = tui.draw_box(t("history.title"), lines, color=tui.CYAN)
            sys.stdout.write(box + "\n")
            sys.stdout.flush()
            n_clear = len(box.split('\n'))
            first   = False

            key = tui.get_key()
            if total > 0:
                if key == "up":
                    if sel > 0:
                        sel -= 1
                        if sel < scroll: scroll = sel
                elif key == "down":
                    if sel < total - 1:
                        sel += 1
                        if sel >= scroll + viewport: scroll = sel - viewport + 1
                elif key == "enter":
                    tui.show_cursor()
                    sys.stdout.write(f"\033[{n_clear}A\033[J")
                    sys.stdout.flush()
                    _history_detail_tui(filtered[sel])
                    first   = True
                    n_clear = 0
                    tui.hide_cursor()
                    continue
                elif key == "o":
                    # Open folder in explorer
                    proj_dir = filtered[sel].get("project_dir", "")
                    if os.path.exists(proj_dir):
                        try:
                            if sys.platform == "win32":
                                os.startfile(proj_dir)
                            else:
                                import subprocess
                                subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", proj_dir])
                        except Exception:
                            pass
                    continue

            if key == "t":
                # Tag filter
                tui.show_cursor()
                sys.stdout.write(f"\033[{n_clear}A\033[J")
                sys.stdout.flush()
                try:
                    tag_filter = input(f"  {tui.MAGENTA}{tui.BOLD}{t('history.filter_tag')}{tui.RESET}").strip()
                except KeyboardInterrupt:
                    tag_filter = ""
                sel     = 0
                scroll  = 0
                first   = True
                n_clear = 0
                tui.hide_cursor()
            elif key in ("esc", "q"):
                break
    finally:
        tui.show_cursor()

def _history_detail_tui(entry):
    ts       = entry.get("timestamp", "N/A")
    proj     = entry.get("project_name", "N/A")
    proj_dir = entry.get("project_dir", "N/A")
    src      = entry.get("source_path", "N/A")
    n_files  = entry.get("total_files", 0)
    size_str = format_size(entry.get("total_bytes", 0))
    dur      = entry.get("duration_seconds", 0)
    deleted  = entry.get("delete_source", False)
    dry      = entry.get("dry_run", False)
    tags     = entry.get("tags", [])
    notes    = entry.get("notes", "")

    mode_str = f"{tui.YELLOW}{t('history.dry_run')}{tui.RESET}" if dry else f"{tui.GREEN}{t('history.completed')}{tui.RESET}"

    lines = [
        f"{tui.BOLD}{t('history.date')}{tui.RESET}        {ts}",
        f"{tui.BOLD}{t('history.project')}{tui.RESET}     {proj}",
        f"{tui.BOLD}{t('history.status')}{tui.RESET}      {mode_str}",
        "---",
        f"{tui.BOLD}{t('history.source')}{tui.RESET}      {src}",
        f"{tui.BOLD}{t('history.destination')}{tui.RESET} {proj_dir}",
        "---",
        f"{tui.BOLD}{t('history.files')}{tui.RESET}       {n_files}",
        f"{tui.BOLD}{t('history.total_size')}{tui.RESET}  {size_str}",
        f"{tui.BOLD}{t('history.duration')}{tui.RESET}    {dur}s",
        f"{tui.BOLD}{t('history.src_deleted')}{tui.RESET} {t('general.yes') if deleted else t('general.no')}",
    ]

    if tags:
        lines.append(f"{tui.BOLD}{t('history.tags')}{tui.RESET}       {', '.join(tags)}")
    if notes:
        lines.append(f"{tui.BOLD}{t('history.notes')}{tui.RESET}      {notes}")

    lines.append("")
    lines.append(f"{tui.DIM}{t('nav.any_key_back')}{tui.RESET}")

    print(tui.draw_box(t("history.detail_title"), lines, color=tui.CYAN))
    tui.get_key()

def statistics_tui():
    """Show global import statistics dashboard."""
    history = load_history()

    if not history:
        lines = [
            f"{tui.YELLOW}{t('stats.empty')}{tui.RESET}",
            "",
            t("stats.empty_hint"),
            "",
            f"{t('nav.esc_q_back')}",
        ]
        tui.clear_screen()
        print(f"\n{tui.CYAN}{tui.BOLD}")
        tui.print_banner()
        print(tui.draw_box(t("stats.title"), lines, color=tui.CYAN))
        while tui.get_key() not in ("esc", "q", "enter"):
            pass
        return

    # Calculate statistics
    real_imports = [e for e in history if not e.get("dry_run")]
    total_imports = len(real_imports)
    total_files   = sum(e.get("total_files", 0) for e in real_imports)
    total_bytes   = sum(e.get("total_bytes", 0) for e in real_imports)
    total_duration = sum(e.get("duration_seconds", 0) for e in real_imports)

    avg_size = total_bytes / total_imports if total_imports > 0 else 0
    avg_speed = total_bytes / total_duration if total_duration > 0 else 0

    if   avg_speed > 1024 * 1024: avg_speed_str = f"{avg_speed / 1024 / 1024:.1f} MB/s"
    elif avg_speed > 1024:         avg_speed_str = f"{avg_speed / 1024:.1f} KB/s"
    else:                          avg_speed_str = f"{avg_speed:.1f} B/s"

    # Group by month
    monthly = defaultdict(lambda: {"count": 0, "bytes": 0})
    for e in real_imports:
        ts = e.get("timestamp", "")[:7]  # "2026-06"
        if ts:
            monthly[ts]["count"] += 1
            monthly[ts]["bytes"] += e.get("total_bytes", 0)

    sorted_months = sorted(monthly.keys(), reverse=True)[:6]  # Last 6 months

    # Find max for bar scaling
    max_count = max((monthly[m]["count"] for m in sorted_months), default=1)

    # Top 3 largest imports
    top3 = sorted(real_imports, key=lambda e: e.get("total_bytes", 0), reverse=True)[:3]

    # Build lines
    lines = [
        f"{tui.BOLD}{t('stats.total_imports')}{tui.RESET}  {total_imports}",
        f"{tui.BOLD}{t('stats.total_files')}{tui.RESET}   {total_files}",
        f"{tui.BOLD}{t('stats.total_data')}{tui.RESET}    {format_size(total_bytes)}",
        f"{tui.BOLD}{t('stats.avg_size')}{tui.RESET}  {format_size(avg_size)}",
        f"{tui.BOLD}{t('stats.avg_speed')}{tui.RESET}       {tui.GREEN}{avg_speed_str}{tui.RESET}",
        "---",
    ]

    if sorted_months:
        lines.append(f"  {tui.BOLD}{t('stats.by_month')}{tui.RESET}")
        lines.append("")
        for m in sorted_months:
            info = monthly[m]
            bar_w = 20
            filled = int(bar_w * info["count"] / max_count) if max_count > 0 else 0
            bar = '█' * filled + '░' * (bar_w - filled)
            lines.append(f"  {m}  {tui.CYAN}{bar}{tui.RESET} {info['count']} {t('stats.imports')}  {format_size(info['bytes'])}")
        lines.append("")

    if top3:
        lines.append("---")
        lines.append(f"  {tui.BOLD}{t('stats.top')}{tui.RESET}")
        lines.append("")
        for i, e in enumerate(top3, 1):
            proj = e.get("project_name", "N/A")
            ts   = e.get("timestamp", "")[:10]
            size = format_size(e.get("total_bytes", 0))
            lines.append(f"  {tui.YELLOW}{i}.{tui.RESET} {ts}  {proj:<15}  {size}")

    lines.append("")
    lines.append(f"{tui.DIM}{t('nav.esc_q_back')}{tui.RESET}")

    tui.clear_screen()
    print(f"\n{tui.CYAN}{tui.BOLD}")
    tui.print_banner()
    print(tui.draw_box(t("stats.title"), lines, color=tui.CYAN))

    while tui.get_key() not in ("esc", "q", "enter"):
        pass

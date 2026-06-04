# DJI Media Importer Pro

A high-performance, zero-dependency TUI (Terminal User Interface) utility designed for drone pilots, videographers, and creators. It automates media transfers from connected DJI SD cards or drones, organizes them into categorized structures, and optionally cleans up the source card—all with zero friction.

---

## Key Features

- **Live Device Detection Spinner**: Actively monitors system drives for a `DCIM` directory and starts importing automatically once connected.
- **Flicker-Free Terminal Rendering**: Uses raw ANSI cursor-repositioning escape sequences (`\033[A` and `\033[H`) to overwrite progress lines in-place instead of clearing the screen, providing a smooth desktop-app experience.
- **Chunked File Copying with Metrics**: Copies files in 4MB memory buffers rather than using blocking system calls. This enables continuous progress tracking, transfer speed measurements (MB/s), and real-time remaining time (ETA) calculations.
- **Zero-Click Default Naming**: Suggests default project folder names (e.g. `Flight_YYYY-MM-DD`). Users can hit **Enter** to instantly accept and run, requiring no typing.
- **Dynamic Save Paths & Fallbacks**: Defaults imports to a configured storage folder (e.g., `E:\Dron`). If the drive is missing, it dynamically falls back to the user's home Pictures directory (`~/Pictures/Drone_Imports`) to prevent write failures.
- **Secure Post-Import Cleanup**: Prompts the user before deleting files from the card. Files are only deleted using secure system handles *after* the entire copy task completes successfully.
- **Automated Directory Layout**: Automatically sorts files by type and extension into structures like:
  ```text
  Destination/
  ├── Wideo/
  │   ├── MP4/
  │   └── MOV/
  └── Zdjecia/
      ├── JPG/
      └── RAW/
  ```

---

## Preview

```text
╭── MEDIA SUMMARY ───────────────────────────────────────────────╮
│ ✔ Device ready for import                                      │
├────────────────────────────────────────────────────────────────┤
│ Source Path:      F:\DCIM                                      │
│ Video files:      2 files (0.36 GB)                            │
│ Photo files:      26 files (1.09 GB)                           │
│ Total files:      28 files                                     │
│ Total size:       1.45 GB                                      │
╰────────────────────────────────────────────────────────────────╯

❓ Project name [default: DJI]: 
❓ Delete source files after import? [y/N]: 
```

```text
╭── COPYING MEDIA ───────────────────────────────────────────────╮
│ Destination:  E:\Dron\2026-06-04 - DJI                         │
├────────────────────────────────────────────────────────────────┤
│ Overall progress: [████████████████░░░░░░░░░░░░░░] 50.2%       │
│ Copying file:     [15/28] DJI_0012.JPG                         │
│ File size:        8.00 MB / 25.41 MB                           │
│ Total progress:   746.40 MB / 1.45 GB                          │
│ Transfer speed:   86.6 MB/s | Remaining: 8s                    │
╰────────────────────────────────────────────────────────────────╯
```

---

## Tech Stack & Architecture

- **Core Language**: Python 3 (Tested on Python 3.14+)
- **Dependencies**: None (Uses Python standard library only: `os`, `shutil`, `re`, `time`, `sys`, `string`, `datetime`)
- **System Compatibility**: Windows (via Command Prompt / PowerShell with enabled VT mode via `os.system('')`), macOS, and Linux.

---

## Usage

### Windows
1. Double-click the provided `Start_DjiSaver.bat` script.
2. Insert your SD card or connect the drone.
3. Accept/Enter the project name, choose folder cleanup, and watch the import complete.

### macOS / Linux
Run the Python script directly from your terminal:
```bash
python main.py
```

---

## Customization

You can change the target directory by editing the variable at the top of `main.py`:
```python
TARGET_ROOT = r"E:\Dron"
```
If this directory is not available, it automatically falls back to:
`~/Pictures/Drone_Imports`

# =============================================================================
#  config.py — Configuration management for DJI Media Importer
# =============================================================================

import os
import json

CONFIG_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "import_history.json")
RESUME_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".import_state.json")

DEFAULT_CONFIG = {
    "TARGET_ROOT":            r"E:\Dron",
    "VIDEO_EXTENSIONS":       [".mp4", ".mov", ".mkv"],
    "PHOTO_EXTENSIONS":       [".jpg", ".jpeg", ".dng", ".raw", ".png"],
    "BUFFER_SIZE_MB":         4,
    "DEFAULT_PROJECT_NAME":   "DJI",
    "DEFAULT_DELETE_SOURCE":  False,
    "FOLDER_STRUCTURE":       "category_and_ext",
    "FILENAME_PATTERN":       "{original}",
    "DUPLICATE_ACTION":       "skip_if_same_otherwise_rename",
    "LANGUAGE":               "pl",
    "THEME":                  "default",
}


def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                cfg.update(loaded)
        except Exception as e:
            print(f"Warning: Failed to load config.json ({e}). Using defaults.")
    else:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
        except Exception:
            pass
    return cfg


def save_config_raw(raw_config):
    """Save raw config dict (lists, not sets) to config.json."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(raw_config, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def prepare_config(cfg):
    """Convert extension lists to sets (lowercase)."""
    cfg["VIDEO_EXTENSIONS"] = {ext.lower() for ext in cfg["VIDEO_EXTENSIONS"]}
    cfg["PHOTO_EXTENSIONS"] = {ext.lower() for ext in cfg["PHOTO_EXTENSIONS"]}
    return cfg


def get_target_root(cfg):
    """Return target root, falling back to ~/Pictures/Drone_Imports if missing."""
    target_root = cfg.get("TARGET_ROOT", DEFAULT_CONFIG["TARGET_ROOT"])
    if not os.path.exists(target_root):
        target_root = os.path.join(os.path.expanduser("~"), "Pictures", "Drone_Imports")
    return target_root


def reload():
    """Reload config from disk and update module-level state."""
    global CONFIG, VIDEO_EXTENSIONS, PHOTO_EXTENSIONS
    CONFIG = prepare_config(load_config())
    VIDEO_EXTENSIONS = CONFIG["VIDEO_EXTENSIONS"]
    PHOTO_EXTENSIONS = CONFIG["PHOTO_EXTENSIONS"]


# ── Module-level state (shared across all modules via `config.CONFIG`) ───────
CONFIG           = prepare_config(load_config())
VIDEO_EXTENSIONS = CONFIG["VIDEO_EXTENSIONS"]
PHOTO_EXTENSIONS = CONFIG["PHOTO_EXTENSIONS"]

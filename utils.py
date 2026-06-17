# =============================================================================
#  utils.py — Utility functions for DJI Media Importer
# =============================================================================

import os
import shutil
import hashlib
import config

def format_size(bytes_size):
    """Format bytes into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def get_free_space(path):
    """Get free space on the disk containing path."""
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

def get_file_md5(filepath):
    """Calculate MD5 hash of a file using standard buffer size."""
    hasher = hashlib.md5()
    buf = config.CONFIG.get("BUFFER_SIZE_MB", 4) * 1024 * 1024
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(buf)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

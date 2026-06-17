# =============================================================================
#  themes.py — Color themes for DJI Media Importer
# =============================================================================

THEMES = {
    "default": {
        "label":     "Default (Cyan)",
        "primary":   "\033[36m",    # Cyan   — main UI boxes, navigation
        "accent":    "\033[35m",    # Magenta — settings, prompts
        "highlight": "\033[32m",    # Green  — arrows, checkmarks, success
        "error":     "\033[31m",    # Red    — errors
        "warning":   "\033[33m",    # Yellow — warnings, status
    },
    "neon": {
        "label":     "Neon Green",
        "primary":   "\033[32m",    # Green
        "accent":    "\033[33m",    # Yellow
        "highlight": "\033[36m",    # Cyan
        "error":     "\033[31m",    # Red
        "warning":   "\033[33m",    # Yellow
    },
    "ocean": {
        "label":     "Ocean Blue",
        "primary":   "\033[34m",    # Blue
        "accent":    "\033[36m",    # Cyan
        "highlight": "\033[32m",    # Green
        "error":     "\033[31m",    # Red
        "warning":   "\033[33m",    # Yellow
    },
    "sunset": {
        "label":     "Sunset",
        "primary":   "\033[33m",    # Yellow
        "accent":    "\033[31m",    # Red
        "highlight": "\033[35m",    # Magenta
        "error":     "\033[31m",    # Red
        "warning":   "\033[33m",    # Yellow
    },
}


def get_theme(name):
    """Return a theme dict by name. Falls back to 'default'."""
    return THEMES.get(name, THEMES["default"])


def get_theme_names():
    """Return list of available theme names."""
    return list(THEMES.keys())


def get_theme_labels():
    """Return list of (name, label) tuples for display."""
    return [(k, v["label"]) for k, v in THEMES.items()]

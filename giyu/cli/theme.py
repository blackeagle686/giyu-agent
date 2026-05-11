"""
Centralized design tokens for the Giyu TUI.
All colors and styles are defined here to keep screens consistent.
"""

from textual.theme import Theme

# ── Modern Premium Palette ───────────────────────────────────────────────────
# Backgrounds
# ── Giyu Design Tokens (Synced with Dashboard) ────────────────────────────────
# Backgrounds
GIYU_DARK     = "#020408"  # Deep Onyx
GIYU_SURFACE  = "#0A0C14"  # Obsidian Surface
GIYU_PANEL    = "#12161D"  # Slate Panel

# Accents
GIYU_CYAN     = "#00f2ff"  # Electric Cyan
GIYU_PURPLE   = "#7000ff"  # Plasma Purple
GIYU_MAGENTA  = "#FF00FF"  # Neon Magenta
GIYU_GLOW     = "#00B4D8"  # Cyber Blue

# Functional
GIYU_BORDER   = "#1C2128"  # Steel Border
GIYU_MUTED    = "#484F58"  # Iron Gray
GIYU_DIMTEXT  = "#94a3b8"  # Muted Ash
GIYU_TEXT     = "#e2e8f0"  # Soft Cloud
GIYU_SUCCESS  = "#10b981"  # Emerald
GIYU_ERROR    = "#ef4444"  # Crimson
GIYU_WARNING  = "#f59e0b"  # Amber

# ── Textual Theme ────────────────────────────────────────────────────────────
GIYU_THEME = Theme(
    name="giyu",
    primary=GIYU_CYAN,
    secondary=GIYU_PURPLE,
    accent=GIYU_CYAN,
    background=GIYU_DARK,
    surface=GIYU_SURFACE,
    panel=GIYU_PANEL,
    boost=GIYU_MUTED,
    warning=GIYU_WARNING,
    error=GIYU_ERROR,
    success=GIYU_SUCCESS,
    dark=True,
)

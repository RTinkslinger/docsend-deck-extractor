"""Canva-inspired styling for the Mac app.

Defines QSS stylesheets and color constants for consistent UI.
"""

# Color Palette (Canva-inspired)
COLORS = {
    "primary": "#8B5CF6",  # Purple
    "primary_hover": "#7C3AED",
    "background": "#FFFFFF",
    "surface": "#F9FAFB",
    "border": "#E5E7EB",
    "text_primary": "#111827",
    "text_secondary": "#6B7280",
    "text_muted": "#9CA3AF",
    "success": "#10B981",
    "error": "#EF4444",
}

# Typography
FONTS = {
    "family": ".AppleSystemUIFont, 'Helvetica Neue', sans-serif",
    "title_size": "16px",
    "subtitle_size": "14px",
    "body_size": "14px",
    "secondary_size": "13px",
    "caption_size": "12px",
}

# Spacing
SPACING = {
    "tight": "4px",
    "compact": "8px",
    "default": "12px",
    "comfortable": "16px",
    "spacious": "24px",
}

# Main window stylesheet
MAIN_WINDOW_STYLE = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}
"""

# Button styles
BUTTON_PRIMARY_STYLE = f"""
QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: {FONTS['body_size']};
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {COLORS['primary_hover']};
}}
QPushButton:pressed {{
    background-color: {COLORS['primary_hover']};
}}
QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_muted']};
}}
"""

BUTTON_SECONDARY_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: {FONTS['body_size']};
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {COLORS['surface']};
    border-color: {COLORS['text_muted']};
}}
QPushButton:pressed {{
    background-color: {COLORS['border']};
}}
"""

BUTTON_TEXT_STYLE = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['primary']};
    border: none;
    padding: 8px;
    font-size: {FONTS['secondary_size']};
}}
QPushButton:hover {{
    color: {COLORS['primary_hover']};
    text-decoration: underline;
}}
"""

# Input styles
INPUT_STYLE = f"""
QLineEdit {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    font-size: {FONTS['body_size']};
}}
QLineEdit:focus {{
    border-color: {COLORS['primary']};
    outline: none;
}}
QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}
"""

# Label styles
LABEL_TITLE_STYLE = f"""
QLabel {{
    color: {COLORS['text_primary']};
    font-size: {FONTS['title_size']};
    font-weight: 600;
}}
"""

LABEL_SUBTITLE_STYLE = f"""
QLabel {{
    color: {COLORS['text_primary']};
    font-size: {FONTS['subtitle_size']};
    font-weight: 500;
}}
"""

LABEL_BODY_STYLE = f"""
QLabel {{
    color: {COLORS['text_secondary']};
    font-size: {FONTS['body_size']};
}}
"""

LABEL_CAPTION_STYLE = f"""
QLabel {{
    color: {COLORS['text_muted']};
    font-size: {FONTS['caption_size']};
}}
"""

LABEL_SUCCESS_STYLE = f"""
QLabel {{
    color: {COLORS['success']};
    font-size: {FONTS['caption_size']};
}}
"""

LABEL_ERROR_STYLE = f"""
QLabel {{
    color: {COLORS['error']};
    font-size: {FONTS['caption_size']};
}}
"""

# Progress bar style
PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    background-color: {COLORS['surface']};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 4px;
}}
"""

# Card/container style
CARD_STYLE = f"""
QFrame {{
    background-color: {COLORS['background']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
"""

# Scrollbar style
SCROLLBAR_STYLE = f"""
QScrollBar:vertical {{
    background-color: {COLORS['surface']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

# Combined application stylesheet
APP_STYLESHEET = f"""
* {{
    font-family: {FONTS['family']};
}}

{MAIN_WINDOW_STYLE}
{SCROLLBAR_STYLE}
"""


def get_stylesheet() -> str:
    """Get the complete application stylesheet."""
    return APP_STYLESHEET

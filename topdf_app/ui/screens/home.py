"""Home screen with URL input.

The primary screen where users paste DocSend URLs to convert.
"""

from __future__ import annotations

import re
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QApplication,
)
from PySide6.QtCore import Signal, Qt, QTimer

from topdf_app.ui import styles


# DocSend URL pattern
DOCSEND_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?docsend\.com/view/[a-zA-Z0-9]+",
    re.IGNORECASE,
)


def is_valid_docsend_url(url: str) -> bool:
    """Check if a URL is a valid DocSend document URL.

    Args:
        url: URL string to validate

    Returns:
        True if valid DocSend URL
    """
    return bool(DOCSEND_URL_PATTERN.match(url.strip()))


class HomeScreen(QWidget):
    """Home screen with URL input.

    Signals:
        convert_clicked: Emitted when convert button is clicked with URL
        settings_clicked: Emitted when settings button is clicked
    """

    convert_clicked = Signal(str)  # url
    settings_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize home screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self._toast_timer: Optional[QTimer] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header with title and settings
        header = self._create_header()
        layout.addLayout(header)

        # URL input section
        url_section = self._create_url_input()
        layout.addWidget(url_section)

        # Status label (for clipboard detection feedback)
        self.status_label = QLabel()
        self.status_label.setStyleSheet(styles.LABEL_SUCCESS_STYLE)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Convert button
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.clicked.connect(self._on_convert_clicked)
        self.convert_btn.setEnabled(False)
        layout.addWidget(self.convert_btn)

        # Flexible space
        layout.addStretch()

        # Toast message (hidden by default, shows above Quit button)
        self.toast_label = QLabel()
        self.toast_label.setStyleSheet(f"""
            QLabel {{
                background-color: {styles.COLORS['text_secondary']};
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 13px;
            }}
        """)
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.hide()
        layout.addWidget(self.toast_label)

    def _create_header(self) -> QHBoxLayout:
        """Create the header with title and settings button.

        Returns:
            Header layout
        """
        header = QHBoxLayout()

        title = QLabel("DocSend to PDF")
        title.setStyleSheet(styles.LABEL_TITLE_STYLE)
        header.addWidget(title)

        header.addStretch()

        settings_btn = QPushButton()
        settings_btn.setText("\u2699\uFE0F")  # Gear emoji with variation selector
        settings_btn.setFixedSize(36, 36)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                color: {styles.COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['surface']};
                color: {styles.COLORS['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {styles.COLORS['border']};
            }}
        """)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setToolTip("Settings")
        settings_btn.clicked.connect(self.settings_clicked.emit)
        header.addWidget(settings_btn)

        return header

    def _create_url_input(self) -> QWidget:
        """Create the URL input section with icon outside frame.

        Returns:
            Container widget with icon and input frame
        """
        # Container for icon + frame
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)

        # Link icon (OUTSIDE the frame)
        icon_label = QLabel("\U0001F517")  # Link emoji
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {styles.COLORS['text_muted']};
                font-size: 18px;
            }}
        """)
        container_layout.addWidget(icon_label)

        # Input frame (contains text field and paste button)
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 8, 8)
        layout.setSpacing(8)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste DocSend URL")
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {styles.COLORS['text_primary']};
                font-size: {styles.FONTS['body_size']};
            }}
        """)
        self.url_input.textChanged.connect(self._on_url_changed)
        layout.addWidget(self.url_input, 1)

        # Paste button
        self.paste_btn = QPushButton("\U0001F4CB")  # Clipboard emoji
        self.paste_btn.setFixedSize(32, 32)
        self.paste_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['border']};
            }}
            QPushButton:pressed {{
                background-color: {styles.COLORS['text_muted']};
            }}
        """)
        self.paste_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paste_btn.setToolTip("Paste from clipboard")
        self.paste_btn.clicked.connect(self._on_paste_clicked)
        layout.addWidget(self.paste_btn)

        container_layout.addWidget(frame, 1)  # Frame stretches

        return container

    def _on_paste_clicked(self) -> None:
        """Handle paste button click - paste from clipboard if valid DocSend URL."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self._show_toast("Could not access clipboard")
            self.url_input.clear()
            return

        text = clipboard.text()
        if text and is_valid_docsend_url(text.strip()):
            self.url_input.setText(text.strip())
            self.url_input.setFocus()
        else:
            # Clear field and show toast for invalid/missing URL
            self.url_input.clear()
            self._show_toast("No DocSend URL in clipboard")

    def _show_toast(self, message: str, duration_ms: int = 2500) -> None:
        """Show a temporary toast message above the Quit button.

        Args:
            message: Message to display
            duration_ms: How long to show the toast (default 2.5 seconds)
        """
        # Cancel any existing toast timer
        if self._toast_timer is not None:
            self._toast_timer.stop()

        self.toast_label.setText(message)
        self.toast_label.show()

        # Setup timer to hide toast
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self._hide_toast)
        self._toast_timer.start(duration_ms)

    def _hide_toast(self) -> None:
        """Hide the toast message."""
        self.toast_label.hide()

    def _on_url_changed(self, text: str) -> None:
        """Handle URL input text change.

        Args:
            text: Current input text
        """
        is_valid = is_valid_docsend_url(text)
        self.convert_btn.setEnabled(is_valid)

        if text.strip() and not is_valid:
            self.status_label.setText("Enter a valid DocSend URL")
            self.status_label.setStyleSheet(styles.LABEL_ERROR_STYLE)
        elif not text.strip():
            self.status_label.setText("")
        else:
            self.status_label.setText("\u2713 Valid URL")
            self.status_label.setStyleSheet(styles.LABEL_SUCCESS_STYLE)

    def _on_convert_clicked(self) -> None:
        """Handle convert button click."""
        url = self.url_input.text().strip()
        if is_valid_docsend_url(url):
            # Emit signal FIRST - this synchronously sets block_focus_hide
            # flag in main_window before we disable the input
            self.convert_clicked.emit(url)
            self.set_loading(True)

    def set_loading(self, loading: bool) -> None:
        """Set the loading state of the convert button.

        Args:
            loading: Whether to show loading state
        """
        if loading:
            self.convert_btn.setEnabled(False)
            self.convert_btn.setText("Converting...")
            self.url_input.setEnabled(False)
        else:
            self.convert_btn.setEnabled(True)
            self.convert_btn.setText("Convert")
            self.url_input.setEnabled(True)

    def clear_input(self) -> None:
        """Clear the URL input field."""
        self.url_input.clear()
        self.status_label.setText("")
        self.set_loading(False)

    def set_url(self, url: str) -> None:
        """Set the URL input field.

        Args:
            url: URL to set
        """
        self.url_input.setText(url)

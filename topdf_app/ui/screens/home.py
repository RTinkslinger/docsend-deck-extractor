"""Home screen with URL input and history.

The primary screen where users paste DocSend URLs to convert.
"""

from __future__ import annotations

import re
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QApplication,
    QSizePolicy,
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


class HistoryItemWidget(QFrame):
    """A single history item in the list."""

    clicked = Signal(str)  # pdf_path

    def __init__(
        self,
        name: str,
        pdf_path: str,
        relative_time: str,
        has_summary: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """Initialize history item.

        Args:
            name: Document name
            pdf_path: Path to PDF
            relative_time: Relative time string
            has_summary: Whether has AI summary
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._setup_ui(name, relative_time, has_summary)

    def _setup_ui(self, name: str, relative_time: str, has_summary: bool) -> None:
        """Setup the UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                padding: 4px 0;
            }}
            QFrame:hover {{
                background-color: {styles.COLORS['surface']};
                border-radius: 4px;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # Document icon
        icon = QLabel("\U0001F4C4")  # Page icon
        icon.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon)

        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {styles.COLORS['text_primary']};
                font-size: {styles.FONTS['secondary_size']};
            }}
        """)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(name_label, 1)

        # Summary indicator
        if has_summary:
            summary_icon = QLabel("\u2728")
            summary_icon.setToolTip("Has AI summary")
            layout.addWidget(summary_icon)

        # Time
        time_label = QLabel(relative_time)
        time_label.setStyleSheet(styles.LABEL_CAPTION_STYLE)
        layout.addWidget(time_label)

    def mousePressEvent(self, event) -> None:
        """Handle click to open PDF."""
        self.clicked.emit(self._pdf_path)
        super().mousePressEvent(event)


class HomeScreen(QWidget):
    """Home screen with URL input.

    Signals:
        convert_clicked: Emitted when convert button is clicked with URL
        settings_clicked: Emitted when settings button is clicked
        history_item_clicked: Emitted when a history item is clicked
    """

    convert_clicked = Signal(str)  # url
    settings_clicked = Signal()
    history_item_clicked = Signal(str)  # pdf_path

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize home screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self._clipboard_url: Optional[str] = None
        self._setup_ui()
        self._setup_clipboard_detection()

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

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {styles.COLORS['border']};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # Recent section header
        recent_header = QHBoxLayout()
        recent_label = QLabel("Recent")
        recent_label.setStyleSheet(styles.LABEL_SUBTITLE_STYLE)
        recent_header.addWidget(recent_label)
        recent_header.addStretch()
        layout.addLayout(recent_header)

        # History container
        self.history_container = QFrame()
        self.history_container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
        """)
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(12, 12, 12, 12)
        self.history_layout.setSpacing(4)

        # Empty state label
        self.empty_label = QLabel("No recent conversions")
        self.empty_label.setStyleSheet(styles.LABEL_CAPTION_STYLE)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_layout.addWidget(self.empty_label)

        layout.addWidget(self.history_container)
        layout.addStretch()

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

    def _create_url_input(self) -> QFrame:
        """Create the URL input section.

        Returns:
            URL input frame
        """
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Link icon
        icon_label = QLabel("\U0001F517")  # Link emoji
        icon_label.setStyleSheet(f"color: {styles.COLORS['text_muted']};")
        layout.addWidget(icon_label)

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

        return frame

    def _setup_clipboard_detection(self) -> None:
        """Setup clipboard monitoring for DocSend URLs."""
        # Check clipboard on focus
        self._check_clipboard()

        # Setup timer for periodic clipboard checking
        self._clipboard_timer = QTimer(self)
        self._clipboard_timer.timeout.connect(self._check_clipboard)
        self._clipboard_timer.start(1000)  # Check every second

    def _check_clipboard(self) -> None:
        """Check clipboard for DocSend URLs."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return

        text = clipboard.text()
        if text and is_valid_docsend_url(text):
            if text != self._clipboard_url:
                self._clipboard_url = text
                self._show_clipboard_detected(text)

    def _show_clipboard_detected(self, url: str) -> None:
        """Show clipboard detection feedback.

        Args:
            url: The detected URL
        """
        self.status_label.setText("\u2713 DocSend URL detected in clipboard")
        self.status_label.setStyleSheet(styles.LABEL_SUCCESS_STYLE)

        # Auto-fill if input is empty
        if not self.url_input.text().strip():
            self.url_input.setText(url)

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
            self.set_loading(True)
            self.convert_clicked.emit(url)

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
        self._clipboard_url = None
        self.status_label.setText("")
        self.set_loading(False)

    def set_url(self, url: str) -> None:
        """Set the URL input field.

        Args:
            url: URL to set
        """
        self.url_input.setText(url)

    def showEvent(self, event) -> None:
        """Handle show event to check clipboard.

        Args:
            event: Show event
        """
        super().showEvent(event)
        self._check_clipboard()

    def update_history(self, entries: List[dict]) -> None:
        """Update the history display.

        Args:
            entries: List of history entry dicts with keys:
                - name: Document name
                - pdf_path: Path to PDF
                - relative_time: Relative time string
                - has_summary: Whether has AI summary
        """
        # Clear existing items (except empty label)
        while self.history_layout.count() > 1:
            item = self.history_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        if not entries:
            self.empty_label.show()
            return

        self.empty_label.hide()

        # Add history items
        for entry in entries[:3]:  # Show max 3 on home screen
            item = HistoryItemWidget(
                name=entry["name"],
                pdf_path=entry["pdf_path"],
                relative_time=entry["relative_time"],
                has_summary=entry.get("has_summary", False),
                parent=self.history_container,
            )
            item.clicked.connect(self.history_item_clicked.emit)
            self.history_layout.addWidget(item)

"""Error screen showing conversion failure.

Displays error message with expandable details and retry option.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QSequentialAnimationGroup, QTimer

from topdf_app.ui import styles


class ErrorScreen(QWidget):
    """Error screen with retry and back options.

    Signals:
        retry_clicked: Emitted when retry button is clicked
        back_clicked: Emitted when back button is clicked
    """

    retry_clicked = Signal()
    back_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize error screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self._error_message: str = ""
        self._error_details: str = ""
        self._details_visible: bool = False

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header with back arrow
        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190")  # Left arrow
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 18px;
                color: {styles.COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                color: {styles.COLORS['text_primary']};
            }}
        """)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        header.addWidget(self.back_btn)

        title = QLabel("Conversion Failed")
        title.setStyleSheet(styles.LABEL_TITLE_STYLE)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Spacer
        layout.addStretch()

        # Error icon
        icon_container = QHBoxLayout()
        icon_container.addStretch()
        self.icon_label = QLabel("\u2717")  # X mark
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                color: {styles.COLORS['error']};
                background-color: #FEE2E2;
                border-radius: 40px;
                padding: 16px 20px;
            }}
        """)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(self.icon_label)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        layout.addSpacing(16)

        # Error message
        self.message_label = QLabel("An error occurred")
        self.message_label.setStyleSheet(styles.LABEL_SUBTITLE_STYLE)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Description
        self.description_label = QLabel(
            "The conversion could not be completed.\n"
            "Please check your internet connection and try again."
        )
        self.description_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        # Expandable details section
        self.details_container = QFrame()
        self.details_container.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
        """)
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(12, 8, 12, 8)
        details_layout.setSpacing(8)

        # Toggle button
        self.toggle_btn = QPushButton("\u25B6  Show Details")  # Right triangle
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {styles.COLORS['text_secondary']};
                font-size: {styles.FONTS['caption_size']};
                text-align: left;
                padding: 4px;
            }}
            QPushButton:hover {{
                color: {styles.COLORS['text_primary']};
            }}
        """)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_details)
        details_layout.addWidget(self.toggle_btn)

        # Details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {styles.COLORS['surface']};
                border: none;
                color: {styles.COLORS['text_secondary']};
                font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
                font-size: 11px;
            }}
        """)
        self.details_text.setFixedHeight(100)
        self.details_text.hide()
        details_layout.addWidget(self.details_text)

        layout.addWidget(self.details_container)

        # Spacer
        layout.addStretch()

        # Retry button
        self.retry_btn = QPushButton("Retry")
        self.retry_btn.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.retry_btn.setMinimumHeight(44)
        self.retry_btn.clicked.connect(self.retry_clicked.emit)
        layout.addWidget(self.retry_btn)

        # Back to Home link
        self.home_btn = QPushButton("Back to Home")
        self.home_btn.setStyleSheet(styles.BUTTON_TEXT_STYLE)
        self.home_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.home_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self.home_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_animations(self) -> None:
        """Setup error animation effects."""
        # Opacity effect for fade-in
        self.icon_opacity = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.icon_opacity)
        self.icon_opacity.setOpacity(1.0)

        # Store original position for shake
        self._original_style = self.icon_label.styleSheet()
        self._shake_step = 0

    def play_error_animation(self) -> None:
        """Play shake animation for error feedback."""
        # Fade in and shake effect
        self.icon_opacity.setOpacity(0.0)

        # Quick fade in
        self.fade_anim = QPropertyAnimation(self.icon_opacity, b"opacity")
        self.fade_anim.setDuration(200)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        # Start shake after fade
        QTimer.singleShot(100, self._do_shake)

    def _do_shake(self) -> None:
        """Perform the shake animation via stylesheet margin changes."""
        self._shake_step = 0
        self._shake_timer = QTimer(self)
        self._shake_timer.timeout.connect(self._shake_tick)
        self._shake_timer.start(50)

    def _shake_tick(self) -> None:
        """One frame of the shake animation."""
        # Shake pattern: right, left, right, left, center
        offsets = [8, -8, 6, -6, 4, -4, 2, -2, 0]

        if self._shake_step < len(offsets):
            offset = offsets[self._shake_step]
            self.icon_label.setStyleSheet(
                self._original_style +
                f"\nQLabel {{ margin-left: {offset}px; }}"
            )
            self._shake_step += 1
        else:
            self._shake_timer.stop()
            self.icon_label.setStyleSheet(self._original_style)

    def _toggle_details(self) -> None:
        """Toggle visibility of error details."""
        self._details_visible = not self._details_visible

        if self._details_visible:
            self.details_text.show()
            self.toggle_btn.setText("\u25BC  Hide Details")  # Down triangle
        else:
            self.details_text.hide()
            self.toggle_btn.setText("\u25B6  Show Details")  # Right triangle

    def set_error(self, message: str, details: str = "") -> None:
        """Set the error to display.

        Args:
            message: User-friendly error message
            details: Technical details (traceback)
        """
        self._error_message = message
        self._error_details = details

        # Parse error message for better display
        display_message = message
        if ":" in message:
            # Extract the main error type
            parts = message.split(":", 1)
            display_message = parts[-1].strip()

        self.message_label.setText(display_message[:100])  # Truncate if too long
        self.details_text.setPlainText(details if details else message)

        # Set appropriate description based on error type
        description = self._get_error_description(message.lower())
        self.description_label.setText(description)

        # Reset details visibility
        self._details_visible = False
        self.details_text.hide()
        self.toggle_btn.setText("\u25B6  Show Details")

    def _get_error_description(self, error: str) -> str:
        """Get a helpful description based on error type.

        Args:
            error: Lowercase error message

        Returns:
            User-friendly description
        """
        if "timeout" in error or "timed out" in error:
            return "The connection took too long.\nCheck your internet and try again."
        elif ("network" in error or "connection" in error) and "timed" not in error:
            return "Network connection failed.\nPlease check your internet connection."
        elif "invalid" in error and ("email" in error or "passcode" in error):
            return "The credentials were rejected.\nPlease check and try again."
        elif "permission" in error:
            return "Cannot save to this location.\nTry a different folder in Settings."
        elif "url" in error:
            return "The URL format is invalid.\nMake sure it's a DocSend link."
        elif "load" in error:
            return "Could not load the document.\nIt may be unavailable or restricted."
        elif "tesseract" in error:
            return "OCR engine not found.\nInstall Tesseract for AI summaries."
        elif "api" in error or "key" in error:
            return "API key issue.\nCheck your Perplexity key in Settings."
        else:
            return "The conversion could not be completed.\nPlease check your internet and try again."

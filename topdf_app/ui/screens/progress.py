"""Progress screen showing conversion status.

Displays a progress bar and status message during conversion.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Signal, Qt, QTimer, QPropertyAnimation, QEasingCurve

from topdf_app.ui import styles


class ProgressScreen(QWidget):
    """Progress screen with progress bar and cancel button.

    Signals:
        cancel_clicked: Emitted when cancel button is clicked
        back_clicked: Emitted when back arrow is clicked
    """

    cancel_clicked = Signal()
    back_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize progress screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
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

        self.title_label = QLabel("Converting...")
        self.title_label.setStyleSheet(styles.LABEL_TITLE_STYLE)
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        # Spacer
        layout.addStretch()

        # Animated document icon (placeholder - using emoji for now)
        icon_container = QHBoxLayout()
        icon_container.addStretch()
        self.icon_label = QLabel("\U0001F4C4")  # Document emoji
        self.icon_label.setStyleSheet("font-size: 48px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(self.icon_label)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        layout.addSpacing(16)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet(styles.PROGRESS_BAR_STYLE + f"""
            QProgressBar {{
                height: 12px;
                font-size: {styles.FONTS['caption_size']};
            }}
        """)
        layout.addWidget(self.progress_bar)

        layout.addSpacing(8)

        # Status message
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Spacer
        layout.addStretch()

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
        self.cancel_btn.setMinimumHeight(44)
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

    def _setup_animations(self) -> None:
        """Setup pulsing animation for the document icon."""
        # Create opacity effect for icon
        self.icon_opacity = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.icon_opacity)

        # Create pulsing animation
        self.pulse_animation = QPropertyAnimation(self.icon_opacity, b"opacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.5)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.setLoopCount(-1)  # Infinite loop

        # Make it ping-pong (fade in and out)
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._toggle_pulse_direction)
        self.pulse_timer.setInterval(1000)

        self._pulse_direction = 1

    def _toggle_pulse_direction(self) -> None:
        """Toggle the pulse animation direction."""
        if self._pulse_direction == 1:
            self.pulse_animation.setStartValue(0.5)
            self.pulse_animation.setEndValue(1.0)
        else:
            self.pulse_animation.setStartValue(1.0)
            self.pulse_animation.setEndValue(0.5)
        self._pulse_direction *= -1
        self.pulse_animation.start()

    def start_animation(self) -> None:
        """Start the pulsing animation."""
        self.pulse_animation.start()
        self.pulse_timer.start()

    def stop_animation(self) -> None:
        """Stop the pulsing animation."""
        self.pulse_animation.stop()
        self.pulse_timer.stop()
        self.icon_opacity.setOpacity(1.0)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelling...")
        self.cancel_clicked.emit()

    def set_progress(self, percent: int, message: str) -> None:
        """Update progress display.

        Args:
            percent: Progress percentage (0-100)
            message: Status message to display
        """
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

        # Update title based on progress
        if percent < 100:
            self.title_label.setText("Converting...")
        else:
            self.title_label.setText("Almost done...")

    def reset(self) -> None:
        """Reset screen to initial state."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")
        self.title_label.setText("Converting...")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.stop_animation()

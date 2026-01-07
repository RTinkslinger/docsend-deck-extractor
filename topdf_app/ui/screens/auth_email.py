"""Auth email screen for email-gated documents.

Prompts user to enter their email to access the document.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Signal, Qt

from topdf_app.ui import styles


class AuthEmailScreen(QWidget):
    """Email authentication screen.

    Signals:
        submit_clicked: Emitted with email when continue is clicked
        cancel_clicked: Emitted when user cancels
    """

    submit_clicked = Signal(str)  # email
    cancel_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize auth email screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._setup_ui()

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
        self.back_btn.clicked.connect(self.cancel_clicked.emit)
        header.addWidget(self.back_btn)

        title = QLabel("Authentication")
        title.setStyleSheet(styles.LABEL_TITLE_STYLE)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Spacer
        layout.addStretch()

        # Lock icon
        icon_container = QHBoxLayout()
        icon_container.addStretch()
        self.icon_label = QLabel("\U0001F512")  # Lock emoji
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                background-color: {styles.COLORS['surface']};
                border-radius: 40px;
                padding: 16px 20px;
            }}
        """)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(self.icon_label)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        layout.addSpacing(16)

        # Title
        self.title_label = QLabel("Email Required")
        self.title_label.setStyleSheet(styles.LABEL_SUBTITLE_STYLE)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel("This document requires your\nemail to access.")
        self.desc_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        layout.addSpacing(16)

        # Email label
        email_label = QLabel("Email")
        email_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        layout.addWidget(email_label)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("investor@fund.com")
        self.email_input.setStyleSheet(styles.INPUT_STYLE)
        self.email_input.setMinimumHeight(44)
        self.email_input.textChanged.connect(self._on_text_changed)
        self.email_input.returnPressed.connect(self._on_submit)
        layout.addWidget(self.email_input)

        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet(styles.LABEL_ERROR_STYLE)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # Spacer
        layout.addStretch()

        # Continue button
        self.submit_btn = QPushButton("Continue")
        self.submit_btn.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.submit_btn.setMinimumHeight(44)
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self._on_submit)
        layout.addWidget(self.submit_btn)

    def _on_text_changed(self, text: str) -> None:
        """Handle email input change.

        Args:
            text: Current input text
        """
        # Simple email validation
        is_valid = "@" in text and "." in text and len(text) >= 5
        self.submit_btn.setEnabled(is_valid)
        self.error_label.hide()

    def _on_submit(self) -> None:
        """Handle submit button click."""
        email = self.email_input.text().strip()
        if email and "@" in email:
            self.set_loading(True)
            self.submit_clicked.emit(email)

    def set_loading(self, loading: bool) -> None:
        """Set the loading state.

        Args:
            loading: Whether to show loading state
        """
        if loading:
            self.submit_btn.setEnabled(False)
            self.submit_btn.setText("Verifying...")
            self.email_input.setEnabled(False)
            self.back_btn.setEnabled(False)
        else:
            self.submit_btn.setText("Continue")
            self.email_input.setEnabled(True)
            self.back_btn.setEnabled(True)
            # Re-enable submit if email is valid
            self._on_text_changed(self.email_input.text())

    def set_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: Error message to display
        """
        self.error_label.setText(message)
        self.error_label.show()

    def reset(self) -> None:
        """Reset screen to initial state."""
        self.email_input.clear()
        self.error_label.hide()
        self.submit_btn.setEnabled(False)
        self.set_loading(False)

    def focus_input(self) -> None:
        """Focus the email input field."""
        self.email_input.setFocus()

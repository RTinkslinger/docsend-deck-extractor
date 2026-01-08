"""Auth passcode screen for password-protected documents.

Prompts user to enter email and passcode to access the document.
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


class AuthPasscodeScreen(QWidget):
    """Email + passcode authentication screen.

    Signals:
        submit_clicked: Emitted with (email, passcode) when continue is clicked
        cancel_clicked: Emitted when user cancels
    """

    submit_clicked = Signal(str, str)  # email, passcode
    cancel_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize auth passcode screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

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

        # Key icon
        icon_container = QHBoxLayout()
        icon_container.addStretch()
        self.icon_label = QLabel("\U0001F510")  # Lock with key emoji
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

        layout.addSpacing(12)

        # Title
        self.title_label = QLabel("Passcode Required")
        self.title_label.setStyleSheet(styles.LABEL_SUBTITLE_STYLE)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel("This document is protected.")
        self.desc_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

        layout.addSpacing(12)

        # Email label
        email_label = QLabel("Email")
        email_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        layout.addWidget(email_label)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("investor@fund.com")
        self.email_input.setStyleSheet(styles.INPUT_STYLE)
        self.email_input.setMinimumHeight(40)
        self.email_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.email_input)

        layout.addSpacing(8)

        # Passcode label
        passcode_label = QLabel("Passcode")
        passcode_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        layout.addWidget(passcode_label)

        # Passcode input with show/hide toggle
        passcode_container = QHBoxLayout()
        passcode_container.setSpacing(0)

        self.passcode_input = QLineEdit()
        self.passcode_input.setPlaceholderText("Enter passcode")
        self.passcode_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.passcode_input.setStyleSheet(styles.INPUT_STYLE + """
            QLineEdit {
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
            }
        """)
        self.passcode_input.setMinimumHeight(40)
        self.passcode_input.textChanged.connect(self._on_text_changed)
        self.passcode_input.returnPressed.connect(self._on_submit)
        passcode_container.addWidget(self.passcode_input)

        # Show/hide toggle button
        self.toggle_btn = QPushButton("\U0001F441")  # Eye emoji
        self.toggle_btn.setFixedSize(44, 40)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['border']};
            }}
        """)
        self.toggle_btn.clicked.connect(self._toggle_password)
        passcode_container.addWidget(self.toggle_btn)

        layout.addLayout(passcode_container)

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

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
        self.cancel_btn.setMinimumHeight(44)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        layout.addWidget(self.cancel_btn)

    def _on_text_changed(self, _: str) -> None:
        """Handle input change."""
        email = self.email_input.text().strip()
        passcode = self.passcode_input.text()

        # Validate both fields
        email_valid = "@" in email and "." in email and len(email) >= 5
        passcode_valid = len(passcode) >= 1

        self.submit_btn.setEnabled(email_valid and passcode_valid)
        self.error_label.hide()

    def _toggle_password(self) -> None:
        """Toggle password visibility."""
        if self.passcode_input.echoMode() == QLineEdit.EchoMode.Password:
            self.passcode_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("\U0001F441\u200D\U0001F5E8")  # Eye with speech
        else:
            self.passcode_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("\U0001F441")  # Eye

    def _on_submit(self) -> None:
        """Handle submit button click."""
        email = self.email_input.text().strip()
        passcode = self.passcode_input.text()

        if email and "@" in email and passcode:
            self.set_loading(True)
            self.submit_clicked.emit(email, passcode)

    def set_loading(self, loading: bool) -> None:
        """Set the loading state.

        Args:
            loading: Whether to show loading state
        """
        if loading:
            self.submit_btn.setEnabled(False)
            self.submit_btn.setText("Verifying...")
            self.email_input.setEnabled(False)
            self.passcode_input.setEnabled(False)
            self.back_btn.setEnabled(False)
            self.toggle_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
        else:
            self.submit_btn.setText("Continue")
            self.email_input.setEnabled(True)
            self.passcode_input.setEnabled(True)
            self.back_btn.setEnabled(True)
            self.toggle_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            # Re-enable submit if fields are valid
            self._on_text_changed("")

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
        self.passcode_input.clear()
        self.passcode_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_btn.setText("\U0001F441")
        self.error_label.hide()
        self.submit_btn.setEnabled(False)
        self.set_loading(False)

    def set_email(self, email: str) -> None:
        """Pre-fill the email field.

        Args:
            email: Email to pre-fill
        """
        self.email_input.setText(email)

    def focus_input(self) -> None:
        """Focus the appropriate input field."""
        if self.email_input.text():
            self.passcode_input.setFocus()
        else:
            self.email_input.setFocus()

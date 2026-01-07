"""Settings panel for app configuration.

Clean, Canva-inspired settings UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QFileDialog,
)
from PySide6.QtCore import Signal, Qt

from topdf_app.ui import styles


class ToggleSwitch(QPushButton):
    """Custom toggle switch widget."""

    toggled_signal = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._on_clicked)
        self._update_style()

    def _on_clicked(self) -> None:
        self._update_style()
        self.toggled_signal.emit(self.isChecked())

    def _update_style(self) -> None:
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLORS['primary']};
                    border: none;
                    border-radius: 12px;
                    text-align: right;
                    padding-right: 4px;
                    color: white;
                    font-size: 14px;
                }}
            """)
            self.setText("\u25CF")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLORS['border']};
                    border: none;
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 4px;
                    color: white;
                    font-size: 14px;
                }}
            """)
            self.setText("\u25CF")

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._update_style()


class SettingsPanel(QWidget):
    """Settings panel with configuration options.

    Signals:
        closed: Emitted when settings panel is closed
        save_folder_changed: Emitted with new save folder path
        start_at_login_changed: Emitted with new start at login value
    """

    closed = Signal()
    save_folder_changed = Signal(str)
    start_at_login_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        self.back_btn = QPushButton("\u2190")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                color: {styles.COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['surface']};
                color: {styles.COLORS['text_primary']};
            }}
        """)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.closed.emit)
        header.addWidget(self.back_btn)

        title = QLabel("Settings")
        title.setStyleSheet(styles.LABEL_TITLE_STYLE)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        layout.addSpacing(24)

        # --- GENERAL SECTION ---
        layout.addWidget(self._create_section_header("General"))
        layout.addSpacing(8)

        # Save Location row
        save_row = self._create_setting_row()
        save_row_layout = QHBoxLayout(save_row)
        save_row_layout.setContentsMargins(16, 12, 16, 12)

        save_left = QVBoxLayout()
        save_left.setSpacing(2)
        save_title = QLabel("Save location")
        save_title.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['body_size']};
                font-weight: 500;
                color: {styles.COLORS['text_primary']};
            }}
        """)
        save_left.addWidget(save_title)

        self.save_path_label = QLabel("~/Downloads")
        self.save_path_label.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['caption_size']};
                color: {styles.COLORS['text_secondary']};
            }}
        """)
        save_left.addWidget(self.save_path_label)
        save_row_layout.addLayout(save_left)

        save_row_layout.addStretch()

        change_btn = QPushButton("Change")
        change_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: {styles.FONTS['caption_size']};
                color: {styles.COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['border']};
            }}
        """)
        change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_btn.clicked.connect(self._on_change_save_location)
        save_row_layout.addWidget(change_btn)

        layout.addWidget(save_row)
        layout.addSpacing(1)

        # Start at Login row
        login_row = self._create_setting_row()
        login_row_layout = QHBoxLayout(login_row)
        login_row_layout.setContentsMargins(16, 12, 16, 12)

        login_left = QVBoxLayout()
        login_left.setSpacing(2)
        login_title = QLabel("Start at login")
        login_title.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['body_size']};
                font-weight: 500;
                color: {styles.COLORS['text_primary']};
            }}
        """)
        login_left.addWidget(login_title)

        login_desc = QLabel("Launch app when you log in")
        login_desc.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['caption_size']};
                color: {styles.COLORS['text_secondary']};
            }}
        """)
        login_left.addWidget(login_desc)
        login_row_layout.addLayout(login_left)

        login_row_layout.addStretch()

        self.login_toggle = ToggleSwitch()
        self.login_toggle.toggled_signal.connect(self._on_login_toggle)
        login_row_layout.addWidget(self.login_toggle)

        layout.addWidget(login_row)

        layout.addSpacing(24)

        # --- SHORTCUTS SECTION ---
        layout.addWidget(self._create_section_header("Keyboard Shortcut"))
        layout.addSpacing(8)

        shortcut_row = self._create_setting_row()
        shortcut_row_layout = QHBoxLayout(shortcut_row)
        shortcut_row_layout.setContentsMargins(16, 12, 16, 12)

        shortcut_left = QVBoxLayout()
        shortcut_left.setSpacing(2)
        shortcut_title = QLabel("Quick open")
        shortcut_title.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['body_size']};
                font-weight: 500;
                color: {styles.COLORS['text_primary']};
            }}
        """)
        shortcut_left.addWidget(shortcut_title)

        shortcut_desc = QLabel("Open app from anywhere")
        shortcut_desc.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['caption_size']};
                color: {styles.COLORS['text_secondary']};
            }}
        """)
        shortcut_left.addWidget(shortcut_desc)
        shortcut_row_layout.addLayout(shortcut_left)

        shortcut_row_layout.addStretch()

        shortcut_badge = QLabel("\u2318\u21E7D")
        shortcut_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: {styles.FONTS['body_size']};
                font-weight: 500;
                color: {styles.COLORS['text_primary']};
            }}
        """)
        shortcut_row_layout.addWidget(shortcut_badge)

        layout.addWidget(shortcut_row)

        layout.addStretch()

    def _create_section_header(self, title: str) -> QLabel:
        """Create a section header label."""
        label = QLabel(title.upper())
        label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                font-weight: 600;
                color: {styles.COLORS['text_muted']};
                letter-spacing: 0.5px;
            }}
        """)
        return label

    def _create_setting_row(self) -> QFrame:
        """Create a setting row frame."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['surface']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
        """)
        return frame

    def _on_change_save_location(self) -> None:
        """Handle save location change."""
        current = self.save_path_label.text()
        if current.startswith("~"):
            current = str(Path.home() / current[2:])

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Save Location",
            current,
            QFileDialog.Option.ShowDirsOnly,
        )

        if folder:
            display = folder
            home = str(Path.home())
            if folder.startswith(home):
                display = "~" + folder[len(home):]

            self.save_path_label.setText(display)
            self.save_folder_changed.emit(folder)

    def _on_login_toggle(self, checked: bool) -> None:
        """Handle login toggle."""
        self.start_at_login_changed.emit(checked)

    def set_save_folder(self, path: str) -> None:
        """Set the save folder display."""
        display = path
        home = str(Path.home())
        if path.startswith(home):
            display = "~" + path[len(home):]
        self.save_path_label.setText(display)

    def set_start_at_login(self, enabled: bool) -> None:
        """Set the start at login toggle."""
        self.login_toggle.setChecked(enabled)

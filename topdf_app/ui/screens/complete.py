"""Complete screen showing conversion success.

Two-phase flow:
1. Naming phase: User can edit the filename before saving
2. Saved phase: Shows actions to open/reveal the PDF
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer, QUrl
from PySide6.QtGui import QDesktopServices

from topdf_app.ui import styles


class CompleteScreen(QWidget):
    """Success screen with naming and PDF actions.

    Signals:
        convert_another_clicked: Emitted when user wants to convert another
        discard_clicked: Emitted when user discards without saving
        file_saved: Emitted when file is saved with final name (pdf_path)
    """

    convert_another_clicked = Signal()
    discard_clicked = Signal()
    file_saved = Signal(str)  # Final PDF path

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize complete screen.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self._temp_pdf_path: Optional[Path] = None
        self._final_pdf_path: Optional[Path] = None
        self._page_count: int = 0
        self._original_name: str = ""
        self._output_dir: Optional[Path] = None
        self._is_saved: bool = False

        # Countdown timer for auto-return to home
        self._countdown_seconds: int = 3
        self._countdown_timer: Optional[QTimer] = None

        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        self.title_label = QLabel("PDF Ready!")
        self.title_label.setStyleSheet(styles.LABEL_TITLE_STYLE)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Success icon
        icon_container = QHBoxLayout()
        icon_container.addStretch()
        self.icon_label = QLabel("\u2713")  # Checkmark
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                color: {styles.COLORS['success']};
                background-color: {styles.COLORS['surface']};
                border-radius: 40px;
                padding: 16px 20px;
            }}
        """)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addWidget(self.icon_label)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        # Page count
        self.pages_label = QLabel("0 pages captured")
        self.pages_label.setStyleSheet(styles.LABEL_CAPTION_STYLE)
        self.pages_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pages_label)

        layout.addSpacing(12)

        # === NAMING SECTION (shown before save) ===
        self.naming_section = QWidget()
        naming_layout = QVBoxLayout(self.naming_section)
        naming_layout.setContentsMargins(0, 0, 0, 0)
        naming_layout.setSpacing(12)

        # Name label
        name_label = QLabel("Name your PDF")
        name_label.setStyleSheet(styles.LABEL_BODY_STYLE)
        naming_layout.addWidget(name_label)

        # Name input
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(styles.INPUT_STYLE)
        self.name_input.setMinimumHeight(44)
        self.name_input.setPlaceholderText("Enter a name...")
        self.name_input.textChanged.connect(self._on_name_changed)
        naming_layout.addWidget(self.name_input)

        # Button row: Save and Discard
        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        # Discard button (secondary)
        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
        self.discard_btn.setMinimumHeight(44)
        self.discard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.discard_btn.clicked.connect(self._on_discard_clicked)
        button_row.addWidget(self.discard_btn)

        # Save button (primary)
        self.save_btn = QPushButton("Save PDF")
        self.save_btn.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.save_btn.setMinimumHeight(44)
        self.save_btn.clicked.connect(self._on_save_clicked)
        button_row.addWidget(self.save_btn)

        naming_layout.addLayout(button_row)
        layout.addWidget(self.naming_section)

        # === SAVED SECTION (shown after save) ===
        self.saved_section = QWidget()
        saved_layout = QVBoxLayout(self.saved_section)
        saved_layout.setContentsMargins(0, 0, 0, 0)
        saved_layout.setSpacing(12)

        # Saved filename
        self.filename_label = QLabel("document.pdf")
        self.filename_label.setStyleSheet(f"""
            QLabel {{
                font-size: {styles.FONTS['body_size']};
                font-weight: 500;
                color: {styles.COLORS['text_primary']};
                padding: 8px 12px;
                background-color: {styles.COLORS['surface']};
                border-radius: 8px;
            }}
        """)
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filename_label.setWordWrap(True)
        saved_layout.addWidget(self.filename_label)

        saved_layout.addSpacing(4)

        # Open PDF button
        self.open_btn = QPushButton("Open PDF")
        self.open_btn.setStyleSheet(styles.BUTTON_PRIMARY_STYLE)
        self.open_btn.setMinimumHeight(44)
        self.open_btn.clicked.connect(self._open_pdf)
        saved_layout.addWidget(self.open_btn)

        # Show in Finder button
        self.finder_btn = QPushButton("Show in Finder")
        self.finder_btn.setStyleSheet(styles.BUTTON_SECONDARY_STYLE)
        self.finder_btn.setMinimumHeight(44)
        self.finder_btn.clicked.connect(self._show_in_finder)
        saved_layout.addWidget(self.finder_btn)

        self.saved_section.hide()
        layout.addWidget(self.saved_section)

        # Spacer
        layout.addStretch()

        # Convert another link with countdown (only shown after save)
        self.another_btn = QPushButton("Back to home in 3...")
        self.another_btn.setStyleSheet(styles.BUTTON_TEXT_STYLE)
        self.another_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.another_btn.clicked.connect(self._on_convert_another_clicked)
        self.another_btn.hide()  # Hidden until saved
        layout.addWidget(self.another_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_animations(self) -> None:
        """Setup success animation effects."""
        self.icon_opacity = QGraphicsOpacityEffect(self.icon_label)
        self.icon_label.setGraphicsEffect(self.icon_opacity)
        self.icon_opacity.setOpacity(0.0)

        self.fade_animation = QPropertyAnimation(self.icon_opacity, b"opacity")
        self.fade_animation.setDuration(400)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        self._original_icon_style = self.icon_label.styleSheet()

    def play_success_animation(self) -> None:
        """Play the success celebration animation."""
        self.icon_opacity.setOpacity(0.0)
        self.fade_animation.start()

        self.icon_label.setStyleSheet(self._original_icon_style + """
            QLabel { background-color: #22C55E; }
        """)
        QTimer.singleShot(300, self._restore_icon_style)

    def _restore_icon_style(self) -> None:
        """Restore icon to normal style after animation."""
        self.icon_label.setStyleSheet(self._original_icon_style)

    def set_result(
        self,
        pdf_path: str,
        page_count: int,
        suggested_name: str,
        output_dir: str = "",
    ) -> None:
        """Set the conversion result to display.

        Args:
            pdf_path: Path to the temporary PDF
            page_count: Number of pages
            suggested_name: Suggested name for the file
            output_dir: Output directory for final save
        """
        self._temp_pdf_path = Path(pdf_path)
        self._page_count = page_count
        self._original_name = suggested_name
        self._output_dir = Path(output_dir) if output_dir else self._temp_pdf_path.parent
        self._is_saved = False

        # Update UI for naming phase
        self.title_label.setText("PDF Ready!")
        self.pages_label.setText(f"{page_count} page{'s' if page_count != 1 else ''} captured")
        self.name_input.setText(suggested_name)
        self.save_btn.setEnabled(True)
        self.save_btn.setText("Save PDF")

        # Show naming section, hide saved section
        self.naming_section.show()
        self.saved_section.hide()
        self.another_btn.hide()

    def _on_name_changed(self, text: str) -> None:
        """Handle name input change."""
        self.save_btn.setEnabled(bool(text.strip()))

    def _on_discard_clicked(self) -> None:
        """Handle discard button click."""
        # Delete temp file if it exists
        if self._temp_pdf_path and self._temp_pdf_path.exists():
            try:
                self._temp_pdf_path.unlink()
            except Exception:
                pass
        self.discard_clicked.emit()
        self.convert_another_clicked.emit()

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        name = self.name_input.text().strip()
        if not name or not self._temp_pdf_path:
            return

        # Sanitize filename
        name = self._sanitize_filename(name)

        # Create final path
        final_path = self._output_dir / f"{name}.pdf"

        # Handle existing file
        final_path = self._get_unique_path(final_path)

        # Move/rename file
        try:
            if self._temp_pdf_path != final_path:
                shutil.move(str(self._temp_pdf_path), str(final_path))
            self._final_pdf_path = final_path
            self._is_saved = True

            # Update UI to saved state
            self.title_label.setText("Saved!")
            self.filename_label.setText(final_path.name)
            self.naming_section.hide()
            self.saved_section.show()
            self.another_btn.show()

            # Start countdown for auto-return to home
            self._start_countdown()

            # Emit signal
            self.file_saved.emit(str(final_path))

        except Exception as e:
            # Show error in button
            self.save_btn.setText(f"Error: {str(e)[:30]}")
            QTimer.singleShot(2000, lambda: self.save_btn.setText("Save PDF"))

    def _sanitize_filename(self, name: str) -> str:
        """Remove invalid filename characters."""
        import re
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
        sanitized = re.sub(r"[\s_]+", " ", sanitized).strip(" .")
        return sanitized[:100] if sanitized else "Document"

    def _get_unique_path(self, path: Path) -> Path:
        """Get unique path by appending numbers if needed."""
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_path = parent / f"{stem} ({counter}){suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    def _open_pdf(self) -> None:
        """Open the PDF in the default application."""
        path = self._final_pdf_path or self._temp_pdf_path
        if path and path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _show_in_finder(self) -> None:
        """Show the PDF in Finder."""
        path = self._final_pdf_path or self._temp_pdf_path
        if path and path.exists():
            subprocess.run(["open", "-R", str(path)])

    def _start_countdown(self) -> None:
        """Start the countdown timer for auto-return to home."""
        self._countdown_seconds = 3
        self._update_countdown_label()

        # Create and start timer
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._on_countdown_tick)
        self._countdown_timer.start(1000)  # 1 second interval

    def _stop_countdown(self) -> None:
        """Stop the countdown timer."""
        if self._countdown_timer:
            self._countdown_timer.stop()
            self._countdown_timer = None

    def _on_countdown_tick(self) -> None:
        """Handle countdown timer tick."""
        self._countdown_seconds -= 1
        self._update_countdown_label()

        if self._countdown_seconds <= 0:
            self._stop_countdown()
            self.convert_another_clicked.emit()

    def _update_countdown_label(self) -> None:
        """Update the countdown button text."""
        if self._countdown_seconds > 0:
            self.another_btn.setText(f"Back to home in {self._countdown_seconds}...")
        else:
            self.another_btn.setText("Convert Another")

    def _on_convert_another_clicked(self) -> None:
        """Handle convert another button click - stops countdown and goes home."""
        self._stop_countdown()
        self.convert_another_clicked.emit()

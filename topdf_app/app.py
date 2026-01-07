"""Main application controller.

Coordinates the tray icon, main window, and core services.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject

from topdf_app.core.state import StateManager, State
from topdf_app.core.settings import SettingsManager
from topdf_app.core.worker import ConversionWorker
from topdf_app.core.shortcuts import ShortcutHandler
from topdf_app.core.history import HistoryManager
from topdf_app.core.macos import (
    bounce_dock,
    show_notification,
    bring_to_front,
    set_login_item,
)
from topdf_app.ui.tray import TrayIcon
from topdf_app.ui.main_window import MainWindow
from topdf_app.ui.screens.home import HomeScreen
from topdf_app.ui.screens.progress import ProgressScreen
from topdf_app.ui.screens.complete import CompleteScreen
from topdf_app.ui.screens.error import ErrorScreen
from topdf_app.ui.screens.auth_email import AuthEmailScreen
from topdf_app.ui.screens.auth_passcode import AuthPasscodeScreen
from topdf_app.ui.settings_panel import SettingsPanel


class DocSendApp(QObject):
    """Main application controller.

    Coordinates:
    - TrayIcon: Menu bar presence
    - MainWindow: UI screens
    - StateManager: Application state
    - SettingsManager: Persistent settings
    - ShortcutHandler: Global keyboard shortcuts
    - ConversionWorker: Background conversion
    """

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the application.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)

        # Core services
        self.state = StateManager(self)
        self.settings = SettingsManager(self)
        self.shortcuts = ShortcutHandler(self)
        self.history = HistoryManager(self)

        # UI components
        self.tray = TrayIcon(self)
        self.window = MainWindow()

        # Worker (will be set when conversion starts)
        self.worker: Optional[ConversionWorker] = None
        self._current_url: Optional[str] = None
        self._pending_pdf_path: Optional[str] = None
        self._pending_page_count: int = 0
        self._pending_company_name: Optional[str] = None

        # Connect signals
        self._connect_signals()

        # Initialize settings in UI
        self._init_settings_ui()

    def _connect_signals(self) -> None:
        """Connect all component signals."""
        # Tray signals
        self.tray.show_window_requested.connect(self._on_show_window)
        self.tray.quit_requested.connect(self._on_quit)

        # Window signals
        self.window.convert_requested.connect(self._on_convert_requested)
        self.window.cancel_requested.connect(self._on_cancel_requested)
        self.window.retry_requested.connect(self._on_retry_requested)
        self.window.convert_another_requested.connect(self._on_convert_another)

        # Auth signals
        self.window.auth_email_submitted.connect(self._on_auth_email_submitted)
        self.window.auth_passcode_submitted.connect(self._on_auth_passcode_submitted)
        self.window.auth_cancelled.connect(self._on_auth_cancelled)

        # History signals
        self.window.history_item_clicked.connect(self._on_history_item_clicked)
        self.tray.history_item_clicked.connect(self._on_history_item_clicked)
        self.history.history_changed.connect(self._on_history_changed)

        # Settings signals
        self.window.save_folder_changed.connect(self._on_save_folder_changed)
        self.window.start_at_login_changed.connect(self._on_start_at_login_changed)

        # Shortcut signals
        self.shortcuts.shortcut_triggered.connect(self._on_shortcut_triggered)

        # State signals
        self.state.state_changed.connect(self._on_state_changed)

        # Complete screen signals
        complete_screen = self.window.screens.get("complete")
        if isinstance(complete_screen, CompleteScreen):
            complete_screen.file_saved.connect(self._on_file_saved)

    def _init_settings_ui(self) -> None:
        """Initialize settings panel with current values."""
        settings_panel = self.window.screens.get("settings")
        if isinstance(settings_panel, SettingsPanel):
            settings_panel.set_save_folder(str(self.settings.save_folder))
            settings_panel.set_start_at_login(self.settings.start_at_login)

        # Initialize history display
        self._update_history_ui()

    def start(self) -> None:
        """Start the application.

        Shows the tray icon and prepares the application for use.
        """
        self.tray.show()

        # Register global shortcut
        self.shortcuts.register()

        # Show window on first launch
        self.window.show()
        self.window._position_near_tray()

    def _on_show_window(self) -> None:
        """Handle request to show the main window."""
        self.window.toggle_visibility()

    def _on_shortcut_triggered(self) -> None:
        """Handle global shortcut activation."""
        # Show window
        if not self.window.isVisible():
            self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.window._position_near_tray()
        bring_to_front()

        # Check clipboard for DocSend URL
        from PySide6.QtWidgets import QApplication
        from topdf_app.ui.screens.home import is_valid_docsend_url, HomeScreen

        clipboard = QApplication.clipboard()
        if clipboard:
            text = clipboard.text()
            if text and is_valid_docsend_url(text):
                # Auto-fill URL
                home_screen = self.window.screens.get("home")
                if isinstance(home_screen, HomeScreen):
                    home_screen.set_url(text)

    def _on_quit(self) -> None:
        """Handle quit request."""
        # Unregister shortcuts
        self.shortcuts.unregister()

        # Clean up any running workers
        if self.worker is not None and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(3000)  # Wait up to 3 seconds

    def _on_convert_requested(self, url: str) -> None:
        """Handle conversion request.

        Args:
            url: DocSend URL to convert
        """
        self._current_url = url
        self._start_conversion(url)

    def _start_conversion(self, url: str) -> None:
        """Start the conversion process.

        Args:
            url: DocSend URL to convert
        """
        # Clean up any existing worker
        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.cancel()
                self.worker.wait(1000)
            self.worker.deleteLater()

        # Reset home screen loading state
        home_screen = self.window.screens.get("home")
        if isinstance(home_screen, HomeScreen):
            home_screen.set_loading(False)

        # Reset progress screen
        progress_screen = self.window.screens.get("progress")
        if isinstance(progress_screen, ProgressScreen):
            progress_screen.reset()

        # Transition to progress state
        self.state.set_state(State.PROGRESS, force=True)

        # Create and start worker
        self.worker = ConversionWorker(
            url=url,
            output_dir=str(self.settings.save_folder),
            parent=self,
        )

        # Connect worker signals
        self.worker.progress.connect(self._on_progress)
        self.worker.auth_required.connect(self._on_auth_required)
        self.worker.complete.connect(self._on_complete)
        self.worker.error.connect(self._on_error)

        # Start conversion
        self.worker.start()

    def _on_cancel_requested(self) -> None:
        """Handle cancel request from progress screen."""
        if self.worker is not None and self.worker.isRunning():
            self.worker.cancel()
            # Don't wait - let it finish in background
            # Go back to home
            self.state.set_state(State.HOME, force=True)

    def _on_retry_requested(self) -> None:
        """Handle retry request from error screen."""
        if self._current_url:
            self._start_conversion(self._current_url)

    def _on_convert_another(self) -> None:
        """Handle convert another request."""
        self._current_url = None
        self.state.set_state(State.HOME, force=True)

    def _on_progress(self, percent: int, message: str) -> None:
        """Handle progress update from worker.

        Args:
            percent: Progress percentage (0-100)
            message: Status message
        """
        progress_screen = self.window.screens.get("progress")
        if isinstance(progress_screen, ProgressScreen):
            progress_screen.set_progress(percent, message)

    def _on_auth_required(self, auth_type: str) -> None:
        """Handle auth required signal from worker.

        Args:
            auth_type: Type of auth needed ("email" or "passcode")
        """
        # Bounce dock to get attention
        bounce_dock()

        # Bring window to front
        if not self.window.isVisible():
            self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        bring_to_front()

        # Show appropriate auth screen
        if auth_type == "email":
            # Reset and show email auth screen
            auth_screen = self.window.screens.get("auth_email")
            if isinstance(auth_screen, AuthEmailScreen):
                auth_screen.reset()
                auth_screen.focus_input()
            self.state.set_state(State.AUTH_EMAIL, force=True)
        else:
            # Reset and show passcode auth screen
            auth_screen = self.window.screens.get("auth_passcode")
            if isinstance(auth_screen, AuthPasscodeScreen):
                auth_screen.reset()
                auth_screen.focus_input()
            self.state.set_state(State.AUTH_PASSCODE, force=True)

    def _on_auth_email_submitted(self, email: str) -> None:
        """Handle email auth submission.

        Args:
            email: Email entered by user
        """
        if self.worker is not None:
            # Provide credentials to worker
            self.worker.provide_credentials(email)

            # Reset auth screen loading state before switching
            auth_screen = self.window.screens.get("auth_email")
            if isinstance(auth_screen, AuthEmailScreen):
                auth_screen.set_loading(False)

            # Go back to progress screen
            self.state.set_state(State.PROGRESS, force=True)

    def _on_auth_passcode_submitted(self, email: str, passcode: str) -> None:
        """Handle passcode auth submission.

        Args:
            email: Email entered by user
            passcode: Passcode entered by user
        """
        if self.worker is not None:
            # Provide credentials to worker
            self.worker.provide_credentials(email, passcode)

            # Reset auth screen loading state before switching
            auth_screen = self.window.screens.get("auth_passcode")
            if isinstance(auth_screen, AuthPasscodeScreen):
                auth_screen.set_loading(False)

            # Go back to progress screen
            self.state.set_state(State.PROGRESS, force=True)

    def _on_auth_cancelled(self) -> None:
        """Handle auth cancellation."""
        if self.worker is not None:
            self.worker.cancel_auth()

        # Go back to home
        self.state.set_state(State.HOME, force=True)

    def _on_complete(self, pdf_path: str, page_count: int, suggested_name: str) -> None:
        """Handle successful conversion.

        Args:
            pdf_path: Path to generated PDF (temporary, may be renamed)
            page_count: Number of pages
            suggested_name: Suggested name for the file
        """
        # Store for complete screen
        self._pending_pdf_path = pdf_path
        self._pending_page_count = page_count
        self._pending_company_name = suggested_name

        # Note: History is added when user saves the file with final name
        # See _on_file_saved

        # Show complete screen
        self._show_complete_screen()

    def _on_error(self, message: str, details: str) -> None:
        """Handle conversion error.

        Args:
            message: Error message
            details: Error traceback
        """
        # Update error screen
        error_screen = self.window.screens.get("error")
        if isinstance(error_screen, ErrorScreen):
            error_screen.set_error(message, details)

        # Transition to error state
        self.state.set_state(State.ERROR, force=True)

        # Clean up worker
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

    # Settings handlers
    def _on_save_folder_changed(self, path: str) -> None:
        """Handle save folder change.

        Args:
            path: New save folder path
        """
        self.settings.save_folder = path

    def _on_start_at_login_changed(self, enabled: bool) -> None:
        """Handle start at login change.

        Args:
            enabled: Whether to start at login
        """
        self.settings.start_at_login = enabled
        set_login_item(enabled)

    def _on_state_changed(self, new_state: State) -> None:
        """Handle state changes.

        Args:
            new_state: The new application state
        """
        # Map states to screens
        state_to_screen = {
            State.HOME: "home",
            State.PROGRESS: "progress",
            State.AUTH_EMAIL: "auth_email",
            State.AUTH_PASSCODE: "auth_passcode",
            State.COMPLETE: "complete",
            State.ERROR: "error",
        }

        screen_name = state_to_screen.get(new_state)
        if screen_name and screen_name in self.window.screens:
            self.window.show_screen(screen_name)

        # Update tray icon for converting state
        is_converting = new_state in (
            State.PROGRESS,
            State.AUTH_EMAIL,
            State.AUTH_PASSCODE,
        )
        self.tray.set_converting(is_converting)

    def _show_complete_screen(self) -> None:
        """Show the complete screen with current result."""
        complete_screen = self.window.screens.get("complete")
        if isinstance(complete_screen, CompleteScreen):
            complete_screen.set_result(
                self._pending_pdf_path or "",
                self._pending_page_count,
                self._pending_company_name or "",
                output_dir=str(self.settings.save_folder),
            )

        self.state.set_state(State.COMPLETE, force=True)

        # Clean up worker
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

    def _on_file_saved(self, final_pdf_path: str) -> None:
        """Handle file saved from complete screen.

        Args:
            final_pdf_path: Path to the saved PDF with final name
        """
        from pathlib import Path

        # Extract name from path
        name = Path(final_pdf_path).stem

        # Add to history with final name
        self.history.add(
            name=name,
            pdf_path=final_pdf_path,
            page_count=self._pending_page_count,
            has_summary=False,
        )

        # Show notification
        show_notification(
            "PDF Saved",
            f"{name}.pdf - {self._pending_page_count} pages",
        )

    # History handlers
    def _on_history_item_clicked(self, pdf_path: str) -> None:
        """Handle history item click - open the PDF.

        Args:
            pdf_path: Path to the PDF file
        """
        import subprocess
        try:
            subprocess.run(["open", pdf_path], check=True)
        except Exception:
            pass

    def _on_history_changed(self) -> None:
        """Handle history changes - update UI."""
        self._update_history_ui()

    def _update_history_ui(self) -> None:
        """Update history display in home screen and tray menu."""
        entries = self.history.get_all()

        # Format for UI
        formatted = [
            {
                "name": entry.name,
                "pdf_path": entry.pdf_path,
                "relative_time": entry.get_relative_time(),
                "has_summary": entry.has_summary,
            }
            for entry in entries
        ]

        # Update home screen
        home_screen = self.window.screens.get("home")
        if isinstance(home_screen, HomeScreen):
            home_screen.update_history(formatted)

        # Update tray menu
        self.tray.update_history(formatted)

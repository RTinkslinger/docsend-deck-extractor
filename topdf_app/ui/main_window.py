"""Main window container with stacked screens.

The main window is a compact 320px wide window that contains all screens
using a QStackedWidget for navigation.
"""

from __future__ import annotations

from typing import Optional, Dict

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent

from topdf_app.ui.styles import APP_STYLESHEET
from topdf_app.ui.screens.home import HomeScreen
from topdf_app.ui.screens.progress import ProgressScreen
from topdf_app.ui.screens.complete import CompleteScreen
from topdf_app.ui.screens.error import ErrorScreen
from topdf_app.ui.screens.auth_email import AuthEmailScreen
from topdf_app.ui.screens.auth_passcode import AuthPasscodeScreen
from topdf_app.ui.settings_panel import SettingsPanel


class MainWindow(QMainWindow):
    """Compact main window with stacked screens.

    Signals:
        convert_requested: Emitted when user requests conversion with URL
        window_hidden: Emitted when window is hidden
    """

    WINDOW_WIDTH = 320
    WINDOW_MIN_HEIGHT = 200

    convert_requested = Signal(str)  # url
    cancel_requested = Signal()
    retry_requested = Signal()
    convert_another_requested = Signal()
    auth_email_submitted = Signal(str)  # email
    auth_passcode_submitted = Signal(str, str)  # email, passcode
    auth_cancelled = Signal()
    settings_requested = Signal()
    settings_closed = Signal()
    save_folder_changed = Signal(str)
    start_at_login_changed = Signal(bool)
    window_hidden = Signal()
    # History signals
    history_item_clicked = Signal(str)  # pdf_path

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the main window.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        self._setup_window()
        self._setup_screens()
        self._connect_signals()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("DocSend to PDF")
        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setMinimumHeight(self.WINDOW_MIN_HEIGHT)

        # Window flags for a compact, floating window
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowTitleHint
        )

        # Apply global stylesheet
        self.setStyleSheet(APP_STYLESHEET)

        # No dock icon for this app (menu bar only)
        # This is handled at the app level via plist

    def _setup_screens(self) -> None:
        """Setup the stacked widget with all screens."""
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create screens
        self.screens: Dict[str, QWidget] = {
            "home": HomeScreen(),
            "progress": ProgressScreen(),
            "complete": CompleteScreen(),
            "error": ErrorScreen(),
            "auth_email": AuthEmailScreen(),
            "auth_passcode": AuthPasscodeScreen(),
            "settings": SettingsPanel(),
        }

        # Add screens to stack
        for screen in self.screens.values():
            self.stack.addWidget(screen)

        # Start with home screen
        self.show_screen("home")

    def _connect_signals(self) -> None:
        """Connect screen signals to window signals."""
        # Home screen
        home_screen = self.screens["home"]
        if isinstance(home_screen, HomeScreen):
            home_screen.convert_clicked.connect(self.convert_requested.emit)

        # Progress screen
        progress_screen = self.screens["progress"]
        if isinstance(progress_screen, ProgressScreen):
            progress_screen.cancel_clicked.connect(self.cancel_requested.emit)
            progress_screen.back_clicked.connect(self._go_home)

        # Complete screen
        complete_screen = self.screens["complete"]
        if isinstance(complete_screen, CompleteScreen):
            complete_screen.convert_another_clicked.connect(self._go_home)

        # Error screen
        error_screen = self.screens["error"]
        if isinstance(error_screen, ErrorScreen):
            error_screen.retry_clicked.connect(self.retry_requested.emit)
            error_screen.back_clicked.connect(self._go_home)

        # Auth email screen
        auth_email_screen = self.screens["auth_email"]
        if isinstance(auth_email_screen, AuthEmailScreen):
            auth_email_screen.submit_clicked.connect(self.auth_email_submitted.emit)
            auth_email_screen.cancel_clicked.connect(self.auth_cancelled.emit)

        # Auth passcode screen
        auth_passcode_screen = self.screens["auth_passcode"]
        if isinstance(auth_passcode_screen, AuthPasscodeScreen):
            auth_passcode_screen.submit_clicked.connect(self.auth_passcode_submitted.emit)
            auth_passcode_screen.cancel_clicked.connect(self.auth_cancelled.emit)

        # Settings panel
        settings_panel = self.screens["settings"]
        if isinstance(settings_panel, SettingsPanel):
            settings_panel.closed.connect(self._on_settings_closed)
            settings_panel.save_folder_changed.connect(self.save_folder_changed.emit)
            settings_panel.start_at_login_changed.connect(self.start_at_login_changed.emit)

        # Home screen settings button and history
        home_screen = self.screens["home"]
        if isinstance(home_screen, HomeScreen):
            home_screen.settings_clicked.connect(self._show_settings)
            home_screen.history_item_clicked.connect(self.history_item_clicked.emit)

    def _show_settings(self) -> None:
        """Show the settings panel."""
        self.settings_requested.emit()
        self.show_screen("settings")

    def _on_settings_closed(self) -> None:
        """Handle settings panel closed."""
        self.settings_closed.emit()
        self.show_screen("home")

    def _go_home(self) -> None:
        """Navigate to home screen and emit signal."""
        self.show_screen("home")
        # Clear the URL input for fresh start
        home_screen = self.screens.get("home")
        if isinstance(home_screen, HomeScreen):
            home_screen.clear_input()
        self.convert_another_requested.emit()

    def show_screen(self, name: str) -> None:
        """Navigate to a specific screen.

        Args:
            name: Screen name (home, progress, auth_email, etc.)
        """
        if name not in self.screens:
            return

        # Stop animations on the previous screen
        current_screen = self.stack.currentWidget()
        if isinstance(current_screen, ProgressScreen):
            current_screen.stop_animation()

        self.stack.setCurrentWidget(self.screens[name])
        # Adjust window size to fit content
        self.adjustSize()

        # Trigger screen-specific animations
        if name == "progress":
            progress_screen = self.screens.get("progress")
            if isinstance(progress_screen, ProgressScreen):
                progress_screen.start_animation()
        elif name == "complete":
            complete_screen = self.screens.get("complete")
            if isinstance(complete_screen, CompleteScreen):
                complete_screen.play_success_animation()
        elif name == "error":
            error_screen = self.screens.get("error")
            if isinstance(error_screen, ErrorScreen):
                error_screen.play_error_animation()

    def get_current_screen(self) -> str:
        """Get the name of the currently displayed screen.

        Returns:
            Screen name
        """
        current_widget = self.stack.currentWidget()
        for name, widget in self.screens.items():
            if widget is current_widget:
                return name
        return "home"

    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
            self.window_hidden.emit()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            # Position window near the menu bar on macOS
            self._position_near_tray()

    def _position_near_tray(self) -> None:
        """Position the window appropriately on screen.

        Centers horizontally near the top of the screen.
        """
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QScreen

        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = geometry.center().x() - self.width() // 2
            y = geometry.top() + 50  # Below menu bar
            self.move(x, y)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.

        Hides the window instead of closing the application.

        Args:
            event: The close event
        """
        event.ignore()
        self.hide()
        self.window_hidden.emit()

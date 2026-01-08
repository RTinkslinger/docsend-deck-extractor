"""Main window container with stacked screens.

The main window is a compact 320px wide dropdown panel that appears
below the menu bar tray icon, using a QStackedWidget for navigation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, TYPE_CHECKING

from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QApplication,
    QVBoxLayout, QPushButton, QFrame, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent, QPixmap

if TYPE_CHECKING:
    from PySide6.QtWidgets import QSystemTrayIcon

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

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the main window.

        Args:
            parent: Optional parent widget
        """
        super().__init__(parent)

        # Reference to tray icon for positioning
        self._tray_icon: Optional[QSystemTrayIcon] = None

        # Flag to prevent focus-based hiding during active operations
        self._block_focus_hide: bool = False

        self._setup_window()
        self._setup_screens()
        self._connect_signals()

        # Connect to application focus changes for click-outside-to-close
        QApplication.instance().focusChanged.connect(self._on_focus_changed)

    def set_tray_icon(self, tray_icon: QSystemTrayIcon) -> None:
        """Set the tray icon reference for positioning.

        Args:
            tray_icon: The system tray icon
        """
        self._tray_icon = tray_icon

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("DocSend to PDF")
        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setMinimumHeight(self.WINDOW_MIN_HEIGHT)

        # Window flags for a menu bar dropdown panel
        # - Tool: stays on top, receives keyboard focus (unlike Popup)
        # - FramelessWindowHint: no title bar (dropdown style)
        # - WindowStaysOnTopHint: always above other windows
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        # Note: Click-outside-to-close is handled by _on_focus_changed()

        # Apply global stylesheet
        self.setStyleSheet(APP_STYLESHEET)

        # No dock icon for this app (menu bar only)
        # This is handled at the app level via plist

    def _setup_screens(self) -> None:
        """Setup the stacked widget with all screens and footer."""
        # Create main container
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create stacked widget for screens
        self.stack = QStackedWidget()

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

        # Create footer with Quit button
        footer = self._create_footer()

        # Add to main layout
        main_layout.addWidget(self.stack, 1)  # Stretch factor 1
        main_layout.addWidget(footer, 0)  # No stretch

        self.setCentralWidget(container)

        # Start with home screen
        self.show_screen("home")

    def _create_footer(self) -> QFrame:
        """Create the footer widget with branding and Quit button.

        Returns:
            Footer frame widget
        """
        footer = QFrame()
        footer.setObjectName("dropdownFooter")
        footer.setStyleSheet("""
            #dropdownFooter {
                background-color: #F9FAFB;
                border-top: 1px solid #E5E7EB;
            }
        """)

        layout = QVBoxLayout(footer)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Dark branded container - clickable, links to devc.com
        branding_container = QPushButton()
        branding_container.setObjectName("brandingContainer")
        branding_container.setCursor(Qt.CursorShape.PointingHandCursor)
        branding_container.setMinimumHeight(80)  # Ensure content is visible
        branding_container.setStyleSheet("""
            #brandingContainer {
                background-color: #1F2937;
                border-radius: 10px;
                border: none;
            }
            #brandingContainer:hover {
                background-color: #374151;
            }
            #brandingContainer:pressed {
                background-color: #1F2937;
            }
        """)
        branding_container.clicked.connect(self._on_branding_clicked)

        from PySide6.QtWidgets import QHBoxLayout
        branding_layout = QHBoxLayout(branding_container)
        branding_layout.setContentsMargins(16, 14, 20, 14)
        branding_layout.setSpacing(14)

        # Logo on left - check bundled app location first, then source location
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller bundled app
            app_dir = Path(sys.executable).parent.parent
            logo_path = app_dir / "Resources" / "logo image" / "DeVC Logo PNG.png"
        else:
            # Running from source
            logo_path = Path(__file__).parent.parent.parent / "logo image" / "DeVC Logo PNG.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_label.setStyleSheet("background: transparent;")
            logo_pixmap = QPixmap(str(logo_path))
            # Scale to 56px width for balanced horizontal layout
            scaled_pixmap = logo_pixmap.scaledToWidth(
                56, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
            branding_layout.addWidget(logo_label)

        # Text container on right - two lines stacked
        text_container = QVBoxLayout()
        text_container.setSpacing(2)

        # Line 1: "made with ❤️"
        line1 = QLabel("made with ❤️")
        line1.setStyleSheet("""
            QLabel {
                color: #E5E7EB;
                font-size: 17px;
                background: transparent;
            }
        """)
        text_container.addWidget(line1)

        # Line 2: "by team DeVC"
        line2 = QLabel("by team DeVC")
        line2.setStyleSheet("""
            QLabel {
                color: #9CA3AF;
                font-size: 16px;
                background: transparent;
            }
        """)
        text_container.addWidget(line2)

        branding_layout.addLayout(text_container)
        branding_layout.addStretch()  # Push content to left

        layout.addWidget(branding_container)

        # Full-width centered Quit button (styled like secondary button)
        quit_btn = QPushButton("Quit")
        quit_btn.setMinimumHeight(40)
        quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #F3F4F6;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                color: #374151;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #E5E7EB;
                border-color: #D1D5DB;
            }
            QPushButton:pressed {
                background-color: #D1D5DB;
            }
        """)
        quit_btn.clicked.connect(self._on_quit_clicked)
        layout.addWidget(quit_btn)

        return footer

    def _connect_signals(self) -> None:
        """Connect screen signals to window signals."""
        # Home screen
        home_screen = self.screens["home"]
        if isinstance(home_screen, HomeScreen):
            home_screen.convert_clicked.connect(self._on_home_convert_clicked)

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

        # Home screen settings button
        home_screen = self.screens["home"]
        if isinstance(home_screen, HomeScreen):
            home_screen.settings_clicked.connect(self._show_settings)

    def _show_settings(self) -> None:
        """Show the settings panel."""
        self.settings_requested.emit()
        self.show_screen("settings")

    def _on_settings_closed(self) -> None:
        """Handle settings panel closed."""
        self.settings_closed.emit()
        self.show_screen("home")

    def _on_home_convert_clicked(self, url: str) -> None:
        """Handle convert click from home screen.

        Sets the block flag BEFORE emitting convert_requested to prevent
        focus-based window hiding when set_loading() disables the input.

        Args:
            url: DocSend URL to convert
        """
        self._block_focus_hide = True
        self.convert_requested.emit(url)

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
            # Position first, then show to avoid flicker
            self._position_below_tray()
            self.show()
            # Ensure window comes to front on macOS
            self.raise_()
            self.activateWindow()
            # Process events to ensure window is fully shown
            QApplication.processEvents()

    def _position_below_tray(self) -> None:
        """Position the dropdown panel centered below the menu bar.

        Centers horizontally on screen, positioned just below the menu bar.
        This matches the macOS Calendar app behavior.
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            # Center horizontally
            x = geometry.center().x() - self.width() // 2
            # Position just below menu bar (availableGeometry excludes menu bar)
            y = geometry.top() + 4
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

    def _on_quit_clicked(self) -> None:
        """Handle quit button click - clean shutdown."""
        # Disconnect focus handler to prevent interference during quit
        try:
            QApplication.instance().focusChanged.disconnect(self._on_focus_changed)
        except RuntimeError:
            pass  # Already disconnected

        # Hide window first
        self.hide()

        # Quit application
        QApplication.quit()

    def _on_branding_clicked(self) -> None:
        """Handle branding container click - open DeVC website."""
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://www.devc.com"))

    def _on_focus_changed(self, old, new) -> None:
        """Handle application focus changes.

        Hides the dropdown when focus moves outside of it.
        This is more reliable than WindowDeactivate for Tool windows on macOS.
        """
        if not self.isVisible():
            return

        # Don't hide during active operations (conversion, auth submission)
        if self._block_focus_hide:
            return

        # Don't hide if we're on an operational screen (not home/settings)
        # This is a robust fallback - if we're showing progress, auth, complete,
        # or error screens, the user is in the middle of something
        current_screen = self.get_current_screen()
        if current_screen not in ("home", "settings"):
            return

        # If new focus widget is None or not a child of this window, hide
        if new is None:
            self.hide()
            self.window_hidden.emit()
        elif not self.isAncestorOf(new) and new is not self:
            self.hide()
            self.window_hidden.emit()

    def set_block_focus_hide(self, block: bool) -> None:
        """Set whether to block focus-based window hiding.

        Use this during active operations like conversion or auth.

        Args:
            block: True to prevent hiding, False to allow
        """
        self._block_focus_hide = block

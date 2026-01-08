"""Menu bar tray icon.

Provides the system tray icon and context menu for the application.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, QObject


def get_icon_path(name: str) -> Path:
    """Get the path to an icon resource file.

    Args:
        name: Icon filename (e.g., 'tray_icon.png')

    Returns:
        Path to the icon file
    """
    import sys

    # When running as a bundled app (PyInstaller)
    if getattr(sys, 'frozen', False):
        # PyInstaller puts data files in the app's Resources directory
        app_dir = Path(sys.executable).parent.parent
        resources_dir = app_dir / "Resources" / "resources"
        icon_path = resources_dir / name
        if icon_path.exists():
            return icon_path

    # When running from source
    resources_dir = Path(__file__).parent.parent.parent / "resources"
    return resources_dir / name


def load_tray_icon() -> QIcon:
    """Load the tray icon from PNG files.

    Qt automatically loads @2x version for Retina displays when
    the base filename is provided.

    Returns:
        QIcon loaded from tray_icon.png (and tray_icon@2x.png for Retina)
    """
    icon_path = get_icon_path("tray_icon.png")
    if icon_path.exists():
        return QIcon(str(icon_path))
    else:
        # Fallback: return empty icon (shouldn't happen in normal operation)
        print(f"Warning: Tray icon not found at {icon_path}")
        return QIcon()


class TrayIcon(QSystemTrayIcon):
    """Menu bar tray icon for the application.

    Signals:
        show_window_requested: Emitted when user wants to show main window
        quit_requested: Emitted when user requests to quit
    """

    show_window_requested = Signal()
    quit_requested = Signal()

    history_item_clicked = Signal(str)  # pdf_path

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize the tray icon.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)

        self._is_converting = False
        self._history_actions: List = []

        # Load icon from PNG file (Qt handles @2x automatically)
        self._icon = load_tray_icon()
        self.setIcon(self._icon)

        # Set tooltip
        self.setToolTip("DocSend to PDF")

        # No context menu - we use the dropdown panel instead
        # Context menu was causing double-popup on click
        self.setContextMenu(None)

        # Connect activation signal (click on tray icon)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (click).

        On macOS, we handle all activation reasons to ensure reliable response.

        Args:
            reason: The activation reason
        """
        # Handle any click/activation - macOS can be inconsistent with Trigger
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
            QSystemTrayIcon.ActivationReason.MiddleClick,
        ):
            self.show_window_requested.emit()

    def set_converting(self, active: bool) -> None:
        """Update icon state during conversion.

        Args:
            active: True if conversion is in progress
        """
        self._is_converting = active
        # TODO: Add separate active icon if visual feedback during conversion is needed
        # For now, icon stays the same

    def update_history(self, history_items: List[Dict]) -> None:
        """Update the history section of the context menu.

        Args:
            history_items: List of history item dicts with 'name' and 'pdf_path'
        """
        menu = self.contextMenu()
        if not menu:
            return

        # Remove old history actions
        for action in self._history_actions:
            menu.removeAction(action)
        self._history_actions.clear()

        if not history_items:
            return

        # Find the separator after "Open" to insert history items
        actions = menu.actions()
        insert_before = None
        for i, action in enumerate(actions):
            if action.text() == "Settings...":
                insert_before = action
                break

        # Add "Recent" label
        recent_label = menu.addAction("Recent Conversions")
        recent_label.setEnabled(False)
        if insert_before:
            menu.removeAction(recent_label)
            menu.insertAction(insert_before, recent_label)
        self._history_actions.append(recent_label)

        # Add history items (max 5 in tray menu)
        for item in history_items[:5]:
            name = item.get("name", "Unknown")
            pdf_path = item.get("pdf_path", "")

            action = menu.addAction(f"  {name}")
            # Store path in action data
            action.setData(pdf_path)
            action.triggered.connect(
                lambda checked, path=pdf_path: self._on_history_item_clicked(path)
            )

            if insert_before:
                menu.removeAction(action)
                menu.insertAction(insert_before, action)

            self._history_actions.append(action)

        # Add separator after history
        sep = menu.addSeparator()
        if insert_before:
            menu.removeAction(sep)
            menu.insertAction(insert_before, sep)
        self._history_actions.append(sep)

    def _on_history_item_clicked(self, pdf_path: str) -> None:
        """Handle history item click.

        Args:
            pdf_path: Path to the PDF
        """
        self.history_item_clicked.emit(pdf_path)

"""Menu bar tray icon.

Provides the system tray icon and context menu for the application.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal, QObject


def create_default_icon(active: bool = False) -> QIcon:
    """Create a simple default icon programmatically.

    Args:
        active: If True, use active/converting color

    Returns:
        QIcon with a simple document icon
    """
    size = 22  # Standard macOS menu bar icon size
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a simple document/PDF icon
    color = QColor("#8B5CF6") if active else QColor("#374151")  # Purple when active
    painter.setPen(color)
    painter.setBrush(color)

    # Document body
    painter.drawRoundedRect(4, 2, 14, 18, 2, 2)

    # Folded corner (lighter)
    painter.setBrush(QColor("#FFFFFF") if not active else QColor("#C4B5FD"))
    corner_points = [(14, 2), (18, 6), (14, 6)]
    from PySide6.QtGui import QPolygon
    from PySide6.QtCore import QPoint
    polygon = QPolygon([QPoint(x, y) for x, y in corner_points])
    painter.drawPolygon(polygon)

    painter.end()
    return QIcon(pixmap)


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

        # Set the icon
        self._normal_icon = create_default_icon(active=False)
        self._active_icon = create_default_icon(active=True)
        self.setIcon(self._normal_icon)

        # Set tooltip
        self.setToolTip("DocSend to PDF")

        # Setup context menu
        self._setup_menu()

        # Connect activation signal (click on tray icon)
        self.activated.connect(self._on_activated)

    def _setup_menu(self) -> None:
        """Setup the context menu for the tray icon."""
        menu = QMenu()

        # Open action
        open_action = menu.addAction("Open")
        open_action.triggered.connect(self.show_window_requested.emit)

        menu.addSeparator()

        # History section (placeholder - will be populated dynamically)
        self._history_menu_start = menu.addSeparator()

        # Settings and Quit
        menu.addAction("Settings...", self._on_settings)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._on_quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon activation (click).

        Args:
            reason: The activation reason
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - also show window
            self.show_window_requested.emit()

    def _on_settings(self) -> None:
        """Handle settings menu action."""
        # For now, just show the window
        # Settings panel will be implemented later
        self.show_window_requested.emit()

    def _on_quit(self) -> None:
        """Handle quit menu action."""
        self.quit_requested.emit()
        QApplication.quit()

    def set_converting(self, active: bool) -> None:
        """Update icon state during conversion.

        Args:
            active: True if conversion is in progress
        """
        self._is_converting = active
        self.setIcon(self._active_icon if active else self._normal_icon)

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

"""Settings manager using QSettings for persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import QSettings, QObject, Signal


class SettingsManager(QObject):
    """Persistent settings using QSettings.

    Stores user preferences like save location, keyboard shortcut, etc.
    """

    setting_changed = Signal(str, object)  # key, value

    # Default values
    DEFAULTS = {
        "save_folder": str(Path.home() / "Downloads"),
        "shortcut": "Cmd+Shift+D",
        "start_at_login": False,
    }

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize settings manager.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._settings = QSettings("topdf", "DocSend to PDF")

    def get(self, key: str, default: object = None) -> object:
        """Get a setting value.

        Args:
            key: Setting key
            default: Default value if key not found (uses DEFAULTS if None)

        Returns:
            The setting value
        """
        if default is None:
            default = self.DEFAULTS.get(key)
        return self._settings.value(key, default)

    def set(self, key: str, value: object) -> None:
        """Set a setting value.

        Args:
            key: Setting key
            value: Value to store
        """
        self._settings.setValue(key, value)
        self._settings.sync()
        self.setting_changed.emit(key, value)

    @property
    def save_folder(self) -> Path:
        """Get the save folder path."""
        return Path(self.get("save_folder"))

    @save_folder.setter
    def save_folder(self, value: Union[Path, str]) -> None:
        """Set the save folder path."""
        self.set("save_folder", str(value))

    @property
    def shortcut(self) -> str:
        """Get the global shortcut."""
        return str(self.get("shortcut"))

    @shortcut.setter
    def shortcut(self, value: str) -> None:
        """Set the global shortcut."""
        self.set("shortcut", value)

    @property
    def start_at_login(self) -> bool:
        """Get start at login preference."""
        return bool(self.get("start_at_login"))

    @start_at_login.setter
    def start_at_login(self, value: bool) -> None:
        """Set start at login preference."""
        self.set("start_at_login", value)

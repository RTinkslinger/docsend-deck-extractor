"""Global keyboard shortcut handler.

Registers and handles global keyboard shortcuts using pynput.
"""

from __future__ import annotations

import threading
from typing import Optional, Set

from PySide6.QtCore import QObject, Signal


class ShortcutHandler(QObject):
    """Handles global keyboard shortcuts.

    Uses pynput to listen for keyboard events globally,
    even when the app is not in focus.

    Signals:
        shortcut_triggered: Emitted when the shortcut is pressed
    """

    shortcut_triggered = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize shortcut handler.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)

        self._listener = None
        self._current_keys: Set = set()
        self._enabled = True

        # Default shortcut: Cmd+Shift+D
        self._shortcut_keys = {"cmd", "shift", "d"}

    def register(self) -> bool:
        """Register the global shortcut listener.

        Returns:
            True if registration was successful
        """
        try:
            from pynput import keyboard

            def on_press(key):
                if not self._enabled:
                    return

                # Normalize key
                key_name = self._normalize_key(key)
                if key_name:
                    self._current_keys.add(key_name)

                # Check if shortcut is pressed
                if self._shortcut_keys.issubset(self._current_keys):
                    # Emit signal (thread-safe via Qt)
                    self.shortcut_triggered.emit()
                    # Clear keys to prevent repeated triggers
                    self._current_keys.clear()

            def on_release(key):
                key_name = self._normalize_key(key)
                if key_name:
                    self._current_keys.discard(key_name)

            self._listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
            )
            self._listener.start()
            return True

        except ImportError:
            # pynput not available
            return False
        except Exception:
            return False

    def _normalize_key(self, key) -> Optional[str]:
        """Normalize a key to a string representation.

        Args:
            key: pynput key object

        Returns:
            Normalized key string or None
        """
        try:
            from pynput.keyboard import Key

            # Special keys
            if key == Key.cmd or key == Key.cmd_l or key == Key.cmd_r:
                return "cmd"
            elif key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                return "shift"
            elif key == Key.ctrl or key == Key.ctrl_l or key == Key.ctrl_r:
                return "ctrl"
            elif key == Key.alt or key == Key.alt_l or key == Key.alt_r:
                return "alt"
            elif hasattr(key, "char") and key.char:
                return key.char.lower()
            elif hasattr(key, "name"):
                return key.name.lower()
            return None
        except Exception:
            return None

    def unregister(self) -> None:
        """Unregister the global shortcut listener."""
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the shortcut.

        Args:
            enabled: Whether shortcuts should be active
        """
        self._enabled = enabled

    def set_shortcut(self, shortcut: str) -> None:
        """Set the shortcut key combination.

        Args:
            shortcut: Shortcut string (e.g., "Cmd+Shift+D")
        """
        # Parse shortcut string
        parts = shortcut.lower().replace(" ", "").split("+")
        self._shortcut_keys = set(parts)

        # Normalize common variations
        normalized = set()
        for part in self._shortcut_keys:
            if part in ("command", "meta", "\u2318"):
                normalized.add("cmd")
            elif part in ("\u21e7",):
                normalized.add("shift")
            elif part in ("control", "\u2303"):
                normalized.add("ctrl")
            elif part in ("option", "\u2325"):
                normalized.add("alt")
            else:
                normalized.add(part)

        self._shortcut_keys = normalized

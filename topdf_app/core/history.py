"""History storage for recent conversions.

Stores the last 10 conversions in a JSON file for quick access.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import QObject, Signal, QStandardPaths


@dataclass
class HistoryEntry:
    """A single conversion history entry."""

    name: str  # Document name
    pdf_path: str  # Path to PDF file
    page_count: int  # Number of pages
    timestamp: str  # ISO format timestamp
    has_summary: bool = False  # Whether AI summary was generated

    @classmethod
    def create(
        cls,
        name: str,
        pdf_path: str,
        page_count: int,
        has_summary: bool = False,
    ) -> "HistoryEntry":
        """Create a new history entry with current timestamp.

        Args:
            name: Document name
            pdf_path: Path to PDF
            page_count: Number of pages
            has_summary: Whether summary was generated

        Returns:
            New HistoryEntry
        """
        return cls(
            name=name,
            pdf_path=pdf_path,
            page_count=page_count,
            timestamp=datetime.now().isoformat(),
            has_summary=has_summary,
        )

    def get_relative_time(self) -> str:
        """Get human-readable relative time.

        Returns:
            String like "2h ago", "1d ago", "just now"
        """
        try:
            dt = datetime.fromisoformat(self.timestamp)
            now = datetime.now()
            diff = now - dt

            seconds = diff.total_seconds()
            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                mins = int(seconds // 60)
                return f"{mins}m ago"
            elif seconds < 86400:
                hours = int(seconds // 3600)
                return f"{hours}h ago"
            elif seconds < 604800:
                days = int(seconds // 86400)
                return f"{days}d ago"
            else:
                weeks = int(seconds // 604800)
                return f"{weeks}w ago"
        except Exception:
            return ""


class HistoryManager(QObject):
    """Manages conversion history storage.

    Signals:
        history_changed: Emitted when history is modified
    """

    MAX_ENTRIES = 10

    history_changed = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize history manager.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)

        self._history: List[HistoryEntry] = []
        self._history_file = self._get_history_path()
        self._load()

    def _get_history_path(self) -> Path:
        """Get the path to the history file.

        Returns:
            Path to history.json
        """
        # Use app data location
        data_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        if not data_path:
            data_path = str(Path.home() / ".topdf")

        data_dir = Path(data_path)
        data_dir.mkdir(parents=True, exist_ok=True)

        return data_dir / "history.json"

    def _load(self) -> None:
        """Load history from disk."""
        try:
            if self._history_file.exists():
                with open(self._history_file, "r") as f:
                    data = json.load(f)
                    self._history = [
                        HistoryEntry(**entry) for entry in data
                    ]
        except Exception:
            self._history = []

    def _save(self) -> None:
        """Save history to disk."""
        try:
            with open(self._history_file, "w") as f:
                json.dump(
                    [asdict(entry) for entry in self._history],
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def add(
        self,
        name: str,
        pdf_path: str,
        page_count: int,
        has_summary: bool = False,
    ) -> None:
        """Add a new entry to history.

        Args:
            name: Document name
            pdf_path: Path to PDF
            page_count: Number of pages
            has_summary: Whether summary was generated
        """
        entry = HistoryEntry.create(
            name=name,
            pdf_path=pdf_path,
            page_count=page_count,
            has_summary=has_summary,
        )

        # Remove duplicate if exists (same PDF path)
        self._history = [
            e for e in self._history if e.pdf_path != pdf_path
        ]

        # Add to front
        self._history.insert(0, entry)

        # Trim to max entries
        self._history = self._history[: self.MAX_ENTRIES]

        self._save()
        self.history_changed.emit()

    def update_summary(self, pdf_path: str) -> None:
        """Mark an entry as having a summary.

        Args:
            pdf_path: Path to the PDF
        """
        for entry in self._history:
            if entry.pdf_path == pdf_path:
                entry.has_summary = True
                self._save()
                self.history_changed.emit()
                break

    def get_all(self) -> List[HistoryEntry]:
        """Get all history entries.

        Returns:
            List of history entries (newest first)
        """
        return self._history.copy()

    def get_recent(self, count: int = 3) -> List[HistoryEntry]:
        """Get most recent entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent entries
        """
        return self._history[:count]

    def clear(self) -> None:
        """Clear all history."""
        self._history = []
        self._save()
        self.history_changed.emit()

    def remove(self, pdf_path: str) -> None:
        """Remove an entry by PDF path.

        Args:
            pdf_path: Path to the PDF to remove
        """
        self._history = [
            e for e in self._history if e.pdf_path != pdf_path
        ]
        self._save()
        self.history_changed.emit()

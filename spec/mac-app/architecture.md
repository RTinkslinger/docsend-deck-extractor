# Mac App Architecture Specification

## Document Info
- **Project**: DocSend to PDF Converter - Mac App
- **Version**: 1.0
- **Last Updated**: 2025-01-07

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    macOS Menu Bar                            │
│                      [Tray Icon]                             │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Compact Main Window (~320px)             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Screen 1: URL Input (Home)                    │  │   │
│  │  │  Screen 2: Progress                            │  │   │
│  │  │  Screen 3: Auth (Email / Passcode)             │  │   │
│  │  │  Screen 4: Ask Summarize                       │  │   │
│  │  │  Screen 5: Summarizing                         │  │   │
│  │  │  Screen 6: Complete                            │  │   │
│  │  │  Screen 7: Error                               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            QThread Worker (Background)                │   │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────────┐   │   │
│  │  │ Scraper  │ │ PDFBuilder │ │ Summarizer       │   │   │
│  │  │(existing)│ │ (existing) │ │ (existing)       │   │   │
│  │  └──────────┘ └────────────┘ └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| Main Entry | `main.py` | Application entry point, initialize Qt |
| App Controller | `app.py` | Main application logic, coordination |
| Tray Icon | `ui/tray.py` | Menu bar icon, context menu, show/hide |
| Main Window | `ui/main_window.py` | Window container with stacked screens |
| Screens | `ui/screens/*.py` | Individual UI screens |
| Conversion Worker | `core/worker.py` | Background thread for conversion |
| State Manager | `core/state.py` | Application state and transitions |
| Settings Manager | `core/settings.py` | QSettings persistence |
| History Manager | `core/history.py` | Recent conversions storage |
| Shortcut Handler | `core/shortcuts.py` | Global keyboard shortcuts |
| Styles | `ui/styles.py` | QSS stylesheets |

---

## 2. Directory Structure

```
topdf_app/                          # Mac GUI Application
├── __init__.py
├── main.py                         # Entry point
├── app.py                          # Main application controller
│
├── core/                           # Core logic
│   ├── __init__.py
│   ├── worker.py                   # ConversionWorker (QThread)
│   ├── state.py                    # State machine
│   ├── history.py                  # Recent conversions
│   ├── settings.py                 # QSettings wrapper
│   └── shortcuts.py                # Global hotkey handler
│
├── ui/                             # User interface
│   ├── __init__.py
│   ├── tray.py                     # QSystemTrayIcon
│   ├── main_window.py              # Main window container
│   ├── settings_panel.py           # Inline settings UI
│   ├── styles.py                   # QSS stylesheets
│   └── screens/                    # Individual screens
│       ├── __init__.py
│       ├── home.py                 # URL input + history
│       ├── progress.py             # Progress bar
│       ├── auth_email.py           # Email-only auth
│       ├── auth_passcode.py        # Email + passcode auth
│       ├── ask_summarize.py        # Summary prompt
│       ├── summarizing.py          # Summary progress
│       ├── complete.py             # Success + actions
│       └── error.py                # Error with details
│
└── resources/                      # Static resources
    ├── icons/
    │   ├── app_icon.icns           # macOS app icon
    │   ├── tray_icon.png           # Menu bar icon
    │   └── tray_icon_active.png    # Animated state
    └── lucide/                     # UI icons
        └── *.svg

packaging/                          # Build & distribution
├── build.py                        # py2app configuration
├── bundle_deps.py                  # Tesseract + Chromium bundling
├── Info.plist                      # macOS metadata
├── create_dmg.sh                   # DMG creation script
└── dmg_background.png              # DMG background image

tests_app/                          # Mac app tests
├── __init__.py
├── conftest.py
├── test_tray.py
├── test_main_window.py
├── test_worker.py
├── test_state.py
├── test_settings.py
├── test_history.py
├── test_shortcuts.py
└── test_integration.py
```

---

## 3. Component Specifications

### 3.1 Main Entry (`main.py`)

```python
import sys
from PySide6.QtWidgets import QApplication
from topdf_app.app import DocSendApp

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    docsend_app = DocSendApp()
    docsend_app.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### 3.2 App Controller (`app.py`)

```python
class DocSendApp:
    """Main application controller."""

    def __init__(self):
        self.tray = TrayIcon()
        self.window = MainWindow()
        self.worker = None
        self.state = StateManager()
        self.settings = SettingsManager()
        self.history = HistoryManager()
        self.shortcuts = ShortcutHandler()

    def start(self):
        """Initialize and show tray icon."""
        self.tray.show()
        self.shortcuts.register()
        self._connect_signals()

    def start_conversion(self, url: str):
        """Begin conversion process."""
        self.state.set_state(State.PROGRESS)
        self.worker = ConversionWorker(url)
        self.worker.progress.connect(self._on_progress)
        self.worker.auth_required.connect(self._on_auth_required)
        self.worker.complete.connect(self._on_complete)
        self.worker.error.connect(self._on_error)
        self.worker.start()
```

### 3.3 Tray Icon (`ui/tray.py`)

```python
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon

class TrayIcon(QSystemTrayIcon):
    """Menu bar tray icon."""

    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("resources/icons/tray_icon.png"))
        self._setup_menu()
        self.activated.connect(self._on_activated)

    def _setup_menu(self):
        menu = QMenu()
        menu.addAction("Open", self._show_window)
        menu.addSeparator()
        # History items added dynamically
        menu.addSeparator()
        menu.addAction("Settings...")
        menu.addAction("Quit", QApplication.quit)
        self.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self._toggle_window()

    def set_converting(self, active: bool):
        """Show animated icon during conversion."""
        icon = "tray_icon_active.png" if active else "tray_icon.png"
        self.setIcon(QIcon(f"resources/icons/{icon}"))
```

### 3.4 Main Window (`ui/main_window.py`)

```python
from PySide6.QtWidgets import QMainWindow, QStackedWidget

class MainWindow(QMainWindow):
    """Compact main window with stacked screens."""

    WINDOW_WIDTH = 320

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocSend to PDF")
        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.CustomizeWindowHint |
            Qt.WindowCloseButtonHint
        )

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add screens
        self.screens = {
            "home": HomeScreen(),
            "progress": ProgressScreen(),
            "auth_email": AuthEmailScreen(),
            "auth_passcode": AuthPasscodeScreen(),
            "ask_summarize": AskSummarizeScreen(),
            "summarizing": SummarizingScreen(),
            "complete": CompleteScreen(),
            "error": ErrorScreen(),
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

    def show_screen(self, name: str):
        """Navigate to specified screen."""
        self.stack.setCurrentWidget(self.screens[name])
        self.adjustSize()  # Resize to fit content
```

### 3.5 Conversion Worker (`core/worker.py`)

```python
from PySide6.QtCore import QThread, Signal
from topdf.converter import Converter
from topdf.auth import AuthType

class ConversionWorker(QThread):
    """Background worker for DocSend conversion."""

    progress = Signal(int, str)        # (percent, status_message)
    auth_required = Signal(str)        # auth_type: "email" or "passcode"
    complete = Signal(str, int)        # (pdf_path, page_count)
    error = Signal(str, str)           # (error_message, details)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.email = None
        self.passcode = None
        self._auth_event = threading.Event()

    def run(self):
        """Execute conversion in background thread."""
        try:
            converter = Converter()

            # Custom progress callback
            def on_progress(current, total, status):
                percent = int((current / total) * 100)
                self.progress.emit(percent, status)

            # Custom auth callback
            def on_auth_required(auth_type: AuthType):
                self.auth_required.emit(auth_type.value)
                self._auth_event.wait()  # Block until credentials provided
                self._auth_event.clear()
                return self.email, self.passcode

            result = asyncio.run(converter.convert(
                url=self.url,
                progress_callback=on_progress,
                auth_callback=on_auth_required
            ))

            self.complete.emit(str(result.pdf_path), result.page_count)

        except Exception as e:
            self.error.emit(str(e), traceback.format_exc())

    def provide_credentials(self, email: str, passcode: str = None):
        """Called from main thread when user enters credentials."""
        self.email = email
        self.passcode = passcode
        self._auth_event.set()  # Resume worker thread
```

### 3.6 State Manager (`core/state.py`)

```python
from enum import Enum
from PySide6.QtCore import QObject, Signal

class State(Enum):
    HOME = "home"
    PROGRESS = "progress"
    AUTH_EMAIL = "auth_email"
    AUTH_PASSCODE = "auth_passcode"
    PDF_READY = "pdf_ready"
    ASK_SUMMARIZE = "ask_summarize"
    SUMMARIZING = "summarizing"
    COMPLETE = "complete"
    ERROR = "error"

class StateManager(QObject):
    """Application state machine."""

    state_changed = Signal(State)

    def __init__(self):
        super().__init__()
        self._state = State.HOME

    @property
    def state(self) -> State:
        return self._state

    def set_state(self, new_state: State):
        self._state = new_state
        self.state_changed.emit(new_state)

    def can_transition(self, from_state: State, to_state: State) -> bool:
        """Validate state transitions."""
        valid_transitions = {
            State.HOME: [State.PROGRESS],
            State.PROGRESS: [State.AUTH_EMAIL, State.PDF_READY, State.ERROR],
            State.AUTH_EMAIL: [State.PROGRESS, State.AUTH_PASSCODE],
            State.AUTH_PASSCODE: [State.PROGRESS],
            State.PDF_READY: [State.ASK_SUMMARIZE, State.COMPLETE],
            State.ASK_SUMMARIZE: [State.SUMMARIZING, State.COMPLETE],
            State.SUMMARIZING: [State.COMPLETE, State.ERROR],
            State.COMPLETE: [State.HOME],
            State.ERROR: [State.PROGRESS, State.HOME],
        }
        return to_state in valid_transitions.get(from_state, [])
```

### 3.7 Settings Manager (`core/settings.py`)

```python
from PySide6.QtCore import QSettings
from pathlib import Path

class SettingsManager:
    """Persistent settings using QSettings."""

    DEFAULTS = {
        "save_folder": str(Path.home() / "Downloads"),
        "summary_mode": "ask",  # auto, ask, off
        "shortcut": "Cmd+Shift+D",
        "start_at_login": False,
    }

    def __init__(self):
        self._settings = QSettings("topdf", "DocSend to PDF")

    def get(self, key: str):
        return self._settings.value(key, self.DEFAULTS.get(key))

    def set(self, key: str, value):
        self._settings.setValue(key, value)
        self._settings.sync()

    @property
    def save_folder(self) -> Path:
        return Path(self.get("save_folder"))

    @property
    def summary_mode(self) -> str:
        return self.get("summary_mode")

    @property
    def shortcut(self) -> str:
        return self.get("shortcut")
```

### 3.8 History Manager (`core/history.py`)

```python
import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HistoryItem:
    pdf_path: str
    company_name: str
    page_count: int
    timestamp: datetime

class HistoryManager:
    """Recent conversions storage."""

    MAX_ITEMS = 10
    HISTORY_FILE = Path.home() / ".config" / "topdf" / "history.json"

    def __init__(self):
        self._items: list[HistoryItem] = []
        self._load()

    def add(self, pdf_path: str, company_name: str, page_count: int):
        item = HistoryItem(
            pdf_path=pdf_path,
            company_name=company_name,
            page_count=page_count,
            timestamp=datetime.now()
        )
        self._items.insert(0, item)
        self._items = self._items[:self.MAX_ITEMS]
        self._save()

    def get_recent(self) -> list[HistoryItem]:
        return self._items

    def _load(self):
        if self.HISTORY_FILE.exists():
            data = json.loads(self.HISTORY_FILE.read_text())
            self._items = [HistoryItem(**item) for item in data]

    def _save(self):
        self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(item) for item in self._items]
        self.HISTORY_FILE.write_text(json.dumps(data, default=str))
```

### 3.9 Shortcut Handler (`core/shortcuts.py`)

```python
from pynput import keyboard

class ShortcutHandler:
    """Global keyboard shortcut handler."""

    def __init__(self, callback):
        self.callback = callback
        self.listener = None
        self.shortcut = {keyboard.Key.cmd, keyboard.Key.shift}
        self.current_keys = set()

    def register(self):
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def unregister(self):
        if self.listener:
            self.listener.stop()

    def _on_press(self, key):
        self.current_keys.add(key)

        # Check for Cmd+Shift+D
        if (self.shortcut.issubset(self.current_keys) and
            hasattr(key, 'char') and key.char == 'd'):
            self.callback()

    def _on_release(self, key):
        self.current_keys.discard(key)
```

---

## 4. Dependency Bundling

### 4.1 Tesseract OCR

**Bundle location:**
```
DocSend to PDF.app/
└── Contents/
    └── Resources/
        └── tesseract/
            ├── bin/
            │   └── tesseract
            └── share/
                └── tessdata/
                    └── eng.traineddata
```

**Runtime setup:**
```python
import os
from pathlib import Path

def setup_tesseract():
    """Configure Tesseract to use bundled binary."""
    if getattr(sys, 'frozen', False):
        # Running as bundled app
        app_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent
        tesseract_path = app_dir / "tesseract" / "bin" / "tesseract"
        tessdata_path = app_dir / "tesseract" / "share" / "tessdata"

        os.environ["PATH"] = f"{tesseract_path.parent}:{os.environ['PATH']}"
        os.environ["TESSDATA_PREFIX"] = str(tessdata_path.parent)
```

**Bundling script (`packaging/bundle_deps.py`):**
```python
def bundle_tesseract():
    """Download and bundle Tesseract for macOS."""
    # Download pre-compiled Tesseract binary
    url = "https://github.com/tesseract-ocr/tesseract/releases/..."

    # Extract to Resources/tesseract/
    # Include eng.traineddata
```

### 4.2 Chromium Browser

**Bundle location:**
```
DocSend to PDF.app/
└── Contents/
    └── Frameworks/
        └── Chromium.app/  (~200MB)
```

**Runtime setup:**
```python
import os
from pathlib import Path

def setup_playwright():
    """Configure Playwright to use bundled Chromium."""
    if getattr(sys, 'frozen', False):
        app_dir = Path(__file__).parent.parent
        browsers_path = app_dir / "Frameworks"
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path)
```

**Bundling script:**
```python
def bundle_chromium():
    """Download and bundle Chromium for Playwright."""
    # Use playwright install to get correct version
    # Copy to Frameworks/Chromium.app/
    # ~200MB
```

---

## 5. Threading Model

### 5.1 Thread Communication

```
┌────────────────────────────────────────────────────────────────┐
│                     Main Thread (Qt)                            │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │ TrayIcon │    │MainWindow│    │  Screens │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│       │              │               │                         │
│       └──────────────┼───────────────┘                         │
│                      │                                          │
│              Qt Signals/Slots                                   │
│                      │                                          │
└──────────────────────┼──────────────────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐
│   Worker Thread     │  │  Shortcut Thread    │
│   (QThread)         │  │  (pynput listener)  │
│                     │  │                     │
│  - Conversion       │  │  - Key monitoring   │
│  - OCR              │  │  - Callback to main │
│  - API calls        │  │                     │
└─────────────────────┘  └─────────────────────┘
```

### 5.2 Signal Definitions

```python
# ConversionWorker signals
progress = Signal(int, str)         # (percent, status)
auth_required = Signal(str)         # auth_type
complete = Signal(str, int)         # (pdf_path, page_count)
error = Signal(str, str)            # (message, details)

# StateManager signals
state_changed = Signal(State)       # new_state

# SettingsManager signals
setting_changed = Signal(str, object)  # (key, value)
```

---

## 6. Data Flow

### 6.1 Conversion Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User enters URL on HomeScreen                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. App validates URL format (docsend.com/view/...)           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. ConversionWorker starts in background thread              │
│    - StateManager.set_state(PROGRESS)                        │
│    - Show ProgressScreen                                     │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌──────────────────────┐   ┌──────────────────────┐
│ 4a. Auth not needed  │   │ 4b. Auth required    │
│     Continue...      │   │     - Emit signal    │
│                      │   │     - Show AuthScreen│
│                      │   │     - Dock bounce    │
│                      │   │     - Wait for input │
└──────────────────────┘   └──────────────────────┘
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Scraper captures screenshots (progress updates)           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. PDFBuilder creates PDF                                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. Save PDF to configured location                           │
│    - Filename from page title or URL slug                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌──────────────────────┐   ┌──────────────────────┐
│ 8a. summary_mode=ask │   │ 8b. summary_mode=off │
│     Show AskSummarize│   │     or mode=auto     │
│     Screen           │   │     (auto runs it)   │
└──────────────────────┘   └──────────────────────┘
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 9. Show CompleteScreen                                       │
│    - Add to history                                          │
│    - Show macOS notification                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Error Handling

### 7.1 Error Types

| Error | Handling | User Message |
|-------|----------|--------------|
| Invalid URL | Show on HomeScreen | "Please enter a valid DocSend URL" |
| Network timeout | Show ErrorScreen | "Connection timed out. Check your internet." |
| Auth failed | Show on AuthScreen | "Invalid credentials. Please try again." |
| Page not found | Show ErrorScreen | "Document not found. It may have been removed." |
| PDF build failed | Show ErrorScreen | "Failed to create PDF. Please try again." |
| Summary failed | Warning, continue | "Summary generation failed. PDF saved." |

### 7.2 Error Recovery

```python
class ErrorScreen(QWidget):
    retry = Signal()
    go_home = Signal()

    def __init__(self):
        # Show error message
        # Expandable details section
        # Retry button → emits retry signal
        # Back to Home link → emits go_home signal
```

---

## 8. macOS Integration

### 8.1 Dock Bounce

```python
from AppKit import NSApp, NSInformationalRequest

def bounce_dock():
    """Request user attention by bouncing dock icon."""
    NSApp.requestUserAttention_(NSInformationalRequest)
```

### 8.2 Notifications

```python
from Foundation import NSUserNotification, NSUserNotificationCenter

def show_notification(title: str, message: str):
    """Show macOS notification."""
    notification = NSUserNotification.alloc().init()
    notification.setTitle_(title)
    notification.setInformativeText_(message)

    center = NSUserNotificationCenter.defaultUserNotificationCenter()
    center.deliverNotification_(notification)
```

### 8.3 Start at Login

```python
from LaunchServices import LSSharedFileListCreate, LSSharedFileListInsertItemURL

def set_login_item(enabled: bool):
    """Add/remove app from Login Items."""
    # Use LSSharedFileList API
```

---

## 9. Build Configuration

### 9.1 py2app Setup (`packaging/build.py`)

```python
from setuptools import setup

APP = ['topdf_app/main.py']
DATA_FILES = [
    ('resources/icons', ['resources/icons/*.png']),
    ('tesseract', ['bundled/tesseract/*']),
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'resources/icons/app_icon.icns',
    'plist': {
        'CFBundleName': 'DocSend to PDF',
        'CFBundleIdentifier': 'com.topdf.docsend',
        'CFBundleVersion': '1.0.0',
        'LSUIElement': True,  # Menu bar app (no dock icon)
        'NSHighResolutionCapable': True,
    },
    'packages': ['PySide6', 'playwright', 'topdf', 'topdf_app'],
    'includes': ['pynput'],
    'frameworks': ['bundled/Chromium.app'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### 9.2 DMG Creation (`packaging/create_dmg.sh`)

```bash
#!/bin/bash

# Create DMG with drag-to-Applications layout
create-dmg \
    --volname "DocSend to PDF" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "DocSend to PDF.app" 150 200 \
    --app-drop-link 450 200 \
    --background "packaging/dmg_background.png" \
    "DocSend_to_PDF_1.0.0.dmg" \
    "dist/"
```

---

## 10. Performance Targets

| Metric | Target |
|--------|--------|
| App startup | <5s to ready state |
| Window show/hide | <100ms |
| 20-page conversion | <60s |
| Memory during conversion | <600MB |
| Memory idle | <100MB |
| DMG size | <300MB |

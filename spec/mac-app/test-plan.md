# Test Plan

## Document Info
- **Project**: DocSend to PDF Converter - Mac App (topdf_app)
- **Version**: 1.0
- **Last Updated**: 2025-01-07
- **Related**: CLI test plan at `spec/test-plan.md`

---

## 1. Testing Strategy

### 1.1 Test Pyramid

```
                    ┌─────────────┐
                    │   Manual    │  ← Real DocSend + fresh macOS install
                    │   E2E       │  ← 25 tests (E2E-APP-01 to E2E-APP-25)
                    ├─────────────┤
                    │ Integration │  ← UI + Worker + Core modules
                    │   Tests     │  ← 20 tests
                    ├─────────────┤
                    │    Unit     │  ← Individual components
                    │    Tests    │  ← 60 tests
                    └─────────────┘
```

### 1.2 Coverage Targets

| Level | Target Coverage | Tool |
|-------|-----------------|------|
| Unit Tests | >85% | pytest-cov |
| Integration Tests | >75% | pytest-cov |
| Overall | >80% | pytest-cov |

### 1.3 Testing Focus Areas

| Area | Priority | Why |
|------|----------|-----|
| Conversion Flow | Critical | Core functionality |
| Auth Handling | Critical | Required for most documents |
| DMG Installation | Critical | First-time user experience |
| State Management | High | UI consistency |
| Threading | High | No UI freezing |
| Error Handling | High | User recovery |
| Settings Persistence | Medium | Quality of life |
| History | Medium | Convenience feature |
| Global Shortcuts | Low | Power user feature |

---

## 2. Unit Tests

### 2.1 tray.py Tests (TrayIcon)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| TRAY-001 | `test_icon_visible` | Tray icon appears | Icon in menu bar |
| TRAY-002 | `test_menu_items` | Context menu structure | All items present |
| TRAY-003 | `test_show_window` | Click tray icon | Window opens below |
| TRAY-004 | `test_hide_window` | Click outside | Window closes |
| TRAY-005 | `test_history_menu` | History submenu | Shows recent PDFs |
| TRAY-006 | `test_settings_action` | Settings menu item | Settings screen shown |
| TRAY-007 | `test_quit_action` | Quit menu item | App exits cleanly |
| TRAY-008 | `test_tooltip_update` | During conversion | Tooltip shows progress |

### 2.2 main_window.py Tests (MainWindow)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| WIN-001 | `test_window_dimensions` | Window size | 320x480 pixels |
| WIN-002 | `test_frameless_window` | No title bar | Clean popup look |
| WIN-003 | `test_stay_on_top` | Window flag | Always above others |
| WIN-004 | `test_screen_navigation` | Switch screens | Correct screen shows |
| WIN-005 | `test_initial_screen` | App launch | Home screen visible |
| WIN-006 | `test_close_on_focus_lost` | Click outside | Window hides |

### 2.3 screens/ Tests

#### HomeScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| HOME-001 | `test_url_input_field` | Text input exists | Can type URL |
| HOME-002 | `test_paste_button` | Paste button | Pastes from clipboard |
| HOME-003 | `test_convert_button` | Convert triggers | Conversion starts |
| HOME-004 | `test_url_validation_valid` | Valid DocSend URL | No error shown |
| HOME-005 | `test_url_validation_invalid` | Non-DocSend URL | Error message |
| HOME-006 | `test_empty_url` | Click convert empty | Error message |
| HOME-007 | `test_history_button` | History button | Opens history |
| HOME-008 | `test_settings_button` | Settings button | Opens settings |

#### ProgressScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| PROG-001 | `test_progress_bar_updates` | Progress signal | Bar advances |
| PROG-002 | `test_percentage_display` | Show percentage | "45%" visible |
| PROG-003 | `test_page_counter` | Current page | "Page 5 of 20" |
| PROG-004 | `test_cancel_button` | Cancel clicked | Conversion stops |
| PROG-005 | `test_url_display` | Show URL | Truncated URL visible |
| PROG-006 | `test_animation` | Progress animation | Smooth visual |

#### AuthScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| AUTH-001 | `test_email_input` | Email field | Can type email |
| AUTH-002 | `test_email_validation` | Invalid email | Error shown |
| AUTH-003 | `test_submit_email` | Submit email | Signal emitted |
| AUTH-004 | `test_passcode_input` | Passcode field | Can type passcode |
| AUTH-005 | `test_passcode_masked` | Passcode display | Dots shown |
| AUTH-006 | `test_submit_passcode` | Submit passcode | Signal emitted |
| AUTH-007 | `test_back_button` | Cancel auth | Returns to home |
| AUTH-008 | `test_error_display` | Invalid creds | Error visible |

#### CompleteScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| COMP-001 | `test_success_message` | Display success | Green checkmark |
| COMP-002 | `test_filename_display` | Show filename | Correct name |
| COMP-003 | `test_open_pdf_button` | Open PDF click | PDF opens |
| COMP-004 | `test_show_in_finder` | Show in Finder | Finder opens |
| COMP-005 | `test_new_conversion` | New button | Returns to home |
| COMP-006 | `test_summary_prompt` | Ask for summary | Dialog appears |

#### ErrorScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| ERR-001 | `test_error_message` | Display error | Message visible |
| ERR-002 | `test_retry_button` | Retry click | Restarts conversion |
| ERR-003 | `test_start_over` | Start over | Returns to home |
| ERR-004 | `test_error_details` | Technical details | Expandable |

#### SettingsScreen Tests

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| SET-001 | `test_save_location_picker` | Browse button | Folder picker opens |
| SET-002 | `test_summary_toggle` | Toggle modes | Cycles auto/ask/off |
| SET-003 | `test_login_toggle` | Start at login | Toggle works |
| SET-004 | `test_api_key_input` | Enter API key | Key saved |
| SET-005 | `test_reset_button` | Reset settings | Defaults restored |
| SET-006 | `test_back_button` | Back to home | Home screen shown |

### 2.4 worker.py Tests (ConversionWorker)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| WORK-001 | `test_start_conversion` | Start worker | Thread starts |
| WORK-002 | `test_progress_signal` | Progress updates | Signals emitted |
| WORK-003 | `test_auth_required_signal` | Auth needed | Signal emitted |
| WORK-004 | `test_complete_signal` | Conversion done | Signal with path |
| WORK-005 | `test_error_signal` | Error occurs | Signal with message |
| WORK-006 | `test_cancel` | Cancel requested | Worker stops |
| WORK-007 | `test_resume_after_auth` | Auth provided | Worker resumes |
| WORK-008 | `test_thread_cleanup` | After completion | Thread cleaned up |
| WORK-009 | `test_browser_cleanup` | On error | Browser terminated |
| WORK-010 | `test_no_main_thread_block` | During conversion | Main thread responsive |

### 2.5 state.py Tests (StateManager)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| STATE-001 | `test_initial_state` | App start | State is HOME |
| STATE-002 | `test_transition_to_progress` | Start conversion | State → PROGRESS |
| STATE-003 | `test_transition_to_auth` | Auth required | State → AUTH_* |
| STATE-004 | `test_transition_to_complete` | PDF ready | State → COMPLETE |
| STATE-005 | `test_transition_to_error` | Error occurs | State → ERROR |
| STATE-006 | `test_invalid_transition` | Bad transition | Exception raised |
| STATE-007 | `test_state_signal` | State changes | Signal emitted |
| STATE-008 | `test_reset_state` | Reset called | State → HOME |

### 2.6 settings.py Tests (SettingsManager)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| SETTINGS-001 | `test_default_save_location` | Fresh install | ~/Downloads |
| SETTINGS-002 | `test_custom_save_location` | Set custom path | Path persisted |
| SETTINGS-003 | `test_summary_mode_default` | Fresh install | "ask" |
| SETTINGS-004 | `test_summary_mode_persist` | Change mode | Survives restart |
| SETTINGS-005 | `test_start_at_login` | Toggle on | Login item created |
| SETTINGS-006 | `test_api_key_save` | Save key | Key in config |
| SETTINGS-007 | `test_api_key_load` | Load key | Key returned |
| SETTINGS-008 | `test_reset_all` | Reset settings | All defaults |

### 2.7 history.py Tests (HistoryManager)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| HIST-001 | `test_add_entry` | Add conversion | Entry stored |
| HIST-002 | `test_entry_fields` | Entry data | url, path, timestamp |
| HIST-003 | `test_max_entries` | Add 15 entries | Only 10 kept |
| HIST-004 | `test_order` | Multiple entries | Newest first |
| HIST-005 | `test_persistence` | Restart app | History loaded |
| HIST-006 | `test_clear_history` | Clear called | Empty list |

### 2.8 shortcuts.py Tests (ShortcutManager)

| Test ID | Test Case | Description | Expected Result |
|---------|-----------|-------------|-----------------|
| SHORT-001 | `test_register_shortcut` | Register ⌘⇧D | Shortcut active |
| SHORT-002 | `test_shortcut_callback` | Press ⌘⇧D | Callback fired |
| SHORT-003 | `test_unregister` | Unregister | Shortcut inactive |
| SHORT-004 | `test_conflict_handling` | Key in use | Error handled |

---

## 3. Integration Tests

### 3.1 UI + Worker Integration

| Test ID | Test Case | Components | Description |
|---------|-----------|------------|-------------|
| INT-APP-001 | `test_home_to_progress` | Home + Worker | URL → Progress screen |
| INT-APP-002 | `test_progress_updates_ui` | Progress + Worker | Signals update UI |
| INT-APP-003 | `test_worker_to_complete` | Worker + Complete | PDF → Complete screen |
| INT-APP-004 | `test_worker_to_error` | Worker + Error | Error → Error screen |
| INT-APP-005 | `test_cancel_flow` | Progress + Worker | Cancel stops worker |

### 3.2 Auth Flow Integration

| Test ID | Test Case | Components | Description |
|---------|-----------|------------|-------------|
| INT-APP-006 | `test_email_auth_flow` | Worker + Auth + Scraper | Email gate handled |
| INT-APP-007 | `test_passcode_auth_flow` | Worker + Auth + Scraper | Passcode gate handled |
| INT-APP-008 | `test_auth_resume` | Auth + Worker | Conversion resumes |
| INT-APP-009 | `test_auth_cancel` | Auth + Worker | Returns to home |
| INT-APP-010 | `test_dock_bounce` | Auth + macOS | Dock bounces |

### 3.3 Core Module Integration

| Test ID | Test Case | Components | Description |
|---------|-----------|------------|-------------|
| INT-APP-011 | `test_scraper_integration` | Worker + topdf.scraper | Screenshots captured |
| INT-APP-012 | `test_pdf_builder_integration` | Worker + topdf.pdf_builder | PDF created |
| INT-APP-013 | `test_summarizer_integration` | Worker + topdf.summarizer | Summary generated |
| INT-APP-014 | `test_config_integration` | Settings + topdf.config | API key flows |

### 3.4 Persistence Integration

| Test ID | Test Case | Components | Description |
|---------|-----------|------------|-------------|
| INT-APP-015 | `test_settings_persist` | Settings + QSettings | Survives restart |
| INT-APP-016 | `test_history_persist` | History + JSON | Survives restart |
| INT-APP-017 | `test_api_key_persist` | Settings + Config | Key survives |

### 3.5 Notification Integration

| Test ID | Test Case | Components | Description |
|---------|-----------|------------|-------------|
| INT-APP-018 | `test_complete_notification` | Worker + macOS | Notification sent |
| INT-APP-019 | `test_notification_click` | Notification + Finder | Opens PDF location |
| INT-APP-020 | `test_error_notification` | Worker + macOS | Error notification |

---

## 4. Manual E2E Test Cases

### 4.1 Installation Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-01 | DMG mount | Double-click DMG | Disk image mounts |
| E2E-APP-02 | Drag to Applications | Drag app icon | App copies to /Applications |
| E2E-APP-03 | First launch | Open app | No Gatekeeper warning* |
| E2E-APP-04 | Menu bar icon | After launch | Icon appears in menu bar |
| E2E-APP-05 | No setup required | First conversion | Works without brew/pip |

*With proper code signing/notarization

### 4.2 Core Workflow Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-06 | Open document | Paste URL → Convert | PDF saved to Downloads |
| E2E-APP-07 | Email protected | Enter email when prompted | PDF saved after auth |
| E2E-APP-08 | Passcode protected | Enter email + passcode | PDF saved after auth |
| E2E-APP-09 | Invalid URL | Enter google.com | Error message shown |
| E2E-APP-10 | Progress display | During conversion | Percentage + page shown |
| E2E-APP-11 | Cancel conversion | Click cancel | Conversion stops |
| E2E-APP-12 | Open PDF | Click Open PDF | Preview.app opens |
| E2E-APP-13 | Show in Finder | Click Show in Finder | Finder reveals file |

### 4.3 Clipboard & Shortcuts Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-14 | Clipboard detection | Copy DocSend URL | Prompt appears |
| E2E-APP-15 | Global shortcut | Press ⌘⇧D | Window opens/closes |
| E2E-APP-16 | Paste button | Click paste | URL from clipboard |

### 4.4 Settings Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-17 | Custom save location | Change in settings | PDFs save to new location |
| E2E-APP-18 | Summary mode | Toggle auto/ask/off | Behavior changes |
| E2E-APP-19 | Start at login | Enable → reboot | App auto-starts |
| E2E-APP-20 | API key | Enter Perplexity key | Key persists |

### 4.5 History Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-21 | History appears | After conversion | Entry in tray menu |
| E2E-APP-22 | History click | Click history item | Finder reveals file |
| E2E-APP-23 | History limit | Convert 15 docs | Only 10 in history |

### 4.6 Summary Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-24 | Generate summary | Complete → Yes | Markdown file created |
| E2E-APP-25 | Skip summary | Complete → No | No markdown file |

### 4.7 Error Handling Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-26 | Network error | Disconnect during conversion | Graceful error screen |
| E2E-APP-27 | Invalid credentials | Enter wrong email | Error + retry option |
| E2E-APP-28 | DocSend unavailable | Use broken URL | Clear error message |
| E2E-APP-29 | Retry after error | Click retry | Conversion restarts |

### 4.8 Bundled Dependency Tests

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-APP-30 | Tesseract bundled | Generate summary on fresh Mac | OCR works |
| E2E-APP-31 | Chromium bundled | Convert on fresh Mac | Browser works |
| E2E-APP-32 | No brew required | Fresh macOS install | App works without Homebrew |

---

## 5. Platform Compatibility Tests

### 5.1 macOS Version Matrix

| macOS Version | Install | Launch | Convert | Summary |
|---------------|---------|--------|---------|---------|
| 11 Big Sur | Test | Test | Test | Test |
| 12 Monterey | Test | Test | Test | Test |
| 13 Ventura | Test | Test | Test | Test |
| 14 Sonoma | Test | Test | Test | Test |
| 15 Sequoia | Test | Test | Test | Test |

### 5.2 Architecture Matrix

| Architecture | macOS 11+ | Notes |
|--------------|-----------|-------|
| Intel (x86_64) | Test | Older Macs |
| Apple Silicon (arm64) | Test | M1/M2/M3 Macs |

---

## 6. Test Fixtures

### 6.1 conftest.py Structure

```python
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance."""
    from topdf_app.ui.main_window import MainWindow
    window = MainWindow()
    yield window
    window.close()

@pytest.fixture
def mock_worker():
    """Mock ConversionWorker for UI tests."""
    from unittest.mock import MagicMock
    worker = MagicMock()
    worker.progress = MagicMock()
    worker.auth_required = MagicMock()
    worker.complete = MagicMock()
    worker.error = MagicMock()
    return worker

@pytest.fixture
def temp_settings(tmp_path, monkeypatch):
    """Temporary settings location."""
    settings_path = tmp_path / "settings"
    monkeypatch.setenv("TOPDF_SETTINGS_PATH", str(settings_path))
    return settings_path

@pytest.fixture
def temp_history(tmp_path, monkeypatch):
    """Temporary history file."""
    history_file = tmp_path / "history.json"
    monkeypatch.setenv("TOPDF_HISTORY_PATH", str(history_file))
    return history_file

@pytest.fixture
def sample_docsen_url():
    """Valid DocSend URL for testing."""
    return "https://docsend.com/view/test123"

@pytest.fixture
def mock_conversion_result():
    """Mock successful conversion result."""
    return {
        "pdf_path": "/tmp/Test Company.pdf",
        "filename": "Test Company.pdf",
        "page_count": 20
    }
```

### 6.2 Qt Test Utilities

```python
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

def click_button(button):
    """Simulate button click."""
    QTest.mouseClick(button, Qt.LeftButton)

def type_text(widget, text):
    """Type text into widget."""
    widget.clear()
    QTest.keyClicks(widget, text)

def wait_for_signal(signal, timeout=5000):
    """Wait for Qt signal."""
    from PySide6.QtCore import QEventLoop, QTimer
    loop = QEventLoop()
    signal.connect(loop.quit)
    QTimer.singleShot(timeout, loop.quit)
    loop.exec()
```

---

## 7. Test Execution

### 7.1 Commands

```bash
# Run all unit tests
pytest tests/mac_app/ -v --ignore=tests/mac_app/test_integration.py

# Run with coverage
pytest tests/mac_app/ -v --cov=topdf_app --cov-report=html

# Run specific component tests
pytest tests/mac_app/test_tray.py -v
pytest tests/mac_app/test_worker.py -v

# Run integration tests
pytest tests/mac_app/test_integration.py -v

# Run with verbose Qt output
QT_DEBUG_PLUGINS=1 pytest tests/mac_app/ -v -s

# Run until first failure
pytest tests/mac_app/ -x
```

### 7.2 Test Environment Setup

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-qt

# Install app dependencies
pip install PySide6 pynput pyobjc-framework-Cocoa

# Ensure core modules available
pip install -e .
```

---

## 8. DMG Testing Checklist

### 8.1 Pre-Release Checklist

| # | Check | Status |
|---|-------|--------|
| 1 | App bundle created without errors | ☐ |
| 2 | Code signing applied | ☐ |
| 3 | Notarization submitted and approved | ☐ |
| 4 | DMG mounts on double-click | ☐ |
| 5 | App drags to Applications | ☐ |
| 6 | App launches without security warning | ☐ |
| 7 | Menu bar icon appears | ☐ |
| 8 | Window opens on tray click | ☐ |
| 9 | Can enter URL and convert | ☐ |
| 10 | PDF saved to Downloads | ☐ |
| 11 | Bundled Tesseract works | ☐ |
| 12 | Bundled Chromium works | ☐ |
| 13 | Settings persist after quit | ☐ |
| 14 | History persists after quit | ☐ |
| 15 | App quits cleanly | ☐ |

### 8.2 Fresh Install Test Protocol

1. Use fresh macOS VM or clean user account
2. No Homebrew installed
3. No Python/pip installed
4. Download DMG from distribution
5. Install by dragging to Applications
6. Launch app
7. Complete full conversion workflow
8. Verify no external dependencies needed

---

## 9. Continuous Integration

### 9.1 GitHub Actions Workflow

```yaml
name: Mac App Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        pip install PySide6 pytest-qt

    - name: Run unit tests
      run: pytest tests/mac_app/ -v --cov=topdf_app --cov-report=xml
      env:
        QT_QPA_PLATFORM: offscreen

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 9.2 Build Verification

```yaml
  build:
    runs-on: macos-latest
    needs: test

    steps:
    - uses: actions/checkout@v4

    - name: Build app bundle
      run: python packaging/build.py

    - name: Verify bundle structure
      run: |
        test -d "dist/DocSend to PDF.app"
        test -f "dist/DocSend to PDF.app/Contents/MacOS/topdf_app"
        test -d "dist/DocSend to PDF.app/Contents/Resources/tesseract"

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: mac-app
        path: dist/*.app
```

---

## 10. Test Reporting

### 10.1 Coverage Report

```bash
pytest tests/mac_app/ --cov=topdf_app --cov-report=html
open htmlcov/index.html
```

### 10.2 Expected Test Results

```
==================== test session starts ====================
platform darwin -- Python 3.11.0
PySide6 6.6.0
collected 105 items

tests/mac_app/test_tray.py ........ [8%]
tests/mac_app/test_main_window.py ...... [13%]
tests/mac_app/test_home_screen.py ........ [21%]
tests/mac_app/test_progress_screen.py ...... [27%]
tests/mac_app/test_auth_screen.py ........ [34%]
tests/mac_app/test_complete_screen.py ...... [40%]
tests/mac_app/test_error_screen.py .... [44%]
tests/mac_app/test_settings_screen.py ...... [50%]
tests/mac_app/test_worker.py .......... [60%]
tests/mac_app/test_state.py ........ [68%]
tests/mac_app/test_settings.py ........ [75%]
tests/mac_app/test_history.py ...... [81%]
tests/mac_app/test_shortcuts.py .... [85%]
tests/mac_app/test_integration.py .................... [100%]

==================== 105 passed in 23.45s ====================
```

---

## 11. Test Schedule by Phase

| Phase | Tests to Run | Timing |
|-------|--------------|--------|
| Phase 1 | Tray + Window unit tests | After infrastructure |
| Phase 2 | Worker + Progress tests | After conversion pipeline |
| Phase 3 | Auth screen tests | After auth flow |
| Phase 4 | Settings + Shortcuts tests | After settings panel |
| Phase 5 | Summary screen tests | After summary integration |
| Phase 6 | Bundled dependency tests | After bundling |
| Phase 7 | DMG installation tests | After packaging |
| Phase 8 | Full E2E suite | Before release |

---

## 12. Bug Tracking

### 12.1 Test Failure Protocol

1. Document failure in issue tracker
2. Include:
   - Test name and ID
   - Error message and stack trace
   - macOS version and architecture
   - Steps to reproduce
   - Screenshots if UI-related
3. Assign priority based on severity
4. Create fix branch
5. Add regression test

### 12.2 Severity Levels

| Level | Definition | Response |
|-------|------------|----------|
| Critical | App crashes or won't install | Fix immediately |
| High | Conversion fails | Fix within 24h |
| Medium | UI issue or minor bug | Fix within 1 week |
| Low | Cosmetic / edge case | Fix when convenient |

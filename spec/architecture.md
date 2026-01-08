# Architecture Specification

## Document Info
- **Project**: DocSend to PDF Converter (topdf)
- **Version**: 2.0
- **Last Updated**: 2025-01-08
- **Changes**: Removed AI summarization, simplified to core PDF conversion

---

## 1. System Overview

### 1.1 High-Level Architecture

```
+------------------------------------------------------------------+
|                         CLI Layer                                 |
|                    (cli.py - Click framework)                     |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|                      Orchestrator                                 |
|                  (converter.py - Coordinates all modules)         |
+-------+-----------------+----------------------------------------+
        |                 |
        v                 v
+---------------+  +---------------+
|   Scraper     |  |  PDF Builder  |
| (scraper.py)  |  |(pdf_builder)  |
+---------------+  +---------------+
        |
        v
+---------------+
|   Auth        |
|   Handler     |
|  (auth.py)    |
+---------------+
```

### 1.2 Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| CLI | `cli.py` | Parse arguments, invoke converter, display results |
| Orchestrator | `converter.py` | Coordinate scraper + builder, handle filename |
| Scraper | `scraper.py` | Navigate DocSend, capture screenshots |
| Auth Handler | `auth.py` | Detect and handle authentication |
| PDF Builder | `pdf_builder.py` | Convert screenshots to PDF |
| Exceptions | `exceptions.py` | Custom exception classes |

---

## 2. Directory Structure

```
docsend-deck-extractor/
|
|-- spec/                           # Specification documents
|   |-- SPEC.md                     # Full specification
|   |-- requirements.md             # Requirements
|   |-- architecture.md             # This document
|   |-- test-plan.md                # Testing strategy
|
|-- topdf/                          # Main package
|   |-- __init__.py                 # Package init, version
|   |-- cli.py                      # Click CLI entry point
|   |-- converter.py                # Main orchestrator
|   |-- scraper.py                  # Playwright DocSend scraper
|   |-- auth.py                     # Authentication handlers
|   |-- pdf_builder.py              # Screenshot to PDF
|   |-- name_extractor.py           # Filename utilities
|   |-- exceptions.py               # Custom exceptions
|
|-- topdf_app/                      # Mac app GUI
|   |-- app.py                      # Application controller
|   |-- main.py                     # Entry point
|   |-- ui/                         # UI components
|   |   |-- screens/                # Screen widgets
|   |   |-- main_window.py          # Main window
|   |   |-- tray.py                 # Menu bar icon
|   |   |-- settings_panel.py       # Settings panel
|   |-- core/                       # App core
|       |-- worker.py               # Background conversion worker
|       |-- settings.py             # Settings management
|       |-- history.py              # Conversion history
|       |-- names.py                # Random name generator
|       |-- state.py                # State machine
|
|-- tests/                          # Test suite
|   |-- conftest.py                 # Pytest fixtures
|   |-- test_cli.py
|   |-- test_scraper.py
|   |-- test_pdf_builder.py
|   |-- test_auth.py
|
|-- converted PDFs/                 # Output directory
|-- pyproject.toml                  # Package configuration
|-- README.md
```

---

## 3. Component Specifications

### 3.1 CLI Module (`cli.py`)

**Purpose**: Entry point for the application

**Interface**:
```python
@click.command()
@click.argument('url')
@click.option('--email', '-e', help='Email for protected documents')
@click.option('--passcode', '-p', help='Passcode for protected documents')
@click.option('--name', '-n', help='Override output filename')
@click.option('--output', '-o', default='converted PDFs', help='Output directory')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--debug', is_flag=True, help='Show browser window')
@click.version_option()
def topdf(url, email, passcode, name, output, verbose, debug):
    """Convert a DocSend link to PDF."""
```

**Dependencies**: click, rich, converter

### 3.2 Orchestrator (`converter.py`)

**Purpose**: Coordinates the conversion workflow

**Interface**:
```python
class Converter:
    def __init__(self, output_dir: str = 'converted PDFs', headless: bool = True):
        pass

    async def convert(
        self,
        url: str,
        email: Optional[str] = None,
        passcode: Optional[str] = None,
        output_name: Optional[str] = None,
        verbose: bool = False
    ) -> ConversionResult:
        """
        Main conversion entry point.

        Returns:
            ConversionResult with pdf_path, page_count
        """
```

**Dependencies**: scraper, pdf_builder

### 3.3 Scraper Module (`scraper.py`)

**Purpose**: Navigate DocSend and capture page screenshots

**Interface**:
```python
class DocSendScraper:
    def __init__(self, headless: bool = True, verbose: bool = False):
        pass

    async def scrape(
        self,
        url: str,
        email: Optional[str] = None,
        passcode: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> ScrapeResult:
        """
        Scrape DocSend document.

        Returns:
            ScrapeResult with screenshots, page_title, page_count
        """

    async def close(self):
        """Cleanup browser resources."""
```

**Internal Methods**:
| Method | Purpose |
|--------|---------|
| `_validate_url` | Verify DocSend URL format |
| `_launch_browser` | Start Playwright browser |
| `_navigate` | Go to URL with retry |
| `_detect_auth_type` | Check for email/passcode gate |
| `_handle_auth` | Fill authentication forms |
| `_dismiss_cookie_banner` | Dismiss cookie consent overlays |
| `_get_page_count` | Extract total page count |
| `_capture_pages` | Screenshot each page |

### 3.4 Auth Handler (`auth.py`)

**Purpose**: Handle DocSend authentication flows

**Interface**:
```python
class AuthType(Enum):
    NONE = "none"
    EMAIL = "email"
    PASSCODE = "passcode"

class AuthHandler:
    async def detect_auth_type(self, page: Page) -> AuthType:
        """Detect which authentication is required."""

    async def handle_email_gate(
        self,
        page: Page,
        email: str
    ) -> bool:
        """Submit email form. Returns success."""

    async def handle_passcode_gate(
        self,
        page: Page,
        email: str,
        passcode: str
    ) -> bool:
        """Submit email + passcode. Returns success."""
```

### 3.5 PDF Builder (`pdf_builder.py`)

**Purpose**: Convert screenshots to PDF

**Interface**:
```python
class PDFBuilder:
    def build(self, screenshots: List[bytes]) -> bytes:
        """
        Convert list of PNG screenshots to PDF.

        Args:
            screenshots: List of PNG image bytes

        Returns:
            PDF file as bytes
        """

    def _normalize_dimensions(self, images: List[Image]) -> List[Image]:
        """Resize images to consistent dimensions."""

    def _optimize_images(self, images: List[Image]) -> List[bytes]:
        """Compress images for smaller PDF size."""
```

### 3.6 Exceptions (`exceptions.py`)

```python
class TopdfError(Exception):
    """Base exception for topdf."""

class InvalidURLError(TopdfError):
    """URL is not a valid DocSend link."""

class AuthenticationError(TopdfError):
    """Authentication failed."""

class EmailRequiredError(AuthenticationError):
    """Email required but not provided."""

class PasscodeRequiredError(AuthenticationError):
    """Passcode required but not provided."""

class ScrapingError(TopdfError):
    """Failed to scrape document."""

class PDFBuildError(TopdfError):
    """Failed to build PDF."""

class TimeoutError(TopdfError):
    """Operation timed out."""
```

---

## 4. Data Flow

```
+---------------------------------------------------------------------+
| INPUT: topdf https://docsend.com/view/abc123 -e user@email.com      |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 1: URL Validation                                               |
|   --> Regex: ^https?://(www\.)?docsend\.com/view/[\w-]+             |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 2: Browser Launch                                               |
|   --> Playwright Chromium (headless)                                 |
|   --> Viewport: 1920x1080                                           |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 3: Navigate to URL                                              |
|   --> page.goto(url, wait_until='networkidle')                      |
|   --> Timeout: 30 seconds                                           |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 4: Auth Detection & Handling                                    |
|   --> Detect: email gate or passcode gate                           |
|   --> If auth required: fill form, submit, wait                     |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 4.5: Dismiss Cookie Banner                                      |
|   --> Detect cookie consent overlay (GDPR banner)                   |
|   --> Click "Accept All" or similar dismiss button                  |
|   --> Fallback: inject CSS to hide known banner selectors           |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 5: Page Enumeration                                             |
|   --> Find: pagination element                                       |
|   --> Extract: total page count (e.g., "1 of 24")                   |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 6: Screenshot Capture Loop                                      |
|   --> For page in range(1, total_pages + 1):                        |
|       --> Navigate to page                                          |
|       --> Wait for render                                           |
|       --> Capture screenshot (PNG)                                  |
|       --> Add to screenshots[]                                      |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 7: PDF Assembly                                                 |
|   --> Load screenshots as PIL Images                                |
|   --> Normalize dimensions                                          |
|   --> Convert to PDF with img2pdf                                   |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 8: Save PDF                                                     |
|   --> filename = --name flag or random cartoon name                 |
|   --> Path: "converted PDFs/{filename}.pdf"                         |
|   --> Handle duplicates: append (1), (2), etc.                      |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| STEP 9: Cleanup                                                      |
|   --> Close browser                                                 |
|   --> Delete temp files                                             |
+----------------------------------+----------------------------------+
                                   |
                                   v
+---------------------------------------------------------------------+
| OUTPUT: converted PDFs/{filename}.pdf                                |
+---------------------------------------------------------------------+
```

---

## 5. Mac App Architecture

### 5.1 State Machine

The Mac app uses a simple state machine for screen navigation:

```python
class State(Enum):
    HOME = "home"           # URL input screen
    PROGRESS = "progress"   # Conversion in progress
    AUTH_EMAIL = "auth_email"       # Email input required
    AUTH_PASSCODE = "auth_passcode" # Passcode input required
    COMPLETE = "complete"   # Conversion complete, show result
    ERROR = "error"         # Error occurred
```

### 5.2 Component Diagram

```
+------------------+
|   System Tray    |
|   (tray.py)      |
+--------+---------+
         |
         v
+------------------+     +-------------------+
|   Main Window    |---->| Settings Panel    |
|  (main_window.py)|     | (settings_panel.py)
+--------+---------+     +-------------------+
         |
         v
+------------------+
|    Screens       |
|  (screens/*.py)  |
|  - HomeScreen    |
|  - ProgressScreen|
|  - AuthScreens   |
|  - CompleteScreen|
|  - ErrorScreen   |
+--------+---------+
         |
         v
+------------------+
| ConversionWorker |
|   (worker.py)    |
|   (QThread)      |
+------------------+
```

### 5.3 Settings

```python
# Default settings
DEFAULTS = {
    "save_folder": "converted PDFs",
    "start_at_login": False,
}
```

---

## 6. Error Handling Strategy

### Exception Hierarchy
```
TopdfError (base)
|-- InvalidURLError
|-- AuthenticationError
|   |-- EmailRequiredError
|   |-- PasscodeRequiredError
|   |-- InvalidCredentialsError
|-- ScrapingError
|   |-- PageLoadError
|   |-- ScreenshotError
|-- PDFBuildError
|-- TimeoutError
```

### Retry Policy
| Operation | Max Retries | Backoff |
|-----------|-------------|---------|
| Page navigation | 3 | Exponential (1s, 2s, 4s) |
| Screenshot capture | 3 | Linear (1s each) |
| Auth form submit | 1 | None |

### Error Messages
All errors should include:
1. What went wrong
2. Possible cause
3. Suggested action

Example:
```
Error: Failed to load DocSend page
Cause: Network timeout after 30 seconds
Action: Check your internet connection and try again
```

---

## 7. Security Considerations

### Data Handling
- No document content logged
- No URLs logged
- DocSend credentials never persisted
- All PDF processing is local
- No external API calls

### Browser Security
- Headless mode (no visual UI)
- Isolated browser context
- Clean up on exit

### Input Validation
- URL format validated
- Email format validated (basic)
- Path traversal prevented

---

## 8. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| 20-page conversion | <60 seconds | End-to-end time |
| Memory usage | <500MB | Peak during conversion |
| PDF size | <5MB per 20 pages | Output file size |
| Browser startup | <5 seconds | First page load |

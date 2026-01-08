# DocSend to PDF

A privacy-focused tool that converts DocSend links to local PDF files. Available as both a **CLI tool** and a **native Mac app**. Designed for investors to save and review pitch decks locally.

Made with ❤️ by [team DeVC](https://www.devc.com)

## Mac App

The Mac app provides a simple, always-accessible interface from your menu bar.

### Installation

1. Download `DocSend-to-PDF-v1.1.0.dmg` from [Releases](https://github.com/RTinkslinger/docsend-deck-extractor/releases)
2. Drag "DocSend to PDF" to Applications
3. Launch the app - it appears in your menu bar

### Usage

1. **Copy a DocSend URL** to your clipboard
2. **Click the menu bar icon** or press **Cmd+Shift+D**
3. The URL auto-fills from clipboard
4. Click **Convert** - PDF saves to `converted PDFs/` folder

### Features

- **Menu bar app** - Always accessible, minimal footprint
- **Global shortcut** - Cmd+Shift+D opens the app instantly
- **Clipboard detection** - Auto-detects DocSend URLs
- **Interactive auth** - Prompts for email/passcode when needed
- **Random naming** - Fun cartoon character names for easy identification
- **History** - Quick access to recent conversions

### Settings

Access settings via the gear icon:
- **Save location** - Choose where PDFs are saved
- **Start at login** - Launch when you log in
- **Keyboard shortcut** - Configure global shortcut

---

## CLI Tool

For automation and scripting, use the command-line interface.

### Features

- **Local Processing** - All PDF conversion happens on your machine; no document data leaves your computer
- **Authentication Support** - Handles email-gated and passcode-protected DocSend links
- **Custom naming** - Name your PDFs with the `--name` flag

### Installation

#### Prerequisites

- Python 3.9+

#### Install the Package

```bash
# Clone the repository
git clone https://github.com/RTinkslinger/docsend-deck-extractor.git
cd docsend-deck-extractor

# Install in editable mode
pip install -e .

# Install Playwright browser
playwright install chromium
```

### Usage

#### Basic Conversion

```bash
# Convert a DocSend link
topdf https://docsend.com/view/abc123

# With custom filename
topdf https://docsend.com/view/abc123 --name "Company Pitch Deck"
```

#### With Authentication

```bash
# Email-protected document
topdf https://docsend.com/view/abc123 --email investor@fund.com

# Passcode-protected document
topdf https://docsend.com/view/abc123 --email investor@fund.com --passcode secret123

# Short flags
topdf https://docsend.com/view/abc123 -e investor@fund.com -p secret123
```

#### Custom Output

```bash
# Custom output directory
topdf https://docsend.com/view/abc123 --output ~/Desktop/decks

# Verbose mode
topdf https://docsend.com/view/abc123 --verbose
```

### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--email` | `-e` | Email for protected documents |
| `--passcode` | `-p` | Passcode for protected documents |
| `--name` | `-n` | Custom output filename |
| `--output` | `-o` | Output directory (default: `converted PDFs/`) |
| `--verbose` | `-v` | Enable verbose output |
| `--debug` | | Show browser window for debugging |
| `--version` | | Show version |
| `--help` | | Show help |

## What's New in v1.1.0

- **Fixed**: PDF duplicate page bug - all pages now captured correctly
- **Fixed**: Cookie consent banner handling for international users
- **Added**: DeVC branding with link to website
- **Improved**: Navigation reliability for DocSend documents
- **Improved**: Resource bundling for standalone Mac app

## How It Works

1. **Browser Automation** - Uses Playwright to open DocSend in headless Chromium
2. **Authentication** - Detects and fills email/passcode gates if required
3. **Screenshot Capture** - Captures each page as a high-quality screenshot
4. **PDF Generation** - Combines screenshots into a single PDF using img2pdf

## Architecture

```
CLI (cli.py)
    |
Converter (converter.py)
    |-- Scraper (scraper.py) --> Auth (auth.py)
    |-- PDFBuilder (pdf_builder.py)
```

## Development

### Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=topdf --cov-report=html

# Code formatting
black topdf/ tests/
ruff check topdf/ tests/

# Type checking
mypy topdf/
```

### Project Structure

```
docsend-deck-extractor/
|-- topdf/                    # Core conversion library
|   |-- cli.py               # CLI entry point
|   |-- converter.py         # Orchestrator
|   |-- scraper.py           # Playwright scraper
|   |-- auth.py              # Authentication handlers
|   |-- pdf_builder.py       # Screenshot to PDF
|   |-- name_extractor.py    # Filename utilities
|   |-- exceptions.py        # Custom exceptions
|-- topdf_app/               # Mac app GUI
|   |-- app.py               # Application controller
|   |-- main.py              # Entry point
|   |-- ui/                  # UI components
|   |   |-- screens/         # Screen widgets
|   |   |-- tray.py          # Menu bar icon
|   |   |-- main_window.py   # Main window
|   |-- core/                # App core
|       |-- worker.py        # Background workers
|       |-- history.py       # History manager
|       |-- names.py         # Random name generator
|-- scripts/                 # Build scripts
|   |-- build_app.py         # PyInstaller build
|   |-- bundle_deps.py       # Dependency bundling
|   |-- create_icon.py       # Icon generation
|-- tests/                   # Test suite
|-- spec/                    # Specifications
|-- converted PDFs/          # Default output directory
|-- pyproject.toml           # Package configuration
```

## Tech Stack

- **[Playwright](https://playwright.dev/)** - Browser automation
- **[PySide6](https://doc.qt.io/qtforpython-6/)** - Mac app GUI
- **[Click](https://click.palletsprojects.com/)** - CLI framework
- **[img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf)** - PDF generation
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting
- **[Pillow](https://pillow.readthedocs.io/)** - Image processing
- **[PyInstaller](https://pyinstaller.org/)** - App bundling

## Privacy

- PDF conversion is 100% local
- No document data is ever sent to external services
- No logging of document content or URLs

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

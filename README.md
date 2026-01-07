# DocSend Deck Extractor

A privacy-focused Python CLI tool that converts DocSend links to local PDF files. Designed for investors to save and review pitch decks locally while preserving confidentiality.

## Features

- **Local Processing** - All PDF conversion happens on your machine; no document data leaves your computer
- **Authentication Support** - Handles email-gated and passcode-protected DocSend links
- **Auto-naming** - Automatically extracts company name from the document for file naming
- **AI Summarization** (Optional) - Generates structured company analysis using Perplexity AI:
  - Company description (≤200 characters)
  - Sector tags (primary + secondary)
  - Early customer traction indicators
  - Recently funded peer companies (up to 10)

## Installation

### Prerequisites

- Python 3.9+
- Tesseract OCR (for name extraction and summarization)

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

### Install the Package

```bash
# Clone the repository
git clone https://github.com/RTinkslinger/docsend-deck-extractor.git
cd docsend-deck-extractor

# Install in editable mode
pip install -e .

# Install Playwright browser
playwright install chromium

# Optional: Install with AI summarization support
pip install -e ".[summarize]"
```

## Usage

### Basic Conversion

```bash
# Convert an open DocSend link
topdf https://docsend.com/view/abc123

# Output: converted PDFs/CompanyName.pdf
```

### With Authentication

```bash
# Email-protected document
topdf https://docsend.com/view/abc123 --email investor@fund.com

# Passcode-protected document
topdf https://docsend.com/view/abc123 --email investor@fund.com --passcode secret123

# Short flags
topdf https://docsend.com/view/abc123 -e investor@fund.com -p secret123
```

### Custom Output

```bash
# Custom filename
topdf https://docsend.com/view/abc123 --name "Acme Corp Series A"

# Custom output directory
topdf https://docsend.com/view/abc123 --output ~/Desktop/decks

# Verbose mode
topdf https://docsend.com/view/abc123 --verbose
```

### AI Summarization

After PDF conversion, you'll be prompted to generate an AI summary. This requires a Perplexity API key.

```bash
# Check configured API keys
topdf --check-key

# Reset saved API keys
topdf --reset-key
```

The summary is saved as a markdown file alongside the PDF (e.g., `CompanyName.md`).

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--email` | `-e` | Email for protected documents |
| `--passcode` | `-p` | Passcode for protected documents |
| `--name` | `-n` | Override output filename |
| `--output` | `-o` | Output directory (default: `converted PDFs/`) |
| `--verbose` | `-v` | Enable verbose output |
| `--check-key` | | Show configured API keys |
| `--reset-key` | | Clear saved API keys |
| `--version` | | Show version |
| `--help` | | Show help |

## How It Works

1. **Browser Automation** - Uses Playwright to open DocSend in headless Chromium
2. **Authentication** - Detects and fills email/passcode gates if required
3. **Screenshot Capture** - Captures each page as a high-quality screenshot
4. **Name Extraction** - Parses page title (fallback: OCR first slide)
5. **PDF Generation** - Combines screenshots into a single PDF using img2pdf
6. **AI Summary** (Optional) - OCR first 5 pages → Perplexity analyzes deck + finds funded peers

## Architecture

```
CLI (cli.py)
    ↓
Converter (converter.py)
    ├── Scraper (scraper.py) → Auth (auth.py)
    ├── PDFBuilder (pdf_builder.py)
    ├── NameExtractor (name_extractor.py)
    └── [Optional] Summarizer (summarizer.py) → Config (config.py)
```

## Configuration

API keys are stored in `~/.config/topdf/config.json`. You can also use environment variables:

```bash
export PERPLEXITY_API_KEY=your-api-key
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
├── topdf/                    # Main package
│   ├── cli.py               # CLI entry point
│   ├── converter.py         # Orchestrator
│   ├── scraper.py           # Playwright scraper
│   ├── auth.py              # Authentication handlers
│   ├── pdf_builder.py       # Screenshot to PDF
│   ├── name_extractor.py    # Company name extraction
│   ├── config.py            # API key management
│   ├── summarizer.py        # AI summarization
│   └── exceptions.py        # Custom exceptions
├── tests/                    # Test suite
├── spec/                     # Specifications
├── converted PDFs/           # Default output directory
├── pyproject.toml           # Package configuration
└── requirements.txt         # Dependencies
```

## Tech Stack

- **[Playwright](https://playwright.dev/)** - Browser automation
- **[Click](https://click.palletsprojects.com/)** - CLI framework
- **[img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf)** - PDF generation
- **[pytesseract](https://github.com/madmaze/pytesseract)** - OCR
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting
- **[Pillow](https://pillow.readthedocs.io/)** - Image processing

## Privacy

- Core PDF conversion is 100% local
- Document data is only sent to AI if you explicitly opt-in to summarization
- No logging of document content or URLs
- API keys are stored locally only

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

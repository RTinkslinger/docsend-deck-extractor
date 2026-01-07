# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**topdf** - A privacy-focused tool that converts DocSend links to PDF files. Designed for investors to locally convert pitch decks. Available as:
- **CLI tool** (`topdf`) - Command-line interface
- **Mac app** (planned) - Native macOS menu bar application with bundled dependencies

Optional AI summarization generates structured company analysis and finds recently funded peer companies using Perplexity.

## Commands

```bash
# Install for development
pip install -e .
playwright install chromium
brew install tesseract  # macOS - only needed for AI summarization

# Run CLI
topdf <docsend_url>
topdf <url> --email user@example.com --passcode secret
topdf <url> --name "Custom Name" --output ~/Desktop
topdf --check-key   # Show configured API keys
topdf --reset-key   # Clear saved API keys

# Run tests
pytest tests/ -v
pytest tests/test_scraper.py -v  # single module
pytest tests/ --cov=topdf --cov-report=html  # with coverage

# Code quality
black topdf/ tests/
ruff check topdf/ tests/
mypy topdf/
```

## Architecture

### CLI Architecture
```
CLI (cli.py) → Converter (converter.py) → Scraper (scraper.py) → Auth (auth.py)
                                        → PDFBuilder (pdf_builder.py)
            → [Optional] Summarizer (summarizer.py) → Config (config.py)
```

### Mac App Architecture (Planned)
```
Tray Icon → Main Window → Screens (Home, Progress, Auth, Complete)
                        → ConversionWorker (QThread) → [Reuses CLI modules]
```

**Conversion flow:**
1. Scraper uses Playwright to open DocSend in headless Chromium
2. Auth handler detects and fills email/passcode gates if required
3. Scraper captures screenshots of each page
4. PDFBuilder combines screenshots into PDF using img2pdf
5. Output saved to `converted PDFs/{name}.pdf` (name from `--name` flag or URL slug)
6. [Optional] AI summary via Perplexity API

## Key Design Decisions

- **Playwright over API**: DocSend renders client-side; no public download API
- **Screenshot capture**: Preserves exact visual fidelity of slides
- **Local-only processing**: Privacy requirement - no document data leaves machine
- **Filename**: User-provided (`--name`) or derived from URL slug (no OCR extraction)

## Tech Stack

- **playwright**: Browser automation
- **click**: CLI framework
- **img2pdf**: PDF generation
- **pytesseract**: OCR for summarization only (optional)
- **rich**: Progress bars and output
- **Pillow**: Image processing
- **openai**: Perplexity API (optional)
- **PySide6**: Mac app GUI (planned)

## Exception Hierarchy

All custom exceptions inherit from `TopdfError` in `exceptions.py`:
- `InvalidURLError`, `AuthenticationError`, `ScrapingError`, `PDFBuildError`, `TimeoutError`
- `SummaryError`, `OCRError` (for summarization)

## Specifications

Detailed specs are in `spec/`:

**CLI specs:**
- `spec/SPEC.md` - Full CLI specification
- `spec/architecture.md` - Component specifications and data flow
- `spec/requirements.md` - Functional and non-functional requirements
- `spec/test-plan.md` - Test cases and coverage targets

**Mac app specs:**
- `spec/mac-app/SPEC.md` - Mac app specification with phased development
- `spec/mac-app/architecture.md` - GUI components, dependency bundling
- `spec/mac-app/requirements.md` - App-specific requirements
- `spec/mac-app/test-plan.md` - GUI test cases

**API Keys:** Stored in `~/.config/topdf/config.json` (Perplexity only)

## Changelog Management

This project uses branch-specific changelog files to document iterations.

### Before Starting Work
1. Check if `changelog/{branch-name}.md` exists for the current branch
2. If NOT, prompt the user to run: `./scripts/setup-hooks.sh`
3. The hook will auto-create changelog files for new branches going forward

### After Each Iteration
When you complete a meaningful unit of work (bug fix, feature, refactor), update the changelog:

1. Get current branch: `git branch --show-current`
2. Convert to filename: replace `/` with `-` (e.g., `fix/bug` → `fix-bug.md`)
3. Update `changelog/{branch-name}.md` with:
   - Iteration number (increment from last)
   - Objective
   - Files modified
   - Changes made
   - Test results

### Changelog Template
```
## Iteration N: [Title]

**Objective:** [What you're trying to achieve]

**Files Modified:**
- `path/to/file`

### Changes Made:
1. [Change description]

### Test Results:
- [Test outcome]

---
```

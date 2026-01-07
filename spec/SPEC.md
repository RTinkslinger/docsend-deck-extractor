# DocSend to PDF Converter - Specification

## Table of Contents
1. [Requirements](#1-requirements)
2. [Design Approach](#2-design-approach)
3. [Technology Architecture](#3-technology-architecture)
4. [Phased Build Plan](#4-phased-build-plan)
5. [Testing Strategy](#5-testing-strategy)

---

# 1. Requirements

## 1.1 Functional Requirements

### FR-1: Core Conversion
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Accept DocSend URL as input via CLI command `topdf <url>` | Must Have |
| FR-1.2 | Convert DocSend document to PDF format | Must Have |
| FR-1.3 | Support multi-page documents (pitch decks typically 10-30 pages) | Must Have |
| FR-1.4 | Preserve visual fidelity of original document | Must Have |

### FR-2: Authentication Handling
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Support open/public DocSend links | Must Have |
| FR-2.2 | Support email-gated DocSend links | Must Have |
| FR-2.3 | Support passcode-protected DocSend links | Must Have |
| FR-2.4 | Prompt user for credentials when required | Must Have |
| FR-2.5 | Accept credentials via CLI flags (`--email`, `--passcode`) | Should Have |

### FR-3: File Naming & Organization
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Use `--name` flag or generate random name for filename | Must Have |
| FR-3.2 | Store converted PDFs in `converted PDFs/` folder | Must Have |
| FR-3.3 | Allow custom output directory via `--output` flag | Should Have |
| FR-3.4 | Handle filename conflicts (append number) | Should Have |

### FR-4: User Experience
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Show progress indicator during conversion | Should Have |
| FR-4.2 | Display success message with output file path | Must Have |
| FR-4.3 | Provide clear error messages for failures | Must Have |
| FR-4.4 | Support `--help` flag with usage documentation | Must Have |

## 1.2 Non-Functional Requirements

### NFR-1: Privacy & Security
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1.1 | All PDF conversion must happen locally | Must Have |
| NFR-1.2 | No logging of document content or URLs | Must Have |
| NFR-1.3 | No document data sent to external services | Must Have |

### NFR-2: Performance
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-2.1 | Convert typical 20-page deck in under 60 seconds | Should Have |
| NFR-2.2 | Minimal memory footprint (< 500MB RAM) | Should Have |

### NFR-3: Reliability
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-3.1 | Handle network timeouts gracefully | Should Have |
| NFR-3.2 | Retry failed page captures (max 3 attempts) | Should Have |

### NFR-4: Maintainability
| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-4.1 | Modular code architecture for easy updates | Should Have |
| NFR-4.2 | Handle DocSend UI changes with minimal code changes | Should Have |

## 1.3 Constraints

- **Platform**: macOS (primary), with potential Linux support
- **Python Version**: 3.9+
- **Network**: Requires internet access to fetch DocSend documents

---

# 2. Design Approach

## 2.1 High-Level Architecture

```
+------------------------------------------------------------------+
|                         CLI Layer                                 |
|                    (cli.py - Click framework)                     |
+------------------------------+-----------------------------------+
                               |
                               v
+------------------------------------------------------------------+
|                      Orchestrator                                 |
|                  (Coordinates all modules)                        |
+-------+-----------------+----------------------------------------+
        |                 |
        v                 v
+---------------+  +---------------+
|   Scraper     |  |  PDF Builder  |
| (Playwright)  |  | (img2pdf)     |
+---------------+  +---------------+
        |
        v
+---------------+
|   Auth        |
|   Handler     |
+---------------+
```

## 2.2 Core Design Decisions

### Decision 1: Headless Browser vs API
**Choice**: Headless browser (Playwright)
**Rationale**: DocSend renders documents client-side; no public API for PDF export

### Decision 2: Screenshot Capture vs DOM Extraction
**Choice**: Screenshot capture
**Rationale**: Preserves exact visual fidelity; handles complex layouts/animations

### Decision 3: Filename Strategy
**Choice**: User-provided name or random cartoon character name
- If `--name` flag provided: use that
- Otherwise: generate fun random name (e.g., "Bugs Bunny", "Mickey Mouse")

---

# 3. Technology Architecture

## 3.1 System Architecture Diagram

```
+------------------------------------------------------------------------+
|                              USER                                       |
|                                                                         |
|   $ topdf https://docsend.com/view/abc123 --email investor@fund.com    |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------------------------------------------+
|                         CLI LAYER (cli.py)                              |
|                                                                         |
|  - Parse arguments (url, email, passcode, name, output)                |
|  - Validate URL format                                                  |
|  - Initialize progress display                                          |
|  - Call orchestrator                                                    |
|  - Display result                                                       |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------------------------------------------+
|                     ORCHESTRATOR (converter.py)                         |
|                                                                         |
|  async def convert(url, email, passcode, output_name):                 |
|      1. scraper.scrape(url, email, passcode) -> screenshots[]          |
|      2. pdf_builder.build(screenshots) -> pdf_bytes                    |
|      3. filename = output_name or generate_random_name()               |
|      4. save_pdf(pdf_bytes, filename, output_dir)                      |
|      5. return result                                                   |
+--------+------------------+--------------------------------------------+
         |                  |
         v                  v
+----------------+   +----------------+
|   SCRAPER      |   |  PDF BUILDER   |
| (scraper.py)   |   |(pdf_builder.py)|
|                |   |                |
| - Launch       |   | - Take image   |
|   browser      |   |   list         |
| - Navigate     |   | - Resize to    |
|   to URL       |   |   consistent   |
| - Detect auth  |   |   dimensions   |
| - Fill forms   |   | - Convert to   |
| - Capture      |   |   PDF pages    |
|   pages        |   | - Combine      |
| - Return       |   |   into single  |
|   screenshots  |   |   PDF          |
+--------+-------+   +----------------+
         |
         v
+----------------+
| AUTH HANDLER   |
|(auth.py)       |
|                |
| - Detect gate  |
|   type         |
| - Email form   |
| - Passcode     |
|   form         |
| - Wait for     |
|   access       |
+----------------+
```

## 3.2 Directory Structure

```
docsend-deck-extractor/
|
|-- spec/                           # Specification documents
|   |-- SPEC.md                     # This document
|   |-- requirements.md             # Detailed requirements
|   |-- architecture.md             # Architecture diagrams
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
|   |-- core/                       # App core (worker, settings, etc.)
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

## 3.3 Dependencies

### Production Dependencies
```
playwright>=1.40.0
Pillow>=10.0.0
img2pdf>=0.5.0
click>=8.1.0
rich>=13.0.0
```

### Development Dependencies
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
```

### System Dependencies
```bash
# After pip install
playwright install chromium
```

---

# 4. Phased Build Plan

## Phase 1: Project Foundation
**Goal**: Set up project structure and basic CLI

### Tasks
- [ ] Create directory structure
- [ ] Create `pyproject.toml` with dependencies
- [ ] Create `topdf/__init__.py` with version
- [ ] Create basic `cli.py` with argument parsing
- [ ] Create `exceptions.py` with custom exceptions
- [ ] Verify `topdf --help` works

## Phase 2: Core Scraper (No Auth)
**Goal**: Scrape and capture pages from open DocSend links

### Tasks
- [ ] Create `scraper.py` with `DocSendScraper` class
- [ ] Implement browser launch/close
- [ ] Implement URL navigation with error handling
- [ ] Implement page count detection
- [ ] Implement page navigation
- [ ] Implement screenshot capture
- [ ] Add retry logic for failed captures

## Phase 3: Authentication Handling
**Goal**: Support email and passcode protected documents

### Tasks
- [ ] Create `auth.py` module
- [ ] Implement auth type detection
- [ ] Implement email gate handler
- [ ] Implement passcode gate handler
- [ ] Integrate auth into scraper flow

## Phase 4: PDF Builder
**Goal**: Convert screenshots to single PDF file

### Tasks
- [ ] Create `pdf_builder.py` module
- [ ] Implement image loading from bytes
- [ ] Implement dimension normalization
- [ ] Implement PDF creation with img2pdf
- [ ] Implement image compression/optimization

## Phase 5: Full Integration
**Goal**: Connect all components into working CLI tool

### Tasks
- [ ] Create `converter.py` orchestrator
- [ ] Wire CLI to orchestrator
- [ ] Add progress indicators
- [ ] Implement random name generation
- [ ] Create output directory if not exists
- [ ] End-to-end testing

## Phase 6: Polish & Documentation
**Goal**: Production-ready release

### Tasks
- [ ] Create comprehensive README.md
- [ ] Add installation instructions
- [ ] Add usage examples
- [ ] Final code review and cleanup
- [ ] Ensure all tests pass

---

# 5. Testing Strategy

## 5.1 Test Pyramid

```
                    +-------------+
                    |   Manual    |  <- Real DocSend links
                    |   E2E       |  <- 5-10 tests
                    +-------------+
                    | Integration |  <- Component combinations
                    |   Tests     |  <- 15-20 tests
                    +-------------+
                    |    Unit     |  <- Individual functions
                    |    Tests    |  <- 40-50 tests
                    +-------------+
```

## 5.2 Unit Tests

### scraper.py Tests
| Test Case | Description |
|-----------|-------------|
| `test_url_validation_valid` | Accept valid DocSend URLs |
| `test_url_validation_invalid` | Reject non-DocSend URLs |
| `test_page_count_parsing` | Extract page count from DOM |
| `test_screenshot_is_png` | Screenshots are valid PNG |
| `test_retry_on_failure` | Retry logic works |
| `test_timeout_handling` | Timeout raises exception |

### auth.py Tests
| Test Case | Description |
|-----------|-------------|
| `test_detect_email_gate` | Detect email-only gate |
| `test_detect_passcode_gate` | Detect passcode gate |
| `test_detect_no_auth` | Detect open document |
| `test_email_form_fill` | Email form filled correctly |
| `test_passcode_form_fill` | Both fields filled |

### pdf_builder.py Tests
| Test Case | Description |
|-----------|-------------|
| `test_single_page_pdf` | PDF with one page |
| `test_multi_page_pdf` | PDF with multiple pages |
| `test_page_order` | Pages in correct order |
| `test_image_resize` | Large images resized |
| `test_empty_input` | Error on empty list |
| `test_pdf_is_valid` | Output is valid PDF |

### cli.py Tests
| Test Case | Description |
|-----------|-------------|
| `test_help_flag` | --help shows usage |
| `test_version_flag` | --version shows version |
| `test_missing_url` | Error without URL |
| `test_invalid_url` | Error for non-DocSend |
| `test_all_options` | All flags parsed correctly |

## 5.3 Manual E2E Test Cases

| ID | Scenario | Steps | Expected Result |
|----|----------|-------|-----------------|
| E2E-1 | Open document | `topdf <open_url>` | PDF saved |
| E2E-2 | Email protected | `topdf <url> -e email` | PDF saved after auth |
| E2E-3 | Passcode protected | `topdf <url> -e email -p pass` | PDF saved after auth |
| E2E-4 | Invalid URL | `topdf https://google.com` | Clear error message |
| E2E-5 | Network timeout | Disconnect wifi mid-scrape | Graceful error |
| E2E-6 | Name override | `topdf <url> --name "Test"` | Saved as "Test.pdf" |
| E2E-7 | Custom output | `topdf <url> -o ~/Desktop` | Saved to Desktop |
| E2E-8 | Duplicate name | Run twice with same URL | Second file has (1) |

## 5.4 CI/CD Test Commands

```bash
# Quick test (unit only)
pytest tests/ -v --ignore=tests/test_integration.py

# Full test suite
pytest tests/ -v --cov=topdf --cov-report=html

# With real DocSend URLs (set env vars)
DOCSEND_OPEN_URL=... pytest tests/test_integration.py -v
```

---

# Summary

This specification provides a complete blueprint for building a privacy-preserving DocSend-to-PDF converter. The recommended approach (Playwright browser automation) ensures confidential pitch decks never leave your machine while providing full control over authentication scenarios.

**Key deliverables**:
- Python CLI tool installable via `pip install -e .`
- Command: `topdf <docsend_url>` with auth and naming options
- Output: PDFs in `converted PDFs/` folder
- 6 implementation phases with testing at each step

**Next step**: Begin Phase 1 implementation.

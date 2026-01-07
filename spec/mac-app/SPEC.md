# DocSend to PDF - Mac App Specification

## Document Info
- **Project**: DocSend to PDF Converter - Mac App
- **Version**: 1.0
- **Last Updated**: 2025-01-07
- **Status**: Planned

---

## Table of Contents
1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
3. [Design Approach](#3-design-approach)
4. [Visual Design System](#4-visual-design-system)
5. [Screen Wireframes](#5-screen-wireframes)
6. [State Machine](#6-state-machine)
7. [Phased Build Plan](#7-phased-build-plan)
8. [Acceptance Criteria](#8-acceptance-criteria)

---

# 1. Overview

## 1.1 Summary

Native macOS menu bar application that converts DocSend links to PDF files. Features a compact wizard-style UI with Canva-inspired design, global keyboard shortcut, and distribution as DMG with all dependencies bundled.

## 1.2 Key Features

| Feature | Description |
|---------|-------------|
| Menu bar app | Always accessible from macOS menu bar |
| Compact window | Ultra-minimal 320px wide wizard interface |
| Global shortcut | ⌘⇧D opens app with clipboard URL |
| Clipboard detection | Auto-detects DocSend URLs in clipboard |
| Interactive auth | Prompts for email/passcode when needed |
| AI summarization | Optional Perplexity-powered analysis |
| History | Recent 10 conversions in tray menu |
| Bundled deps | Zero post-install setup (Tesseract + Chromium included) |

## 1.3 Architecture Relationship

The Mac app wraps the existing `topdf/` Python modules:

```
topdf_app/          # Mac app GUI layer
    │
    └── imports from:
        topdf.scraper       # Browser automation
        topdf.converter     # Orchestration
        topdf.pdf_builder   # PDF generation
        topdf.auth          # Auth handling
        topdf.summarizer    # AI summary
        topdf.config        # API keys
```

---

# 2. Requirements

## 2.1 Functional Requirements

### FR-APP-1: Core App Functionality

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-1.1 | Menu bar icon always visible when app running | Must Have |
| FR-APP-1.2 | Click icon opens compact 320px window | Must Have |
| FR-APP-1.3 | Global shortcut (⌘⇧D) opens app | Should Have |
| FR-APP-1.4 | Auto-detect DocSend URLs in clipboard | Should Have |
| FR-APP-1.5 | URL input field with validation | Must Have |

### FR-APP-2: Conversion Flow

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-2.1 | Progress screen with percentage and status | Must Have |
| FR-APP-2.2 | Cancel button during conversion | Should Have |
| FR-APP-2.3 | macOS notification on completion | Should Have |
| FR-APP-2.4 | Open PDF / Show in Finder actions | Must Have |
| FR-APP-2.5 | Save As option for custom location | Should Have |

### FR-APP-3: Authentication

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-3.1 | Email-only auth screen when needed | Must Have |
| FR-APP-3.2 | Email + passcode auth screen when needed | Must Have |
| FR-APP-3.3 | Dock bounce for attention during auth | Should Have |
| FR-APP-3.4 | Clear error messages for auth failures | Must Have |

### FR-APP-4: Settings

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-4.1 | Configurable save location | Should Have |
| FR-APP-4.2 | Summary mode selector (auto/ask/off) | Should Have |
| FR-APP-4.3 | Keyboard shortcut customization | Nice to Have |
| FR-APP-4.4 | Start at login option | Should Have |
| FR-APP-4.5 | API key management for Perplexity | Should Have |

### FR-APP-5: History

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-5.1 | Recent 10 conversions stored | Should Have |
| FR-APP-5.2 | History accessible from tray menu | Should Have |
| FR-APP-5.3 | Click history item opens PDF | Should Have |

### FR-APP-6: Distribution

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-APP-6.1 | DMG installer with drag-to-Applications | Must Have |
| FR-APP-6.2 | Tesseract OCR bundled in app | Must Have |
| FR-APP-6.3 | Chromium browser bundled in app | Must Have |
| FR-APP-6.4 | No post-install setup required | Must Have |
| FR-APP-6.5 | App launches without errors on clean macOS | Must Have |

## 2.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-APP-1 | Platform | macOS 11+ (Big Sur) |
| NFR-APP-2 | Conversion time | <60s for 20-page deck |
| NFR-APP-3 | App bundle size | <300MB DMG |
| NFR-APP-4 | First launch time | <5s to ready state |
| NFR-APP-5 | Memory usage | <600MB during conversion |
| NFR-APP-6 | Window size | 320px wide, variable height |

---

# 3. Design Approach

## 3.1 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| GUI Framework | PySide6 | Native Qt widgets for macOS |
| Global Shortcuts | pynput | Keyboard shortcut handling |
| macOS APIs | pyobjc-framework-Cocoa | Dock bounce, notifications |
| Packaging | py2app | Create .app bundle |
| Browser | Playwright + Chromium | Bundled, headless scraping |
| OCR | Tesseract | Bundled binary |

## 3.2 Threading Model

```
Main Thread (Qt event loop)
    │
    │  start_conversion()
    ├──────────────────────────►  Worker Thread (QThread)
    │                                   │
    │  progress_signal                  │ asyncio.run(convert())
    │◄──────────────────────────────────┤
    │                                   │
    │  auth_required_signal             │
    │◄──────────────────────────────────┤
    │                                   │ (waits for credentials)
    │  provide_credentials()            │
    ├──────────────────────────────────►│
    │                                   │ (resumes)
    │  complete_signal                  │
    │◄──────────────────────────────────┤
```

## 3.3 Dependency Bundling Strategy

### Tesseract OCR (~30MB)

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

At runtime: Set `TESSDATA_PREFIX` environment variable.

### Chromium Browser (~200MB)

```
DocSend to PDF.app/
└── Contents/
    └── Frameworks/
        └── Chromium.app/
```

At runtime: Set `PLAYWRIGHT_BROWSERS_PATH` environment variable.

---

# 4. Visual Design System

## 4.1 Color Palette (Canva-inspired)

| Role | Color | Usage |
|------|-------|-------|
| Primary | `#8B5CF6` (Purple) | Primary buttons, active states |
| Primary Hover | `#7C3AED` | Button hover states |
| Background | `#FFFFFF` | Main window background |
| Surface | `#F9FAFB` | Card backgrounds, inputs |
| Border | `#E5E7EB` | Subtle borders, dividers |
| Text Primary | `#111827` | Headlines, primary text |
| Text Secondary | `#6B7280` | Descriptions, labels |
| Text Muted | `#9CA3AF` | Placeholder text, hints |
| Success | `#10B981` | Success states, checkmarks |
| Error | `#EF4444` | Error states, warnings |

## 4.2 Typography

```
Font Family: SF Pro Display (system) / Inter (fallback)

Hierarchy:
- Title:      16px, Semi-bold (600), #111827
- Subtitle:   14px, Medium (500), #111827
- Body:       14px, Regular (400), #374151
- Secondary:  13px, Regular (400), #6B7280
- Caption:    12px, Regular (400), #9CA3AF
```

## 4.3 Component Styles

```
Buttons:
- Primary (filled):   8px radius, #8B5CF6 bg, white text
- Secondary (outline): 8px radius, 1px #E5E7EB border
- Text (no border):   Just text + icon

Inputs:
- 8px border-radius
- 1px #E5E7EB border
- #F9FAFB background
- 12px horizontal padding

Cards/Sections:
- 12px border-radius
- 1px #E5E7EB border
- 16px padding
- White background
```

## 4.4 Spacing Scale

```
4px  - Tight (icon-to-text)
8px  - Compact (between related items)
12px - Default (form fields)
16px - Comfortable (section padding)
24px - Spacious (between sections)
```

## 4.5 Icons

- Style: Outlined, 20px size, 1.5px stroke
- Source: Lucide Icons (open source)
- Key icons: Link, Download, Settings, Check, X, ChevronRight, Lock, File

---

# 5. Screen Wireframes

Window: 320px wide, white background, 12px rounded corners, subtle shadow

## 5.1 Home Screen

```
┌────────────────────────────────────┐
│                                    │
│  DocSend to PDF            ⚙️      │  ← Title + gear icon
│                                    │
│  ┌────────────────────────────┐    │
│  │ 🔗  Paste DocSend URL      │    │  ← Input field
│  └────────────────────────────┘    │
│                                    │
│  ✓ Clipboard detected              │  ← Status text
│                                    │
│  ┌────────────────────────────┐    │
│  │        Convert             │    │  ← Primary button
│  └────────────────────────────┘    │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │  ← Divider
│                                    │
│  Recent                   See all › │
│  ┌────────────────────────────┐    │
│  │ 📄 Company X Deck      2h  │    │  ← History items
│  │ 📄 Startup Y Pitch    1d   │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.2 Progress Screen

```
┌────────────────────────────────────┐
│                                    │
│  ←  Converting...                  │
│                                    │
│           ┌──────┐                 │
│           │  📄  │                 │  ← Animated icon
│           └──────┘                 │
│                                    │
│  ████████████░░░░░░░░░░  60%       │  ← Progress bar
│                                    │
│  Capturing page 6 of 10            │
│                                    │
│  ┌────────────────────────────┐    │
│  │         Cancel             │    │  ← Secondary button
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.3 Auth Screen (Email Only)

```
┌────────────────────────────────────┐
│                                    │
│  ←  Authentication                 │
│                                    │
│           ┌──────┐                 │
│           │  🔒  │                 │  ← Lock icon
│           └──────┘                 │
│                                    │
│  Email Required                    │
│  This document requires your       │
│  email to access.                  │
│                                    │
│  Email                             │
│  ┌────────────────────────────┐    │
│  │ investor@fund.com          │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │        Continue            │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.4 Auth Screen (Email + Passcode)

```
┌────────────────────────────────────┐
│                                    │
│  ←  Authentication                 │
│                                    │
│           ┌──────┐                 │
│           │  🔐  │                 │  ← Key icon
│           └──────┘                 │
│                                    │
│  Passcode Required                 │
│  This document is protected.       │
│                                    │
│  Email                             │
│  ┌────────────────────────────┐    │
│  │ investor@fund.com          │    │
│  └────────────────────────────┘    │
│                                    │
│  Passcode                          │
│  ┌────────────────────────────┐    │
│  │ ••••••••                👁 │    │  ← Show/hide toggle
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │        Continue            │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.5 Ask Summarize Screen

```
┌────────────────────────────────────┐
│                                    │
│  PDF Ready!                        │
│                                    │
│           ┌──────┐                 │
│           │  ✓   │                 │  ← Success checkmark
│           └──────┘                 │
│                                    │
│  Company X Deck.pdf                │
│  12 pages saved                    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ ✨ Generate AI Summary?    │    │
│  │                            │    │
│  │ Analyzes deck content and  │    │
│  │ finds similar funded cos   │    │
│  │                            │    │
│  │ ┌──────────┐ ┌──────────┐ │    │
│  │ │   Skip   │ │ Generate │ │    │
│  │ └──────────┘ └──────────┘ │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.6 Summarizing Screen

```
┌────────────────────────────────────┐
│                                    │
│  Generating Summary...             │
│                                    │
│           ┌──────┐                 │
│           │  ◠   │                 │  ← Spinner
│           └──────┘                 │
│                                    │
│  ┌────────────────────────────┐    │
│  │ ✓  Extracting text (OCR)   │    │  ← Complete
│  │ →  Analyzing with AI...    │    │  ← In progress
│  │ ○  Finding similar cos     │    │  ← Pending
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │     Skip & Continue        │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

## 5.7 Complete Screen

```
┌────────────────────────────────────┐
│                                    │
│  Conversion Complete!              │
│                                    │
│           ┌──────┐                 │
│           │  ✓   │                 │  ← Large checkmark
│           └──────┘                 │
│                                    │
│  Company X Deck.pdf                │
│  12 pages                          │
│                                    │
│  ┌────────────────────────────┐    │
│  │  📄  Open PDF              │    │  ← Primary action
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │  📁  Show in Finder        │    │  ← Secondary action
│  └────────────────────────────┘    │
│                                    │
│         Save As...                 │  ← Text link
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─    │
│                                    │
│  🔗  Convert Another               │
│                                    │
└────────────────────────────────────┘
```

## 5.8 Error Screen

```
┌────────────────────────────────────┐
│                                    │
│  ←  Conversion Failed              │
│                                    │
│           ┌──────┐                 │
│           │  ✗   │                 │  ← Error icon
│           └──────┘                 │
│                                    │
│  Could not access document         │
│  The page may have moved or        │
│  requires different credentials.   │
│                                    │
│  ┌────────────────────────────┐    │
│  │ ▼  Show Details            │    │  ← Expandable
│  │ ┌────────────────────────┐ │    │
│  │ │ TimeoutError: Page     │ │    │  ← Error details
│  │ │ load exceeded 30s      │ │    │
│  │ └────────────────────────┘ │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │         Retry              │    │
│  └────────────────────────────┘    │
│                                    │
│         Back to Home               │
│                                    │
└────────────────────────────────────┘
```

## 5.9 Settings Panel

```
┌────────────────────────────────────┐
│                                    │
│  Settings                          │
│                                    │
│  ┌────────────────────────────┐    │
│  │ 📁 Save Location       ›   │    │
│  │    ~/Downloads             │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ ✨ AI Summary              │    │
│  │    ┌─────────────────┐     │    │
│  │    │ Ask each time ▼ │     │    │  ← Dropdown
│  │    └─────────────────┘     │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ ⌨️ Keyboard Shortcut       │    │
│  │    ⌘⇧D                     │    │
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ 🚀 Start at Login     [○]  │    │  ← Toggle
│  └────────────────────────────┘    │
│                                    │
│  ┌────────────────────────────┐    │
│  │ 🔑 API Key            ›    │    │
│  └────────────────────────────┘    │
│                                    │
└────────────────────────────────────┘
```

---

# 6. State Machine

```
                              HOME
                                │
                          [Convert]
                                │
                                ▼
                            PROGRESS
                                │
           ┌────────────────────┼────────────────────┐
           │                    │                    │
           ▼                    ▼                    ▼
     AUTH_EMAIL           PDF_READY               ERROR
           │                    │                    │
           ▼                    │            ┌──────┴──────┐
     AUTH_PASSCODE?             │            │             │
       (if needed)              │         [Retry]    [Back]
           │                    │            │             │
           └───────┐            │            ▼             ▼
                   ▼            ▼         PROGRESS       HOME
              [Continue]   ┌────┴────┐
                   │       │         │
                   ▼       ▼         ▼
              PROGRESS   (mode)    (mode)
                         "ask"     "auto"/"off"
                           │         │
                           ▼         │
                    ASK_SUMMARIZE    │
                      │      │       │
                [Skip] │      │ [Summarize]
                      │      │       │
                      │      ▼       ▼
                      │  SUMMARIZING │
                      │      │       │
                      ▼      ▼       ▼
                      └──►COMPLETE◄──┘
                              │
                    [Convert Another]
                              │
                              ▼
                            HOME
```

## State Definitions

| State | Description |
|-------|-------------|
| HOME | URL input screen with history |
| PROGRESS | Conversion in progress with progress bar |
| AUTH_EMAIL | Email-only auth prompt (dock bounces) |
| AUTH_PASSCODE | Email + passcode prompt (dock bounces) |
| PDF_READY | Internal state (decides next screen) |
| ASK_SUMMARIZE | Prompt user to generate summary |
| SUMMARIZING | AI summary generation in progress |
| COMPLETE | Success screen with actions |
| ERROR | Failure screen with expandable details |

---

# 7. Phased Build Plan

## Phase 1: Core Infrastructure
**Goal**: Basic app shell with tray icon and window

### Tasks
- [ ] 1.1 Create `topdf_app/` directory structure
- [ ] 1.2 Implement `QSystemTrayIcon` menu bar icon
- [ ] 1.3 Create `MainWindow` with `QStackedWidget` for screens
- [ ] 1.4 Implement `HomeScreen` with URL input
- [ ] 1.5 Add clipboard auto-detection
- [ ] 1.6 Test tray icon show/hide window

### Exit Criteria
- [ ] Tray icon appears in menu bar
- [ ] Click opens/closes window
- [ ] URL input accepts DocSend URLs

---

## Phase 2: Conversion Pipeline
**Goal**: Working conversion with progress display

### Tasks
- [ ] 2.1 Create `ConversionWorker` (QThread)
- [ ] 2.2 Integrate existing `topdf.converter`
- [ ] 2.3 Implement `ProgressScreen` with progress bar
- [ ] 2.4 Create `CompleteScreen` with actions
- [ ] 2.5 Implement Open PDF / Show in Finder
- [ ] 2.6 Wire up tray icon animation during conversion
- [ ] 2.7 Test full conversion flow

### Exit Criteria
- [ ] Can convert open DocSend link
- [ ] Progress bar updates in real-time
- [ ] PDF opens correctly after completion

---

## Phase 3: Authentication Flow
**Goal**: Support protected documents

### Tasks
- [ ] 3.1 Create `InteractiveScraper` adapter
- [ ] 3.2 Implement `AuthEmailScreen`
- [ ] 3.3 Implement `AuthPasscodeScreen`
- [ ] 3.4 Add dock bounce for attention (`NSApp.requestUserAttention`)
- [ ] 3.5 Thread-safe auth wait/resume mechanism
- [ ] 3.6 Test email-protected documents
- [ ] 3.7 Test passcode-protected documents

### Exit Criteria
- [ ] Email auth flow works
- [ ] Passcode auth flow works
- [ ] Dock bounces when auth needed

---

## Phase 4: Settings & Shortcuts
**Goal**: Configurable preferences and global hotkey

### Tasks
- [ ] 4.1 Create inline `SettingsPanel`
- [ ] 4.2 Implement `QSettings` persistence
- [ ] 4.3 Add save location selector
- [ ] 4.4 Add summary mode dropdown
- [ ] 4.5 Implement global shortcut with pynput
- [ ] 4.6 Add "Start at Login" with `LSSharedFileList`
- [ ] 4.7 Test settings persistence

### Exit Criteria
- [ ] Settings persist between launches
- [ ] ⌘⇧D opens app from anywhere
- [ ] Start at login works

---

## Phase 5: AI Summary & History
**Goal**: Optional AI analysis and recent conversions

### Tasks
- [ ] 5.1 Create `AskSummarizeScreen`
- [ ] 5.2 Create `SummarizingScreen`
- [ ] 5.3 Integrate `topdf.summarizer` with summary modes
- [ ] 5.4 Implement history storage (JSON file)
- [ ] 5.5 Add history to tray menu
- [ ] 5.6 Implement macOS notifications (`NSUserNotification`)
- [ ] 5.7 API key management in settings

### Exit Criteria
- [ ] Summary generation works (when API key configured)
- [ ] History shows recent 10 conversions
- [ ] Notifications appear on completion

---

## Phase 6: Dependency Bundling
**Goal**: Bundle Tesseract and Chromium in app

### Tasks
- [ ] 6.1 Script to download and extract Tesseract binary
- [ ] 6.2 Script to download and extract Chromium
- [ ] 6.3 Modify app to use bundled binaries
- [ ] 6.4 Set environment variables at runtime
- [ ] 6.5 Test on clean macOS (no brew packages)
- [ ] 6.6 Verify OCR works with bundled Tesseract
- [ ] 6.7 Verify scraping works with bundled Chromium

### Exit Criteria
- [ ] App works on macOS with no Tesseract installed
- [ ] App works on macOS with no Chromium installed
- [ ] Total bundle size <300MB

---

## Phase 7: DMG Packaging
**Goal**: Distributable installer

### Tasks
- [ ] 7.1 Configure py2app build script
- [ ] 7.2 Create app icon (icns format)
- [ ] 7.3 Configure Info.plist with proper metadata
- [ ] 7.4 Create DMG with drag-to-Applications layout
- [ ] 7.5 Add background image to DMG
- [ ] 7.6 Test install on clean macOS 11
- [ ] 7.7 Test install on macOS 12, 13, 14

### Exit Criteria
- [ ] DMG mounts correctly
- [ ] Drag to Applications works
- [ ] App launches after install
- [ ] No Gatekeeper issues

---

## Phase 8: Polish & Testing
**Goal**: Production-ready release

### Tasks
- [ ] 8.1 Final UI polish and animations
- [ ] 8.2 Error handling edge cases
- [ ] 8.3 Memory leak testing
- [ ] 8.4 Performance optimization
- [ ] 8.5 Full E2E test suite
- [ ] 8.6 Documentation
- [ ] 8.7 Release checklist

### Exit Criteria
- [ ] All acceptance criteria met
- [ ] No critical bugs
- [ ] Documentation complete

---

# 8. Acceptance Criteria

## 8.1 Core Functionality

- [ ] Menu bar icon appears on launch
- [ ] Click icon opens compact window
- [ ] ⌘⇧D shortcut opens app with clipboard URL
- [ ] Auto-detects DocSend URLs in clipboard
- [ ] Progress bar shows during conversion
- [ ] Auth screen appears when needed (dock bounces)
- [ ] PDF opens correctly after completion
- [ ] Show in Finder works
- [ ] Save As works

## 8.2 Settings & History

- [ ] Settings persist between launches
- [ ] Summary mode (auto/ask/off) works
- [ ] Save location customizable
- [ ] History shows recent 10 conversions
- [ ] History items open PDFs

## 8.3 AI Summary

- [ ] Summary generation works with valid API key
- [ ] API key persists in config
- [ ] Summary skippable
- [ ] Summary failure doesn't break PDF

## 8.4 Distribution

- [ ] DMG installs cleanly on fresh macOS 11+
- [ ] App launches without errors
- [ ] Bundled Tesseract works
- [ ] Bundled Chromium works
- [ ] No post-install setup required

## 8.5 Performance

- [ ] 20-page deck converts in <60s
- [ ] Memory usage <600MB during conversion
- [ ] App startup <5s
- [ ] DMG size <300MB

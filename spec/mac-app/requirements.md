# Requirements Specification

## Document Info
- **Project**: DocSend to PDF Converter - Mac App (topdf_app)
- **Version**: 1.0
- **Last Updated**: 2025-01-07
- **Related**: CLI spec at `spec/requirements.md`

---

## 1. Functional Requirements

### FR-APP-1: Core Application

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-1.1 | Menu bar icon always visible when app running | Must Have | Icon appears in system menu bar |
| FR-APP-1.2 | Compact window (320px width) | Must Have | Window matches design spec |
| FR-APP-1.3 | Window opens below menu bar icon | Must Have | Position is contextually correct |
| FR-APP-1.4 | Global keyboard shortcut (⌘⇧D) | Should Have | Shortcut toggles window |
| FR-APP-1.5 | Clipboard auto-detection for DocSend URLs | Should Have | DocSend URLs trigger prompt |
| FR-APP-1.6 | Start at login option | Should Have | App can auto-launch on boot |
| FR-APP-1.7 | Click outside window to close | Should Have | Standard menu bar behavior |
| FR-APP-1.8 | System tray menu with quick actions | Should Have | History, Settings, Quit options |

### FR-APP-2: URL Input & Validation

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-2.1 | Accept DocSend URLs via text input field | Must Have | URL entered and validated |
| FR-APP-2.2 | Paste button for clipboard content | Should Have | Button pastes and starts conversion |
| FR-APP-2.3 | Validate URL before starting conversion | Must Have | Invalid URLs show error |
| FR-APP-2.4 | Support docsend.com/view/* URLs | Must Have | Standard URLs accepted |
| FR-APP-2.5 | Support custom domain DocSend links | Should Have | Custom domains recognized |

### FR-APP-3: Conversion Flow

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-3.1 | Show progress screen during conversion | Must Have | Progress percentage visible |
| FR-APP-3.2 | Display current page being captured | Should Have | "Page 5 of 20" shown |
| FR-APP-3.3 | Cancel button to abort conversion | Must Have | Cancellation works cleanly |
| FR-APP-3.4 | macOS notification on completion | Should Have | Native notification appears |
| FR-APP-3.5 | Handle multi-page documents (10-50+ pages) | Must Have | All pages captured |
| FR-APP-3.6 | Preserve visual fidelity of slides | Must Have | Screenshots match original |
| FR-APP-3.7 | Generate valid PDF output | Must Have | PDF opens in Preview.app |

### FR-APP-4: Authentication Handling

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-4.1 | Detect email-gated documents | Must Have | Auth screen triggered |
| FR-APP-4.2 | Show email input screen when required | Must Have | Email entry UI appears |
| FR-APP-4.3 | Detect passcode-gated documents | Must Have | Passcode screen triggered |
| FR-APP-4.4 | Show passcode input screen when required | Must Have | Passcode entry UI appears |
| FR-APP-4.5 | Dock icon bounce on auth required | Should Have | User attention captured |
| FR-APP-4.6 | Resume conversion after auth provided | Must Have | Seamless continuation |
| FR-APP-4.7 | Handle invalid credentials gracefully | Must Have | Error message shown |

### FR-APP-5: Completion & Output

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-5.1 | Show completion screen with PDF preview | Must Have | Success state visible |
| FR-APP-5.2 | "Open PDF" button to launch Preview | Must Have | PDF opens in default app |
| FR-APP-5.3 | "Show in Finder" button | Should Have | Finder reveals file |
| FR-APP-5.4 | Display filename and save location | Should Have | Output path shown |
| FR-APP-5.5 | Auto-name from page title or URL slug | Must Have | Sensible default name |
| FR-APP-5.6 | Default save to Downloads folder | Must Have | Predictable location |
| FR-APP-5.7 | Handle filename conflicts | Should Have | Appends (1), (2), etc. |

### FR-APP-6: AI Summarization (Optional)

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-6.1 | Prompt for AI summary after conversion | Should Have | Ask dialog appears |
| FR-APP-6.2 | Settings option: auto/ask/off | Should Have | User can set preference |
| FR-APP-6.3 | Show summarization progress screen | Should Have | Progress indicator visible |
| FR-APP-6.4 | Extract text via OCR for analysis | Should Have | Text extracted from pages |
| FR-APP-6.5 | Generate structured company analysis | Should Have | JSON with name, sector, etc. |
| FR-APP-6.6 | Find recently funded peer companies | Should Have | Perplexity search works |
| FR-APP-6.7 | Save markdown summary alongside PDF | Should Have | .md file created |
| FR-APP-6.8 | Summary failure must not break PDF | Must Have | PDF saved regardless |

### FR-APP-7: Settings Panel

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-7.1 | Save location customization | Should Have | Custom folder selectable |
| FR-APP-7.2 | Summary mode toggle (auto/ask/off) | Should Have | Preference persists |
| FR-APP-7.3 | Start at login toggle | Should Have | Login item created/removed |
| FR-APP-7.4 | Global shortcut customization | Nice to Have | User can change hotkey |
| FR-APP-7.5 | Perplexity API key management | Should Have | Key entry and storage |
| FR-APP-7.6 | Reset to defaults option | Should Have | Clears all settings |

### FR-APP-8: History & Quick Access

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-8.1 | Store last 10 conversions | Should Have | History persists |
| FR-APP-8.2 | Show history in tray menu | Should Have | Quick access list |
| FR-APP-8.3 | Click history item to reveal in Finder | Should Have | File location opens |
| FR-APP-8.4 | Clear history option | Should Have | History can be reset |

### FR-APP-9: Error Handling

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-APP-9.1 | Show error screen with clear message | Must Have | Error is actionable |
| FR-APP-9.2 | Retry button for transient failures | Should Have | User can retry |
| FR-APP-9.3 | Start Over button to return home | Must Have | Easy recovery path |
| FR-APP-9.4 | Handle network timeouts | Should Have | Timeout message shown |
| FR-APP-9.5 | Handle DocSend unavailability | Should Have | Clear error message |

---

## 2. Non-Functional Requirements

### NFR-APP-1: Platform & Compatibility

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-1.1 | Support macOS 11 Big Sur and later | Must Have | App runs on macOS 11+ |
| NFR-APP-1.2 | Support both Intel and Apple Silicon | Must Have | Universal binary or separate builds |
| NFR-APP-1.3 | No external runtime dependencies | Must Have | Works after DMG install |
| NFR-APP-1.4 | Code signing for Gatekeeper | Should Have | No security warnings |
| NFR-APP-1.5 | Notarization for macOS 10.15+ | Should Have | Apple notarized |

### NFR-APP-2: Performance

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-2.1 | Convert 20-page deck in under 60 seconds | Should Have | Timing meets target |
| NFR-APP-2.2 | App launch to ready state under 5 seconds | Should Have | Fast startup |
| NFR-APP-2.3 | Memory usage under 600MB during conversion | Should Have | Memory monitored |
| NFR-APP-2.4 | Idle memory under 100MB | Should Have | Low background footprint |
| NFR-APP-2.5 | UI remains responsive during conversion | Must Have | No freezing |

### NFR-APP-3: Privacy & Security

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-3.1 | Core PDF conversion happens locally | Must Have | No external API for PDF |
| NFR-APP-3.2 | Document data only sent if user opts in | Must Have | Explicit consent |
| NFR-APP-3.3 | API keys stored in macOS Keychain | Should Have | Secure storage |
| NFR-APP-3.4 | No logging of document content | Must Have | No sensitive logs |
| NFR-APP-3.5 | DocSend credentials not stored | Should Have | Entered each time |

### NFR-APP-4: Installation & Distribution

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-4.1 | DMG installer with drag-to-Applications | Must Have | Standard macOS install |
| NFR-APP-4.2 | No post-install setup required | Must Have | Works immediately |
| NFR-APP-4.3 | Tesseract OCR bundled in app | Must Have | OCR works without brew |
| NFR-APP-4.4 | Chromium bundled in app | Must Have | Browser works without setup |
| NFR-APP-4.5 | DMG size under 300MB | Should Have | Reasonable download |
| NFR-APP-4.6 | Clean uninstall by deleting .app | Should Have | No system pollution |

### NFR-APP-5: User Experience

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-5.1 | Native macOS look and feel | Should Have | Follows Apple HIG |
| NFR-APP-5.2 | Consistent with Canva-inspired design | Should Have | Matches spec colors |
| NFR-APP-5.3 | Smooth animations and transitions | Nice to Have | Polished feel |
| NFR-APP-5.4 | Accessible to screen readers | Nice to Have | VoiceOver compatible |

### NFR-APP-6: Reliability

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| NFR-APP-6.1 | Graceful handling of network issues | Should Have | No crashes |
| NFR-APP-6.2 | Retry failed page captures (max 3) | Should Have | Transient failures handled |
| NFR-APP-6.3 | Browser cleanup on crash | Should Have | No zombie processes |
| NFR-APP-6.4 | State recovery after app restart | Nice to Have | Resume incomplete work |

---

## 3. Constraints

### Technical Constraints
- **Platform**: macOS only (11 Big Sur and later)
- **Python Version**: 3.9 or higher (bundled in app)
- **GUI Framework**: PySide6 (Qt for Python)
- **Packaging Tool**: py2app for .app bundle creation
- **Architecture**: Must support both Intel (x86_64) and Apple Silicon (arm64)

### Bundled Dependencies (Must Include)
- **Tesseract OCR**: Binary + eng.traineddata (~30MB)
- **Chromium**: Full browser via Playwright (~200MB)
- **Python Runtime**: Embedded Python interpreter

### Size Constraints
- **App Bundle**: Target < 250MB
- **DMG Installer**: Target < 300MB (compressed)

### Operational Constraints
- **Network**: Requires internet access for DocSend
- **Storage**: ~50-100MB per converted PDF
- **Concurrent Use**: Single conversion at a time

---

## 4. Assumptions

1. User has macOS 11 Big Sur or later installed
2. User has valid email/passcode when required by DocSend
3. DocSend's web interface remains relatively stable
4. User has permissions to download shared documents
5. Internet connection is available during conversion
6. ~500MB disk space available for app + conversions

---

## 5. Dependencies

### Python Packages (Bundled)

| Dependency | Version | Purpose |
|------------|---------|---------|
| PySide6 | >=6.5.0 | Qt GUI framework |
| playwright | >=1.40.0 | Browser automation |
| Pillow | >=10.0.0 | Image processing |
| img2pdf | >=0.5.0 | PDF creation |
| pytesseract | >=0.3.10 | OCR interface |
| pynput | >=1.7.0 | Global keyboard shortcuts |
| pyobjc-framework-Cocoa | >=9.0 | macOS integration |

### Bundled Binaries

| Dependency | Size | Purpose |
|------------|------|---------|
| Tesseract | ~30MB | OCR engine binary |
| Chromium | ~200MB | Headless browser |
| Python 3.11 | ~50MB | Runtime interpreter |

### Optional Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| openai | >=1.0.0 | Perplexity API (summarization) |

---

## 6. User Stories

### Primary User Journey

```
As an investor reviewing pitch decks,
I want to convert DocSend links to PDF with one click,
So that I can read decks offline and archive them locally.
```

### Key User Stories

| ID | User Story | Acceptance Criteria |
|----|------------|---------------------|
| US-1 | As a user, I want to paste a DocSend URL and get a PDF | URL → PDF in < 60s |
| US-2 | As a user, I want the app to handle authentication for me | Auth flow is seamless |
| US-3 | As a user, I want a global shortcut to start conversion | ⌘⇧D opens app |
| US-4 | As a user, I want clipboard detection for DocSend URLs | Auto-prompt appears |
| US-5 | As a user, I want to see progress during conversion | Percentage shown |
| US-6 | As a user, I want to be notified when conversion completes | macOS notification |
| US-7 | As a user, I want to access recent conversions quickly | History in tray menu |
| US-8 | As a user, I want optional AI summary of pitch decks | Ask/auto/off modes |
| US-9 | As a user, I want zero setup after installation | DMG → drag → works |

---

## 7. Acceptance Criteria Summary

### Must Have (MVP)
- [ ] Menu bar app launches and shows icon
- [ ] Window opens below tray icon
- [ ] URL input accepts valid DocSend URLs
- [ ] Conversion captures all pages
- [ ] Progress shown during conversion
- [ ] Auth screens appear when needed
- [ ] PDF saved to Downloads folder
- [ ] Completion screen with Open PDF button
- [ ] Error handling with clear messages
- [ ] App works after DMG install (no setup)

### Should Have (v1.0)
- [ ] Global shortcut (⌘⇧D)
- [ ] Clipboard URL detection
- [ ] macOS notifications
- [ ] History in tray menu
- [ ] Settings panel
- [ ] AI summarization option
- [ ] Start at login option
- [ ] Custom save location

### Nice to Have (Future)
- [ ] Custom shortcut configuration
- [ ] Batch conversion
- [ ] Dark mode support
- [ ] Automatic updates

---

## 8. Glossary

| Term | Definition |
|------|------------|
| Menu Bar App | macOS app that lives in the top menu bar |
| Tray Icon | The icon in the macOS menu bar |
| DMG | Disk Image, standard macOS installer format |
| py2app | Python tool for creating macOS .app bundles |
| PySide6 | Official Qt bindings for Python |
| QThread | Qt class for background thread execution |
| Gatekeeper | macOS security feature for app verification |
| Notarization | Apple's app verification service |
| Universal Binary | App that runs on both Intel and Apple Silicon |
| Dock Bounce | macOS attention mechanism for background apps |

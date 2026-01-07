# Changelog - Main Branch

## Iteration 1: Random Naming & Completion Flow Redesign

**Objective:** Improve user experience with random PDF names, editable naming flow, and better AI summary prompts

**Files Modified:**
- `topdf_app/core/names.py` (NEW)
- `topdf_app/ui/screens/complete.py`
- `topdf_app/ui/screens/home.py`
- `topdf_app/core/worker.py`
- `topdf_app/app.py`
- `tests/test_app_ui.py`

### Changes Made:
1. **Random Cartoon Names System**
   - Created `names.py` with pool of ~990 cartoon character names
   - NameManager class tracks used names with JSON persistence
   - Ensures unique names until pool exhausted, then resets

2. **Two-Phase Completion Flow**
   - Completion screen now shows editable name input with suggested name
   - User explicitly saves with "Save PDF" button
   - After save, shows "Saved!" state with Open/Show in Finder actions
   - Added `file_saved` signal for history tracking

3. **AI Summary Card**
   - Replaced subtle hint with prominent card design
   - Shows sparkle icon, title, description
   - "Configure" button navigates to settings

4. **Settings Icon Styling**
   - Updated to Canva-style with rounded hover background
   - Added pressed state and tooltip

5. **Worker Updates**
   - Now generates random names instead of extracting from document
   - Passes suggested name to completion screen

### Test Results:
- All 33 UI tests pass
- Name manager unit tests pass
- Manual testing required for full flow verification

---

## Iteration 2: UI Polish - Completion & Settings Screens

**Objective:** Fix completion screen flow issues and redesign settings screen with clean Canva-style UI

**Files Modified:**
- `topdf_app/ui/screens/complete.py`
- `topdf_app/ui/settings_panel.py`

### Changes Made:

1. **Completion Screen Flow Fixes**
   - Naming phase: Shows "Save PDF" and "Discard" buttons only
   - "Convert Another" link now hidden until user saves
   - AI summary card moved to saved phase (after user clicks Save)
   - AI summary card redesigned with vertical layout (icon + text on top, full-width button below)
   - Added `discard_clicked` signal for cleanup
   - Discard deletes temp file before returning to home

2. **Settings Screen Redesign (Canva-style)**
   - Removed emoji icons from section headers
   - Clean section headers with uppercase labels (GENERAL, AI SUMMARIES, KEYBOARD SHORTCUT)
   - Each setting is a clean row with title, description, and control
   - Proper input fields with border, padding, and focus states
   - Custom ToggleSwitch widget for boolean settings
   - "Get key" link to Perplexity API page
   - Removed heavy bordered cards, now uses subtle grouped rows
   - Consistent spacing and typography

3. **UI Improvements**
   - Better visual hierarchy with section headers
   - Cleaner input field styling (no underlines)
   - Proper toggle switch instead of text-based toggle
   - More professional, cohesive look

### Test Results:
- All 33 UI tests pass

---

## Iteration 3: API Key Detection & Tesseract OCR Fixes

**Objective:** Fix API key detection bug and make Tesseract OCR work reliably across different environments

**Files Modified:**
- `topdf_app/app.py`
- `topdf_app/core/worker.py`
- `topdf/summarizer.py`

### Changes Made:

1. **API Key Detection Bug Fix**
   - Fixed import of non-existent `ConfigManager` class
   - Changed to use plain functions: `get_api_key`, `save_api_key`, `clear_api_key`
   - Updated 4 locations in `app.py` and `worker.py`

2. **Tesseract OCR Reliability**
   - Added `_verify_tesseract()` function that tests if binary actually works
   - Added `_find_working_tesseract()` with priority-based fallback chain
   - Priority order: Homebrew (most reliable) > system PATH > bundled
   - Bundled tesseract skipped if it has broken library dependencies
   - Simplified `extract_text()` to use the new helper functions

3. **Why These Changes**
   - Bundled tesseract at `bundle/tesseract/bin/tesseract` has broken dylib dependencies (error -9)
   - System Homebrew at `/opt/homebrew/bin/tesseract` works reliably
   - New logic verifies each candidate with `tesseract --version` before using it

### Test Results:
- All 33 UI tests pass
- Homebrew tesseract verified working

---

## Iteration 4: Remove AI Summarization Feature

**Objective:** Remove all AI summarization functionality from the Mac app to focus purely on DocSend-to-PDF conversion

**Files Deleted:**
- `topdf_app/ui/screens/ask_summarize.py`
- `topdf_app/ui/screens/summarizing.py`
- `topdf/summarizer.py`
- `topdf/config.py`
- `tests/test_summarizer.py`
- `tests/test_config.py`
- `bundle/tesseract/` (entire directory)

**Files Modified:**
- `topdf_app/app.py` - Removed SummaryWorker, summary signals, API key handling
- `topdf_app/core/worker.py` - Removed SummaryWorker class and SummaryStep enum
- `topdf_app/core/state.py` - Removed PDF_READY, ASK_SUMMARIZE, SUMMARIZING states
- `topdf_app/core/settings.py` - Removed summary_mode setting
- `topdf_app/core/bundle.py` - Removed all tesseract-related code
- `topdf_app/ui/main_window.py` - Removed summary screen references and signals
- `topdf_app/ui/screens/complete.py` - Removed AI summary card and configure button
- `topdf_app/ui/settings_panel.py` - Removed AI Summaries section (summary mode, API key)
- `topdf/cli.py` - Removed --check-key, --reset-key flags and summary prompts
- `topdf/exceptions.py` - Removed SummaryError and OCRError classes
- `pyproject.toml` - Removed pytesseract dependency and summarize optional deps
- `tests/test_cli.py` - Fixed version check to use __version__

### Changes Made:

1. **Mac App UI Simplification**
   - Complete screen now just shows naming + save flow
   - Settings panel has only: Save location, Start at login, Keyboard shortcut
   - Removed 2 entire screen classes (AskSummarizeScreen, SummarizingScreen)
   - Removed all summary-related signals and handlers

2. **State Machine Simplification**
   - States reduced from 9 to 6 (HOME, PROGRESS, AUTH_EMAIL, AUTH_PASSCODE, COMPLETE, ERROR)
   - Removed intermediate PDF_READY state
   - Simplified state transitions

3. **Bundling Cleanup**
   - Removed all tesseract bundling logic
   - Bundle now only contains Chromium for Playwright
   - Removed ~100 lines from bundle.py

4. **CLI Cleanup**
   - Removed API key management (--check-key, --reset-key)
   - Removed summary generation prompt after PDF conversion
   - Simpler, focused on PDF conversion only

5. **Dependencies**
   - Removed pytesseract from core dependencies
   - Removed openai from optional summarize dependencies
   - Removed the entire "summarize" optional dependency group

### Test Results:
- 120 tests pass, 1 skipped (integration test)
- All 33 UI tests pass

### Lines of Code Removed:
- ~1,500 lines of summarization-related code removed
- App is now leaner and focused on core functionality

---

## Iteration 5: Code Review Cleanup

**Objective:** Remove unused imports and dead code identified during code review

**Files Modified:**
- `topdf_app/ui/screens/home.py`
- `topdf_app/core/shortcuts.py`
- `topdf_app/core/worker.py`

### Changes Made:

1. **home.py Cleanup**
   - Merged duplicate typing imports (`from typing import Optional` and `from typing import List`)
   - Removed unused `QClipboard` import (clipboard accessed via `QApplication.clipboard()`)
   - Removed unused `see_all_btn` widget (placeholder with no click handler)

2. **shortcuts.py Cleanup**
   - Removed unused `Callable` import from typing

3. **worker.py Cleanup**
   - Removed duplicate `from pathlib import Path` inside `run()` method (already imported at module level)

### Test Results:
- All 120 tests pass, 1 skipped (integration test)

---

## Iteration 6: Documentation Update for GitHub Release

**Objective:** Update all documentation files to remove AI summarization references and prepare for GitHub release

**Files Modified:**
- `README.md`
- `RELEASE.md`
- `spec/SPEC.md`
- `spec/architecture.md`
- `spec/requirements.md`
- `spec/test-plan.md`

### Changes Made:

1. **README.md Complete Rewrite**
   - Added Mac app documentation (installation, usage, features, settings)
   - Updated CLI documentation (removed --check-key, --reset-key)
   - Removed AI summarization, Tesseract, Perplexity references
   - Updated architecture diagram
   - Updated project structure
   - Updated tech stack (removed pytesseract, openai)

2. **RELEASE.md Simplified**
   - Removed Tesseract bundling steps
   - Removed AI summary testing checklist
   - Updated build outputs (only Chromium bundled now)
   - Simplified troubleshooting section

3. **spec/SPEC.md Rewrite**
   - Removed Phase 7 (AI Summarization)
   - Reduced to 6 phases
   - Removed FR-5 and FR-6 (summarization and API key requirements)
   - Updated architecture diagram
   - Simplified test cases

4. **spec/architecture.md Rewrite**
   - Removed Config and Summarizer modules
   - Removed summarization data flow
   - Removed Perplexity configuration section
   - Added Mac app architecture section
   - Updated exception hierarchy (removed SummaryError, OCRError)

5. **spec/requirements.md Simplified**
   - Removed FR-5 (AI Summarization) and FR-6 (API Key Management)
   - Removed Tesseract from system dependencies
   - Removed pytesseract and openai from dependencies
   - Updated glossary (removed LLM, summarization terms)

6. **spec/test-plan.md Simplified**
   - Removed config.py and summarizer.py test sections
   - Removed summarization integration tests
   - Reduced E2E tests from 18 to 8
   - Removed Tesseract installation from CI workflow

### Test Results:
- Documentation updates only, no code changes

---

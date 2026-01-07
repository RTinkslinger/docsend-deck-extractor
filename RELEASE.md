# Release Checklist

This document outlines the steps to build and release a new version of DocSend to PDF.

## Pre-Release Checks

### 1. Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check topdf/ topdf_app/`
- [ ] Type checking passes: `mypy topdf/`
- [ ] Code formatted: `black topdf/ topdf_app/ tests/`

### 2. Version Update
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `scripts/build_app.py` (VERSION constant)
- [ ] Update version in `DocSendToPDF.spec` (info_plist)

### 3. Test on Clean Environment
- [ ] Test CLI installation: `pip install -e . && topdf --help`
- [ ] Test Mac app launch: `python3 -m topdf_app.main`
- [ ] Test conversion with a real DocSend URL
- [ ] Test auth flow (email-gated document)
- [ ] Test error handling (invalid URL, network issues)

## Build Process

### 1. Bundle Dependencies
```bash
# Run from project root
python3 scripts/bundle_deps.py
```

This downloads:
- Chromium browser (via Playwright)

### 2. Create App Icon
```bash
python3 scripts/create_icon.py
```

Generates `resources/app_icon.icns`

### 3. Build Application
```bash
# Full build including DMG
python3 scripts/build_app.py

# Skip DMG creation (faster for testing)
python3 scripts/build_app.py --skip-dmg

# Clean build
python3 scripts/build_app.py --clean
```

Build outputs:
- `dist/DocSend to PDF.app` - Application bundle
- `dist/DocSend-to-PDF-Installer-1.0.0.dmg` - Installer image

### 4. Test Built App
- [ ] Launch app from `dist/DocSend to PDF.app`
- [ ] Verify menu bar icon appears
- [ ] Test URL input and conversion
- [ ] Verify PDF opens correctly
- [ ] Test global shortcut (Cmd+Shift+D)
- [ ] Test settings panel
- [ ] Test with auth-protected document

## Post-Build Verification

### 1. App Bundle Checks
```bash
# Check app structure
ls -la "dist/DocSend to PDF.app/Contents/"

# Verify Chromium is bundled
ls "dist/DocSend to PDF.app/Contents/Resources/bundle/chromium/"

# Check code signature (if signed)
codesign -dv "dist/DocSend to PDF.app"
```

### 2. DMG Verification
- [ ] Mount DMG and verify contents
- [ ] Drag to Applications and launch
- [ ] Test on fresh macOS account (if possible)

## Release

### 1. Create GitHub Release
- [ ] Create new release tag (e.g., `v1.0.0`)
- [ ] Write release notes
- [ ] Upload DMG as release asset

### 2. Release Notes Template
```markdown
## DocSend to PDF v1.0.0

### Features
- Menu bar app for quick access
- Global shortcut (Cmd+Shift+D)
- Clipboard URL detection
- Interactive authentication
- Random cartoon character naming
- Conversion history

### Requirements
- macOS 11.0 or later

### Installation
1. Download DocSend-to-PDF-Installer-1.0.0.dmg
2. Open DMG and drag app to Applications
3. Launch from Applications or menu bar
```

## Troubleshooting

### Build Fails
- Check PyInstaller is installed: `pip install pyinstaller`
- Ensure bundle directory exists: `ls bundle/chromium`
- Try clean build: `python3 scripts/build_app.py --clean`

### App Won't Launch
- Check Console.app for crash logs
- Verify Python dependencies in app bundle
- Test with verbose: `./dist/DocSend\ to\ PDF.app/Contents/MacOS/DocSend\ to\ PDF`

### Chromium Issues
- Re-run bundle script: `python3 scripts/bundle_deps.py`
- Check PLAYWRIGHT_BROWSERS_PATH is set correctly
- Verify chromium executable permissions

## Quick Reference

```bash
# Full release build
python3 scripts/build_app.py --clean

# Test only (no DMG)
python3 scripts/build_app.py --skip-dmg

# Run tests
pytest tests/ -v

# Run app in development
python3 -m topdf_app.main
```

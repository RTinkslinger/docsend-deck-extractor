"""
py2app build script for DocSend to PDF Mac app.

Usage:
    python setup_app.py py2app

This creates a standalone .app bundle in the dist/ directory.
"""

import sys
from pathlib import Path
from setuptools import setup

APP = ['topdf_app/main.py']
APP_NAME = 'DocSend to PDF'

# Check for icon
icon_file = Path('resources/app_icon.icns')
if not icon_file.exists():
    print("Warning: App icon not found. Run: python scripts/create_icon.py")
    icon_file = None

OPTIONS = {
    'argv_emulation': False,
    'iconfile': str(icon_file) if icon_file else None,
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': 'com.topdf.docsend-to-pdf',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '11.0',
        'LSUIElement': True,  # Menu bar app (no dock icon)
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'CFBundleDocumentTypes': [],
        'NSHumanReadableCopyright': 'Copyright © 2024 topdf',
    },
    'packages': [
        'topdf',
        'topdf_app',
        'PySide6',
        'playwright',
        'PIL',
        'img2pdf',
        'click',
        'rich',
    ],
    'includes': [
        'pytesseract',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._darwin',
        'pynput.mouse',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'IPython',
        'jupyter',
    ],
    'frameworks': [],
    # Note: bundle/ will be copied separately after build
}

# Only add pyobjc if on macOS
if sys.platform == 'darwin':
    OPTIONS['includes'].extend([
        'AppKit',
        'Foundation',
        'objc',
    ])

setup(
    name=APP_NAME,
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

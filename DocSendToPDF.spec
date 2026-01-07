# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DocSend to PDF Mac app.

Build with:
    pyinstaller DocSendToPDF.spec
"""

import sys
from pathlib import Path

# Project paths
project_dir = Path(SPECPATH)
bundle_dir = project_dir / 'bundle'

# Collect data files
datas = []

# Add bundle directory if it exists (excluding Chromium - copied separately)
if bundle_dir.exists():
    # Add tessdata only (Chromium will be copied manually after build)
    tessdata_dir = bundle_dir / 'tesseract' / 'share' / 'tessdata'
    if tessdata_dir.exists():
        datas.append((str(tessdata_dir), 'bundle/tesseract/share/tessdata'))

# Note: Chromium bundle must be copied manually after PyInstaller build
# because PyInstaller cannot properly handle the complex .app structure

# Hidden imports for packages that PyInstaller doesn't detect
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'pynput',
    'pynput.keyboard',
    'pynput.keyboard._darwin',
    'pynput.mouse',
    'pynput.mouse._darwin',
    'pytesseract',
    'PIL',
    'PIL.Image',
    'img2pdf',
    'click',
    'rich',
    'rich.console',
    'rich.progress',
    'playwright',
    'playwright.sync_api',
    'AppKit',
    'Foundation',
    'objc',
]

a = Analysis(
    ['topdf_app/main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'IPython',
        'jupyter',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DocSend to PDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app_icon.icns' if Path('resources/app_icon.icns').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DocSend to PDF',
)

app = BUNDLE(
    coll,
    name='DocSend to PDF.app',
    icon='resources/app_icon.icns' if Path('resources/app_icon.icns').exists() else None,
    bundle_identifier='com.topdf.docsend-to-pdf',
    info_plist={
        'CFBundleName': 'DocSend to PDF',
        'CFBundleDisplayName': 'DocSend to PDF',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '11.0',
        'LSUIElement': True,  # Menu bar app (no dock icon)
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSHumanReadableCopyright': 'Copyright 2024 topdf',
    },
)

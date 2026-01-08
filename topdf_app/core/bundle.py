"""Bundled dependencies configuration.

Sets up paths for bundled Chromium when running as a packaged application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def get_chromium_dir() -> Optional[Path]:
    """Get the directory containing bundled Chromium.

    Returns:
        Path to chromium directory, or None if not found
    """
    # When running as a packaged app (.app bundle)
    if getattr(sys, 'frozen', False):
        # PyInstaller puts resources in Contents/Resources
        # Chromium is copied directly to Resources/chromium (not Resources/bundle/chromium)
        app_dir = Path(sys.executable).parent.parent
        chromium_dir = app_dir / "Resources" / "chromium"
        if chromium_dir.exists():
            return chromium_dir

    # When running from source
    source_dir = Path(__file__).parent.parent.parent
    chromium_dir = source_dir / "bundle" / "chromium"
    if chromium_dir.exists():
        return chromium_dir

    return None


def get_chromium_path() -> Optional[Path]:
    """Get the path to the bundled Chromium browser executable.

    Returns:
        Path to Chromium executable, or None if not bundled
    """
    chromium_dir = get_chromium_dir()
    if not chromium_dir:
        return None

    # Find the chromium version directory (e.g., chromium-1200)
    for version_dir in chromium_dir.glob("chromium-*"):
        # Playwright now uses "Google Chrome for Testing"
        # Try arm64 paths first (Apple Silicon), then Intel
        for arch_dir in ["chrome-mac-arm64", "chrome-mac"]:
            for app_name in ["Google Chrome for Testing.app", "Chromium.app"]:
                chrome_path = version_dir / arch_dir / app_name / "Contents" / "MacOS"
                if chrome_path.exists():
                    # Find the executable
                    for exe_name in ["Google Chrome for Testing", "Chromium"]:
                        exe_path = chrome_path / exe_name
                        if exe_path.exists():
                            return exe_path
    return None


def setup_bundled_environment() -> dict:
    """Configure environment variables for bundled dependencies.

    This should be called early in application startup to ensure
    bundled binaries are used instead of system ones.

    Returns:
        Dict of environment variables that were set
    """
    env_vars = {}

    # Chromium/Playwright configuration
    chromium_dir = get_chromium_dir()
    if chromium_dir and chromium_dir.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(chromium_dir)
        env_vars["PLAYWRIGHT_BROWSERS_PATH"] = os.environ["PLAYWRIGHT_BROWSERS_PATH"]

    return env_vars


def is_bundled() -> bool:
    """Check if running with bundled Chromium.

    Returns:
        True if chromium directory exists
    """
    return get_chromium_dir() is not None


def get_bundle_info() -> dict:
    """Get information about the bundle.

    Returns:
        Dict with bundle status information
    """
    chromium_dir = get_chromium_dir()
    chromium_path = get_chromium_path()

    info = {
        "bundled": chromium_dir is not None,
        "chromium_dir": str(chromium_dir) if chromium_dir else None,
        "chromium_path": str(chromium_path) if chromium_path else None,
        "frozen": getattr(sys, 'frozen', False),
    }

    return info

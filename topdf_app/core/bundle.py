"""Bundled dependencies configuration.

Sets up paths for bundled Chromium when running as a packaged application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def get_bundle_dir() -> Optional[Path]:
    """Get the bundle directory for packaged dependencies.

    Returns:
        Path to bundle directory, or None if not found
    """
    # When running as a packaged app (.app bundle)
    if getattr(sys, 'frozen', False):
        # py2app puts resources in Contents/Resources
        app_dir = Path(sys.executable).parent.parent
        bundle_dir = app_dir / "Resources" / "bundle"
        if bundle_dir.exists():
            return bundle_dir

    # When running from source
    source_dir = Path(__file__).parent.parent.parent
    bundle_dir = source_dir / "bundle"
    if bundle_dir.exists():
        return bundle_dir

    return None


def get_chromium_path() -> Optional[Path]:
    """Get the path to the bundled Chromium browser.

    Returns:
        Path to Chromium executable, or None if not bundled
    """
    bundle_dir = get_bundle_dir()
    if bundle_dir:
        chromium_dir = bundle_dir / "chromium"
        if chromium_dir.exists():
            # Find the chromium version directory
            for version_dir in chromium_dir.glob("chromium-*"):
                # Playwright now uses "Google Chrome for Testing"
                # Try arm64 paths first
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
    bundle_dir = get_bundle_dir()

    if not bundle_dir:
        return env_vars

    # Chromium/Playwright configuration
    chromium_dir = bundle_dir / "chromium"
    if chromium_dir.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(chromium_dir)
        env_vars["PLAYWRIGHT_BROWSERS_PATH"] = os.environ["PLAYWRIGHT_BROWSERS_PATH"]

    return env_vars


def is_bundled() -> bool:
    """Check if running with bundled dependencies.

    Returns:
        True if bundle directory exists
    """
    return get_bundle_dir() is not None


def get_bundle_info() -> dict:
    """Get information about the bundle.

    Returns:
        Dict with bundle status information
    """
    bundle_dir = get_bundle_dir()

    info = {
        "bundled": bundle_dir is not None,
        "bundle_path": str(bundle_dir) if bundle_dir else None,
        "chromium_bundled": get_chromium_path() is not None,
        "chromium_path": str(get_chromium_path()) if get_chromium_path() else None,
    }

    return info

#!/usr/bin/env python3
"""Build the DocSend to PDF Mac app and create DMG installer.

Usage:
    python scripts/build_app.py [--skip-bundle] [--skip-dmg] [--clean]

Steps:
1. Create app icon if missing
2. Bundle dependencies (Tesseract, Chromium) if missing
3. Build .app with PyInstaller
4. Copy Chromium to app bundle
5. Create DMG installer
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Paths
PROJECT_DIR = Path(__file__).parent.parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
RESOURCES_DIR = PROJECT_DIR / "resources"
BUNDLE_DIR = PROJECT_DIR / "bundle"

APP_NAME = "DocSend to PDF"
DMG_NAME = "DocSend-to-PDF-Installer"
VERSION = "1.0.0"


def run_command(cmd: list, cwd: Path = None, env: dict = None, show_output: bool = False) -> bool:
    """Run a command and return success status."""
    print(f"  Running: {' '.join(str(c) for c in cmd)}")
    try:
        if show_output:
            result = subprocess.run(
                cmd,
                cwd=cwd or PROJECT_DIR,
                env=env or os.environ,
            )
        else:
            result = subprocess.run(
                cmd,
                cwd=cwd or PROJECT_DIR,
                env=env or os.environ,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"  Error: {result.stderr[:500] if result.stderr else 'unknown'}")
        return result.returncode == 0
    except Exception as e:
        print(f"  Exception: {e}")
        return False


def ensure_icon():
    """Ensure app icon exists."""
    icon_path = RESOURCES_DIR / "app_icon.icns"
    if icon_path.exists():
        print("  Icon already exists")
        return True

    print("  Creating app icon...")
    return run_command([sys.executable, str(PROJECT_DIR / "scripts" / "create_icon.py")])


def ensure_bundle():
    """Ensure dependencies are bundled."""
    chromium_dir = BUNDLE_DIR / "chromium"
    if chromium_dir.exists() and list(chromium_dir.glob("chromium-*")):
        print("  Bundle already exists")
        return True

    print("  Bundling dependencies...")
    return run_command([sys.executable, str(PROJECT_DIR / "scripts" / "bundle_deps.py")])


def clean_build():
    """Clean previous build artifacts."""
    print("  Cleaning previous builds...")
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    return True


def build_app():
    """Build the .app bundle with PyInstaller."""
    print("  Building app with PyInstaller...")

    # Check PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("  Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Run PyInstaller
    spec_file = PROJECT_DIR / "DocSendToPDF.spec"
    if not spec_file.exists():
        print(f"  Spec file not found: {spec_file}")
        return False

    return run_command(["pyinstaller", str(spec_file)], show_output=True)


def copy_chromium_to_app():
    """Copy Chromium bundle into the app's Resources."""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if not app_path.exists():
        print(f"  App not found at {app_path}")
        return False

    resources_path = app_path / "Contents" / "Resources"
    bundle_dest = resources_path / "bundle"
    chromium_dest = bundle_dest / "chromium"

    # Remove existing chromium if present
    if chromium_dest.exists():
        shutil.rmtree(chromium_dest)

    print("  Copying Chromium to app bundle...")

    # Copy chromium
    chromium_src = BUNDLE_DIR / "chromium"
    if chromium_src.exists():
        bundle_dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(chromium_src, chromium_dest, symlinks=True)
        print(f"  Copied Chromium ({sum(1 for _ in chromium_dest.rglob('*'))} files)")
    else:
        print("  Warning: Chromium bundle not found")

    return True


def create_dmg():
    """Create DMG installer."""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / f"{DMG_NAME}-{VERSION}.dmg"

    if not app_path.exists():
        print(f"  App not found at {app_path}")
        return False

    print("  Creating DMG...")

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    # Create DMG using hdiutil
    temp_dmg = DIST_DIR / "temp.dmg"
    sparse_path = DIST_DIR / "temp.sparseimage"

    # Clean up any previous temp files
    for f in [temp_dmg, sparse_path]:
        if f.exists():
            f.unlink()

    # Create temporary sparse image
    cmd = [
        "hdiutil", "create",
        "-size", "1g",
        "-fs", "HFS+",
        "-volname", APP_NAME,
        "-type", "SPARSE",
        str(temp_dmg),
    ]
    if not run_command(cmd):
        return False

    # Find the created sparse image
    if not sparse_path.exists():
        sparse_path = temp_dmg.with_suffix(".dmg.sparseimage")

    # Mount the sparse image
    volume_path = Path(f"/Volumes/{APP_NAME}")

    # Unmount if already mounted
    if volume_path.exists():
        subprocess.run(["hdiutil", "detach", str(volume_path)], capture_output=True)

    mount_result = subprocess.run(
        ["hdiutil", "attach", str(sparse_path), "-mountpoint", str(volume_path)],
        capture_output=True,
        text=True,
    )
    if mount_result.returncode != 0:
        print(f"  Mount error: {mount_result.stderr}")
        return False

    try:
        # Copy app to volume
        dest_app = volume_path / f"{APP_NAME}.app"
        print(f"  Copying app to DMG volume...")
        shutil.copytree(app_path, dest_app, symlinks=True)

        # Create Applications symlink
        apps_link = volume_path / "Applications"
        if not apps_link.exists():
            apps_link.symlink_to("/Applications")

    finally:
        # Unmount
        subprocess.run(["hdiutil", "detach", str(volume_path)], capture_output=True)

    # Convert sparse image to compressed DMG
    cmd = [
        "hdiutil", "convert",
        str(sparse_path),
        "-format", "UDZO",
        "-imagekey", "zlib-level=9",
        "-o", str(dmg_path),
    ]
    if not run_command(cmd):
        return False

    # Clean up sparse image
    if sparse_path.exists():
        sparse_path.unlink()

    print(f"  Created: {dmg_path}")

    # Show size
    size_mb = dmg_path.stat().st_size / (1024 * 1024)
    print(f"  DMG size: {size_mb:.1f} MB")

    return True


def show_results():
    """Show build results."""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / f"{DMG_NAME}-{VERSION}.dmg"

    print("\n" + "=" * 50)
    print("Build Results:")
    print("=" * 50)

    if app_path.exists():
        size_mb = sum(f.stat().st_size for f in app_path.rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"\nApp: {app_path}")
        print(f"     Size: {size_mb:.1f} MB")

    if dmg_path.exists():
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"\nDMG: {dmg_path}")
        print(f"     Size: {size_mb:.1f} MB")


def main():
    parser = argparse.ArgumentParser(description="Build DocSend to PDF Mac app")
    parser.add_argument("--skip-bundle", action="store_true", help="Skip dependency bundling")
    parser.add_argument("--skip-dmg", action="store_true", help="Skip DMG creation")
    parser.add_argument("--clean", action="store_true", help="Clean build before starting")
    args = parser.parse_args()

    print("=" * 50)
    print(f"Building {APP_NAME} v{VERSION}")
    print("=" * 50)

    steps = []

    if args.clean:
        steps.append(("Cleaning build", clean_build))

    steps.append(("Checking icon", ensure_icon))

    if not args.skip_bundle:
        steps.append(("Bundling dependencies", ensure_bundle))

    steps.extend([
        ("Building app with PyInstaller", build_app),
        ("Copying Chromium to app", copy_chromium_to_app),
    ])

    if not args.skip_dmg:
        steps.append(("Creating DMG", create_dmg))

    for step_name, step_func in steps:
        print(f"\n[{step_name}]")
        if not step_func():
            print(f"\n*** Build FAILED at: {step_name} ***")
            return 1

    show_results()

    print("\n" + "=" * 50)
    print("Build complete!")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())

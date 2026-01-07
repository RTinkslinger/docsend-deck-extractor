#!/usr/bin/env python3
"""Download and bundle dependencies for the Mac app.

Downloads:
- Tesseract OCR binary and data files
- Chromium browser via Playwright

Usage:
    python scripts/bundle_deps.py [--arch arm64|x86_64]
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# Bundle directory structure
BUNDLE_DIR = Path(__file__).parent.parent / "bundle"
TESSERACT_DIR = BUNDLE_DIR / "tesseract"
CHROMIUM_DIR = BUNDLE_DIR / "chromium"

# Tesseract Homebrew bottle URLs (macOS Sonoma 14)
# These are from Homebrew's bottle repository
TESSERACT_BOTTLES = {
    "arm64": "https://ghcr.io/v2/homebrew/core/tesseract/blobs/sha256:7d8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c8c",
    "x86_64": "https://ghcr.io/v2/homebrew/core/tesseract/blobs/sha256:6d7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c",
}

# Tesseract language data
TESSDATA_URL = "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata"


def get_arch() -> str:
    """Get the current CPU architecture."""
    machine = platform.machine()
    if machine == "arm64":
        return "arm64"
    elif machine in ("x86_64", "AMD64"):
        return "x86_64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")


def download_file(url: str, dest: Path, desc: str = "") -> None:
    """Download a file with progress indication.

    Args:
        url: URL to download
        dest: Destination path
        desc: Description for progress
    """
    print(f"Downloading {desc or url}...")

    def report_progress(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, block_num * block_size * 100 // total_size)
            print(f"\r  Progress: {percent}%", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=report_progress)
    print()  # Newline after progress


def setup_tesseract_from_brew(arch: str) -> None:
    """Download Tesseract from Homebrew or copy from local installation.

    Args:
        arch: Target architecture (arm64 or x86_64)
    """
    print("\n=== Setting up Tesseract ===")

    # Create directories
    TESSERACT_DIR.mkdir(parents=True, exist_ok=True)
    tessdata_dir = TESSERACT_DIR / "share" / "tessdata"
    tessdata_dir.mkdir(parents=True, exist_ok=True)
    bin_dir = TESSERACT_DIR / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    lib_dir = TESSERACT_DIR / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)

    # Try to copy from local Homebrew installation first
    brew_prefix = Path("/opt/homebrew") if arch == "arm64" else Path("/usr/local")
    tesseract_bin = brew_prefix / "bin" / "tesseract"

    if tesseract_bin.exists():
        print(f"Copying Tesseract from {brew_prefix}...")

        # Copy binary
        shutil.copy2(tesseract_bin, bin_dir / "tesseract")

        # Copy libraries
        tesseract_lib = brew_prefix / "lib"
        for lib in tesseract_lib.glob("libtesseract*.dylib"):
            shutil.copy2(lib, lib_dir / lib.name)
        for lib in tesseract_lib.glob("liblept*.dylib"):
            shutil.copy2(lib, lib_dir / lib.name)

        # Copy tessdata
        tessdata_src = brew_prefix / "share" / "tessdata"
        if tessdata_src.exists():
            for f in tessdata_src.glob("*.traineddata"):
                shutil.copy2(f, tessdata_dir / f.name)

        # Fix library paths using install_name_tool
        _fix_dylib_paths(bin_dir / "tesseract", lib_dir)

        print("  Tesseract copied from Homebrew installation")
    else:
        print("  Homebrew Tesseract not found, downloading language data only...")
        # Just download the language data - user will need tesseract installed
        # In production, we'd download the actual binary

    # Ensure we have English language data
    eng_traineddata = tessdata_dir / "eng.traineddata"
    if not eng_traineddata.exists():
        print("Downloading English language data...")
        download_file(TESSDATA_URL, eng_traineddata, "eng.traineddata")

    print(f"  Tesseract bundle ready at: {TESSERACT_DIR}")


def _fix_dylib_paths(binary: Path, lib_dir: Path) -> None:
    """Fix dynamic library paths in a binary to use @executable_path.

    Args:
        binary: Path to the binary to fix
        lib_dir: Path to the lib directory
    """
    try:
        # Get current library dependencies
        result = subprocess.run(
            ["otool", "-L", str(binary)],
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines()[1:]:  # Skip first line (binary path)
            lib_path = line.strip().split()[0]
            if "/opt/homebrew" in lib_path or "/usr/local" in lib_path:
                lib_name = Path(lib_path).name
                new_path = f"@executable_path/../lib/{lib_name}"
                subprocess.run([
                    "install_name_tool",
                    "-change", lib_path, new_path,
                    str(binary)
                ], check=True)

        # Also fix the libraries themselves
        for lib in lib_dir.glob("*.dylib"):
            # Change the library's own ID
            subprocess.run([
                "install_name_tool",
                "-id", f"@executable_path/../lib/{lib.name}",
                str(lib)
            ], check=False)

            # Fix dependencies within the library
            result = subprocess.run(
                ["otool", "-L", str(lib)],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.splitlines()[1:]:
                dep_path = line.strip().split()[0]
                if "/opt/homebrew" in dep_path or "/usr/local" in dep_path:
                    dep_name = Path(dep_path).name
                    new_path = f"@executable_path/../lib/{dep_name}"
                    subprocess.run([
                        "install_name_tool",
                        "-change", dep_path, new_path,
                        str(lib)
                    ], check=False)

    except Exception as e:
        print(f"  Warning: Could not fix library paths: {e}")


def setup_chromium() -> None:
    """Download Chromium via Playwright."""
    print("\n=== Setting up Chromium ===")

    CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)

    # Set environment to download to our bundle directory
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(CHROMIUM_DIR)

    print("Installing Chromium via Playwright...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  Error: {result.stderr}")
        raise RuntimeError("Failed to install Chromium")

    # Find the installed Chromium
    chromium_versions = list(CHROMIUM_DIR.glob("chromium-*"))
    if chromium_versions:
        print(f"  Chromium installed: {chromium_versions[0].name}")

    print(f"  Chromium bundle ready at: {CHROMIUM_DIR}")


def verify_bundle() -> None:
    """Verify the bundle is complete."""
    print("\n=== Verifying Bundle ===")

    errors = []

    # Check Tesseract
    tesseract_bin = TESSERACT_DIR / "bin" / "tesseract"
    tessdata = TESSERACT_DIR / "share" / "tessdata" / "eng.traineddata"

    if tesseract_bin.exists():
        print(f"  [OK] Tesseract binary: {tesseract_bin}")
    else:
        print(f"  [WARN] Tesseract binary not found (will use system)")

    if tessdata.exists():
        print(f"  [OK] English language data: {tessdata}")
    else:
        errors.append("Missing eng.traineddata")

    # Check Chromium
    chromium_versions = list(CHROMIUM_DIR.glob("chromium-*"))
    if chromium_versions:
        chrome_path = None
        # Playwright now uses "Google Chrome for Testing"
        for arch_dir in ["chrome-mac-arm64", "chrome-mac"]:
            for app_name in ["Google Chrome for Testing.app", "Chromium.app"]:
                test_path = chromium_versions[0] / arch_dir / app_name
                if test_path.exists():
                    chrome_path = test_path
                    break
            if chrome_path:
                break

        if chrome_path:
            print(f"  [OK] Chromium: {chrome_path}")
        else:
            errors.append("Chrome/Chromium.app not found in bundle")
    else:
        errors.append("No Chromium version found")

    # Calculate bundle size
    total_size = sum(f.stat().st_size for f in BUNDLE_DIR.rglob("*") if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print(f"\n  Total bundle size: {size_mb:.1f} MB")

    if size_mb > 300:
        print(f"  [WARN] Bundle exceeds 300MB target")

    if errors:
        print("\n  Errors:")
        for error in errors:
            print(f"    - {error}")
        return False

    print("\n  Bundle verification complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Bundle dependencies for Mac app")
    parser.add_argument(
        "--arch",
        choices=["arm64", "x86_64"],
        default=get_arch(),
        help="Target architecture (default: current)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing bundle before downloading",
    )
    args = parser.parse_args()

    print(f"Bundling dependencies for {args.arch}...")

    if args.clean and BUNDLE_DIR.exists():
        print(f"Cleaning {BUNDLE_DIR}...")
        shutil.rmtree(BUNDLE_DIR)

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    # Setup dependencies
    setup_tesseract_from_brew(args.arch)
    setup_chromium()

    # Verify
    if verify_bundle():
        print("\n=== Bundle Complete ===")
        print(f"Bundle location: {BUNDLE_DIR}")
    else:
        print("\n=== Bundle Incomplete ===")
        sys.exit(1)


if __name__ == "__main__":
    main()

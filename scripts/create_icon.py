#!/usr/bin/env python3
"""Generate the app icon for DocSend to PDF.

Creates a simple document-style icon with the app's purple color scheme.
Outputs to resources/app_icon.icns
"""

import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL not found. Install with: pip install Pillow")
    exit(1)

# App colors
PRIMARY_COLOR = "#8B5CF6"  # Purple
BACKGROUND_COLOR = "#FFFFFF"
ACCENT_COLOR = "#7C3AED"
TEXT_COLOR = "#FFFFFF"

# Icon sizes needed for icns
ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_icon(size: int) -> Image.Image:
    """Create an icon at the specified size.

    Args:
        size: Icon size in pixels

    Returns:
        PIL Image
    """
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    padding = size * 0.1
    doc_width = size - (padding * 2)
    doc_height = size - (padding * 2)
    corner_size = size * 0.2

    # Document shape coordinates
    x1, y1 = padding, padding
    x2, y2 = size - padding, size - padding

    # Draw document background (rounded rectangle)
    primary_rgb = hex_to_rgb(PRIMARY_COLOR)

    # Main document body
    draw.rounded_rectangle(
        [x1, y1, x2, y2],
        radius=size * 0.08,
        fill=primary_rgb,
    )

    # Folded corner effect (lighter shade)
    corner_points = [
        (x2 - corner_size, y1),  # Top of fold
        (x2, y1 + corner_size),  # Right of fold
        (x2 - corner_size, y1 + corner_size),  # Corner
    ]
    accent_rgb = hex_to_rgb(ACCENT_COLOR)
    draw.polygon(corner_points, fill=accent_rgb)

    # Draw "PDF" text or lines to represent content
    line_color = (255, 255, 255, 180)  # Semi-transparent white
    line_y_start = y1 + size * 0.35
    line_spacing = size * 0.12
    line_margin = size * 0.15

    for i in range(3):
        line_y = line_y_start + (i * line_spacing)
        # Vary line lengths
        line_end = x2 - line_margin - (i * size * 0.1)
        if line_y + size * 0.03 < y2 - padding:
            draw.rounded_rectangle(
                [x1 + line_margin, line_y, line_end, line_y + size * 0.04],
                radius=size * 0.02,
                fill=line_color,
            )

    # Draw arrow or download indicator at bottom
    arrow_size = size * 0.15
    arrow_y = y2 - padding - arrow_size
    arrow_x = (x1 + x2) / 2

    # Down arrow
    arrow_points = [
        (arrow_x, arrow_y + arrow_size),  # Bottom point
        (arrow_x - arrow_size * 0.6, arrow_y),  # Top left
        (arrow_x + arrow_size * 0.6, arrow_y),  # Top right
    ]
    draw.polygon(arrow_points, fill=(255, 255, 255, 200))

    return img


def create_iconset(output_dir: Path) -> None:
    """Create an iconset directory with all required sizes.

    Args:
        output_dir: Directory to create iconset in
    """
    iconset_dir = output_dir / "app_icon.iconset"
    iconset_dir.mkdir(parents=True, exist_ok=True)

    for size in ICON_SIZES:
        # Regular resolution
        icon = create_icon(size)
        icon.save(iconset_dir / f"icon_{size}x{size}.png")

        # @2x (Retina) resolution for smaller sizes
        if size <= 512:
            icon_2x = create_icon(size * 2)
            icon_2x.save(iconset_dir / f"icon_{size}x{size}@2x.png")

    return iconset_dir


def convert_to_icns(iconset_dir: Path, output_path: Path) -> bool:
    """Convert iconset to icns using iconutil.

    Args:
        iconset_dir: Path to .iconset directory
        output_path: Output .icns path

    Returns:
        True if successful
    """
    try:
        result = subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(output_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"iconutil error: {result.stderr}")
            return False
        return True
    except FileNotFoundError:
        print("iconutil not found. This script requires macOS.")
        return False


def main():
    # Determine output paths
    script_dir = Path(__file__).parent.parent
    resources_dir = script_dir / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    output_icns = resources_dir / "app_icon.icns"

    print("Creating app icon...")

    # Create iconset in temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        iconset_dir = create_iconset(tmpdir)
        print(f"  Created iconset at {iconset_dir}")

        # Convert to icns
        if convert_to_icns(iconset_dir, output_icns):
            print(f"  Created {output_icns}")
        else:
            print("  Failed to create icns file")
            return 1

    # Also save a PNG preview
    preview_path = resources_dir / "app_icon_preview.png"
    preview = create_icon(512)
    preview.save(preview_path)
    print(f"  Created preview at {preview_path}")

    print("\nIcon creation complete!")
    return 0


if __name__ == "__main__":
    exit(main())

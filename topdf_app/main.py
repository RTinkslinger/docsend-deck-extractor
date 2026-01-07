#!/usr/bin/env python3
"""Entry point for the DocSend to PDF Mac app.

Run with: python -m topdf_app.main
"""

import sys

# Configure bundled dependencies FIRST, before any other imports
from topdf_app.core.bundle import setup_bundled_environment
_bundle_env = setup_bundled_environment()


def main() -> int:
    """Application entry point.

    Returns:
        Exit code
    """
    # Import Qt after creating QApplication
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    # Create application
    app = QApplication(sys.argv)

    # Configure application
    app.setApplicationName("DocSend to PDF")
    app.setOrganizationName("topdf")
    app.setOrganizationDomain("topdf.local")

    # Keep running when main window is closed (tray app)
    app.setQuitOnLastWindowClosed(False)

    # macOS specific: Hide dock icon (menu bar app only)
    # This is typically done via Info.plist LSUIElement=true
    # But we can also do it programmatically:
    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except ImportError:
        # pyobjc not available, dock icon will show
        pass

    # Import and create main app controller
    from topdf_app.app import DocSendApp
    docsend_app = DocSendApp()
    docsend_app.start()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

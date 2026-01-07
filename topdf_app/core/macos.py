"""macOS-specific utilities.

Provides integration with macOS features like dock bounce and notifications.
"""

from __future__ import annotations


def bounce_dock() -> None:
    """Bounce the dock icon to get user attention.

    Uses NSApplicationActivationPolicyAccessory informational request.
    """
    try:
        from AppKit import NSApp, NSInformationalRequest
        NSApp.requestUserAttention_(NSInformationalRequest)
    except ImportError:
        # pyobjc not available
        pass
    except Exception:
        # Failed, not critical
        pass


def bounce_dock_critical() -> None:
    """Bounce the dock icon continuously until app is focused.

    Uses NSCriticalRequest for persistent bouncing.
    """
    try:
        from AppKit import NSApp, NSCriticalRequest
        NSApp.requestUserAttention_(NSCriticalRequest)
    except ImportError:
        # pyobjc not available
        pass
    except Exception:
        # Failed, not critical
        pass


def show_notification(title: str, message: str, subtitle: str = "") -> None:
    """Show a macOS notification.

    Args:
        title: Notification title
        message: Notification body
        subtitle: Optional subtitle
    """
    try:
        from Foundation import (
            NSUserNotification,
            NSUserNotificationCenter,
        )

        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)
        if subtitle:
            notification.setSubtitle_(subtitle)

        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)
    except ImportError:
        # pyobjc not available
        pass
    except Exception:
        # Notification failed, not critical
        pass


def bring_to_front() -> None:
    """Bring the application to the front."""
    try:
        from AppKit import NSApp, NSApplicationActivateIgnoringOtherApps
        NSApp.activateIgnoringOtherApps_(True)
    except ImportError:
        pass
    except Exception:
        pass


def set_login_item(enabled: bool) -> bool:
    """Add or remove the app from Login Items.

    Args:
        enabled: True to add to login items, False to remove

    Returns:
        True if operation succeeded
    """
    try:
        import subprocess
        import sys

        # Get the app bundle path
        # When running as a bundled app, this will be the .app path
        # When running as script, we use the Python executable
        if getattr(sys, 'frozen', False):
            # Bundled app
            app_path = sys.executable
            # Go up to find the .app bundle
            import os
            while app_path and not app_path.endswith('.app'):
                app_path = os.path.dirname(app_path)
        else:
            # Running as script - use Python path (won't really work as login item)
            app_path = sys.executable

        if enabled:
            # Add to login items using osascript
            script = f'''
            tell application "System Events"
                make login item at end with properties {{path:"{app_path}", hidden:false}}
            end tell
            '''
        else:
            # Remove from login items
            app_name = "Python"  # Will be "DocSend to PDF" when bundled
            if app_path.endswith('.app'):
                import os
                app_name = os.path.basename(app_path).replace('.app', '')

            script = f'''
            tell application "System Events"
                delete login item "{app_name}"
            end tell
            '''

        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    except Exception:
        return False


def is_login_item() -> bool:
    """Check if the app is in Login Items.

    Returns:
        True if app is a login item
    """
    try:
        import subprocess

        script = '''
        tell application "System Events"
            get the name of every login item
        end tell
        '''

        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Check if our app is in the list
            items = result.stdout.strip()
            return "DocSend to PDF" in items or "Python" in items

        return False
    except Exception:
        return False

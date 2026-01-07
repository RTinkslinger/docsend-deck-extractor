"""Tests for the DocSend to PDF Mac app UI components.

Tests cover:
- Screen components (home, progress, complete, error, auth)
- URL validation
- Loading states
- Navigation between screens
- Animations
"""

import pytest
from unittest.mock import MagicMock, patch

# Skip all tests if PySide6 is not available
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


@pytest.fixture(scope="module")
def app():
    """Create QApplication instance for tests."""
    # Check if app already exists
    existing_app = QApplication.instance()
    if existing_app:
        yield existing_app
    else:
        app = QApplication([])
        yield app


class TestHomeScreen:
    """Tests for the home screen component."""

    def test_home_screen_creation(self, app):
        """Test home screen can be created."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        assert screen is not None
        assert screen.url_input is not None
        assert screen.convert_btn is not None

    def test_url_validation_valid(self, app):
        """Test valid DocSend URL enables convert button."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        screen.url_input.setText("https://docsend.com/view/abc123")
        assert screen.convert_btn.isEnabled()

    def test_url_validation_invalid(self, app):
        """Test invalid URL disables convert button."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        screen.url_input.setText("https://example.com/test")
        assert not screen.convert_btn.isEnabled()

    def test_url_validation_empty(self, app):
        """Test empty URL disables convert button."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        screen.url_input.setText("")
        assert not screen.convert_btn.isEnabled()

    def test_loading_state(self, app):
        """Test loading state disables input and changes button text."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        screen.url_input.setText("https://docsend.com/view/abc123")

        screen.set_loading(True)
        assert not screen.convert_btn.isEnabled()
        assert screen.convert_btn.text() == "Converting..."
        assert not screen.url_input.isEnabled()

        screen.set_loading(False)
        assert screen.convert_btn.text() == "Convert"
        assert screen.url_input.isEnabled()

    def test_clear_input(self, app):
        """Test clear_input resets the screen."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        screen.url_input.setText("https://docsend.com/view/abc123")
        screen.set_loading(True)

        screen.clear_input()
        assert screen.url_input.text() == ""
        assert screen.convert_btn.text() == "Convert"
        assert screen.url_input.isEnabled()

    def test_convert_signal_emitted(self, app):
        """Test convert signal is emitted with URL."""
        from topdf_app.ui.screens.home import HomeScreen

        screen = HomeScreen()
        url = "https://docsend.com/view/abc123"
        screen.url_input.setText(url)

        signal_received = []
        screen.convert_clicked.connect(lambda u: signal_received.append(u))
        screen._on_convert_clicked()

        assert len(signal_received) == 1
        assert signal_received[0] == url


class TestProgressScreen:
    """Tests for the progress screen component."""

    def test_progress_screen_creation(self, app):
        """Test progress screen can be created."""
        from topdf_app.ui.screens.progress import ProgressScreen

        screen = ProgressScreen()
        assert screen is not None
        assert screen.progress_bar is not None
        assert screen.cancel_btn is not None

    def test_set_progress(self, app):
        """Test setting progress updates UI."""
        from topdf_app.ui.screens.progress import ProgressScreen

        screen = ProgressScreen()
        screen.set_progress(50, "Converting page 3 of 6")

        assert screen.progress_bar.value() == 50
        assert "Converting page 3 of 6" in screen.status_label.text()

    def test_reset(self, app):
        """Test reset returns to initial state."""
        from topdf_app.ui.screens.progress import ProgressScreen

        screen = ProgressScreen()
        screen.set_progress(75, "Almost done")

        screen.reset()
        assert screen.progress_bar.value() == 0
        assert screen.cancel_btn.isEnabled()
        assert screen.cancel_btn.text() == "Cancel"

    def test_animation_methods(self, app):
        """Test animation start/stop methods exist and work."""
        from topdf_app.ui.screens.progress import ProgressScreen

        screen = ProgressScreen()
        screen.start_animation()
        screen.stop_animation()
        # Should not raise any errors


class TestCompleteScreen:
    """Tests for the complete screen component."""

    def test_complete_screen_creation(self, app):
        """Test complete screen can be created."""
        from topdf_app.ui.screens.complete import CompleteScreen

        screen = CompleteScreen()
        assert screen is not None
        assert screen.open_btn is not None
        assert screen.finder_btn is not None

    def test_set_result(self, app, tmp_path):
        """Test setting result updates display with editable name."""
        from topdf_app.ui.screens.complete import CompleteScreen

        screen = CompleteScreen()
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_text("test")

        screen.set_result(str(pdf_path), 10, "Test Company")

        # Name input should be populated with suggested name
        assert screen.name_input.text() == "Test Company"
        assert "10 pages" in screen.pages_label.text()
        # Naming section should not be hidden, saved section should be hidden
        assert not screen.naming_section.isHidden()
        assert screen.saved_section.isHidden()

    def test_success_animation(self, app):
        """Test success animation method exists."""
        from topdf_app.ui.screens.complete import CompleteScreen

        screen = CompleteScreen()
        screen.play_success_animation()
        # Should not raise any errors


class TestErrorScreen:
    """Tests for the error screen component."""

    def test_error_screen_creation(self, app):
        """Test error screen can be created."""
        from topdf_app.ui.screens.error import ErrorScreen

        screen = ErrorScreen()
        assert screen is not None
        assert screen.retry_btn is not None

    def test_set_error(self, app):
        """Test setting error updates display."""
        from topdf_app.ui.screens.error import ErrorScreen

        screen = ErrorScreen()
        screen.set_error("Connection timed out", "Full traceback here")

        assert "timed out" in screen.message_label.text().lower()

    def test_error_descriptions(self, app):
        """Test error descriptions are appropriate."""
        from topdf_app.ui.screens.error import ErrorScreen

        screen = ErrorScreen()

        test_cases = [
            ("Connection timed out", "connection took too long"),
            ("Network error occurred", "Network connection failed"),
            ("Invalid email or passcode", "credentials were rejected"),
            ("Permission denied", "Cannot save to this location"),
        ]

        for error_msg, expected_fragment in test_cases:
            screen.set_error(error_msg, "")
            assert expected_fragment.lower() in screen.description_label.text().lower()

    def test_error_animation(self, app):
        """Test error animation method exists."""
        from topdf_app.ui.screens.error import ErrorScreen

        screen = ErrorScreen()
        screen.play_error_animation()
        # Should not raise any errors


class TestAuthEmailScreen:
    """Tests for the auth email screen component."""

    def test_auth_email_screen_creation(self, app):
        """Test auth email screen can be created."""
        from topdf_app.ui.screens.auth_email import AuthEmailScreen

        screen = AuthEmailScreen()
        assert screen is not None
        assert screen.email_input is not None
        assert screen.submit_btn is not None

    def test_email_validation(self, app):
        """Test email validation enables submit button."""
        from topdf_app.ui.screens.auth_email import AuthEmailScreen

        screen = AuthEmailScreen()

        screen.email_input.setText("invalid")
        assert not screen.submit_btn.isEnabled()

        screen.email_input.setText("valid@example.com")
        assert screen.submit_btn.isEnabled()

    def test_loading_state(self, app):
        """Test loading state disables controls."""
        from topdf_app.ui.screens.auth_email import AuthEmailScreen

        screen = AuthEmailScreen()
        screen.email_input.setText("test@example.com")

        screen.set_loading(True)
        assert screen.submit_btn.text() == "Verifying..."
        assert not screen.email_input.isEnabled()

        screen.set_loading(False)
        assert screen.submit_btn.text() == "Continue"
        assert screen.email_input.isEnabled()


class TestAuthPasscodeScreen:
    """Tests for the auth passcode screen component."""

    def test_auth_passcode_screen_creation(self, app):
        """Test auth passcode screen can be created."""
        from topdf_app.ui.screens.auth_passcode import AuthPasscodeScreen

        screen = AuthPasscodeScreen()
        assert screen is not None
        assert screen.email_input is not None
        assert screen.passcode_input is not None
        assert screen.submit_btn is not None

    def test_validation(self, app):
        """Test both fields required for submit."""
        from topdf_app.ui.screens.auth_passcode import AuthPasscodeScreen

        screen = AuthPasscodeScreen()

        # Neither field
        assert not screen.submit_btn.isEnabled()

        # Only email
        screen.email_input.setText("test@example.com")
        assert not screen.submit_btn.isEnabled()

        # Both fields
        screen.passcode_input.setText("secret")
        assert screen.submit_btn.isEnabled()

    def test_loading_state(self, app):
        """Test loading state disables all controls."""
        from topdf_app.ui.screens.auth_passcode import AuthPasscodeScreen

        screen = AuthPasscodeScreen()
        screen.email_input.setText("test@example.com")
        screen.passcode_input.setText("secret")

        screen.set_loading(True)
        assert screen.submit_btn.text() == "Verifying..."
        assert not screen.email_input.isEnabled()
        assert not screen.passcode_input.isEnabled()

        screen.set_loading(False)
        assert screen.submit_btn.text() == "Continue"
        assert screen.email_input.isEnabled()
        assert screen.passcode_input.isEnabled()


class TestMainWindow:
    """Tests for the main window component."""

    def test_main_window_creation(self, app):
        """Test main window can be created."""
        from topdf_app.ui.main_window import MainWindow

        window = MainWindow()
        assert window is not None
        assert window.stack is not None

    def test_screen_navigation(self, app):
        """Test navigation between screens."""
        from topdf_app.ui.main_window import MainWindow

        window = MainWindow()

        # Start on home
        assert window.get_current_screen() == "home"

        # Navigate to progress
        window.show_screen("progress")
        assert window.get_current_screen() == "progress"

        # Navigate to complete
        window.show_screen("complete")
        assert window.get_current_screen() == "complete"

        # Navigate to error
        window.show_screen("error")
        assert window.get_current_screen() == "error"

    def test_invalid_screen_navigation(self, app):
        """Test navigating to invalid screen does nothing."""
        from topdf_app.ui.main_window import MainWindow

        window = MainWindow()
        window.show_screen("home")
        window.show_screen("nonexistent_screen")

        # Should still be on home
        assert window.get_current_screen() == "home"


class TestURLValidation:
    """Tests for URL validation function."""

    def test_valid_urls(self, app):
        """Test valid DocSend URLs pass validation."""
        from topdf_app.ui.screens.home import is_valid_docsend_url

        valid_urls = [
            "https://docsend.com/view/abc123",
            "https://www.docsend.com/view/abc123",
            "http://docsend.com/view/test123",
            "https://docsend.com/view/ABC123XYZ",
        ]

        for url in valid_urls:
            assert is_valid_docsend_url(url), f"URL should be valid: {url}"

    def test_invalid_urls(self, app):
        """Test invalid URLs fail validation."""
        from topdf_app.ui.screens.home import is_valid_docsend_url

        invalid_urls = [
            "https://example.com/view/abc123",
            "https://docsend.com/abc123",
            "https://docsend.com/",
            "not-a-url",
            "",
            "https://google.com/view/abc123",
        ]

        for url in invalid_urls:
            assert not is_valid_docsend_url(url), f"URL should be invalid: {url}"


class TestConversionWorker:
    """Tests for the conversion worker."""

    def test_worker_creation(self, app):
        """Test worker can be created."""
        from topdf_app.core.worker import ConversionWorker

        worker = ConversionWorker(
            url="https://docsend.com/view/test",
            output_dir="/tmp",
        )
        assert worker is not None
        assert worker.url == "https://docsend.com/view/test"

    def test_worker_cancel(self, app):
        """Test worker can be cancelled."""
        from topdf_app.core.worker import ConversionWorker

        worker = ConversionWorker(url="https://docsend.com/view/test")
        worker.cancel()
        assert worker._cancelled

    def test_worker_provide_credentials(self, app):
        """Test credentials can be provided to worker."""
        from topdf_app.core.worker import ConversionWorker

        worker = ConversionWorker(url="https://docsend.com/view/test")
        worker.provide_credentials("test@example.com", "secret123")

        assert worker.email == "test@example.com"
        assert worker.passcode == "secret123"

    def test_error_formatting(self, app):
        """Test error messages are user-friendly."""
        from topdf_app.core.worker import ConversionWorker

        worker = ConversionWorker(url="https://docsend.com/view/test")

        # Test timeout error
        class MockTimeoutError(Exception):
            pass

        result = worker._format_error(MockTimeoutError("request timed out"))
        assert "timeout" in result.lower() or "timed out" in result.lower()

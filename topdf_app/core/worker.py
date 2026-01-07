"""Background worker for DocSend conversion.

Runs the conversion process in a separate thread to keep the UI responsive.
"""

from __future__ import annotations

import asyncio
import threading
import traceback
from typing import Optional
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QObject


class ConversionWorker(QThread):
    """Background worker thread for DocSend conversion.

    Supports interactive authentication by pausing and waiting for
    credentials when a protected document is encountered.

    Signals:
        progress: (percent, status_message) - Progress updates
        auth_required: (auth_type) - Auth needed ("email" or "passcode")
        complete: (pdf_path, page_count, company_name) - Conversion complete
        error: (error_message, details) - Conversion failed
    """

    progress = Signal(int, str)  # percent (0-100), status message
    auth_required = Signal(str)  # auth_type: "email" or "passcode"
    complete = Signal(str, int, str)  # pdf_path, page_count, company_name
    error = Signal(str, str)  # error_message, traceback

    def __init__(
        self,
        url: str,
        output_dir: Optional[str] = None,
        output_name: Optional[str] = None,
        email: Optional[str] = None,
        passcode: Optional[str] = None,
        parent: Optional[QObject] = None,
    ):
        """Initialize the conversion worker.

        Args:
            url: DocSend URL to convert
            output_dir: Output directory for PDF
            output_name: Custom output filename
            email: Email for protected documents (can be provided later)
            passcode: Passcode for protected documents (can be provided later)
            parent: Parent QObject
        """
        super().__init__(parent)

        self.url = url
        self.output_dir = output_dir or "converted PDFs"
        self.output_name = output_name
        self.email = email
        self.passcode = passcode

        self._cancelled = False
        self._auth_event = threading.Event()
        self._auth_provided = False

    def run(self) -> None:
        """Execute conversion in background thread."""
        try:
            # Import here to avoid loading heavy modules at startup
            from topdf.scraper import DocSendScraper
            from topdf.pdf_builder import PDFBuilder
            from topdf.exceptions import (
                EmailRequiredError,
                PasscodeRequiredError,
            )

            self.progress.emit(0, "Initializing...")

            # Initialize components
            scraper = DocSendScraper(headless=True, verbose=False)
            pdf_builder = PDFBuilder(optimize=True)

            # Progress callback for scraping
            def on_scrape_progress(current: int, total: int) -> None:
                if self._cancelled:
                    return
                # Scraping is 60% of the work
                percent = int((current / total) * 60)
                self.progress.emit(percent, f"Capturing page {current} of {total}")

            # First attempt - may fail if auth is needed
            self.progress.emit(5, "Loading document...")

            try:
                scrape_result = asyncio.run(
                    scraper.scrape(
                        url=self.url,
                        email=self.email,
                        passcode=self.passcode,
                        progress_callback=on_scrape_progress,
                    )
                )
            except EmailRequiredError:
                if self._cancelled:
                    return

                # Need email - signal UI and wait
                self.progress.emit(10, "Authentication required...")
                self.auth_required.emit("email")

                # Wait for credentials
                self._auth_event.wait()
                self._auth_event.clear()

                if self._cancelled or not self._auth_provided:
                    return

                # Retry with credentials
                self.progress.emit(15, "Authenticating...")
                scrape_result = asyncio.run(
                    scraper.scrape(
                        url=self.url,
                        email=self.email,
                        passcode=self.passcode,
                        progress_callback=on_scrape_progress,
                    )
                )

            except PasscodeRequiredError:
                if self._cancelled:
                    return

                # Need passcode - signal UI and wait
                self.progress.emit(10, "Authentication required...")
                self.auth_required.emit("passcode")

                # Wait for credentials
                self._auth_event.wait()
                self._auth_event.clear()

                if self._cancelled or not self._auth_provided:
                    return

                # Retry with credentials
                self.progress.emit(15, "Authenticating...")
                scrape_result = asyncio.run(
                    scraper.scrape(
                        url=self.url,
                        email=self.email,
                        passcode=self.passcode,
                        progress_callback=on_scrape_progress,
                    )
                )

            if self._cancelled:
                return

            # Step 2: Generate random name (65%)
            self.progress.emit(62, "Generating name...")

            from topdf_app.core.names import get_name_manager

            name_manager = get_name_manager()

            if self.output_name:
                # User provided a name
                suggested_name = self.output_name
            else:
                # Generate a fun random cartoon name
                suggested_name = name_manager.get_random_name()

            if self._cancelled:
                return

            # Step 3: Build PDF (95%)
            self.progress.emit(70, "Building PDF...")
            pdf_bytes = pdf_builder.build(scrape_result.screenshots)

            if self._cancelled:
                return

            # Step 4: Save PDF (100%)
            self.progress.emit(90, "Saving PDF...")

            # Save to output directory with suggested name (user can rename later)
            output_dir = Path(self.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{suggested_name}.pdf"

            # Make unique if exists
            counter = 1
            base_name = suggested_name
            while output_path.exists():
                output_path = output_dir / f"{base_name} ({counter}).pdf"
                counter += 1

            output_path.write_bytes(pdf_bytes)

            self.progress.emit(100, "Complete!")
            self.complete.emit(
                str(output_path),
                scrape_result.page_count,
                suggested_name,  # Pass the suggested name for editing
            )

        except Exception as e:
            if not self._cancelled:
                error_msg = self._format_error(e)
                self.error.emit(error_msg, traceback.format_exc())

    def _format_error(self, e: Exception) -> str:
        """Format exception into user-friendly error message.

        Args:
            e: Exception to format

        Returns:
            Formatted error message
        """
        # Import exception types for better error messages
        try:
            from topdf.exceptions import (
                TopdfError,
                InvalidURLError,
                PageLoadError,
                TimeoutError as TopdfTimeoutError,
                InvalidCredentialsError,
            )

            if isinstance(e, InvalidURLError):
                return "Invalid DocSend URL format"
            elif isinstance(e, InvalidCredentialsError):
                return "Invalid email or passcode"
            elif isinstance(e, PageLoadError):
                return "Could not load the document. Check your internet connection."
            elif isinstance(e, TopdfTimeoutError):
                return "Connection timed out. Please try again."
            elif isinstance(e, TopdfError):
                # Use the structured error message
                return e.message
        except ImportError:
            pass

        # Handle network errors
        error_str = str(e).lower()
        if "timeout" in error_str:
            return "Connection timed out. Please check your internet."
        elif "network" in error_str or "connection" in error_str:
            return "Network error. Please check your internet connection."
        elif "permission" in error_str:
            return "Permission denied. Cannot save file to this location."

        # Default: use the exception message
        return str(e)[:200] if len(str(e)) > 200 else str(e)

    def provide_credentials(self, email: str, passcode: Optional[str] = None) -> None:
        """Provide authentication credentials.

        Called from the main thread when user enters credentials.

        Args:
            email: Email address
            passcode: Optional passcode for protected documents
        """
        self.email = email
        self.passcode = passcode
        self._auth_provided = True
        self._auth_event.set()

    def cancel(self) -> None:
        """Request cancellation of the conversion."""
        self._cancelled = True
        self._auth_event.set()  # Unblock if waiting for auth

    def cancel_auth(self) -> None:
        """Cancel authentication and abort conversion."""
        self._cancelled = True
        self._auth_provided = False
        self._auth_event.set()


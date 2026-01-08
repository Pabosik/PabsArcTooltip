"""
Arc Raiders Helper - Main Application.
Coordinates OCR scanning and overlay display.
"""

import time
import tkinter as tk
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from pathlib import Path
from threading import Thread

from dotenv import load_dotenv

from src.arc_helper.config import get_settings
from src.arc_helper.config import reload_settings
from src.arc_helper.database import Database
from src.arc_helper.database import Item
from src.arc_helper.database import get_database
from src.arc_helper.ocr import get_ocr_engine
from src.arc_helper.overlay import OverlayWindow
from src.arc_helper.overlay import StatusWindow

load_dotenv(Path(__file__).with_name(".env"), override=False)


class ScannerState(Enum):
    """State machine for the scanner."""

    IDLE = auto()  # Scanning for trigger (INVENTORY)
    ACTIVE = auto()  # Inventory detected, scanning tooltip
    PAUSED = auto()  # Temporarily paused
    STOPPED = auto()  # Fully stopped


class DebugOverlay:
    """Semi-transparent overlay showing the tooltip capture area."""

    def __init__(self, root: tk.Tk, settings):
        self.root = root
        self.settings = settings

        self.window = tk.Toplevel(root)
        self.window.title("Capture Area")
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.3)  # Semi-transparent
        self.window.overrideredirect(True)
        self.window.config(bg="red")

        # Update position periodically
        self._update_position()

    def _update_position(self):
        """Update overlay position to follow cursor."""
        try:
            from src.arc_helper.ocr import get_cursor_position

            cursor = get_cursor_position()

            x = cursor.x + self.settings.tooltip_capture.offset_x
            y = cursor.y + self.settings.tooltip_capture.offset_y
            w = self.settings.tooltip_capture.width
            h = self.settings.tooltip_capture.height

            self.window.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        # Schedule next update (every 50ms for smooth following)
        self.root.after(50, self._update_position)

    def destroy(self):
        self.window.destroy()


@dataclass
class ScannerStats:
    """Statistics for the scanner."""

    trigger_scans: int = 0
    tooltip_scans: int = 0
    items_detected: int = 0
    items_found_in_db: int = 0
    last_item: str | None = None
    last_item_time: float = 0


@dataclass
class Scanner:
    """
    Main scanner that coordinates OCR and overlay.

    Uses a two-phase approach:
    1. Low-frequency scan for "INVENTORY" text (trigger)
    2. When triggered, high-frequency scan for item names
    """

    root: tk.Tk
    overlay: OverlayWindow
    status: StatusWindow
    db: Database = field(default_factory=get_database)
    state: ScannerState = ScannerState.IDLE
    stats: ScannerStats = field(default_factory=ScannerStats)

    # Cooldown tracking
    _last_shown_item: str = ""
    _last_shown_time: float = 0

    # Thread control
    _running: bool = False
    _scan_thread: Thread | None = None

    def start(self) -> None:
        """Start the scanner in a background thread."""
        if self._running:
            return

        self._running = True
        self.state = ScannerState.IDLE
        self._scan_thread = Thread(target=self._scan_loop, daemon=True)
        self._scan_thread.start()
        print("Scanner started")

    def stop(self) -> None:
        """Stop the scanner."""
        self._running = False
        self.state = ScannerState.STOPPED
        if self._scan_thread:
            self._scan_thread.join(timeout=2.0)
        print("Scanner stopped")

    def pause(self) -> None:
        """Pause scanning."""
        self.state = ScannerState.PAUSED

    def resume(self) -> None:
        """Resume scanning."""
        self.state = ScannerState.IDLE

    def _scan_loop(self) -> None:
        """Main scanning loop running in background thread."""
        settings = get_settings()
        ocr = get_ocr_engine()

        while self._running:
            try:
                if self.state == ScannerState.PAUSED:
                    time.sleep(0.1)
                    continue

                if self.state == ScannerState.STOPPED:
                    break

                # Phase 1: Check for trigger (INVENTORY)
                if self.state == ScannerState.IDLE:
                    self._update_status("scanning")

                    if ocr.check_trigger(settings.trigger_region):
                        # Trigger detected! Switch to active mode
                        self.state = ScannerState.ACTIVE
                        self._update_status("active")
                        print("INVENTORY detected - activating tooltip scanner")
                    else:
                        # Wait before next trigger scan
                        time.sleep(settings.scan.trigger_scan_interval)

                    self.stats.trigger_scans += 1

                # Phase 2: Active mode - scan tooltip
                elif self.state == ScannerState.ACTIVE:
                    # First, verify trigger is still present
                    if not ocr.check_trigger(settings.trigger_region):
                        # Inventory closed, go back to idle
                        self.state = ScannerState.IDLE
                        self._update_status("scanning")
                        print("INVENTORY closed - returning to idle")
                        continue

                    # Scan tooltip at cursor position
                    item_name = ocr.extract_item_name_at_cursor()
                    self.stats.tooltip_scans += 1

                    if item_name:
                        self._handle_detected_item(item_name)

                    # Wait before next tooltip scan
                    time.sleep(settings.scan.tooltip_scan_interval)

            except Exception as e:
                print(f"Scanner error: {e}")
                self._update_status("error")
                time.sleep(1.0)  # Back off on error

    def _handle_detected_item(self, item_name: str) -> None:
        """Handle a detected item name."""
        settings = get_settings()
        current_time = time.time()

        # Check cooldown - don't spam the same item
        if (
            item_name == self._last_shown_item
            and current_time - self._last_shown_time < settings.overlay.cooldown
        ):
            return

        self.stats.items_detected += 1
        self.stats.last_item = item_name
        self.stats.last_item_time = current_time

        # Look up in database
        recommendation = self.db.lookup(item_name)

        if recommendation:
            self.stats.items_found_in_db += 1
            print(f"Found: {item_name} → {recommendation.action}")
        else:
            print(f"Unknown item: {item_name}")

        # Show overlay (must be done on main thread)
        self._show_overlay(item_name, recommendation)

        # Update cooldown tracking
        self._last_shown_item = item_name
        self._last_shown_time = current_time

    def _show_overlay(self, item_name: str, recommendation: Item | None) -> None:
        """Show overlay on main thread."""
        self.root.after(0, lambda: self.overlay.show(item_name, recommendation))

    def _update_status(self, status: str) -> None:
        """Update status display on main thread."""

        def update():
            if status == "scanning":
                self.status.set_scanning()
            elif status == "active":
                self.status.set_active()
            elif status == "error":
                self.status.set_error("Error")

        self.root.after(0, update)


class Application:
    """Main application controller."""

    def __init__(self):
        """Initialize the application."""
        # Load settings
        self.settings = reload_settings()

        # Initialize database
        self.db = get_database()

        # Create main Tk root (hidden)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

        # Create overlay and status windows
        self.overlay = OverlayWindow(self.root)
        self.status = StatusWindow(self.root)

        # Debug overlay for visualizing capture area (separate from debug_mode)
        self.debug_overlay = None
        if self.settings.show_capture_area:
            self.debug_overlay = DebugOverlay(self.root, self.settings)

        # Create scanner
        self.scanner = Scanner(
            root=self.root,
            overlay=self.overlay,
            status=self.status,
            db=self.db,
        )

        # Bind close handler
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def run(self) -> None:
        """Start the application."""
        print("=" * 50)
        print("Arc Raiders Helper - Started")
        print("=" * 50)
        print(f"Database: {self.db.count()} items loaded")
        print(f"Debug mode: {self.settings.debug_mode}")
        print("=" * 50)
        print("Trigger Region:")
        print(
            f"  Position: ({self.settings.trigger_region.x}, {self.settings.trigger_region.y})"
        )
        print(
            f"  Size: {self.settings.trigger_region.width}x{self.settings.trigger_region.height}"
        )
        print("=" * 50)
        print(f"Trigger scan interval: {self.settings.scan.trigger_scan_interval}s")
        print(f"Tooltip scan interval: {self.settings.scan.tooltip_scan_interval}s")
        print("=" * 50)
        print("Looking for INVENTORY screen...")
        print("Press Ctrl+C in terminal to quit")
        print("=" * 50)

        # Start scanner
        self.scanner.start()

        # Run Tk mainloop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit()

    def quit(self) -> None:
        """Clean shutdown."""
        print("\nShutting down...")
        self.scanner.stop()
        self.root.quit()
        self.root.destroy()


def main() -> None:
    """Entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

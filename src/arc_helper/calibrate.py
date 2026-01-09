"""
Calibration tool for Arc Raiders Helper.
Helps configure screen regions for trigger and tooltip detection.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import ImageGrab
from PIL import ImageTk

from arc_helper.config import OverlaySettings
from arc_helper.config import ScanSettings
from arc_helper.config import Settings
from arc_helper.config import TooltipRegion
from arc_helper.config import TriggerRegion
from arc_helper.config import get_settings
from arc_helper.ocr import get_ocr_engine


class RegionSelector:
    """Widget for configuring a screen region."""

    def __init__(
        self,
        parent: ttk.Frame,
        title: str,
        initial_x: int,
        initial_y: int,
        initial_width: int,
        initial_height: int,
        color: str = "red",
    ):
        self.parent = parent
        self.title = title
        self.color = color

        # Current values
        self.x = tk.IntVar(value=initial_x)
        self.y = tk.IntVar(value=initial_y)
        self.width = tk.IntVar(value=initial_width)
        self.height = tk.IntVar(value=initial_height)

        # Overlay window for visualization
        self.overlay: tk.Toplevel | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create UI elements."""
        # Frame for this region
        frame = ttk.LabelFrame(self.parent, text=self.title, padding=10)
        frame.pack(fill="x", pady=5)

        # Grid of sliders
        sliders = [
            ("X", self.x, 0, 2500),
            ("Y", self.y, 0, 1500),
            ("Width", self.width, 20, 800),
            ("Height", self.height, 20, 300),
        ]

        for row, (label, var, min_val, max_val) in enumerate(sliders):
            ttk.Label(frame, text=label, width=6).grid(row=row, column=0, sticky="w")

            slider = ttk.Scale(
                frame,
                from_=min_val,
                to=max_val,
                variable=var,
                orient="horizontal",
                length=200,
                command=lambda _: self._on_change(),
            )
            slider.grid(row=row, column=1, sticky="ew", padx=5)

            value_label = ttk.Label(frame, textvariable=var, width=5)
            value_label.grid(row=row, column=2)

        frame.columnconfigure(1, weight=1)

    def _on_change(self) -> None:
        """Update overlay when values change."""
        if self.overlay and self.overlay.winfo_exists():
            self._update_overlay()

    def show_overlay(self) -> None:
        """Show colored rectangle on screen."""
        if self.overlay:
            self.overlay.destroy()

        self.overlay = tk.Toplevel()
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.4)
        self.overlay.overrideredirect(True)
        self.overlay.config(bg=self.color)

        self._update_overlay()

    def _update_overlay(self) -> None:
        """Update overlay position and size."""
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.geometry(
                f"{self.width.get()}x{self.height.get()}+{self.x.get()}+{self.y.get()}"
            )

    def hide_overlay(self) -> None:
        """Hide the overlay."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def get_bbox(self) -> tuple[int, int, int, int]:
        """Get region as (left, top, right, bottom)."""
        x, y = self.x.get(), self.y.get()
        return (x, y, x + self.width.get(), y + self.height.get())


class CalibrationTool:
    """Main calibration application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arc Raiders Helper - Calibration")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        # Load current settings
        self.settings = get_settings()

        # OCR engine for testing
        self.ocr = get_ocr_engine()

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Create the calibration UI."""
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Instructions
        instructions = ttk.Label(
            main_frame,
            text=(
                "Configure the screen regions for Arc Raiders Helper:\n\n"
                "1. TRIGGER region: Where 'INVENTORY' text appears\n"
                "2. TOOLTIP region: Where item names appear\n\n"
                "Use 'Show' to visualize each region on screen."
            ),
            justify="left",
        )
        instructions.pack(fill="x", pady=(0, 15))

        # Trigger region selector
        self.trigger_selector = RegionSelector(
            main_frame,
            "Trigger Region (INVENTORY text)",
            self.settings.trigger_region.x,
            self.settings.trigger_region.y,
            self.settings.trigger_region.width,
            self.settings.trigger_region.height,
            color="blue",
        )

        # Trigger buttons
        trigger_btn_frame = ttk.Frame(main_frame)
        trigger_btn_frame.pack(fill="x", pady=5)
        ttk.Button(
            trigger_btn_frame,
            text="Show Region",
            command=self.trigger_selector.show_overlay,
        ).pack(side="left", padx=2)
        ttk.Button(
            trigger_btn_frame, text="Hide", command=self.trigger_selector.hide_overlay
        ).pack(side="left", padx=2)
        ttk.Button(trigger_btn_frame, text="Test OCR", command=self._test_trigger).pack(
            side="left", padx=2
        )

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Tooltip region selector
        self.tooltip_selector = RegionSelector(
            main_frame,
            "Tooltip Region (Item name)",
            self.settings.tooltip_region.x,
            self.settings.tooltip_region.y,
            self.settings.tooltip_region.width,
            self.settings.tooltip_region.height,
            color="green",
        )

        # Tooltip buttons
        tooltip_btn_frame = ttk.Frame(main_frame)
        tooltip_btn_frame.pack(fill="x", pady=5)
        ttk.Button(
            tooltip_btn_frame,
            text="Show Region",
            command=self.tooltip_selector.show_overlay,
        ).pack(side="left", padx=2)
        ttk.Button(
            tooltip_btn_frame, text="Hide", command=self.tooltip_selector.hide_overlay
        ).pack(side="left", padx=2)
        ttk.Button(tooltip_btn_frame, text="Test OCR", command=self._test_tooltip).pack(
            side="left", padx=2
        )

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Preview area
        preview_frame = ttk.LabelFrame(main_frame, text="OCR Test Result", padding=10)
        preview_frame.pack(fill="x", pady=5)

        self.preview_label = ttk.Label(
            preview_frame, text="Click 'Test OCR' to preview"
        )
        self.preview_label.pack()

        self.result_label = ttk.Label(
            preview_frame, text="", font=("Segoe UI", 11, "bold")
        )
        self.result_label.pack(pady=5)

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(15, 0))

        ttk.Button(
            btn_frame, text="Save Configuration", command=self._save_config
        ).pack(side="left", padx=5)
        ttk.Button(
            btn_frame, text="Reset to Defaults", command=self._reset_defaults
        ).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", command=self.root.quit).pack(
            side="right", padx=5
        )

    def _test_trigger(self) -> None:
        """Test OCR on trigger region."""
        bbox = self.trigger_selector.get_bbox()

        # Capture and test
        image = ImageGrab.grab(bbox=bbox)

        # Show preview
        self._show_preview(image)

        # Test for INVENTORY
        class TempRegion:
            def __init__(self, x, y, w, h):
                self.x, self.y, self.width, self.height = x, y, w, h

            @property
            def bbox(self):
                return (self.x, self.y, self.x + self.width, self.y + self.height)

        region = TempRegion(
            self.trigger_selector.x.get(),
            self.trigger_selector.y.get(),
            self.trigger_selector.width.get(),
            self.trigger_selector.height.get(),
        )

        found = self.ocr.check_trigger(region)

        if found:
            self.result_label.config(text="✓ INVENTORY detected!", foreground="green")
        else:
            self.result_label.config(text="✗ INVENTORY not found", foreground="red")

    def _test_tooltip(self) -> None:
        """Test OCR on tooltip region."""
        bbox = self.tooltip_selector.get_bbox()

        # Capture and test
        image = ImageGrab.grab(bbox=bbox)

        # Show preview
        self._show_preview(image)

        # Extract item name
        class TempRegion:
            def __init__(self, x, y, w, h):
                self.x, self.y, self.width, self.height = x, y, w, h

            @property
            def bbox(self):
                return (self.x, self.y, self.x + self.width, self.y + self.height)

        region = TempRegion(
            self.tooltip_selector.x.get(),
            self.tooltip_selector.y.get(),
            self.tooltip_selector.width.get(),
            self.tooltip_selector.height.get(),
        )

        item_name = self.ocr.extract_item_name(region)

        if item_name:
            self.result_label.config(text=f"✓ Found: '{item_name}'", foreground="green")
        else:
            self.result_label.config(text="✗ No text detected", foreground="red")

    def _show_preview(self, image) -> None:
        """Show image preview."""
        # Resize for display
        display_width = min(350, image.width)
        ratio = display_width / image.width
        display_height = int(image.height * ratio)
        display_img = image.resize((display_width, display_height))

        # Convert for Tk
        photo = ImageTk.PhotoImage(display_img)
        self.preview_label.config(image=photo)
        self.preview_label.image = photo  # Keep reference

    def _save_config(self) -> None:
        """Save configuration to .env file."""
        # Build new settings
        settings = Settings(
            trigger_region=TriggerRegion(
                x=self.trigger_selector.x.get(),
                y=self.trigger_selector.y.get(),
                width=self.trigger_selector.width.get(),
                height=self.trigger_selector.height.get(),
            ),
            tooltip_region=TooltipRegion(
                x=self.tooltip_selector.x.get(),
                y=self.tooltip_selector.y.get(),
                width=self.tooltip_selector.width.get(),
                height=self.tooltip_selector.height.get(),
            ),
            overlay=OverlaySettings(),
            scan=ScanSettings(),
        )

        # Save to .env
        settings.save_to_env()

        messagebox.showinfo("Saved", "Configuration saved to .env file!")

    def _reset_defaults(self) -> None:
        """Reset to default values."""
        # Trigger defaults
        self.trigger_selector.x.set(50)
        self.trigger_selector.y.set(50)
        self.trigger_selector.width.set(200)
        self.trigger_selector.height.set(50)

        # Tooltip defaults
        self.tooltip_selector.x.set(500)
        self.tooltip_selector.y.set(150)
        self.tooltip_selector.width.set(400)
        self.tooltip_selector.height.set(60)

    def run(self) -> None:
        """Start the calibration tool."""
        self.root.mainloop()

        # Cleanup overlays on exit
        self.trigger_selector.hide_overlay()
        self.tooltip_selector.hide_overlay()


def main() -> None:
    """Entry point for calibration tool."""
    tool = CalibrationTool()
    tool.run()


if __name__ == "__main__":
    main()

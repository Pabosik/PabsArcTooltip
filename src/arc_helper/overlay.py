"""
Overlay UI for Arc Raiders Helper.
Displays item recommendations as a non-intrusive popup.
"""

import tkinter as tk

from .config import get_settings
from .database import Item

# Action colors for visual feedback
ACTION_COLORS: dict[str, str] = {
    "SELL": "#FFD700",  # Gold
    "RECYCLE": "#00CED1",  # Dark Turquoise
    "KEEP": "#32CD32",  # Lime Green
    "USE": "#FF69B4",  # Hot Pink
    "TRASH": "#FF4444",  # Red
    "UNKNOWN": "#888888",  # Gray
}


class OverlayWindow:
    """Transparent overlay window for showing recommendations."""

    def __init__(self, root: tk.Tk):
        """Initialize overlay as a toplevel window."""
        self.root = root
        self.settings = get_settings()

        # Create toplevel window for overlay
        self.window = tk.Toplevel(root)
        self.window.title("Arc Raiders Helper")

        # Make window transparent and always on top
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.9)
        self.window.overrideredirect(True)  # Remove window decorations

        # Start hidden
        self.window.withdraw()

        # Position
        self.overlay_x = self.settings.overlay.x
        self.overlay_y = self.settings.overlay.y

        # Setup UI
        self._setup_ui()

        # Auto-hide timer ID
        self._hide_after_id: str | None = None

    def _setup_ui(self) -> None:
        """Create the overlay UI elements."""
        # Main frame with dark background
        self.frame = tk.Frame(
            self.window,
            bg="#1a1a2e",
            padx=15,
            pady=10,
            highlightbackground="#4a4a6a",
            highlightthickness=2,
        )
        self.frame.pack()

        # Item name label
        self.name_label = tk.Label(
            self.frame,
            text="Item Name",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#1a1a2e",
        )
        self.name_label.pack(anchor="w")

        # Action label (big and colored)
        self.action_label = tk.Label(
            self.frame,
            text="ACTION",
            font=("Segoe UI", 20, "bold"),
            fg="#FFD700",
            bg="#1a1a2e",
        )
        self.action_label.pack(anchor="w", pady=(5, 0))

        # Notes label
        self.notes_label = tk.Label(
            self.frame,
            text="",
            font=("Segoe UI", 10),
            fg="#aaaaaa",
            bg="#1a1a2e",
            wraplength=250,
            justify=tk.LEFT,
        )
        self.notes_label.pack(anchor="w", pady=(5, 0))

    def show(self, item_name: str, recommendation: Item | None) -> None:
        """Show the overlay with item info."""
        # Cancel any pending hide
        if self._hide_after_id:
            self.window.after_cancel(self._hide_after_id)

        # Update content
        self.name_label.config(text=item_name)

        if recommendation:
            action_str = recommendation.action
            # Try to get color for known actions, default to white
            color = ACTION_COLORS.get(action_str.upper(), "#FFFFFF")
            self.action_label.config(text=f"→ {action_str}", fg=color)

            # Show recycle_for or keep_for based on action
            detail_text = ""
            action_upper = action_str.upper()
            if "RECYCLE" in action_upper and recommendation.recycle_for:
                detail_text = f"For: {recommendation.recycle_for}"
            elif recommendation.keep_for:
                detail_text = f"For: {recommendation.keep_for}"
            self.notes_label.config(text=detail_text)
        else:
            self.action_label.config(text="→ UNKNOWN", fg=ACTION_COLORS["UNKNOWN"])
            self.notes_label.config(text="Item not in database")

        # Position and show
        self.window.geometry(f"+{self.overlay_x}+{self.overlay_y}")
        self.window.deiconify()
        self.window.lift()

        # Auto-hide after configured time
        hide_ms = int(self.settings.overlay.display_time * 1000)
        self._hide_after_id = self.window.after(hide_ms, self.hide)

    def hide(self) -> None:
        """Hide the overlay."""
        self.window.withdraw()

    def set_position(self, x: int, y: int) -> None:
        """Update overlay position."""
        self.overlay_x = x
        self.overlay_y = y

    def is_visible(self) -> bool:
        """Check if overlay is currently visible."""
        try:
            return self.window.winfo_viewable()
        except tk.TclError:
            return False


class StatusWindow:
    """Small status indicator showing scanner state."""

    def __init__(self, root: tk.Tk):
        """Initialize status window."""
        self.root = root

        # Create toplevel for status
        self.window = tk.Toplevel(root)
        self.window.title("Arc Helper Status")
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.8)
        self.window.overrideredirect(True)

        # Position in corner
        self.window.geometry("+10+10")

        # UI
        self.frame = tk.Frame(self.window, bg="#1a1a2e", padx=8, pady=4)
        self.frame.pack()

        self.status_label = tk.Label(
            self.frame,
            text="● Scanning...",
            font=("Segoe UI", 9),
            fg="#888888",
            bg="#1a1a2e",
        )
        self.status_label.pack()

    def set_scanning(self) -> None:
        """Show scanning state."""
        self.status_label.config(text="● Scanning...", fg="#888888")

    def set_active(self) -> None:
        """Show active/inventory detected state."""
        self.status_label.config(text="● INVENTORY", fg="#32CD32")

    def set_error(self, message: str) -> None:
        """Show error state."""
        self.status_label.config(text=f"● {message}", fg="#FF4444")

    def hide(self) -> None:
        """Hide the status window."""
        self.window.withdraw()

    def show(self) -> None:
        """Show the status window."""
        self.window.deiconify()

"""
Configuration module for Arc Raiders Helper.
Uses Pydantic Settings for type-safe configuration via environment variables.
"""

import ctypes
import sys
from pathlib import Path

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


def get_app_dir() -> Path:
    """Get the application directory (handles both dev and bundled modes)."""
    if getattr(sys, "frozen", False):
        # Running as compiled executable
        return Path(sys.executable).parent
    # Running as script - go up from config.py -> arc_helper -> src -> root
    return Path(__file__).parent.parent.parent


APP_DIR = get_app_dir()


def get_screen_resolution() -> tuple[int, int]:
    """Get the primary monitor resolution."""
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def get_tesseract_path() -> str | None:
    """Find Tesseract executable - checks bundled location first."""
    # Check for bundled Tesseract
    bundled = APP_DIR / "tesseract" / "tesseract.exe"
    if bundled.exists():
        return str(bundled)

    # Check common installation paths
    common_paths = [
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    ]
    for path in common_paths:
        if path.exists():
            return str(path)

    # Return None - will use system PATH
    return None


class Region(BaseModel):
    """Base class for screen regions."""

    x: int = Field(default=0, description="Left edge X coordinate")
    y: int = Field(default=0, description="Top edge Y coordinate")
    width: int = Field(default=100, description="Region width")
    height: int = Field(default=100, description="Region height")

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """Get bounding box as (left, top, right, bottom)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class TriggerRegion(Region):
    """Region where INVENTORY text appears - menu mode."""

    model_config = SettingsConfigDict(env_prefix="TRIGGER_REGION_")

    x: int = Field(default=1450, description="Left edge of trigger region")
    y: int = Field(default=23, description="Top edge of trigger region")
    width: int = Field(default=173, description="Width of trigger region")
    height: int = Field(default=44, description="Height of trigger region")


class TriggerRegion2(Region):
    """Region where INVENTORY text appears - in-raid mode."""

    model_config = SettingsConfigDict(env_prefix="TRIGGER_REGION2_")

    x: int = Field(default=1295, description="Left edge of trigger region 2")
    y: int = Field(default=38, description="Top edge of trigger region 2")
    width: int = Field(default=173, description="Width of trigger region 2")
    height: int = Field(default=44, description="Height of trigger region 2")


class TooltipRegion(Region):
    """Region where item name appears in tooltip - used for calibration only."""

    model_config = SettingsConfigDict(env_prefix="TOOLTIP_REGION_")

    x: int = Field(default=500, description="Left edge of tooltip region")
    y: int = Field(default=150, description="Top edge of tooltip region")
    width: int = Field(default=400, description="Width of tooltip region")
    height: int = Field(default=60, description="Height of tooltip region")


class TooltipCaptureSettings(BaseSettings):
    """Settings for cursor-relative tooltip capture."""

    model_config = SettingsConfigDict(env_prefix="TOOLTIP_CAPTURE_")

    width: int = Field(default=550, description="Width of capture area around cursor")
    height: int = Field(default=550, description="Height of capture area around cursor")
    offset_x: int = Field(default=50, description="X offset from cursor")
    offset_y: int = Field(default=-500, description="Y offset from cursor")


class OverlaySettings(BaseSettings):
    """Settings for the overlay window."""

    model_config = SettingsConfigDict(env_prefix="OVERLAY_")

    x: int = Field(default=100, description="Overlay X position")
    y: int = Field(default=100, description="Overlay Y position")
    display_time: float = Field(
        default=4.0, description="How long overlay stays visible"
    )
    cooldown: float = Field(default=2.0, description="Minimum time between same item")


class ScanSettings(BaseSettings):
    """Settings for scanning intervals."""

    model_config = SettingsConfigDict(env_prefix="")

    trigger_scan_interval: float = Field(
        default=0.5, description="Seconds between trigger scans"
    )
    tooltip_scan_interval: float = Field(
        default=0.3, description="Seconds between tooltip scans"
    )


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Nested settings
    trigger_region: TriggerRegion = Field(default_factory=TriggerRegion)
    trigger_region2: TriggerRegion2 = Field(default_factory=TriggerRegion2)
    tooltip_region: TooltipRegion = Field(default_factory=TooltipRegion)
    tooltip_capture: TooltipCaptureSettings = Field(
        default_factory=TooltipCaptureSettings
    )
    overlay: OverlaySettings = Field(default_factory=OverlaySettings)
    scan: ScanSettings = Field(default_factory=ScanSettings)

    # Tesseract - auto-detect if not specified
    tesseract_path: str | None = Field(default_factory=get_tesseract_path)

    # Database in app directory
    database_path: Path = Field(default_factory=lambda: APP_DIR / "items.db")

    # Debug settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    debug_output_dir: Path = Field(default_factory=lambda: APP_DIR / "debug")
    show_capture_area: bool = Field(
        default=False, description="Show red overlay for capture area"
    )


# Singleton settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings

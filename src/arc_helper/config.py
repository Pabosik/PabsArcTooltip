"""
Configuration management using Pydantic Settings.
Loads from .env file and environment variables.
"""

from pathlib import Path

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Region(BaseSettings):
    """Screen region definition."""

    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 50

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """Return as (left, top, right, bottom) for PIL ImageGrab."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class TriggerRegion(Region):
    """Region where 'INVENTORY' text appears."""

    model_config = SettingsConfigDict(env_prefix="TRIGGER_REGION_")

    x: int = Field(default=50, description="Left edge of trigger region")
    y: int = Field(default=50, description="Top edge of trigger region")
    width: int = Field(default=200, description="Width of trigger region")
    height: int = Field(default=50, description="Height of trigger region")


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

    width: int = Field(default=500, description="Width of capture area around cursor")
    height: int = Field(default=400, description="Height of capture area around cursor")
    offset_x: int = Field(
        default=50, description="X offset from cursor (positive = right)"
    )
    offset_y: int = Field(
        default=-50, description="Y offset from cursor (positive = down)"
    )


class OverlaySettings(BaseSettings):
    """Overlay display settings."""

    model_config = SettingsConfigDict(env_prefix="OVERLAY_")

    x: int = Field(default=100, description="Overlay X position")
    y: int = Field(default=100, description="Overlay Y position")
    display_time: float = Field(
        default=4.0, description="How long overlay stays visible"
    )
    cooldown: float = Field(
        default=2.0, description="Min time between same item overlays"
    )


class ScanSettings(BaseSettings):
    """OCR scanning intervals."""

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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Nested settings
    trigger_region: TriggerRegion = Field(default_factory=TriggerRegion)
    tooltip_region: TooltipRegion = Field(
        default_factory=TooltipRegion
    )  # For calibration
    tooltip_capture: TooltipCaptureSettings = Field(
        default_factory=TooltipCaptureSettings
    )
    overlay: OverlaySettings = Field(default_factory=OverlaySettings)
    scan: ScanSettings = Field(default_factory=ScanSettings)

    # OCR settings
    tesseract_path: str | None = Field(
        default=None, description="Path to tesseract executable"
    )

    # Debug settings
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    debug_output_dir: Path = Field(
        default=Path("./debug"), description="Debug output directory"
    )
    show_capture_area: bool = Field(
        default=False, description="Show red overlay for capture area"
    )

    # Database
    database_path: Path = Field(
        default=Path("items.db"), description="SQLite database path"
    )

    @field_validator("tesseract_path", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        """Convert empty string to None."""
        if v == "":
            return None
        return v

    def save_to_env(self, path: Path | None = None) -> None:
        """Save current settings to .env file."""
        if path is None:
            path = Path(".env")

        lines = [
            "# Arc Raiders Helper Configuration",
            "",
            "# Trigger Region (INVENTORY text location)",
            f"TRIGGER_REGION_X={self.trigger_region.x}",
            f"TRIGGER_REGION_Y={self.trigger_region.y}",
            f"TRIGGER_REGION_WIDTH={self.trigger_region.width}",
            f"TRIGGER_REGION_HEIGHT={self.trigger_region.height}",
            "",
            "# Tooltip Region (Item name location)",
            f"TOOLTIP_REGION_X={self.tooltip_region.x}",
            f"TOOLTIP_REGION_Y={self.tooltip_region.y}",
            f"TOOLTIP_REGION_WIDTH={self.tooltip_region.width}",
            f"TOOLTIP_REGION_HEIGHT={self.tooltip_region.height}",
            "",
            "# Overlay Settings",
            f"OVERLAY_X={self.overlay.x}",
            f"OVERLAY_Y={self.overlay.y}",
            f"OVERLAY_DISPLAY_TIME={self.overlay.display_time}",
            f"OVERLAY_COOLDOWN={self.overlay.cooldown}",
            "",
            "# Scan Intervals",
            f"TRIGGER_SCAN_INTERVAL={self.scan.trigger_scan_interval}",
            f"TOOLTIP_SCAN_INTERVAL={self.scan.tooltip_scan_interval}",
            "",
            "# OCR Settings",
            f"TESSERACT_PATH={self.tesseract_path or ''}",
            "",
            "# Debug Settings",
            f"DEBUG_MODE={str(self.debug_mode).lower()}",
            f"DEBUG_OUTPUT_DIR={self.debug_output_dir}",
        ]

        path.write_text("\n".join(lines))


def load_settings() -> Settings:
    """Load settings from .env file and environment."""
    # Let Pydantic handle nested settings automatically
    # This ensures .env file is loaded correctly
    return Settings()


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from disk."""
    global _settings
    _settings = load_settings()
    return _settings

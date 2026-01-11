# Arc Raiders Helper

A screen overlay tool that helps you manage your inventory in Arc Raiders by automatically detecting items and displaying recommended actions (keep, recycle, etc.).

---

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [First Run Setup](#first-run-setup)
- [Calibration Tool](#calibration-tool)
- [Configuration](#configuration)
- [Item Database](#item-database)
- [Building from Source](#building-from-source)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## How It Works

The tool uses a two-phase detection system:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Phase 1: TRIGGER DETECTION (low frequency, every 500ms)        │
│  ─────────────────────────────────────────────────────────      │
│  Scans specific screen regions looking for "INVENTORY" text     │
│  This indicates that the inventory is open                      │
│                                                                 │
│                          │                                      │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │  INVENTORY detected?  │                          │
│              └───────────┬───────────┘                          │
│                    YES   │                                      │
│                          ▼                                      │
│                                                                 │
│  Phase 2: TOOLTIP DETECTION (high frequency, every 300ms)       │
│  ─────────────────────────────────────────────────────────      │
│  Captures area around cursor → Finds tooltip → Extracts         │
│  item name via OCR → Looks up in database → Shows overlay       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detection Details

1. **Trigger Detection**: Continuously scans two screen regions (menu mode and in-raid mode) looking for the word "INVENTORY". This indicates that you have opened your inventory in the game.

2. **Tooltip Detection**: Once the inventory is detected, the tool starts scanning the area around your mouse cursor for item tooltips. When you hover over an item, it:
   - Captures a region around your cursor
   - Identifies the tooltip by its cream-colored background
   - Filters out colored tags (rarity, item type)
   - Extracts the item name using OCR

3. **Overlay Display**: If the item is found in the database, an overlay appears showing the recommended action (e.g., "KEEP - needed for crafting" or "RECYCLE - not useful").

---

## Features

- **Automatic detection** - No hotkey needed, detects when inventory is open
- **Cursor-following** - Finds tooltips wherever they appear on screen
- **Two-phase scanning** - Minimizes CPU usage by only running tooltip OCR when inventory is open
- **Resolution profiles** - Pre-configured settings for common screen resolutions
- **Calibration tool** - GUI tool to configure screen regions for any resolution
- **OCR-based** - Reads item names directly from screen using Tesseract
- **SQLite database** - Load items from CSV files
- **Configurable** - All settings stored in `.env` file
- **Debug mode** - Saves intermediate images for troubleshooting OCR issues
- **Bundled Tesseract** - Pre-built releases include Tesseract (no separate install needed)

---

## Requirements

### To Run Pre-built Release

- Windows 10/11
- Arc Raiders running in **borderless windowed** or **windowed** mode (not fullscreen)

### To Run from Source

- Windows 10/11
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed

### To Build from Source

- All of the above, plus:
- PyInstaller (`uv sync --all-extras`)

---

## Installation

### Option 1: Pre-built Release (Recommended)

1. Download the latest release from the [Releases](https://github.com/yourusername/arc-raiders-helper/releases) page
2. Extract the zip file to a folder of your choice
3. Run `ArcRaidersHelper.exe`

The release includes all dependencies, including Tesseract OCR.

### Option 2: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/arc-raiders-helper.git
   cd arc-raiders-helper
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install Tesseract OCR:
   - Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to `C:\Program Files\Tesseract-OCR\`
   - Or set `TESSERACT_PATH` in `.env` to your installation path

4. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   uv run arc-helper
   ```

---

## First Run Setup

On first launch, the application will:

1. **Detect your screen resolution**
2. **Check for a pre-configured profile** for your resolution
3. **If found**: Automatically apply the settings and start
4. **If not found**: Display a message asking you to run the Calibration tool

### Supported Resolutions

The following resolutions have pre-configured profiles:

| Resolution | Aspect Ratio | Status |
|------------|--------------|--------|
| 3440x1440 | 21:9 (Ultrawide QHD) | ✅ Configured |
| 2560x1440 | 16:9 (QHD) | ⚠️ Needs calibration |
| 1920x1080 | 16:9 (Full HD) | ⚠️ Needs calibration |
| 3840x2160 | 16:9 (4K UHD) | ⚠️ Needs calibration |
| 2560x1080 | 21:9 (Ultrawide FHD) | ⚠️ Needs calibration |

If your resolution isn't listed or shows "Needs calibration", run the Calibration tool to configure it.

---

## Calibration Tool

The Calibration tool (`Calibrate.exe` or `uv run arc-calibrate`) provides a GUI to configure the screen regions for your specific setup.

### When to Calibrate

- First time using the app with an unsupported resolution
- After changing your screen resolution
- After changing Arc Raiders display settings
- If item detection isn't working correctly

### How to Calibrate

1. **Launch Arc Raiders** and open your inventory (in the menu)
2. **Run the Calibration tool**:
   - Pre-built: Run `Calibrate.exe`
   - From source: Run `uv run arc-calibrate`

3. **Configure Trigger Region 1 (Menu Mode)**:
   - Click "Show Region" to see the yellow rectangle on screen
   - Adjust the sliders until it covers the "INVENTORY" text
   - Click "Test OCR" - should show "✓ INVENTORY detected!"
   - Click "Hide"

4. **Configure Trigger Region 2 (In-Raid Mode)**:
   - Open your inventory while in a raid
   - Repeat the same process with the blue rectangle
   - The "INVENTORY" text may be in a different position in-raid

5. **Configure Tooltip Region** (optional, for testing):
   - Hover over an item in your inventory
   - Adjust the green rectangle to cover the item name area
   - Click "Test OCR" to verify item names are detected

6. **Click "Save Configuration"** to save to `.env` file

### Database Management

The Calibration tool also includes database management features:

- **Load CSV...** - Import items from a CSV file (replaces existing items)
- **View Items** - See all items currently in the database
- **Clear Database** - Remove all items from the database

This makes it easy to update your item database without running any commands.

---

## Configuration

All configuration is stored in the `.env` file in the application directory. You can edit this file with any text editor.

### Configuration Options

```env
# =============================================================================
# TRIGGER REGIONS - Where "INVENTORY" text appears
# =============================================================================

# Region 1 - Menu mode
TRIGGER_REGION_X=1450
TRIGGER_REGION_Y=23
TRIGGER_REGION_WIDTH=173
TRIGGER_REGION_HEIGHT=44

# Region 2 - In-raid mode
TRIGGER_REGION2_X=1295
TRIGGER_REGION2_Y=38
TRIGGER_REGION2_WIDTH=173
TRIGGER_REGION2_HEIGHT=44

# =============================================================================
# TOOLTIP CAPTURE - Area captured around cursor to find tooltip
# =============================================================================

TOOLTIP_CAPTURE_WIDTH=550
TOOLTIP_CAPTURE_HEIGHT=550
TOOLTIP_CAPTURE_OFFSET_X=50      # Horizontal offset from cursor
TOOLTIP_CAPTURE_OFFSET_Y=-500    # Vertical offset from cursor (negative = above)

# =============================================================================
# OVERLAY SETTINGS - How the recommendation overlay appears
# =============================================================================

OVERLAY_X=100                    # Overlay X position on screen
OVERLAY_Y=100                    # Overlay Y position on screen
OVERLAY_DISPLAY_TIME=4.0         # How long the overlay stays visible (seconds)
OVERLAY_COOLDOWN=2.0             # Minimum time between showing same item (seconds)

# =============================================================================
# SCANNING SETTINGS - How often the app scans the screen
# =============================================================================

TRIGGER_SCAN_INTERVAL=0.5        # Seconds between trigger scans
TOOLTIP_SCAN_INTERVAL=0.3        # Seconds between tooltip scans

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

DEBUG_MODE=false                 # Enable to save debug images and logs
SHOW_CAPTURE_AREA=false          # Show red rectangle around capture area
```

### Debug Mode

Enable debug mode to troubleshoot OCR issues:

1. Set `DEBUG_MODE=true` in `.env`
2. Run the application
3. Check the `debug/` folder for:
   - `trigger_raw.png` / `trigger_processed.png` - Trigger region captures
   - `tooltip_capture_raw.png` / `tooltip_capture_processed.png` - Tooltip captures
   - `tooltip_mask.png`, `tooltip_cropped.png`, etc. - OCR preprocessing steps
   - `arc_helper.log` - Detailed log file with all operations

---

## Item Database

Items are stored in `items.db` (SQLite database). You can import items from a CSV file.## Item Database

Items are stored in `items.db` (SQLite database). You can manage the database using the Calibration tool or by editing the CSV file directly.

### CSV Format

Create or edit `items.csv` with the following columns:
```csv
name,action,recycle_for,keep_for
Advanced Arc Powercell,Keep,2x ARC Powercell,Medical Lab: Surge Shield Recharger
ARC CIRCUITRY,RECYCLE,ARC Alloy,
BASIC ELECTRONICS,RECYCLE,Basic components,
MEDICAL SUPPLIES,USE,,Emergency healing
```

| Column | Description |
|--------|-------------|
| `name` | Item name as it appears in-game (case-insensitive matching) |
| `action` | Recommended action: `KEEP`, `RECYCLE`, `SELL`, `USE`, `TRASH`, or any custom text |
| `recycle_for` | What you get when recycling (shown when action is RECYCLE) |
| `keep_for` | Why to keep it (shown when action is KEEP or USE) |

### Managing the Database

The easiest way to update the item database is through the **Calibration tool**:

1. Edit `items.csv` in Excel, Google Sheets, or any text editor
2. Run `Calibrate.exe` (or `uv run arc-calibrate`)
3. In the "Item Database" section at the bottom:
   - Click **"Load CSV..."** to import your updated CSV file
   - Click **"View Items"** to see all items currently in the database
   - Click **"Clear Database"** to remove all items and start fresh

The database is automatically created on first run. Loading a CSV file will replace all existing items.

### Tips for the CSV File

- You can use Excel or Google Sheets to edit the CSV - just make sure to save as CSV format
- Item names are matched case-insensitively (e.g., "Arc Circuitry" will match "ARC CIRCUITRY")
- Leave `recycle_for` or `keep_for` empty if not applicable
- The `action` field can be any text - it will be displayed as-is on the overlay

---

## Building from Source

### Prerequisites

1. Python 3.11 or higher
2. uv package manager
3. Tesseract OCR installed at `C:\Program Files\Tesseract-OCR\`

### Build Steps

1. Clone the repository and install dev dependencies:
   ```bash
   git clone https://github.com/yourusername/arc-raiders-helper.git
   cd arc-raiders-helper
   uv sync --all-extras
   ```

2. Run the build script:
   ```bash
   uv run python build.py
   ```

3. Find the output in `dist/ArcRaidersHelper/`

### Build Output

```
dist/ArcRaidersHelper/
├── ArcRaidersHelper.exe    # Main application (shows console window)
├── Calibrate.exe           # Calibration tool (GUI only)
├── _internal/              # Python dependencies (don't modify)
├── tesseract/              # Bundled Tesseract OCR
│   ├── tesseract.exe
│   ├── *.dll
│   └── tessdata/
│       └── eng.traineddata
├── .env                    # Configuration file (edit this)
├── .env.example            # Configuration reference
├── resolutions.json        # Pre-configured resolution profiles
├── sample_items.csv        # Example item database
└── README.md               # This file
```

---

## Troubleshooting

### "INVENTORY not detected"

- Make sure Arc Raiders is running in **borderless windowed** or **windowed** mode (not exclusive fullscreen)
- Run the Calibration tool to verify the trigger region covers the "INVENTORY" text exactly
- Enable debug mode and check `debug/trigger_processed.png` to see what the OCR is seeing

### "Item not found in database"

- Check that the item name in your CSV matches exactly how it appears in-game (case-sensitive, typically ALL CAPS)
- Enable debug mode and check the logs to see what item name was extracted
- The OCR might be misreading characters - check `debug/tooltip_capture_processed.png`

### "OCR is reading incorrect text"

- The tooltip must have a cream/beige background for proper detection
- Colored tags (rarity, item type) should be automatically filtered out
- Run the Calibration tool and use "Test OCR" on the tooltip region
- Enable debug mode and examine the preprocessing images in `debug/`

### "Application won't start"

- Check that the `.env` file exists (copy from `.env.example` if missing)
- Make sure the `.env` file has valid values (no syntax errors)
- Check the console window for error messages
- If debug mode was enabled, check `arc_helper.log` for details

### "High CPU usage"

Increase the scan intervals in `.env`:
```env
TRIGGER_SCAN_INTERVAL=1.0
TOOLTIP_SCAN_INTERVAL=0.5
```

### "Tesseract not found" (when running from source)

1. Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
2. Either add to system PATH, or set in `.env`:
   ```env
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```
3. Verify installation: `tesseract --version`

---

## Contributing

Contributions are welcome! Here's how you can help:

### Resolution Profiles

If you calibrate the app for a new resolution, please submit the values! This helps other users with the same resolution.

1. Run the Calibration tool and find working values for your resolution
2. Open `resolutions.json` and add your resolution's profile
3. Submit a pull request

### Item Database

Help build a comprehensive item database:

1. Create or update item entries in CSV format
2. Test that the items are detected correctly
3. Submit your CSV additions

### Bug Reports

When reporting issues, please include:

- Your screen resolution
- Debug images from the `debug/` folder (if applicable)
- The `arc_helper.log` file (enable debug mode first)
- Steps to reproduce the issue

---

## Project Structure

```
arc-raiders-helper/
├── pyproject.toml              # Package configuration
├── build.py                    # Build script for PyInstaller
├── ArcRaidersHelper.spec       # PyInstaller spec file
├── .env.example                # Example configuration
├── sample_items.csv            # Sample item data
├── README.md                   # This file
├── src/arc_helper/
│   ├── __init__.py
│   ├── config.py               # Settings and logging setup
│   ├── logging_config.py       # Logging configuration
│   ├── database.py             # SQLite database and CSV import
│   ├── ocr.py                  # Screen capture and OCR
│   ├── overlay.py              # Tkinter overlay window
│   ├── resolution_profiles.py  # Resolution-based configuration
│   ├── resolutions.json        # Pre-configured resolution profiles
│   ├── main.py                 # Main application entry point
│   └── calibrate.py            # Calibration tool
└── test_*.py                   # Test scripts
```

---

## License

MIT License - Free to use and modify.

---

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- [PyInstaller](https://pyinstaller.org/) for executable packaging
- [Pydantic](https://docs.pydantic.dev/) for configuration management
- Arc Raiders community for item information

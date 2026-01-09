# Arc Raiders Helper

A lightweight overlay tool that helps you decide what to do with items in Arc Raiders. The tool automatically detects when your inventory is open and shows recommendations for items you hover over.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Low-frequency scan (every 500ms)                           │
│  Looking for "INVENTORY" text on screen                     │
│                          │                                  │
│                          ▼                                  │
│              ┌───────────────────────┐                      │
│              │  INVENTORY detected?  │                      │
│              └───────────┬───────────┘                      │
│                          │ YES                              │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  High-frequency scan (every 300ms)                   │   │
│  │  Capture area around cursor → Find tooltip → Extract │   │
│  │  item name                                           │   │
│  │                          │                           │   │
│  │                          ▼                           │   │
│  │              ┌───────────────────────┐               │   │
│  │              │  Look up in database  │               │   │
│  │              └───────────┬───────────┘               │   │
│  │                          │                           │   │
│  │                          ▼                           │   │
│  │              ┌───────────────────────┐               │   │
│  │              │  Show overlay with    │               │   │
│  │              │  recommendation       │               │   │
│  │              └───────────────────────┘               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

The tooltip in Arc Raiders follows your cursor, so the tool captures an area around your cursor position and uses OCR to find and extract the item name from the tooltip.

## Features

- **Automatic detection** - No hotkey needed, detects when inventory is open
- **Cursor-following** - Finds tooltips wherever they appear on screen
- **OCR-based** - Reads item names directly from screen
- **SQLite database** - Load items from CSV files
- **Pydantic configuration** - Type-safe settings via `.env` file
- **Low CPU usage** - Two-phase scanning minimizes unnecessary work

## Requirements

- Windows 10/11
- Python 3.11+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Installation

### 1. Install Tesseract OCR

Download from: https://github.com/UB-Mannheim/tesseract/wiki

During installation, note the path (typically `C:\Program Files\Tesseract-OCR`).

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo>
cd arc-raiders-helper

# Copy example environment file
cp .env.example .env

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 3. Configure Tesseract Path (if needed)

Edit `.env` and set:
```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 4. Load Your Item Database

Prepare a CSV file with columns: `name`, `action`, `recycle_for`, `keep_for`

```csv
name,action,recycle_for,keep_for
Scrap Metal,RECYCLE,Electronic components,
Gold Watch,SELL,,
Medical Kit,KEEP,,Essential healing item
```

Load it into the database:

```python
from arc_helper.database import load_csv_to_database

load_csv_to_database("my_items.csv")
```

Or use the sample file:

```python
from arc_helper.database import load_csv_to_database

load_csv_to_database("items.csv")
```

## Usage

### Step 1: Calibrate Screen Regions

First, configure where the tool should look on your screen:

```bash
uv run arc-calibrate
```

1. Open Arc Raiders and go to your inventory
2. Position the **blue box** over the "INVENTORY" text
3. Position the **green box** over where item names appear in tooltips
4. Click "Test OCR" for each to verify detection works
5. Click "Save Configuration"

### Step 2: Run the Helper

```bash
uv run arc-helper
```

The tool will:
1. Continuously scan for "INVENTORY" text (low frequency)
2. When inventory is open, scan for item names (higher frequency)
3. Show an overlay with the recommendation

## Database Schema

The database has 4 columns:

| Column | Description |
|--------|-------------|
| `name` | Item name (primary key, case-insensitive) |
| `action` | One of: `SELL`, `RECYCLE`, `KEEP`, `USE`, `TRASH` |
| `recycle_for` | What you get when recycling (shown for RECYCLE items) |
| `keep_for` | Why to keep it (shown for KEEP/USE items) |

### Loading Data

```python
from arc_helper.database import Database, load_csv_to_database

# Simple: load CSV (clears existing data)
load_csv_to_database("items.csv")

# Or: append to existing data
load_csv_to_database("more_items.csv", clear_existing=False)

# Or: use Database class directly
db = Database()
db.load_csv("items.csv", clear_existing=True)
print(f"Loaded {db.count()} items")
```

## Configuration

All settings are in `.env`:

```env
# Trigger region (where INVENTORY text appears - fixed position)
TRIGGER_REGION_X=50
TRIGGER_REGION_Y=50
TRIGGER_REGION_WIDTH=200
TRIGGER_REGION_HEIGHT=50

# Tooltip capture (area captured around cursor to find tooltip)
TOOLTIP_CAPTURE_WIDTH=500
TOOLTIP_CAPTURE_HEIGHT=400
TOOLTIP_CAPTURE_OFFSET_X=50    # Start 50px right of cursor
TOOLTIP_CAPTURE_OFFSET_Y=-50   # Start 50px above cursor

# Overlay settings
OVERLAY_X=100
OVERLAY_Y=100
OVERLAY_DISPLAY_TIME=4.0
OVERLAY_COOLDOWN=2.0

# Scan intervals (seconds)
TRIGGER_SCAN_INTERVAL=0.5
TOOLTIP_SCAN_INTERVAL=0.3

# Tesseract path (leave empty to use PATH)
TESSERACT_PATH=

# Debug mode
DEBUG_MODE=false
```

## Troubleshooting

### "INVENTORY not detected"

1. Run `uv run arc-calibrate`
2. Adjust the blue trigger region to exactly cover the INVENTORY text
3. Click "Test OCR" - should show "✓ INVENTORY detected!"

### "Item name not reading correctly"

1. Run `uv run arc-calibrate`
2. Adjust the green tooltip region to cover ONLY the item name
3. Exclude category tags, icons, and description text
4. Click "Test OCR" to verify

### "Tesseract not found"

1. Install Tesseract from the link above
2. Add to PATH, or set `TESSERACT_PATH` in `.env`
3. Verify with: `tesseract --version`

### High CPU Usage

Increase scan intervals in `.env`:
```env
TRIGGER_SCAN_INTERVAL=1.0
TOOLTIP_SCAN_INTERVAL=0.5
```

## Project Structure

```
arc-raiders-helper/
├── pyproject.toml           # Package config (uv/pip)
├── .env.example             # Example configuration
├── .env                     # Your configuration (create this)
├── items.csv         # Sample item data
├── items.db                 # SQLite database (created on first run)
└── src/arc_helper/
    ├── __init__.py
    ├── config.py            # Pydantic settings
    ├── database.py          # SQLite + CSV loading
    ├── ocr.py               # Screen capture & OCR
    ├── overlay.py           # Tkinter overlay UI
    ├── main.py              # Main application
    └── calibrate.py         # Calibration tool
```

## License

Free to use and modify for personal use.

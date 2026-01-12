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

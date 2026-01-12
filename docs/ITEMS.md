## Item Database

Items are stored in `items.db` (SQLite database). You can manage the database using the [Calibration tool](CALIBRATION.md) or by editing the CSV file directly.

### CSV Format

Edit `items.csv` with the following columns:
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

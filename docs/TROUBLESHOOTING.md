## Troubleshooting

Here are some common errors you may experience and how to deal with them.

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

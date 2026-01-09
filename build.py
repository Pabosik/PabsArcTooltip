"""Build script to create standalone executable."""

import shutil
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
OUTPUT = DIST / "ArcRaidersHelper"
TESSERACT_SRC = Path(r"C:\Program Files\Tesseract-OCR")


def build():
    """Build the executable."""

    # Clean previous builds
    if DIST.exists():
        shutil.rmtree(DIST)
    if BUILD.exists():
        shutil.rmtree(BUILD)

    # Build main app using spec file
    PyInstaller.__main__.run(
        [
            "ArcRaidersHelper.spec",
            "--clean",
        ]
    )

    # Build calibration tool
    PyInstaller.__main__.run(
        [
            "src/arc_helper/calibrate.py",
            "--name=Calibrate",
            "--onedir",
            "--windowed",
            "--distpath",
            str(DIST),
            "--clean",
        ]
    )

    # Move calibrate exe to main folder
    calibrate_dir = DIST / "Calibrate"
    if calibrate_dir.exists():
        calibrate_exe = calibrate_dir / "Calibrate.exe"
        if calibrate_exe.exists():
            shutil.copy(calibrate_exe, OUTPUT / "Calibrate.exe")
        shutil.rmtree(calibrate_dir)

    # Copy user-editable files
    shutil.copy(ROOT / ".env.example", OUTPUT / ".env.example")
    shutil.copy(ROOT / ".env.example", OUTPUT / ".env")
    shutil.copy(ROOT / "sample_items.csv", OUTPUT / "sample_items.csv")
    shutil.copy(ROOT / "README.md", OUTPUT / "README.md")

    # Bundle Tesseract
    tesseract_dest = OUTPUT / "tesseract"
    if TESSERACT_SRC.exists():
        print(f"Bundling Tesseract from {TESSERACT_SRC}...")

        tesseract_dest.mkdir(exist_ok=True)

        for file in TESSERACT_SRC.glob("*.exe"):
            shutil.copy(file, tesseract_dest)
        for file in TESSERACT_SRC.glob("*.dll"):
            shutil.copy(file, tesseract_dest)

        tessdata_dest = tesseract_dest / "tessdata"
        tessdata_dest.mkdir(exist_ok=True)
        tessdata_src = TESSERACT_SRC / "tessdata"

        for filename in ["eng.traineddata", "osd.traineddata"]:
            src = tessdata_src / filename
            if src.exists():
                shutil.copy(src, tessdata_dest)

        print("✓ Tesseract bundled")
    else:
        print(f"⚠ Tesseract not found at {TESSERACT_SRC}")

    print("\n" + "=" * 50)
    print("✓ Build complete!")
    print("=" * 50)
    print(f"\nOutput folder: {OUTPUT}")

    total_size = sum(f.stat().st_size for f in OUTPUT.rglob("*") if f.is_file())
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build()

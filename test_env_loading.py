"""Quick test to verify .env file is loading correctly."""

from src.arc_helper.config import load_settings

if __name__ == "__main__":
    print("Testing .env file loading...")
    print("=" * 50)

    settings = load_settings()

    print("Trigger Region:")
    print(f"  X: {settings.trigger_region.x} (expected: 1450)")
    print(f"  Y: {settings.trigger_region.y} (expected: 23)")
    print(f"  Width: {settings.trigger_region.width} (expected: 173)")
    print(f"  Height: {settings.trigger_region.height} (expected: 44)")
    print()

    print(f"Debug Mode: {settings.debug_mode} (expected: False)")
    print(f"Scan Interval: {settings.scan.trigger_scan_interval} (expected: 0.5)")
    print()

    if settings.trigger_region.x == 1450 and settings.trigger_region.y == 23:
        print("✓ SUCCESS: .env file loaded correctly!")
    else:
        print("✗ FAIL: .env file not loaded, using defaults")
        print("  Make sure you're running from the project root directory")

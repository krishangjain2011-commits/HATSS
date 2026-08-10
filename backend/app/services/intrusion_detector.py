"""Intrusion detection and logging."""

import time
from pathlib import Path
from datetime import datetime

# Configuration
INTRUSION_DIR = Path("data/intruder_snaps")
INTRUSION_DIR.mkdir(parents=True, exist_ok=True)
ALERT_COOLDOWN = 8  # seconds between intrusion captures

last_alert_time = 0


def should_capture_intrusion() -> bool:
    """Check if enough time has passed for another capture."""
    global last_alert_time
    
    current_time = time.time()
    if current_time - last_alert_time > ALERT_COOLDOWN:
        last_alert_time = current_time
        return True
    return False


def save_intrusion_image(image_data: bytes, timestamp: int | None = None) -> str | None:
    """Save intrusion image to disk."""
    try:
        if timestamp is None:
            timestamp = int(time.time())
        
        filename = f"{timestamp}.jpg"
        filepath = INTRUSION_DIR / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filename
    except Exception as e:
        print(f"❌ Failed to save intrusion image: {e}")
        return None


def get_intrusion_images(limit: int = 6) -> list[str]:
    """Get list of recent intrusion images."""
    try:
        images = sorted(
            [f.name for f in INTRUSION_DIR.glob("*.jpg")],
            reverse=True
        )
        return images[:limit]
    except Exception as e:
        print(f"⚠️  Error listing intrusion images: {e}")
        return []


def get_intrusion_count() -> int:
    """Get total intrusion count."""
    try:
        return len(list(INTRUSION_DIR.glob("*.jpg")))
    except Exception as e:
        print(f"⚠️  Error counting intrusions: {e}")
        return 0


def get_intrusion_image_path(filename: str) -> Path | None:
    """Get full path to intrusion image."""
    filepath = INTRUSION_DIR / filename
    if filepath.exists():
        return filepath
    return None

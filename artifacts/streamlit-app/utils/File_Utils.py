import os
import uuid
from pathlib import Path

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file bytes to disk, returning the path."""
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    path = UPLOADS_DIR / safe_name
    path.write_bytes(file_bytes)
    return str(path)


def get_uploads_dir() -> Path:
    return UPLOADS_DIR


def get_reports_dir() -> Path:
    return REPORTS_DIR


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.1f} MB"
    return f"{size_bytes / 1024 ** 3:.1f} GB"

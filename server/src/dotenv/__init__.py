"""Lightweight fallback for python-dotenv used in tests."""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import os


def load_dotenv(dotenv_path: Optional[Path] = None) -> bool:
    """Minimal load_dotenv implementation that supports key=value pairs."""
    if dotenv_path is None:
        return False

    path = Path(dotenv_path)
    if not path.exists():
        return False

    loaded = False
    for line in path.read_text().splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())
        loaded = True
    return loaded

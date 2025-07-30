import os
import re
import difflib
import sys
from deefuse.config import DURATION_TOLERANCE_SEC

# ── REGEX FOR PARSING ───────────────────────────────────────────────────
VERSION_RX = re.compile(
    r"\s*(?:-|–)?\s*(original mix|extended mix|radio edit|edit|mix|remaster(?:ed)?|"
    r"version|clean|explicit|intro|outro|interlude)\s*$", re.I
)

# ── DURATION & FILENAME PARSING ──────────────────────────────────────────
def format_duration(seconds: float) -> str:
    """Converts seconds into a MM:SS string format."""
    try:
        s = int(float(seconds))
        return f"{s//60}:{s%60:02d}"
    except (ValueError, TypeError):
        return str(seconds)

def is_duration_close(duration_a: float, duration_b: float) -> bool:
    """Checks if two durations are within the configured tolerance."""
    return abs(duration_a - duration_b) <= DURATION_TOLERANCE_SEC

def parse_track_from_filename(filename: str) -> str:
    """Extracts the track title from a 'Artist - Title' formatted filename."""
    stem, _ = os.path.splitext(filename)
    parts = stem.split(" - ", 1)
    return parts[1].strip() if len(parts) == 2 else stem.strip()

# ── STRING NORMALIZATION FOR MATCHING ────────────────────────────────────
def normalize_strict(s: str) -> str:
    """A strict normalization for auto-matching."""
    s = s.lower().replace("_", "'")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\bthe\b", "", s)
    return re.sub(r"\s+", " ", s).strip()

def clean_title_strict(title: str) -> str:
    """Strictly cleans a title by removing track numbers and version info."""
    title = re.sub(r"^\d+\s*[-._]*\s*", "", title)
    title = re.sub(r"[\[\(].*?[\]\)]", "", title)
    return title.replace("_", "'").strip()

def normalize_relaxed_artist(artist: str) -> str:
    """A more relaxed normalization for artist names."""
    return re.sub(r"\s+", " ", artist.replace("&", "and")).strip()

def normalize_relaxed_title(title: str) -> str:
    """Relaxes a title by removing track numbers and common version tags."""
    title = re.sub(r"^[0-9]+\s*[.\-]?\s*", "", title)
    title = re.sub(r"[\[\(].*?[\]\)]", "", title)
    title = VERSION_RX.sub("", title)
    return re.sub(r"\s+", " ", title.replace("_", "'")).strip()

def get_string_ratio(a: str, b: str) -> float:
    """Calculates the similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, a, b).ratio()


def asset_path(relative: str) -> str:
    """Return absolute path to resource, works for dev and PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, relative)

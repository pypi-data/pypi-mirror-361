import csv
import os
from typing import List, Tuple
from .config import SKIPPED_CSV, MATCHED_CSV, SKIP_HDR, MATCH_HDR

def _ensure_header(file_path: str, header: List[str]):
    """Creates a CSV file with a header if it doesn't exist."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)


def load_skipped() -> Tuple[List[List[str]], List[str]]:
    """Loads and sorts all rows from the skipped tracks CSV."""
    _ensure_header(SKIPPED_CSV, SKIP_HDR)
    with open(SKIPPED_CSV, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    data.sort(key=lambda r: r[1].lower())  # Sort by artist name
    return data, header


def log_match(local_data: List[str], deezer_data: List[str]):
    """Appends a successfully matched track to the matched CSV."""
    _ensure_header(MATCHED_CSV, MATCH_HDR)
    with open(MATCHED_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(local_data + deezer_data)


def log_skip(row: List[str]):
    """Appends a track to the skipped CSV."""
    _ensure_header(SKIPPED_CSV, SKIP_HDR)
    with open(SKIPPED_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)


def remove_from_skipped(local_row_to_remove: List[str]):
    """Removes a track from the skipped CSV, usually after it has been matched."""
    try:
        with open(SKIPPED_CSV, 'r', newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))

        header, data = rows[0], rows[1:]

        # Keep rows that DON'T match the first 3 columns (Track, Artist, Album)
        updated_data = [
            r for r in data if r[:3] != local_row_to_remove[:3]
        ]

        with open(SKIPPED_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(updated_data)

    except FileNotFoundError:
        # If the file doesn't exist, there's nothing to remove.
        pass
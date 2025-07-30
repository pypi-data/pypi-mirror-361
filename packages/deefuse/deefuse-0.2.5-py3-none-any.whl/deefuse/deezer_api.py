import requests
from typing import List, Dict, Any, Optional, Tuple
from .config import DEEZER_API_URL
from .utils import (
    is_duration_close, normalize_strict, clean_title_strict,
    normalize_relaxed_artist, normalize_relaxed_title, get_string_ratio,
    format_duration
)


def search_strict_match(local_meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Performs a strict search on Deezer for automated matching.

    Args:
        local_meta: A dict with 'artist', 'track', and 'dur_raw'.

    Returns:
        A dictionary with Deezer track info if a confident match is found, otherwise None.
    """
    query = f"{local_meta['artist']} {clean_title_strict(local_meta['track'])}"
    try:
        response = requests.get(DEEZER_API_URL, params={"q": query}, timeout=10)
        response.raise_for_status()
        results = response.json().get("data", [])

        local_track_norm = normalize_strict(local_meta["track"])
        local_artist_norm = normalize_strict(local_meta["artist"])

        for item in results:
            deezer_track_norm = normalize_strict(item["title"])
            deezer_artist_norm = normalize_strict(item["artist"]["name"])

            if (local_track_norm in deezer_track_norm or deezer_track_norm in local_track_norm) and \
                    local_artist_norm in deezer_artist_norm and \
                    is_duration_close(local_meta["dur_raw"], item["duration"]):
                return {
                    "track": item["title"],
                    "artist": item["artist"]["name"],
                    "album": item["album"]["title"],
                    "duration": item["duration"],
                    "url": item["link"]
                }
    except requests.RequestException:
        pass  # Ignore network errors during auto-scan
    return None


def search_relaxed_match(artist: str, track: str) -> Tuple[List, List]:
    """
    Performs a relaxed search, intended for manual user queries.
    Raises an exception on network/API errors.
    """

    def fetch_results(query: str) -> List[Dict]:
        response = requests.get(DEEZER_API_URL, params={"q": query}, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])

    # Fetch initial results with a combined query
    results = fetch_results(f"{normalize_relaxed_artist(artist)} {normalize_relaxed_title(track)}")
    # If no results, try searching just by track title as a fallback
    if not results:
        results = fetch_results(normalize_relaxed_title(track))

    # Process results into a more usable format
    deezer_full_data = []
    for item in results:
        deezer_full_data.append([
            item["artist"]["name"], item["title"], item["album"]["title"],
            item["duration"], item["link"]
        ])

    # Filter results based on similarity scoring
    target_artist = normalize_relaxed_artist(artist).lower()
    target_track = normalize_relaxed_title(track).lower()

    filtered_data = []
    for row in deezer_full_data:
        res_artist = normalize_relaxed_artist(row[0]).lower()
        res_track = normalize_relaxed_title(row[1]).lower()

        artist_ok = get_string_ratio(res_artist, target_artist) > 0.55 or \
                    target_artist in res_artist or res_artist in target_artist
        track_ok = get_string_ratio(res_track, target_track) > 0.50 or \
                   target_track in res_track or res_track in target_track

        if artist_ok and track_ok:
            filtered_data.append(row)

    # If filtering removed all results, return the original unfiltered list
    final_data = filtered_data if filtered_data else deezer_full_data

    # Format for display in the Treeview
    display_rows = [[r[1], r[0], r[2], format_duration(r[3])] for r in final_data]

    return final_data, display_rows
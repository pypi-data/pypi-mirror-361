# ── FILE & PATHS ────────────────────────────────────────────────────────
SKIPPED_CSV = "skipped_tracks.csv"
MATCHED_CSV = "matched_tracks.csv"
DOWNLOAD_PATH = None  # None ⇒ uses the default deemix download folder

# ── DEEMIX & API SETTINGS ───────────────────────────────────────────────
DEEMIX_CLI = "deemix"
BITRATES_PREFER = ["flac", "320"]  # try FLAC first, then 320-kbps MP3
DEEZER_API_URL = "https://api.deezer.com/search"

# ── SCANNING & MATCHING ─────────────────────────────────────────────────
SUPPORTED_EXTENSIONS = [".flac", ".mp3", ".m4a"]
DURATION_TOLERANCE_SEC = 10

# ── CSV HEADERS ─────────────────────────────────────────────────────────
SKIP_HDR = ["Track", "Artist", "Album", "Duration"]
MATCH_HDR = [
    "Local Track", "Local Artist", "Local Album", "Local Duration",
    "Deezer Track", "Deezer Artist", "Deezer Album", "Deezer Duration",
    "Deezer URL"
]
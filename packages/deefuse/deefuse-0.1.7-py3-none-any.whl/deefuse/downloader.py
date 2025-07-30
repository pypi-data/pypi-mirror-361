import subprocess
from .config import DEEMIX_CLI, DOWNLOAD_PATH, BITRATES_PREFER

def _run_deemix_command(url: str, bitrate: str) -> bool:
    """Constructs and runs a single deemix download command."""
    command = [DEEMIX_CLI, "-b", bitrate]
    if DOWNLOAD_PATH:
        command += ["-p", DOWNLOAD_PATH]
    command.append(url)

    try:
        # Using DEVNULL to hide command output from the console
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Catches download errors or if deemix CLI isn't found
        return False


def download_track_with_fallback(url: str) -> bool:
    """
    Attempts to download a track using preferred bitrates, falling back to the next best.
    """
    for bitrate in BITRATES_PREFER:
        if _run_deemix_command(url, bitrate):
            return True  # Success
    return False  # All bitrates failed
<div style="
  background: white;
  padding: 16px;
  display: flex;
  justify-content: center;
">
  <img 
    src="https://github.com/user-attachments/assets/09298035-dcb7-4762-a6f3-e27165714beb" 
    alt="deefuse_logo_high_dpi" 
    style="
      max-width: 100%;
      height: auto;
      display: block;
    "
  />
</div>

# DeeFuse

DeeFuse is a desktop application for upgrading your existing music library using tracks downloaded from Deezer. It scans your existing files, finds matches via the Deezer API and downloads the highest quality versions using the `deemix` command line interface. This aims to improve bitrate, metadata and organization.

## Features

- Automatic scanning of a directory for `.flac`, `.mp3` and `.m4a` files
- Strict matching of artist, title and duration for unattended downloads
- Manual search and relaxed matching when no automatic match is found
- Progress dialog with the ability to cancel a scan
- CSV logs for skipped and matched tracks

## Requirements

- Python 3.9 or newer
- The [deemix](https://deemix.app/) CLI available on your `PATH`

The application installs its Python dependencies automatically when you install the package.

## Installation

Install the package from source:

```bash
pip install .
```

This will install a `deefuse` entry point.

## Building a standalone executable

Use PyInstaller's module mode to bundle the application:

```bash
pyinstaller --noconsole --onefile -n DeeFuse -m deefuse
```

Running in module mode ensures the package context is correctly set when the
executable starts.

## Usage

Run the program either with the installed command or via the module:

```bash
deefuse
# or
python -m deefuse
```

Select your music directory and click **Scan & Download**. Matches will be downloaded automatically. Unmatched tracks will appear in the **Skipped Tracks** table where you can perform manual searches and downloads.

Matched and skipped tracks are recorded in `matched_tracks.csv` and `skipped_tracks.csv` respectively.

## License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.

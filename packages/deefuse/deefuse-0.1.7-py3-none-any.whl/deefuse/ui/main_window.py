import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from mutagen import File as MutagenFile

# Import from our refactored modules
from deefuse import utils, config, csv_handler, downloader, deezer_api
from .progress_dialog import ProgressDialog


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        icon = utils.asset_path("assets/deefuse_desktop.ico")
        try:
            self.iconbitmap(icon)
        except Exception:
            pass
        self.title("DeeFuse")
        self.geometry("1400x880")
        self.minsize(1200, 700)

        # App state
        self.music_directory = ""
        self.is_scanning = False
        self.skipped_rows, self.skipped_header = csv_handler.load_skipped()
        self.deezer_results_full = []
        self.download_rows = []
        self.download_statuses = []

        self._configure_styles()
        self._build_ui()
        self._populate_skipped_treeview()

        # Custom event for refreshing UI from other threads
        self.bind("<<RefreshUI>>", self._refresh_ui_from_event)

    def _configure_styles(self):
        """Set up the appearance for CTk and ttk widgets."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # DPI Awareness for Windows
        if sys.platform == "win32":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        # ttk.Treeview style
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#1f2a36",
            fieldbackground="#1f2a36",
            foreground="#E8E8E8",
            rowheight=28,
            font=("Segoe UI", 13)  # Increased font size for better readability
        )

        style.map("Treeview", background=[("selected", "#006699")],
                  foreground=[("selected", "white")])

        style.configure("Treeview.Heading", background="#0f2a44",
                        foreground="#7CC7FF", font=("Segoe UI", 10, "bold"))

        self.font_h1 = ctk.CTkFont(size=18, weight="bold")
        self.font_h2 = ctk.CTkFont(size=14, weight="bold")

    def _create_treeview(self, parent, columns, height):
        """Factory function to create a styled Treeview with a scrollbar."""
        frame = ctk.CTkFrame(parent, corner_radius=6)
        frame.columnconfigure(0, weight=1)

        tv = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=scrollbar.set)

        tv.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        for col in columns:
            tv.heading(col, text=col)
            tv.column(col, anchor="w", width=160, stretch=True)

        return frame, tv

    def _build_ui(self):
        """Construct the main application window."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(7, weight=1)

        # --- Top Section: Directory Selection & Scan Button ---
        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        dir_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(dir_frame, text="Music Directory:", font=self.font_h2).grid(row=0, column=0, sticky="w")
        self.dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="Select music directory…")
        self.dir_entry.grid(row=0, column=1, sticky="ew", padx=(10, 10))
        ctk.CTkButton(dir_frame, text="Browse", command=self._select_directory, width=80).grid(row=0, column=2,
                                                                                               padx=(0, 10))
        self.scan_btn = ctk.CTkButton(dir_frame, text="Scan & Download", command=self._start_scan, fg_color="#28a745",
                                      hover_color="#23913c", width=120)
        self.scan_btn.grid(row=0, column=3)

        # --- Skipped Tracks Table ---
        ctk.CTkLabel(self, text="Skipped Tracks", font=self.font_h2).grid(row=2, column=0, sticky="w", padx=20,
                                                                          pady=(10, 0))
        skip_frame, self.skip_tv = self._create_treeview(self, config.SKIP_HDR, 8)
        skip_frame.grid(row=3, column=0, sticky="ew", padx=20)
        self.skip_tv.bind("<<TreeviewSelect>>", self._on_skipped_track_select)

        # --- Deezer Results Table ---
        ctk.CTkLabel(self, text="Deezer Results", font=self.font_h2).grid(row=4, column=0, sticky="w", padx=20,
                                                                          pady=(8, 0))
        dz_frame, self.dz_tv = self._create_treeview(self, ["Track", "Artist", "Album", "Duration"], 5)
        dz_frame.grid(row=5, column=0, sticky="ew", padx=20)
        self.dz_tv.bind("<<TreeviewSelect>>", self._show_detail_view)
        self.dz_tv.bind("<Double-1>", self._on_deezer_result_double_click)

        # --- Download Progress Table ---
        ctk.CTkLabel(self, text="Download Progress", font=self.font_h2).grid(row=6, column=0, sticky="w", padx=20,
                                                                             pady=(8, 0))
        dl_frame, self.dl_tv = self._create_treeview(self, ["Status", "Track", "Artist", "Album"], 5)
        dl_frame.grid(row=7, column=0, sticky="nsew", padx=20)

        # --- Detail View ---
        self.detail_textbox = ctk.CTkTextbox(self, height=70, font=("Consolas", 10), wrap="word", state="disabled")
        self.detail_textbox.grid(row=8, column=0, sticky="ew", padx=20, pady=8)

        # --- Bottom Buttons ---
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=9, column=0, pady=(0, 12))
        ctk.CTkButton(btn_row, text="Search Deezer", command=self._manual_search).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Download Track", command=self._manual_download, fg_color="#28a745",
                      hover_color="#23913c").pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Clear Progress", command=self._clear_download_progress, fg_color="#ffc107",
                      hover_color="#d39e00").pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Exit", command=self.destroy, fg_color="#dc3545", hover_color="#bd2c3a").pack(
            side="right", padx=6)

    # --- Event Handlers & Actions ---

    def _select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.music_directory = directory
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def _start_scan(self):
        if not self.music_directory or not os.path.exists(self.music_directory):
            messagebox.showerror("Error", "Please select a valid music directory.")
            return
        if self.is_scanning:
            messagebox.showinfo("Info", "A scan is already in progress.")
            return

        all_files = [os.path.join(r, f) for r, _, fs in os.walk(self.music_directory)
                     for f in fs if os.path.splitext(f)[1].lower() in config.SUPPORTED_EXTENSIONS]

        if not all_files:
            messagebox.showinfo("Info", "No supported audio files found in the selected directory.")
            return

        self.is_scanning = True
        self.scan_btn.configure(text="Scanning…", state="disabled")
        self.progress_dialog = ProgressDialog(self, len(all_files))

        # Run the scan in a separate thread to keep the UI responsive
        threading.Thread(target=self._scan_worker, args=(all_files,), daemon=True).start()

    def _scan_worker(self, file_paths: list):
        """Worker thread for scanning files and finding matches."""
        try:
            for path in file_paths:
                if self.progress_dialog.is_cancelled:
                    break
                self._process_file_for_auto_match(path)
        finally:
            self.is_scanning = False
            self.scan_btn.configure(text="Scan & Download", state="normal")

            if hasattr(self, "progress_dialog") and self.progress_dialog.winfo_exists():
                if not self.progress_dialog.is_cancelled:
                    messagebox.showinfo("Scan Complete",
                                        f"Files processed: {self.progress_dialog.processed}\n"
                                        f"Matched & downloaded: {self.progress_dialog.matched}\n"
                                        f"Skipped: {self.progress_dialog.skipped}\n"
                                        f"Failed: {self.progress_dialog.failed}")
                self.progress_dialog.destroy()

            # Reload data and refresh the UI
            self.skipped_rows, _ = csv_handler.load_skipped()
            self.event_generate("<<RefreshUI>>")

    def _process_file_for_auto_match(self, path: str):
        """Analyzes a single file, searches Deezer, and downloads if a match is found."""
        rel_path = os.path.relpath(path, self.music_directory)
        parts = rel_path.split(os.sep)

        if len(parts) < 3:  # Expects Artist/Album/Track folder structure
            self.progress_dialog.update_progress(os.path.basename(path), "failed", "Directory structure too shallow")
            return

        artist, album, filename = parts[0], parts[1], parts[2]
        track = utils.parse_track_from_filename(filename)

        try:
            duration = MutagenFile(path).info.length
        except Exception:
            duration = 0

        local_meta = {"track": track, "artist": artist, "album": album, "dur_raw": duration}
        self.progress_dialog.update_progress(filename, "processing", f"Searching: {artist} – {track}")

        match = deezer_api.search_strict_match(local_meta)

        if match:
            self.progress_dialog.update_progress(filename, "matched",
                                                 f"Match found: {match['artist']} – {match['track']}")
            local_row_data = [track, artist, album, utils.format_duration(duration)]
            dz_row_data = [match["track"], match["artist"], match["album"], utils.format_duration(match["duration"]),
                           match["url"]]

            # Start download in a new thread
            dl_thread = threading.Thread(
                target=self._auto_download_thread,
                args=(match["url"], local_row_data, dz_row_data),
                daemon=True
            )
            dl_thread.start()
        else:
            self.progress_dialog.update_progress(filename, "skipped", f"No close match found for: {artist} – {track}")
            row_to_skip = [track, artist, album, utils.format_duration(duration)]
            csv_handler.log_skip(row_to_skip)

    def _auto_download_thread(self, url, local_data, deezer_data):
        """Handles the download for an auto-matched track."""
        if downloader.download_track_with_fallback(url):
            csv_handler.log_match(local_data, deezer_data)
            csv_handler.remove_from_skipped(local_data)
        else:
            # Optionally handle failed auto-downloads, e.g., log them differently
            pass

    def _populate_skipped_treeview(self):
        """Clears and refills the skipped tracks table."""
        self.skip_tv.delete(*self.skip_tv.get_children())
        for row in self.skipped_rows:
            self.skip_tv.insert("", "end", values=row)

    def _on_skipped_track_select(self, event=None):
        """When a skipped track is selected, perform a relaxed search on Deezer."""
        selected_item = self.skip_tv.selection()
        if not selected_item:
            return

        self._show_detail_view(event)

        selected_row = self.skip_tv.item(selected_item[0])["values"]
        track_title, artist_name = selected_row[0], selected_row[1]

        try:
            full_results, display_rows = deezer_api.search_relaxed_match(artist_name, track_title)
            self.deezer_results_full = full_results
            self.dz_tv.delete(*self.dz_tv.get_children())
            for row in display_rows:
                self.dz_tv.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Deezer API Error", f"Failed to fetch results from Deezer: {e}")
            self.deezer_results_full = []
            self.dz_tv.delete(*self.dz_tv.get_children())

    def _manual_search(self):
        """Button action to trigger a search for the selected skipped track."""
        if not self.skip_tv.selection():
            messagebox.showinfo("Info", "Select a track from the 'Skipped Tracks' list to search for it.")
            return
        self._on_skipped_track_select()

    def _on_deezer_result_double_click(self, event):
        """Handles double-clicking a result in the Deezer table to start a download."""
        if self.dz_tv.identify_row(event.y):
            self._manual_download()

    def _manual_download(self):
        """Button action to download the selected Deezer result."""
        if not self.dz_tv.selection():
            messagebox.showinfo("Info", "Select a result from the 'Deezer Results' list to download.")
            return
        if not self.skip_tv.selection():
            messagebox.showinfo("Info", "Select the original skipped track you are trying to match.")
            return

        dz_index = self.dz_tv.index(self.dz_tv.selection()[0])
        dz_data = self.deezer_results_full[dz_index]

        sk_index = self.skip_tv.index(self.skip_tv.selection()[0])
        local_data = self.skipped_rows[sk_index]

        # Add to download progress view
        dl_index = len(self.download_rows)
        self.download_rows.append([dz_data[1], dz_data[0], dz_data[2]])  # Track, Artist, Album
        self.download_statuses.append("Queued")
        self._refresh_download_progress_treeview()

        # Start download in a new thread
        threading.Thread(
            target=self._manual_download_thread,
            args=(dz_data, local_data, sk_index, dl_index),
            daemon=True
        ).start()

    def _manual_download_thread(self, deezer_data, local_data, skipped_idx, download_idx):
        """Worker thread for manual downloads."""
        url = deezer_data[4]
        self.download_statuses[download_idx] = "▶️ Downloading"
        self.event_generate("<<RefreshUI>>")

        is_success = downloader.download_track_with_fallback(url)
        self.download_statuses[download_idx] = "✅ Downloaded" if is_success else "❌ Failed"

        if is_success:
            # Log match and remove from skipped list
            dz_log_data = [deezer_data[1], deezer_data[0], deezer_data[2], utils.format_duration(deezer_data[3]),
                           deezer_data[4]]
            csv_handler.log_match(local_data, dz_log_data)
            csv_handler.remove_from_skipped(local_data)

            # Remove from in-memory list
            if skipped_idx < len(self.skipped_rows):
                del self.skipped_rows[skipped_idx]

        self.event_generate("<<RefreshUI>>")

    def _refresh_ui_from_event(self, event=None):
        """Refreshes all data-driven UI components."""
        self._populate_skipped_treeview()
        self._refresh_download_progress_treeview()

    def _refresh_download_progress_treeview(self):
        """Clears and refills the download progress table."""
        self.dl_tv.delete(*self.dl_tv.get_children())

        # Combine status and data, then sort by artist name
        display_data = sorted(
            zip(self.download_statuses, self.download_rows),
            key=lambda x: x[1][1].lower()  # Sort by artist (index 1 of download_rows)
        )

        for status, (track, artist, album) in display_data:
            self.dl_tv.insert("", "end", values=[status, track, artist, album])

    def _clear_download_progress(self):
        """Clears the download progress view."""
        self.download_rows.clear()
        self.download_statuses.clear()
        self._refresh_download_progress_treeview()

    def _show_detail_view(self, event):
        """Displays formatted details of a selected track in the textbox."""
        try:
            widget = event.widget
            selected_item = widget.selection()
        except AttributeError:
            # Fallback for when event is None
            widget = self.skip_tv
            selected_item = widget.selection()

        if not selected_item:
            return

        values = widget.item(selected_item[0])["values"]
        headers = config.SKIP_HDR if widget is self.skip_tv else ["Track", "Artist", "Album", "Duration"]

        detail_text = "\n".join(f"{h}: {v}" for h, v in zip(headers, values))

        self.detail_textbox.configure(state="normal")
        self.detail_textbox.delete("1.0", "end")
        self.detail_textbox.insert("end", detail_text)
        self.detail_textbox.configure(state="disabled")
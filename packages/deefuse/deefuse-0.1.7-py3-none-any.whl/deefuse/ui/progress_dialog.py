import customtkinter as ctk


class ProgressDialog(ctk.CTkToplevel):
    """A Toplevel window to show scanning progress."""

    def __init__(self, parent, total_files: int):
        super().__init__(parent)
        self.title("Scanning Files")
        self.geometry("500x300")
        self.transient(parent)
        self.grab_set()

        self.total = total_files
        self.processed = self.matched = self.skipped = self.failed = 0
        self.is_cancelled = False

        self._build_ui()

    def _build_ui(self):
        self.lbl_progress = ctk.CTkLabel(self, text="Initializing…", font=ctk.CTkFont(size=14))
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.lbl_stats = ctk.CTkLabel(self, text="Processed: 0 | Matched: 0 | Skipped: 0 | Failed: 0")
        self.lbl_current_file = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=10))
        self.log_textbox = ctk.CTkTextbox(self, height=110, font=ctk.CTkFont(size=9))
        self.btn_cancel = ctk.CTkButton(self, text="Cancel", command=self._cancel)

        self.lbl_progress.pack(pady=4, padx=20, fill="x")
        self.progress_bar.pack(pady=4, padx=20, fill="x")
        self.lbl_stats.pack(pady=4, padx=20, fill="x")
        self.lbl_current_file.pack(pady=2, padx=20, fill="x")
        self.log_textbox.pack(pady=4, padx=20, fill="both", expand=True)
        self.btn_cancel.pack(pady=4, padx=20)

    def update_progress(self, file: str, status: str, message: str = ""):
        """Updates the progress bars and labels."""
        if self.is_cancelled:
            return

        if status in ("matched", "skipped", "failed"):
            self.processed += 1
            if status == "matched":
                self.matched += 1
            elif status == "skipped":
                self.skipped += 1
            elif status == "failed":
                self.failed += 1

        percentage = self.processed / self.total if self.total > 0 else 0
        self.progress_bar.set(percentage)

        self.lbl_progress.configure(text=f"Progress: {self.processed}/{self.total} ({percentage:.1%})")
        self.lbl_stats.configure(
            text=f"Processed: {self.processed} | Matched: {self.matched} | Skipped: {self.skipped} | Failed: {self.failed}")
        self.lbl_current_file.configure(text=file)

        if message:
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")

        self.update_idletasks()

    def _cancel(self):
        """Flags the process as cancelled and closes the dialog."""
        self.is_cancelled = True
        self.destroy()
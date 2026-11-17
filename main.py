import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from organizer.core import run_organization

APP_TITLE = "Smart Media Organizer AI"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("820x620")
        self.minsize(720, 540)
        self.configure(bg="#101827")
        self.source = tk.StringVar()
        self.destination = tk.StringVar()
        self.api_key = tk.StringVar()
        self.use_online = tk.BooleanVar(value=True)
        self.copy_duplicates = tk.BooleanVar(value=True)
        self.stop_event = threading.Event()
        self._build()

    def _build(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#101827")
        style.configure("TLabel", background="#101827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground="#ffffff")
        style.configure("Sub.TLabel", foreground="#9ca3af")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("TCheckbutton", background="#101827", foreground="#e5e7eb")
        style.configure("Horizontal.TProgressbar", troughcolor="#263244", background="#38bdf8")

        root = ttk.Frame(self, padding=22)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Smart Media Organizer AI", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Sort photos and videos into folders. Originals are never moved or deleted.",
                  style="Sub.TLabel").pack(anchor="w", pady=(4, 18))

        self._path_row(root, "Source folder", self.source, self.pick_source)
        self._path_row(root, "Destination folder", self.destination, self.pick_destination)

        api_frame = ttk.LabelFrame(root, text="Hybrid AI settings", padding=12)
        api_frame.pack(fill="x", pady=12)
        ttk.Checkbutton(api_frame, text="Use OpenAI online vision when API key is provided",
                        variable=self.use_online).pack(anchor="w")
        ttk.Label(api_frame, text="OpenAI API key (optional; selected images / sampled video frames are sent online):",
                  style="Sub.TLabel").pack(anchor="w", pady=(8, 4))
        self.key_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=75)
        self.key_entry.pack(fill="x")
        ttk.Checkbutton(api_frame, text="Copy exact duplicate files into Duplicates_Review (recommended)",
                        variable=self.copy_duplicates).pack(anchor="w", pady=(10, 0))

        note = ("Offline mode uses local CLIP if installed. Without CLIP, the app falls back to "
                "filename-based categories. Online vision needs an OpenAI API key and API billing.")
        ttk.Label(root, text=note, style="Sub.TLabel", wraplength=740).pack(anchor="w", pady=(2, 12))

        buttons = ttk.Frame(root)
        buttons.pack(fill="x")
        self.start_btn = ttk.Button(buttons, text="Start organizing", command=self.start)
        self.start_btn.pack(side="left")
        ttk.Button(buttons, text="Open destination", command=self.open_destination).pack(side="left", padx=8)

        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(18, 8))
        self.status = tk.StringVar(value="Ready. Choose source and destination folders.")
        ttk.Label(root, textvariable=self.status).pack(anchor="w")
        self.log = tk.Text(root, height=13, bg="#0b1220", fg="#d1d5db",
                           insertbackground="white", relief="flat", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, pady=(10, 0))
        self.log.configure(state="disabled")

    def _path_row(self, parent, label, variable, command):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        ttk.Label(frame, text=label, width=18).pack(side="left")
        ttk.Entry(frame, textvariable=variable).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(frame, text="Browse", command=command).pack(side="left")

    def pick_source(self):
        p = filedialog.askdirectory(title="Select folder containing photos and videos")
        if p: self.source.set(p)

    def pick_destination(self):
        p = filedialog.askdirectory(title="Select where organized copies will be saved")
        if p: self.destination.set(p)

    def log_line(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def update_ui(self, message=None, progress=None, log=None):
        def apply():
            if message is not None: self.status.set(message)
            if progress is not None: self.progress["value"] = progress
            if log is not None: self.log_line(log)
        self.after(0, apply)

    def start(self):
        src, dst = self.source.get().strip(), self.destination.get().strip()
        if not src or not Path(src).is_dir():
            messagebox.showerror("Missing source", "Please select an existing source folder.")
            return
        if not dst:
            messagebox.showerror("Missing destination", "Please select a destination folder.")
            return
        srcp, dstp = Path(src).resolve(), Path(dst).resolve()
        if srcp == dstp or srcp in dstp.parents:
            messagebox.showerror("Invalid destination",
                "Destination must not be the source folder or a folder inside it.")
            return
        if dstp in srcp.parents:
            messagebox.showerror("Invalid destination",
                "Choose a destination outside the source folder to avoid scanning output files.")
            return
        if self.use_online.get() and self.api_key.get().strip():
            ok = messagebox.askyesno("Online AI privacy notice",
                "Selected photos and sampled video frames will be sent to OpenAI for analysis. "
                "Videos themselves are not uploaded. Continue?")
            if not ok: return
        self.start_btn.configure(state="disabled")
        self.progress["value"] = 0
        self.log_line("---- New organization run ----")
        options = (self.api_key.get().strip(), self.use_online.get(), self.copy_duplicates.get())
        thread = threading.Thread(target=self.worker, args=(srcp, dstp, *options), daemon=True)
        thread.start()

    def worker(self, src, dst, api_key, use_online, copy_duplicates):
        try:
            result = run_organization(
                src, dst, api_key, use_online, copy_duplicates,
                progress_cb=lambda done, total, name: self.update_ui(
                    message=f"Processing {done}/{total}: {name}",
                    progress=(done / max(total, 1)) * 100,
                    log=f"[{done}/{total}] {name}"
                )
            )
            self.update_ui(message="Finished successfully.", progress=100,
                log=(f"Finished. Scanned: {result['scanned']}, copied: {result['copied']}, "
                     f"duplicates: {result['duplicates']}, errors: {result['errors']}"))
            self.after(0, lambda: messagebox.showinfo("Completed",
                f"Organization completed.\n\nScanned: {result['scanned']}\n"
                f"Copied: {result['copied']}\nDuplicates: {result['duplicates']}\n"
                f"Errors: {result['errors']}\n\nOriginal files were not changed."))
        except Exception as exc:
            self.update_ui(message="Stopped because of an error.", log=f"ERROR: {exc}")
            self.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))

    def open_destination(self):
        p = self.destination.get().strip()
        if p and Path(p).exists():
            os.startfile(p)
        else:
            messagebox.showinfo("Destination", "Choose a destination folder first.")

if __name__ == "__main__":
    App().mainloop()

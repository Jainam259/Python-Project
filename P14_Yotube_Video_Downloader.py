"""
╔══════════════════════════════════════════════════════════════════╗
║          YouTube Downloader Pro — by Jainam                      ║
║          8K · 4K · HD · Audio  |  Premium Dark UI                ║
╚══════════════════════════════════════════════════════════════════╝
Requirements:
    pip install yt-dlp customtkinter pillow requests
"""

import customtkinter as ctk
import threading
import subprocess
import sys
import os
import time
from pathlib import Path
from tkinter import filedialog, messagebox

# ─── Auto-install yt_dlp ─────────────────────────────────────────────────────
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# ─── PIL optional ────────────────────────────────────────────────────────────
try:
    from PIL import Image
    import urllib.request, io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ─── Theme ───────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Palette ─────────────────────────────────────────────────────────────────
BG_ROOT     = "#080808"
BG_CARD     = "#111111"
BG_SURFACE  = "#181818"
BG_INPUT    = "#1E1E1E"
BORDER_DIM  = "#252525"
BORDER_LIT  = "#3A3A3A"

RED         = "#FF1744"
RED_HOVER   = "#D50000"
RED_DIM     = "#660A19"

GOLD        = "#FFC400"
BLUE_AUDIO  = "#1565C0"
BLUE_HOVER  = "#0D47A1"

TEXT_HI     = "#F5F5F5"
TEXT_MID    = "#AAAAAA"
TEXT_LO     = "#555555"

SUCCESS     = "#00E676"
WARNING     = "#FF9100"

# ─── Quality Options ─────────────────────────────────────────────────────────
VIDEO_QUALITIES = [
    "Best Available",
    "8K (4320p) ✦",
    "4K (2160p)",
    "1440p (2K)",
    "1080p (Full HD)",
    "720p (HD)",
    "480p (SD)",
    "360p",
]

AUDIO_QUALITIES = [
    "Best Audio",
    "320 kbps  MP3",
    "256 kbps  MP3",
    "192 kbps  MP3",
    "128 kbps  MP3",
    "Best  M4A/AAC",
    "FLAC  Lossless",
]

QUALITY_MAP = {
    "Best Available"    : "bestvideo+bestaudio/best",
    "8K (4320p) ✦"     : "bestvideo[height<=4320]+bestaudio/best[height<=4320]",
    "4K (2160p)"        : "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "1440p (2K)"        : "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
    "1080p (Full HD)"   : "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p (HD)"         : "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p (SD)"         : "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "360p"              : "bestvideo[height<=360]+bestaudio/best[height<=360]",
}

AUDIO_MAP = {
    "Best Audio"        : {"format": "bestaudio/best", "codec": "mp3",  "quality": "0"},
    "320 kbps  MP3"     : {"format": "bestaudio/best", "codec": "mp3",  "quality": "320"},
    "256 kbps  MP3"     : {"format": "bestaudio/best", "codec": "mp3",  "quality": "256"},
    "192 kbps  MP3"     : {"format": "bestaudio/best", "codec": "mp3",  "quality": "192"},
    "128 kbps  MP3"     : {"format": "bestaudio/best", "codec": "mp3",  "quality": "128"},
    "Best  M4A/AAC"     : {"format": "bestaudio/best", "codec": "m4a",  "quality": "0"},
    "FLAC  Lossless"    : {"format": "bestaudio/best", "codec": "flac", "quality": "0"},
}


# ─── Custom Widgets ───────────────────────────────────────────────────────────
class Divider(ctk.CTkFrame):
    """A slim 1 px horizontal rule."""
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", BORDER_DIM)
        kw.setdefault("height", 1)
        kw.setdefault("corner_radius", 0)
        super().__init__(master, **kw)


class SectionLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        kw.setdefault("font", ("Segoe UI", 10, "bold"))
        kw.setdefault("text_color", TEXT_LO)
        kw.setdefault("anchor", "w")
        super().__init__(master, text=text.upper(), **kw)


# ─── Main App ─────────────────────────────────────────────────────────────────
class YoutubeDownloaderApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader Pro")
        self.geometry("960x820")
        self.minsize(860, 720)
        self.configure(fg_color=BG_ROOT)

        self.download_path  = str(Path.home() / "Downloads")
        self.is_downloading = False
        self.video_info     = None
        self.thumb_image    = None

        self._build_ui()

    # ── Layout scaffold ──────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        for r in range(7):
            self.grid_rowconfigure(r, weight=0)
        self.grid_rowconfigure(6, weight=1)   # log expands

        self._build_titlebar()       # row 0
        self._build_url_section()    # row 1
        self._build_info_card()      # row 2
        self._build_options()        # row 3
        self._build_action_buttons() # row 4
        self._build_progress()       # row 5
        self._build_log()            # row 6

    # ── Title bar ────────────────────────────────────────────────────────────
    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0, height=58)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text="▶",
                     font=("Segoe UI", 20, "bold"),
                     text_color=RED).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(inner, text="YouTube Downloader Pro",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_HI).pack(side="left")
        ctk.CTkLabel(inner, text="   8K · 4K · HD · Audio",
                     font=("Segoe UI", 12),
                     text_color=TEXT_LO).pack(side="left")

        Divider(self).grid(row=0, column=0, sticky="sew")

    # ── URL input section ────────────────────────────────────────────────────
    def _build_url_section(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="ew", padx=24, pady=(20, 0))
        wrap.grid_columnconfigure(1, weight=1)

        SectionLabel(wrap, "Video URL").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        # Icon box
        icon_box = ctk.CTkFrame(wrap, fg_color=BG_SURFACE,
                                width=44, height=44, corner_radius=10,
                                border_width=1, border_color=BORDER_DIM)
        icon_box.grid(row=1, column=0, padx=(0, 8))
        icon_box.grid_propagate(False)
        ctk.CTkLabel(icon_box, text="🔗", font=("Segoe UI", 17),
                     text_color=RED).place(relx=0.5, rely=0.5, anchor="center")

        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            wrap, textvariable=self.url_var,
            placeholder_text="Paste a YouTube URL  (e.g. https://youtu.be/…)",
            font=("Segoe UI", 13), height=44,
            fg_color=BG_SURFACE,
            border_color=BORDER_DIM,
            border_width=1,
            text_color=TEXT_HI,
            placeholder_text_color=TEXT_LO,
            corner_radius=10,
        )
        self.url_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        self.url_entry.bind("<Return>", lambda _: self._fetch_info_thread())

        self.fetch_btn = ctk.CTkButton(
            wrap, text="Fetch Info", width=120, height=44,
            font=("Segoe UI", 13, "bold"),
            fg_color=RED, hover_color=RED_HOVER,
            corner_radius=10,
            command=self._fetch_info_thread,
        )
        self.fetch_btn.grid(row=1, column=2)

    # ── Info card ────────────────────────────────────────────────────────────
    def _build_info_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                            corner_radius=14,
                            border_width=1, border_color=BORDER_DIM)
        card.grid(row=2, column=0, sticky="ew", padx=24, pady=(16, 0))
        card.grid_columnconfigure(1, weight=1)

        # Thumbnail
        self.thumb_label = ctk.CTkLabel(
            card, text="Thumbnail",
            font=("Segoe UI", 10), text_color=TEXT_LO,
            width=170, height=96,
            fg_color=BG_SURFACE, corner_radius=10,
        )
        self.thumb_label.grid(row=0, column=0, rowspan=4,
                              padx=18, pady=18, sticky="nw")

        # Title
        self.title_lbl = ctk.CTkLabel(
            card, text="No video loaded — paste a URL above",
            font=("Segoe UI", 15, "bold"),
            text_color=TEXT_HI, anchor="w", wraplength=620,
        )
        self.title_lbl.grid(row=0, column=1, sticky="ew",
                            padx=(6, 18), pady=(20, 4))

        # Channel · Duration · Views
        self.meta_lbl = ctk.CTkLabel(
            card,
            text="Duration: —  ·  Channel: —  ·  Views: —",
            font=("Segoe UI", 12), text_color=TEXT_MID, anchor="w",
        )
        self.meta_lbl.grid(row=1, column=1, sticky="ew", padx=(6, 18), pady=2)

        # Available qualities badge row
        self.avail_lbl = ctk.CTkLabel(
            card, text="Available qualities: —",
            font=("Segoe UI", 11, "bold"),
            text_color=GOLD, anchor="w",
        )
        self.avail_lbl.grid(row=2, column=1, sticky="ew",
                            padx=(6, 18), pady=(2, 18))

    # ── Options row ──────────────────────────────────────────────────────────
    def _build_options(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=3, column=0, sticky="ew", padx=24, pady=(18, 0))
        wrap.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- Mode toggle ---
        mode_card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12,
                                 border_width=1, border_color=BORDER_DIM)
        mode_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        SectionLabel(mode_card, "Download Mode").pack(anchor="w", padx=14, pady=(12, 6))

        self.mode_var = ctk.StringVar(value="Video")
        rb_kw = dict(font=("Segoe UI", 12), text_color=TEXT_HI,
                     fg_color=RED, hover_color=RED_HOVER,
                     border_color=BORDER_LIT, variable=self.mode_var)

        ctk.CTkRadioButton(mode_card, text="Video + Audio",
                           value="Video",
                           command=self._on_mode_change, **rb_kw
                           ).pack(anchor="w", padx=14, pady=3)
        ctk.CTkRadioButton(mode_card, text="Audio Only",
                           value="Audio",
                           command=self._on_mode_change, **rb_kw
                           ).pack(anchor="w", padx=14, pady=(3, 14))

        # --- Video Quality ---
        vq_card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12,
                               border_width=1, border_color=BORDER_DIM)
        vq_card.grid(row=0, column=1, sticky="nsew", padx=6)

        SectionLabel(vq_card, "Video Quality").pack(anchor="w", padx=14, pady=(12, 6))
        self.vq_var = ctk.StringVar(value="1080p (Full HD)")
        self.vq_menu = ctk.CTkOptionMenu(
            vq_card, values=VIDEO_QUALITIES, variable=self.vq_var,
            font=("Segoe UI", 12),
            fg_color=BG_INPUT, button_color=RED, button_hover_color=RED_HOVER,
            dropdown_fg_color=BG_SURFACE,
            dropdown_text_color=TEXT_HI,
            dropdown_hover_color="#2A2A2A",
            text_color=TEXT_HI,
            width=180, corner_radius=8,
        )
        self.vq_menu.pack(anchor="w", padx=14, pady=(0, 14))

        # --- Audio Quality ---
        aq_card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12,
                               border_width=1, border_color=BORDER_DIM)
        aq_card.grid(row=0, column=2, sticky="nsew", padx=6)

        SectionLabel(aq_card, "Audio Quality").pack(anchor="w", padx=14, pady=(12, 6))
        self.aq_var = ctk.StringVar(value="320 kbps  MP3")
        self.aq_menu = ctk.CTkOptionMenu(
            aq_card, values=AUDIO_QUALITIES, variable=self.aq_var,
            font=("Segoe UI", 12),
            fg_color=BG_INPUT, button_color=RED, button_hover_color=RED_HOVER,
            dropdown_fg_color=BG_SURFACE,
            dropdown_text_color=TEXT_HI,
            dropdown_hover_color="#2A2A2A",
            text_color=TEXT_HI,
            width=180, corner_radius=8,
        )
        self.aq_menu.pack(anchor="w", padx=14, pady=(0, 14))

        # --- Save To ---
        path_card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12,
                                 border_width=1, border_color=BORDER_DIM)
        path_card.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        SectionLabel(path_card, "Save Location").pack(anchor="w", padx=14, pady=(12, 6))
        self.path_lbl = ctk.CTkLabel(
            path_card,
            text=self._short_path(self.download_path),
            font=("Segoe UI", 11), text_color=TEXT_HI, anchor="w",
        )
        self.path_lbl.pack(anchor="w", padx=14, pady=(0, 6))
        ctk.CTkButton(
            path_card, text="📂  Browse", width=110, height=30,
            font=("Segoe UI", 11),
            fg_color=BG_SURFACE, hover_color="#282828",
            border_width=1, border_color=BORDER_LIT,
            corner_radius=8, command=self._browse_folder,
        ).pack(anchor="w", padx=14, pady=(0, 14))

    # ── Action buttons ───────────────────────────────────────────────────────
    def _build_action_buttons(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=4, column=0, sticky="ew", padx=24, pady=(16, 0))
        bar.grid_columnconfigure((0, 1, 2), weight=1)

        self.dl_video_btn = ctk.CTkButton(
            bar, text="⬇   Download Video",
            font=("Segoe UI", 14, "bold"), height=50,
            fg_color=RED, hover_color=RED_HOVER,
            corner_radius=12,
            command=lambda: self._start_download("video"),
        )
        self.dl_video_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.dl_audio_btn = ctk.CTkButton(
            bar, text="🎵   Download Audio",
            font=("Segoe UI", 14, "bold"), height=50,
            fg_color=BG_CARD, hover_color=BLUE_HOVER,
            border_width=1, border_color=RED,
            text_color=TEXT_HI,
            corner_radius=12,
            command=lambda: self._start_download("audio"),
        )
        self.dl_audio_btn.grid(row=0, column=1, sticky="ew", padx=6)

        self.open_btn = ctk.CTkButton(
            bar, text="📁   Open Folder",
            font=("Segoe UI", 14, "bold"), height=50,
            fg_color=BG_SURFACE, hover_color="#222222",
            border_width=1, border_color=BORDER_LIT,
            text_color=TEXT_MID,
            corner_radius=12,
            command=self._open_folder,
        )
        self.open_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

    # ── Progress strip ───────────────────────────────────────────────────────
    def _build_progress(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=5, column=0, sticky="ew", padx=24, pady=(12, 0))
        wrap.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(
            wrap, height=6, corner_radius=3,
            fg_color=BG_SURFACE, progress_color=RED,
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.progress_bar.set(0)

        self.status_lbl = ctk.CTkLabel(
            wrap, text="Ready",
            font=("Segoe UI", 11), text_color=TEXT_LO, anchor="w",
        )
        self.status_lbl.grid(row=1, column=0, sticky="w")

    # ── Activity log ─────────────────────────────────────────────────────────
    def _build_log(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD,
                            corner_radius=14,
                            border_width=1, border_color=BORDER_DIM)
        card.grid(row=6, column=0, sticky="nsew", padx=24, pady=(14, 20))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 6))

        ctk.CTkLabel(hdr, text="⬤  Activity Log",
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_LO).pack(side="left")

        ctk.CTkButton(
            hdr, text="Clear", width=58, height=24,
            font=("Segoe UI", 10),
            fg_color=BG_SURFACE, hover_color="#222222",
            border_width=1, border_color=BORDER_DIM,
            text_color=TEXT_LO, corner_radius=6,
            command=self._clear_log,
        ).pack(side="right")

        Divider(card).grid(row=0, column=0, sticky="sew", pady=(38, 0))

        self.log_box = ctk.CTkTextbox(
            card, font=("Consolas", 11),
            text_color="#CCCCCC",
            fg_color=BG_ROOT,
            wrap="word", state="disabled",
            border_width=0, corner_radius=0,
        )
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=14, pady=10)

    # ─── Helpers ─────────────────────────────────────────────────────────────
    def _short_path(self, path):
        p = Path(path)
        s = str(p)
        return ("…/" + p.name) if len(s) > 30 else s

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_lbl.configure(text=self._short_path(folder))

    def _open_folder(self):
        p = self.download_path
        if sys.platform == "win32":
            os.startfile(p)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", p])
        else:
            subprocess.Popen(["xdg-open", p])

    def _on_mode_change(self):
        disabled = self.mode_var.get() == "Audio"
        self.vq_menu.configure(
            state="disabled" if disabled else "normal",
            fg_color="#141414" if disabled else BG_INPUT,
            text_color=TEXT_LO if disabled else TEXT_HI,
        )

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _log(self, msg: str):
        self.log_box.configure(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}]  {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text: str, color: str = TEXT_LO):
        self.status_lbl.configure(text=text, text_color=color)

    def _set_progress(self, val: float):
        self.progress_bar.set(val)

    # ─── Fetch Info ───────────────────────────────────────────────────────────
    def _fetch_info_thread(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please paste a YouTube URL first.")
            return
        self.fetch_btn.configure(state="disabled", text="Fetching…")
        threading.Thread(target=self._fetch_info, args=(url,), daemon=True).start()

    def _fetch_info(self, url: str):
        try:
            self._log("Fetching video information…")
            opts = {"quiet": True, "no_warnings": True, "skip_download": True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.video_info = info
            title    = info.get("title", "Unknown")
            channel  = info.get("uploader", "Unknown")
            views    = f"{info.get('view_count', 0):,}"
            duration = self._fmt_dur(info.get("duration", 0))

            formats  = info.get("formats", [])
            heights  = sorted(
                {f.get("height") for f in formats if f.get("height")},
                reverse=True
            )
            avail    = "  ·  ".join([f"{h}p" for h in heights[:7]])

            self.after(0, lambda: self._apply_info(title, channel, views, duration, avail))
            self.after(0, lambda: self._log(f"✓  {title}"))
            self.after(0, lambda: self._log(
                f"   Channel: {channel}   Duration: {duration}   Views: {views}"))

            if PIL_AVAILABLE:
                thumb = info.get("thumbnail")
                if thumb:
                    threading.Thread(target=self._load_thumb,
                                     args=(thumb,), daemon=True).start()
        except Exception as e:
            self.after(0, lambda: self._log(f"✗  Error: {e}"))
            self.after(0, lambda: messagebox.showerror("Fetch Error", str(e)))
        finally:
            self.after(0, lambda: self.fetch_btn.configure(
                state="normal", text="Fetch Info"))

    def _apply_info(self, title, channel, views, duration, avail):
        self.title_lbl.configure(
            text=title[:88] + ("…" if len(title) > 88 else ""))
        self.meta_lbl.configure(
            text=f"Duration: {duration}   ·   Channel: {channel}   ·   Views: {views}")
        self.avail_lbl.configure(
            text=f"Available: {avail or 'N/A'}")

    def _load_thumb(self, url: str):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data)).resize((170, 96))
            self.thumb_image = ctk.CTkImage(img, size=(170, 96))
            self.after(0, lambda: self.thumb_label.configure(
                image=self.thumb_image, text="", fg_color="transparent"))
        except Exception:
            pass

    @staticmethod
    def _fmt_dur(sec: int) -> str:
        if not sec:
            return "—"
        h, r = divmod(int(sec), 3600)
        m, s = divmod(r, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"

    # ─── Download ─────────────────────────────────────────────────────────────
    def _start_download(self, mode: str):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL",
                "Paste a YouTube URL and click Fetch Info first.")
            return
        if self.is_downloading:
            messagebox.showinfo("Busy", "A download is already in progress.")
            return
        self.is_downloading = True
        self._set_progress(0)
        threading.Thread(target=self._download, args=(url, mode), daemon=True).start()

    def _download(self, url: str, mode: str):
        outtmpl = os.path.join(self.download_path, "%(title)s.%(ext)s")
        try:
            self.after(0, lambda: self._set_status(
                "Preparing download…", WARNING))

            if mode == "audio":
                aq     = self.aq_var.get()
                cfg    = AUDIO_MAP[aq]
                pproc  = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": cfg["codec"],
                    **({"preferredquality": cfg["quality"]}
                       if cfg["quality"] != "0" else {}),
                }]
                opts = {
                    "format"          : cfg["format"],
                    "outtmpl"         : outtmpl,
                    "postprocessors"  : pproc,
                    "progress_hooks"  : [self._hook],
                    "quiet"           : True,
                    "no_warnings"     : True,
                }
                self.after(0, lambda: self._log(f"🎵  Downloading audio  [{aq}]…"))

            else:
                vq   = self.vq_var.get()
                fmt  = QUALITY_MAP.get(vq, "bestvideo+bestaudio/best")
                opts = {
                    "format"              : fmt,
                    "outtmpl"             : outtmpl,
                    "merge_output_format" : "mp4",
                    "progress_hooks"      : [self._hook],
                    "quiet"               : True,
                    "no_warnings"         : True,
                    "postprocessors"      : [{
                        "key"           : "FFmpegVideoConvertor",
                        "preferedformat": "mp4",
                    }],
                }
                self.after(0, lambda: self._log(f"⬇   Downloading video  [{vq}]…"))

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            self.after(0, lambda: self._set_status("Download complete!", SUCCESS))
            self.after(0, lambda: self._set_progress(1.0))
            self.after(0, lambda: self._log(
                "✓  Saved to: " + self.download_path))
            self.after(0, lambda: messagebox.showinfo(
                "Done", "Download complete!\nSaved to:\n" + self.download_path))

        except Exception as e:
            err = str(e)
            self.after(0, lambda: self._set_status("Download failed", RED))
            self.after(0, lambda: self._log(f"✗  Error: {err}"))
            self.after(0, lambda: messagebox.showerror("Download Failed", err))
        finally:
            self.is_downloading = False

    def _hook(self, d: dict):
        status = d.get("status", "")
        if status == "downloading":
            total      = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            speed      = d.get("_speed_str", "—").strip()
            eta        = d.get("_eta_str", "—").strip()
            pct_str    = d.get("_percent_str", "0%").strip()

            if total > 0:
                pct = downloaded / total
                self.after(0, lambda p=pct: self._set_progress(p))

            msg = f"Downloading…  {pct_str}   ·   Speed: {speed}   ·   ETA: {eta}"
            self.after(0, lambda m=msg: self._set_status(m, WARNING))

        elif status == "finished":
            self.after(0, lambda: self._set_status("Processing file…", TEXT_MID))
            self.after(0, lambda: self._log("   ⚙  Merging / converting…"))


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = YoutubeDownloaderApp()
    app.mainloop()
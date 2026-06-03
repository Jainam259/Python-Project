# ============================================================
#  🎙 Speech ↔ Text Converter  |  Premium Edition v2
# ============================================================

import customtkinter as ctk
import threading
import time
from tkinter import messagebox

# ── Safe imports with user-friendly error messages ──────────
try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False

try:
    import pyttsx3
    TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    import pyaudio
    PYAUDIO_OK = True
except ImportError:
    PYAUDIO_OK = False

# ─────────────────────────────────────────
#  Theme & Appearance
# ─────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark":        "#0D0F1A",
    "bg_card":        "#12152B",
    "bg_input":       "#0A0C1C",
    "accent_blue":    "#4A90E2",
    "accent_cyan":    "#00D4FF",
    "accent_green":   "#00E5A0",
    "accent_red":     "#FF4C6A",
    "accent_purple":  "#8B5CF6",
    "text_primary":   "#E8EEFF",
    "text_secondary": "#6B7AA1",
    "border":         "#1E2347",
    "btn_listen":     "#0F3D3D",
    "btn_listen_h":   "#1A6060",
    "btn_speak":      "#1B3A6B",
    "btn_speak_h":    "#2D5FAA",
    "btn_clear":      "#3B1F2B",
    "btn_clear_h":    "#6B2040",
    "btn_exit":       "#1C1C2E",
    "btn_exit_h":     "#2E2E45",
    "btn_debug":      "#2B2000",
    "btn_debug_h":    "#4A3800",
}

# ─────────────────────────────────────────
#  TTS Engine (safe init)
# ─────────────────────────────────────────
engine = None
if TTS_OK:
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 1.0)
        voices = engine.getProperty('voices')
        for v in voices:
            if any(x in v.name.lower() for x in ["zira", "david", "en_", "english"]):
                engine.setProperty('voice', v.id)
                break
    except Exception:
        engine = None
        TTS_OK = False


# ─────────────────────────────────────────
#  Pulse Indicator Canvas
# ─────────────────────────────────────────
class PulseIndicator(ctk.CTkCanvas):
    def __init__(self, master, size=44, **kwargs):
        super().__init__(master, width=size, height=size,
                         bg=COLORS["bg_card"], highlightthickness=0, **kwargs)
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self._running = False
        self._step = 0
        self._draw_idle()

    def _draw_idle(self):
        self.delete("all")
        r = self.size // 2 - 5
        self.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                         fill=COLORS["bg_dark"], outline=COLORS["border"], width=2)
        mr = r // 2
        self.create_oval(self.cx - mr, self.cy - mr, self.cx + mr, self.cy + mr,
                         fill=COLORS["accent_blue"], outline="")

    def _animate(self):
        if not self._running:
            self._draw_idle()
            return
        import math
        self.delete("all")
        self._step = (self._step + 1) % 30
        p = self._step / 30
        for color, max_r in [(COLORS["accent_cyan"], self.size // 2 - 2),
                             (COLORS["accent_blue"], self.size // 2 - 8)]:
            af = abs(math.sin(p * math.pi))
            r = int(max_r * (0.5 + 0.5 * af))
            self.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                             fill="", outline=color, width=max(1, int(3 * af)))
        mr = self.size // 6
        self.create_oval(self.cx - mr, self.cy - mr, self.cx + mr, self.cy + mr,
                         fill=COLORS["accent_cyan"], outline="")
        self.after(50, self._animate)

    def start(self):
        self._running = True
        self._step = 0
        self._animate()

    def stop(self):
        self._running = False


# ─────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────
class SpeechConverterApp:

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Speech ↔ Text Converter")
        self.root.geometry("980x750")
        self.root.resizable(False, False)
        self.root.configure(fg_color=COLORS["bg_dark"])

        self._mic_list = []
        self._selected_mic_index = None
        self._is_listening = False

        self._build_ui()
        self._load_microphones()
        self._check_dependencies()

    # ──────────────────────────────────────
    #  Dependency Check Banner
    # ──────────────────────────────────────
    def _check_dependencies(self):
        missing = []
        if not SR_OK:
            missing.append("speech_recognition  →  pip install SpeechRecognition")
        if not PYAUDIO_OK:
            missing.append("pyaudio  →  pip install pyaudio   (or  pipwin install pyaudio  on Windows)")
        if not TTS_OK:
            missing.append("pyttsx3  →  pip install pyttsx3")

        if missing:
            msg = "⚠️  Missing packages:\n\n" + "\n".join(missing)
            self._set_status("⚠️  Missing packages — see console", COLORS["accent_red"])
            self.textbox.insert("end", msg)
            messagebox.showwarning("Missing Dependencies", msg)

    # ──────────────────────────────────────
    #  UI Construction
    # ──────────────────────────────────────
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color=COLORS["bg_card"],
                              corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="🎙  Speech  ↔  Text  Converter",
                     font=("Trebuchet MS", 26, "bold"),
                     text_color=COLORS["text_primary"]).pack(side="left", padx=28, pady=16)
        self.clock_lbl = ctk.CTkLabel(header, text="", font=("Consolas", 12),
                                      text_color=COLORS["text_secondary"])
        self.clock_lbl.pack(side="right", padx=28)
        self._tick_clock()

        ctk.CTkFrame(self.root, height=2, fg_color=COLORS["accent_blue"],
                     corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self.root, fg_color=COLORS["bg_dark"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        # ── Microphone selector ─────────────────
        mic_card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=12,
                                border_color=COLORS["border"], border_width=1)
        mic_card.pack(fill="x", pady=(0, 12))

        mic_inner = ctk.CTkFrame(mic_card, fg_color="transparent")
        mic_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(mic_inner, text="🎙  Microphone",
                     font=("Trebuchet MS", 13, "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 12))

        self.mic_var = ctk.StringVar(value="Loading microphones…")
        self.mic_dropdown = ctk.CTkOptionMenu(
            mic_inner,
            variable=self.mic_var,
            values=["Loading…"],
            width=520, height=34,
            font=("Consolas", 12),
            fg_color=COLORS["bg_input"],
            button_color=COLORS["accent_blue"],
            button_hover_color=COLORS["btn_speak_h"],
            text_color=COLORS["text_primary"],
            command=self._on_mic_selected
        )
        self.mic_dropdown.pack(side="left")

        self.test_mic_btn = ctk.CTkButton(
            mic_inner, text="🔍 Test Mic", width=100, height=34,
            font=("Trebuchet MS", 12),
            fg_color=COLORS["btn_debug"], hover_color=COLORS["btn_debug_h"],
            text_color=COLORS["accent_cyan"],
            border_color=COLORS["accent_cyan"], border_width=1,
            command=self._test_microphone
        )
        self.test_mic_btn.pack(side="left", padx=(10, 0))

        self.refresh_btn = ctk.CTkButton(
            mic_inner, text="↻", width=36, height=34,
            font=("Trebuchet MS", 14, "bold"),
            fg_color=COLORS["bg_input"], hover_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            command=self._load_microphones
        )
        self.refresh_btn.pack(side="left", padx=(6, 0))

        # ── Text Area ──────────────────────────
        text_card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=14,
                                 border_color=COLORS["border"], border_width=1)
        text_card.pack(fill="x", pady=(0, 12))

        top_row = ctk.CTkFrame(text_card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(10, 4))
        ctk.CTkLabel(top_row, text="TEXT AREA", font=("Consolas", 10, "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left")
        self.char_count = ctk.CTkLabel(top_row, text="0 chars",
                                       font=("Consolas", 10),
                                       text_color=COLORS["text_secondary"])
        self.char_count.pack(side="right")

        self.textbox = ctk.CTkTextbox(
            text_card, width=900, height=230,
            font=("Consolas", 15),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"], border_width=1,
            corner_radius=10, wrap="word"
        )
        self.textbox.pack(padx=16, pady=(0, 14))
        self.textbox.bind("<KeyRelease>", self._update_char_count)

        # ── Status Bar ─────────────────────────
        st_card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=12,
                               border_color=COLORS["border"], border_width=1)
        st_card.pack(fill="x", pady=(0, 16))
        st_inner = ctk.CTkFrame(st_card, fg_color="transparent")
        st_inner.pack(fill="x", padx=16, pady=10)

        self.pulse = PulseIndicator(st_inner, size=40)
        self.pulse.pack(side="left", padx=(0, 10))

        self.status_lbl = ctk.CTkLabel(
            st_inner, text="Ready  —  select a microphone and press  🎤 Speech → Text",
            font=("Trebuchet MS", 13), text_color=COLORS["text_secondary"]
        )
        self.status_lbl.pack(side="left")

        self.progress = ctk.CTkProgressBar(st_inner, width=110, height=6,
                                           progress_color=COLORS["accent_cyan"],
                                           fg_color=COLORS["bg_dark"], corner_radius=4)
        self.progress.pack(side="right", padx=(0, 4))
        self.progress.set(0)

        # ── Action Buttons ─────────────────────
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack()

        btns = [
            ("🎤  Speech → Text", COLORS["btn_listen"],  COLORS["btn_listen_h"],
             COLORS["accent_green"],  self.start_listening),
            ("🔊  Text → Speech",  COLORS["btn_speak"],   COLORS["btn_speak_h"],
             COLORS["accent_blue"],  self.text_to_speech),
            ("🗑  Clear",           COLORS["btn_clear"],   COLORS["btn_clear_h"],
             COLORS["accent_red"],   self.clear_text),
            ("✕  Exit",            COLORS["btn_exit"],    COLORS["btn_exit_h"],
             COLORS["text_secondary"], self.root.destroy),
        ]
        for i, (txt, fg, hov, bdr, cmd) in enumerate(btns):
            ctk.CTkButton(
                btn_row, text=txt, width=210, height=52,
                font=("Trebuchet MS", 14, "bold"),
                fg_color=fg, hover_color=hov,
                text_color=COLORS["text_primary"],
                border_color=bdr, border_width=1,
                corner_radius=12, command=cmd
            ).grid(row=0, column=i, padx=8)

    # ──────────────────────────────────────
    #  Microphone helpers
    # ──────────────────────────────────────
    def _load_microphones(self):
        """Populate dropdown with available mics."""
        self.mic_dropdown.configure(values=["Loading…"])
        self.mic_var.set("Loading…")

        def _worker():
            if not SR_OK or not PYAUDIO_OK:
                self.root.after(0, lambda: self.mic_var.set(
                    "⚠ pyaudio / speech_recognition not installed"))
                return
            try:
                names = sr.Microphone.list_microphone_names()
                if not names:
                    self.root.after(0, lambda: self._no_mic_found())
                    return
                self._mic_list = names
                display = [f"[{i}]  {n}" for i, n in enumerate(names)]

                def _update():
                    self.mic_dropdown.configure(values=display)
                    self.mic_var.set(display[0])
                    self._selected_mic_index = 0
                    self._set_status(
                        f"✅  Found {len(names)} microphone(s)  —  ready",
                        COLORS["accent_green"])

                self.root.after(0, _update)
            except Exception as e:
                self.root.after(0, lambda: self._set_status(
                    f"❌  Mic error: {e}", COLORS["accent_red"]))

        threading.Thread(target=_worker, daemon=True).start()

    def _no_mic_found(self):
        self.mic_dropdown.configure(values=["⚠  No microphone detected"])
        self.mic_var.set("⚠  No microphone detected")
        self._selected_mic_index = None
        self._set_status("❌  No microphone found — plug one in and press ↻",
                         COLORS["accent_red"])

    def _on_mic_selected(self, value: str):
        try:
            idx = int(value.split("]")[0].replace("[", "").strip())
            self._selected_mic_index = idx
            self._set_status(f"🎙  Microphone #{idx} selected", COLORS["accent_blue"])
        except Exception:
            self._selected_mic_index = None

    # ── Mic test ───────────────────────────
    def _test_microphone(self):
        if not SR_OK or not PYAUDIO_OK:
            messagebox.showerror("Missing Package",
                                 "Install pyaudio and SpeechRecognition first:\n\n"
                                 "pip install pyaudio SpeechRecognition")
            return
        if self._selected_mic_index is None:
            messagebox.showwarning("No Mic", "Please select a microphone first.")
            return

        def _worker():
            try:
                self._set_status("🔍  Testing microphone…", COLORS["accent_cyan"])
                with sr.Microphone(device_index=self._selected_mic_index) as src:
                    r = sr.Recognizer()
                    r.adjust_for_ambient_noise(src, duration=1)
                    energy = r.energy_threshold
                self._set_status(
                    f"✅  Mic OK  |  Ambient energy: {int(energy)}  (lower = quieter room)",
                    COLORS["accent_green"])
            except OSError as e:
                self._set_status(f"❌  Mic open failed: {e}", COLORS["accent_red"])
                self.root.after(0, lambda: messagebox.showerror(
                    "Microphone Error",
                    f"Cannot open microphone #{self._selected_mic_index}.\n\n"
                    f"Error: {e}\n\n"
                    "Fix steps:\n"
                    "1. Allow microphone access in Windows Privacy Settings\n"
                    "2. Make sure the mic is not used by another app\n"
                    "3. Try a different mic from the dropdown"))
            except Exception as e:
                self._set_status(f"❌  Test error: {e}", COLORS["accent_red"])

        threading.Thread(target=_worker, daemon=True).start()

    # ──────────────────────────────────────
    #  Speech → Text
    # ──────────────────────────────────────
    def _listen_worker(self):
        if not SR_OK or not PYAUDIO_OK:
            self._set_status("❌  Install pyaudio + SpeechRecognition first",
                             COLORS["accent_red"])
            self.root.after(0, lambda: messagebox.showerror(
                "Missing Packages",
                "Run:\n  pip install pyaudio SpeechRecognition"))
            return

        if self._selected_mic_index is None:
            self._set_status("❌  No microphone selected", COLORS["accent_red"])
            return

        recognizer = sr.Recognizer()
        # Tune recognizer for responsiveness
        recognizer.pause_threshold = 1.0        # stop after 1 s of silence
        recognizer.non_speaking_duration = 0.5
        recognizer.dynamic_energy_threshold = True

        try:
            with sr.Microphone(device_index=self._selected_mic_index) as source:
                self._set_status("🎤  Adjusting for background noise…",
                                 COLORS["accent_cyan"])
                self.pulse.start()
                self._animate_progress(0.2, COLORS["accent_cyan"])

                recognizer.adjust_for_ambient_noise(source, duration=0.8)

                self._set_status("🎤  Listening  —  speak now…",
                                 COLORS["accent_cyan"])
                self._animate_progress(0.4, COLORS["accent_cyan"])

                audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)

                self._set_status("⚙️  Recognizing…", COLORS["accent_blue"])
                self._animate_progress(0.75, COLORS["accent_blue"])
                self.pulse.stop()

            # Send to Google STT
            text = recognizer.recognize_google(audio, language="en-IN")

            def _insert():
                self.textbox.delete("1.0", "end")
                self.textbox.insert("end", text)
                self._update_char_count()

            self.root.after(0, _insert)
            self._animate_progress(1.0, COLORS["accent_green"])
            self._set_status("✅  Speech converted successfully!", COLORS["accent_green"])

        except sr.WaitTimeoutError:
            self._animate_progress(0, COLORS["accent_red"])
            self._set_status("⏱  Timeout — no speech detected. Try speaking louder.",
                             COLORS["accent_red"])
        except sr.UnknownValueError:
            self._animate_progress(0, COLORS["accent_red"])
            self._set_status(
                "❓  Couldn't understand — try speaking clearly or check mic volume",
                COLORS["accent_red"])
        except sr.RequestError as e:
            self._animate_progress(0, COLORS["accent_red"])
            self._set_status(f"🌐  Google API error: {e}  (check internet connection)",
                             COLORS["accent_red"])
        except OSError as e:
            self._animate_progress(0, COLORS["accent_red"])
            self._set_status(f"❌  Mic error: {e}  — try 🔍 Test Mic first",
                             COLORS["accent_red"])
        except Exception as e:
            self._animate_progress(0, COLORS["accent_red"])
            self._set_status(f"❌  Error: {e}", COLORS["accent_red"])
        finally:
            self.pulse.stop()
            self._is_listening = False

    def start_listening(self):
        if self._is_listening:
            self._set_status("⚠️  Already listening…", COLORS["accent_cyan"])
            return
        self._is_listening = True
        threading.Thread(target=self._listen_worker, daemon=True).start()

    # ──────────────────────────────────────
    #  Text → Speech
    # ──────────────────────────────────────
    def text_to_speech(self):
        if not TTS_OK or engine is None:
            messagebox.showerror("Missing Package",
                                 "Run:  pip install pyttsx3")
            return
        text = self.textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("No Text", "Please type or record text first.")
            return

        def _speak():
            self._set_status("🔊  Speaking…", COLORS["accent_blue"])
            self._animate_progress(0.5, COLORS["accent_blue"])
            try:
                engine.say(text)
                engine.runAndWait()
                self._animate_progress(1.0, COLORS["accent_green"])
                self._set_status("✅  Finished speaking", COLORS["accent_green"])
            except Exception as e:
                self._animate_progress(0, COLORS["accent_red"])
                self._set_status(f"❌  TTS error: {e}", COLORS["accent_red"])

        threading.Thread(target=_speak, daemon=True).start()

    # ──────────────────────────────────────
    #  Clear
    # ──────────────────────────────────────
    def clear_text(self):
        self.textbox.delete("1.0", "end")
        self._update_char_count()
        self._animate_progress(0)
        self._set_status("🗑  Cleared  —  Ready", COLORS["text_secondary"])

    # ──────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────
    def _tick_clock(self):
        self.clock_lbl.configure(text=time.strftime("%H:%M:%S  |  %d %b %Y"))
        self.root.after(1000, self._tick_clock)

    def _update_char_count(self, event=None):
        n = len(self.textbox.get("1.0", "end-1c"))
        self.char_count.configure(text=f"{n} chars")

    def _animate_progress(self, val: float, color: str = COLORS["accent_cyan"]):
        self.progress.configure(progress_color=color)
        self.progress.set(val)

    def _set_status(self, msg: str, color: str = COLORS["text_secondary"]):
        self.root.after(0, lambda: self.status_lbl.configure(
            text=msg, text_color=color))


# ─────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────
if __name__ == "__main__":
    root = ctk.CTk()
    app = SpeechConverterApp(root)
    root.mainloop()
"""
Currency Converter - Modern Desktop App
Uses tkinter for UI + exchangerate-api (free, no key needed)
Fallback static rates included if offline
"""

import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import json
import threading

# ─────────────────────────────────────────
# All supported currencies with country names
# ─────────────────────────────────────────
CURRENCIES = {
    "USD": "🇺🇸 US Dollar",
    "EUR": "🇪🇺 Euro",
    "GBP": "🇬🇧 British Pound",
    "JPY": "🇯🇵 Japanese Yen",
    "INR": "🇮🇳 Indian Rupee",
    "AUD": "🇦🇺 Australian Dollar",
    "CAD": "🇨🇦 Canadian Dollar",
    "CHF": "🇨🇭 Swiss Franc",
    "CNY": "🇨🇳 Chinese Yuan",
    "HKD": "🇭🇰 Hong Kong Dollar",
    "NZD": "🇳🇿 New Zealand Dollar",
    "SEK": "🇸🇪 Swedish Krona",
    "NOK": "🇳🇴 Norwegian Krone",
    "DKK": "🇩🇰 Danish Krone",
    "SGD": "🇸🇬 Singapore Dollar",
    "MXN": "🇲🇽 Mexican Peso",
    "BRL": "🇧🇷 Brazilian Real",
    "ZAR": "🇿🇦 South African Rand",
    "AED": "🇦🇪 UAE Dirham",
    "SAR": "🇸🇦 Saudi Riyal",
    "TRY": "🇹🇷 Turkish Lira",
    "RUB": "🇷🇺 Russian Ruble",
    "KRW": "🇰🇷 South Korean Won",
    "IDR": "🇮🇩 Indonesian Rupiah",
    "MYR": "🇲🇾 Malaysian Ringgit",
    "THB": "🇹🇭 Thai Baht",
    "PKR": "🇵🇰 Pakistani Rupee",
    "BDT": "🇧🇩 Bangladeshi Taka",
    "EGP": "🇪🇬 Egyptian Pound",
    "NGN": "🇳🇬 Nigerian Naira",
    "KES": "🇰🇪 Kenyan Shilling",
    "GHS": "🇬🇭 Ghanaian Cedi",
    "TZS": "🇹🇿 Tanzanian Shilling",
    "UAH": "🇺🇦 Ukrainian Hryvnia",
    "PLN": "🇵🇱 Polish Zloty",
    "CZK": "🇨🇿 Czech Koruna",
    "HUF": "🇭🇺 Hungarian Forint",
    "RON": "🇷🇴 Romanian Leu",
    "BGN": "🇧🇬 Bulgarian Lev",
    "HRK": "🇭🇷 Croatian Kuna",
    "ILS": "🇮🇱 Israeli Shekel",
    "CLP": "🇨🇱 Chilean Peso",
    "COP": "🇨🇴 Colombian Peso",
    "PEN": "🇵🇪 Peruvian Sol",
    "ARS": "🇦🇷 Argentine Peso",
    "VND": "🇻🇳 Vietnamese Dong",
    "PHP": "🇵🇭 Philippine Peso",
    "TWD": "🇹🇼 Taiwan Dollar",
    "QAR": "🇶🇦 Qatari Riyal",
    "KWD": "🇰🇼 Kuwaiti Dinar",
    "BHD": "🇧🇭 Bahraini Dinar",
    "OMR": "🇴🇲 Omani Rial",
    "JOD": "🇯🇴 Jordanian Dinar",
    "LKR": "🇱🇰 Sri Lankan Rupee",
    "NPR": "🇳🇵 Nepalese Rupee",
    "MMK": "🇲🇲 Myanmar Kyat",
    "MAD": "🇲🇦 Moroccan Dirham",
    "DZD": "🇩🇿 Algerian Dinar",
    "TND": "🇹🇳 Tunisian Dinar",
    "UGX": "🇺🇬 Ugandan Shilling",
    "ETB": "🇪🇹 Ethiopian Birr",
    "XOF": "🌍 West African CFA Franc",
    "XAF": "🌍 Central African CFA Franc",
    "ISK": "🇮🇸 Icelandic Króna",
    "MZN": "🇲🇿 Mozambican Metical",
    "CRC": "🇨🇷 Costa Rican Colón",
    "GTQ": "🇬🇹 Guatemalan Quetzal",
    "HNL": "🇭🇳 Honduran Lempira",
    "NIO": "🇳🇮 Nicaraguan Córdoba",
    "DOP": "🇩🇴 Dominican Peso",
    "BOB": "🇧🇴 Bolivian Boliviano",
    "PYG": "🇵🇾 Paraguayan Guaraní",
    "UYU": "🇺🇾 Uruguayan Peso",
    "GEL": "🇬🇪 Georgian Lari",
    "AMD": "🇦🇲 Armenian Dram",
    "AZN": "🇦🇿 Azerbaijani Manat",
    "KZT": "🇰🇿 Kazakhstani Tenge",
    "UZS": "🇺🇿 Uzbekistani Som",
    "MNT": "🇲🇳 Mongolian Tögrög",
    "KHR": "🇰🇭 Cambodian Riel",
    "LAK": "🇱🇦 Lao Kip",
    "BND": "🇧🇳 Brunei Dollar",
    "MOP": "🇲🇴 Macanese Pataca",
    "FJD": "🇫🇯 Fijian Dollar",
    "PGK": "🇵🇬 Papua New Guinean Kina",
    "SZL": "🇸🇿 Swazi Lilangeni",
    "LSL": "🇱🇸 Lesotho Loti",
    "NAD": "🇳🇦 Namibian Dollar",
    "BWP": "🇧🇼 Botswanan Pula",
    "ZMW": "🇿🇲 Zambian Kwacha",
    "MWK": "🇲🇼 Malawian Kwacha",
    "RWF": "🇷🇼 Rwandan Franc",
    "MUR": "🇲🇺 Mauritian Rupee",
    "SCR": "🇸🇨 Seychellois Rupee",
    "MVR": "🇲🇻 Maldivian Rufiyaa",
    "BTN": "🇧🇹 Bhutanese Ngultrum",
    "AFN": "🇦🇫 Afghan Afghani",
    "IRR": "🇮🇷 Iranian Rial",
    "IQD": "🇮🇶 Iraqi Dinar",
    "SYP": "🇸🇾 Syrian Pound",
    "YER": "🇾🇪 Yemeni Rial",
    "LBP": "🇱🇧 Lebanese Pound",
    "SDG": "🇸🇩 Sudanese Pound",
    "LYD": "🇱🇾 Libyan Dinar",
    "SOS": "🇸🇴 Somali Shilling",
}

# ─────────────────────────────────────────
# Fallback static rates (vs USD base)
# ─────────────────────────────────────────
FALLBACK_RATES = {
    "USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 149.5, "INR": 83.1,
    "AUD": 1.53, "CAD": 1.36, "CHF": 0.90, "CNY": 7.24, "HKD": 7.82,
    "NZD": 1.63, "SEK": 10.42, "NOK": 10.55, "DKK": 6.88, "SGD": 1.34,
    "MXN": 17.15, "BRL": 4.97, "ZAR": 18.63, "AED": 3.67, "SAR": 3.75,
    "TRY": 32.2, "RUB": 91.5, "KRW": 1325.0, "IDR": 15600.0, "MYR": 4.72,
    "THB": 35.1, "PKR": 278.5, "BDT": 110.0, "EGP": 30.9, "NGN": 1550.0,
    "KES": 131.0, "GHS": 12.5, "TZS": 2530.0, "UAH": 37.2, "PLN": 3.98,
    "CZK": 22.6, "HUF": 356.0, "RON": 4.57, "BGN": 1.80, "ILS": 3.65,
    "CLP": 955.0, "COP": 3950.0, "PEN": 3.72, "ARS": 880.0, "VND": 24800.0,
    "PHP": 56.2, "TWD": 31.5, "QAR": 3.64, "KWD": 0.307, "BHD": 0.377,
    "OMR": 0.385, "JOD": 0.709, "LKR": 315.0, "NPR": 133.5, "MAD": 10.1,
    "ISK": 137.0, "GEL": 2.65, "KZT": 450.0, "MNT": 3450.0, "FJD": 2.25,
}

# ─────────────────────────────────────────
# Fetch live rates
# ─────────────────────────────────────────
rates_cache = {}

def fetch_rates(base="USD", on_done=None):
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            data = json.loads(resp.read())
            if data.get("result") == "success":
                if on_done:
                    on_done(data["rates"], True)
                return
    except Exception:
        pass
    # Fallback: convert FALLBACK_RATES to requested base
    base_rate = FALLBACK_RATES.get(base, 1.0)
    converted = {k: round(v / base_rate, 6) for k, v in FALLBACK_RATES.items()}
    if on_done:
        on_done(converted, False)


# ─────────────────────────────────────────
# Main App
# ─────────────────────────────────────────
class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌍 Currency Converter")
        self.geometry("640x680")
        self.resizable(False, False)
        self.configure(bg="#0D1117")

        self.rates = {}
        self.is_live = False
        self._setup_styles()
        self._build_ui()
        self._load_rates()

    # ── Styles ──────────────────────────
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TCombobox",
            fieldbackground="#161B22",
            background="#161B22",
            foreground="#E6EDF3",
            selectbackground="#238636",
            selectforeground="white",
            arrowcolor="#58A6FF",
            borderwidth=0,
            relief="flat",
            padding=(8, 6),
            font=("Segoe UI", 11)
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", "#161B22")],
            foreground=[("readonly", "#E6EDF3")],
            background=[("active", "#1F2937")],
        )
        style.configure("TScrollbar",
            background="#21262D",
            troughcolor="#0D1117",
            arrowcolor="#58A6FF",
            borderwidth=0
        )

    # ── UI Build ────────────────────────
    def _build_ui(self):
        BG = "#0D1117"
        CARD = "#161B22"
        ACCENT = "#58A6FF"
        GREEN = "#3FB950"
        TEXT = "#E6EDF3"
        MUTED = "#8B949E"

        # Header
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(28, 10))

        tk.Label(header, text="💱", font=("Segoe UI Emoji", 28), bg=BG).pack(side="left")
        title_frame = tk.Frame(header, bg=BG)
        title_frame.pack(side="left", padx=12)
        tk.Label(title_frame, text="Currency Converter",
                 font=("Segoe UI", 20, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        self.status_label = tk.Label(title_frame, text="⏳ Loading rates...",
                 font=("Segoe UI", 9), fg=MUTED, bg=BG)
        self.status_label.pack(anchor="w")

        # Separator
        tk.Frame(self, height=1, bg="#21262D").pack(fill="x", padx=30, pady=8)

        # ── FROM card ──
        from_card = tk.Frame(self, bg=CARD, bd=0)
        from_card.pack(fill="x", padx=30, pady=(10, 6))
        from_card.configure(highlightbackground="#30363D", highlightthickness=1)

        inner_from = tk.Frame(from_card, bg=CARD)
        inner_from.pack(fill="x", padx=18, pady=14)

        tk.Label(inner_from, text="FROM", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")

        from_row = tk.Frame(inner_from, bg=CARD)
        from_row.pack(fill="x", pady=(6, 0))

        self.amount_var = tk.StringVar(value="1")
        self.amount_entry = tk.Entry(from_row, textvariable=self.amount_var,
            font=("Segoe UI", 22, "bold"), fg=TEXT, bg=CARD,
            insertbackground=ACCENT, bd=0, highlightthickness=0, width=10)
        self.amount_entry.pack(side="left")
        self.amount_entry.bind("<KeyRelease>", lambda e: self._convert())

        # From currency dropdown
        currency_list = [f"{code} — {name}" for code, name in sorted(CURRENCIES.items())]
        self.from_var = tk.StringVar(value="USD — 🇺🇸 US Dollar")
        self.from_combo = ttk.Combobox(from_row, textvariable=self.from_var,
            values=currency_list, state="readonly",
            font=("Segoe UI", 11), width=28)
        self.from_combo.pack(side="right")
        self.from_combo.bind("<<ComboboxSelected>>", lambda e: self._on_from_change())

        # ── Swap button ──
        swap_frame = tk.Frame(self, bg=BG)
        swap_frame.pack(pady=4)
        self.swap_btn = tk.Button(swap_frame, text="⇅  Swap",
            font=("Segoe UI", 10, "bold"), fg=ACCENT, bg="#21262D",
            activeforeground=TEXT, activebackground="#30363D",
            bd=0, padx=16, pady=7, cursor="hand2",
            relief="flat", command=self._swap)
        self.swap_btn.pack()

        # ── TO card ──
        to_card = tk.Frame(self, bg=CARD, bd=0)
        to_card.pack(fill="x", padx=30, pady=(6, 12))
        to_card.configure(highlightbackground="#30363D", highlightthickness=1)

        inner_to = tk.Frame(to_card, bg=CARD)
        inner_to.pack(fill="x", padx=18, pady=14)

        tk.Label(inner_to, text="TO", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=CARD).pack(anchor="w")

        to_row = tk.Frame(inner_to, bg=CARD)
        to_row.pack(fill="x", pady=(6, 0))

        self.result_var = tk.StringVar(value="—")
        tk.Label(to_row, textvariable=self.result_var,
            font=("Segoe UI", 22, "bold"), fg=GREEN, bg=CARD, width=10,
            anchor="w").pack(side="left")

        self.to_var = tk.StringVar(value="INR — 🇮🇳 Indian Rupee")
        self.to_combo = ttk.Combobox(to_row, textvariable=self.to_var,
            values=currency_list, state="readonly",
            font=("Segoe UI", 11), width=28)
        self.to_combo.pack(side="right")
        self.to_combo.bind("<<ComboboxSelected>>", lambda e: self._convert())

        # ── Rate info ──
        self.rate_label = tk.Label(self, text="",
            font=("Segoe UI", 10), fg=MUTED, bg=BG)
        self.rate_label.pack(pady=(0, 8))

        # ── Separator ──
        tk.Frame(self, height=1, bg="#21262D").pack(fill="x", padx=30, pady=6)

        # ── Quick convert row ──
        tk.Label(self, text="QUICK AMOUNTS", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=BG).pack(padx=30, anchor="w", pady=(6, 4))

        quick_frame = tk.Frame(self, bg=BG)
        quick_frame.pack(padx=30, fill="x", pady=(0, 10))
        for amt in [1, 10, 50, 100, 500, 1000]:
            btn = tk.Button(quick_frame, text=str(amt),
                font=("Segoe UI", 10), fg=TEXT, bg="#21262D",
                activeforeground=TEXT, activebackground="#30363D",
                bd=0, padx=12, pady=6, cursor="hand2", relief="flat",
                command=lambda a=amt: self._set_quick(a))
            btn.pack(side="left", padx=3)

        # ── Popular pairs ──
        tk.Frame(self, height=1, bg="#21262D").pack(fill="x", padx=30, pady=6)
        tk.Label(self, text="POPULAR PAIRS", font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=BG).pack(padx=30, anchor="w", pady=(4, 6))

        pairs_frame = tk.Frame(self, bg=BG)
        pairs_frame.pack(padx=30, fill="x")
        self.pair_labels = []
        pairs = [("USD","EUR"),("USD","GBP"),("USD","JPY"),("USD","INR"),
                 ("EUR","GBP"),("GBP","JPY")]
        for i, (a, b) in enumerate(pairs):
            row = i // 3
            col = i % 3
            lbl = tk.Label(pairs_frame, text=f"{a}/{b}\n—",
                font=("Segoe UI", 9), fg=TEXT, bg="#161B22",
                width=12, pady=8, cursor="hand2",
                highlightbackground="#30363D", highlightthickness=1)
            lbl.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            lbl.bind("<Button-1>", lambda e, x=a, y=b: self._set_pair(x, y))
            self.pair_labels.append((lbl, a, b))

        # ── Footer ──
        self.footer = tk.Label(self, text="",
            font=("Segoe UI", 8), fg=MUTED, bg=BG)
        self.footer.pack(pady=12)

    # ── Logic ───────────────────────────
    def _load_rates(self):
        def on_done(rates, live):
            self.rates = rates
            self.is_live = live
            status = f"✅ Live rates loaded" if live else "⚠️ Using offline rates"
            self.status_label.config(text=status, fg="#3FB950" if live else "#F0883E")
            self._convert()
            self._update_pairs()
            self.footer.config(text="Powered by open.er-api.com  •  Rates update every 24h")

        threading.Thread(target=lambda: fetch_rates("USD", on_done), daemon=True).start()

    def _get_code(self, combo_val):
        return combo_val.split(" — ")[0].strip()

    def _convert(self):
        try:
            amount = float(self.amount_var.get().replace(",", ""))
        except ValueError:
            self.result_var.set("—")
            self.rate_label.config(text="Enter a valid number")
            return

        from_code = self._get_code(self.from_var.get())
        to_code = self._get_code(self.to_var.get())

        if not self.rates:
            self.result_var.set("Loading...")
            return

        # Convert via USD base
        from_rate = self.rates.get(from_code, 1.0)
        to_rate = self.rates.get(to_code, 1.0)

        # If rates are USD-based
        result = (amount / from_rate) * to_rate
        rate = to_rate / from_rate

        # Format large numbers
        if result >= 1_000_000:
            fmt_result = f"{result:,.2f}"
        elif result >= 1000:
            fmt_result = f"{result:,.2f}"
        elif result < 0.01:
            fmt_result = f"{result:.6f}"
        else:
            fmt_result = f"{result:,.4f}"

        self.result_var.set(fmt_result)

        # Rate label
        r_fmt = f"{rate:.6f}".rstrip("0").rstrip(".")
        self.rate_label.config(
            text=f"1 {from_code} = {r_fmt} {to_code}"
        )

    def _on_from_change(self):
        # Reload rates for new base currency for accuracy
        self._convert()

    def _swap(self):
        from_val = self.from_var.get()
        to_val = self.to_var.get()
        self.from_var.set(to_val)
        self.to_var.set(from_val)
        self._convert()

    def _set_quick(self, amount):
        self.amount_var.set(str(amount))
        self._convert()

    def _set_pair(self, a, b):
        currency_list_keys = sorted(CURRENCIES.keys())
        for code in currency_list_keys:
            if code == a:
                self.from_var.set(f"{a} — {CURRENCIES[a]}")
            if code == b:
                self.to_var.set(f"{b} — {CURRENCIES[b]}")
        self._convert()

    def _update_pairs(self):
        for lbl, a, b in self.pair_labels:
            ra = self.rates.get(a, 1.0)
            rb = self.rates.get(b, 1.0)
            rate = rb / ra
            r_fmt = f"{rate:.4f}".rstrip("0").rstrip(".")
            lbl.config(text=f"{a}/{b}\n{r_fmt}")


# ─────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()
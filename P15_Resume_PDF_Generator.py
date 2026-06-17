"""
Beautiful Resume PDF Generator — Canvas-based for full design control
Author: Jainam | Tools: ReportLab canvas
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading, os, re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Theme ──────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_DARK  = "#0f1117"
BG_CARD  = "#1a1d2e"
BG_INPUT = "#12151f"
ACCENT   = "#6c63ff"
ACCENT2  = "#00d4aa"
TEXT_PRI = "#e8eaf6"
TEXT_SEC = "#8b92b8"
BORDER   = "#2a2d3e"
SUCCESS  = "#00d4aa"
ERROR    = "#ff6b6b"


def hex_color(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    return colors.Color(r, g, b)


# ══════════════════════════════════════════════════════════════════════════════
#  BEAUTIFUL PDF ENGINE — pure canvas for pixel-perfect control
# ══════════════════════════════════════════════════════════════════════════════

class BeautifulResumePDF:
    # Brand palette
    C_PRIMARY   = hex_color("#1a1a2e")   # deep navy — left sidebar bg
    C_ACCENT    = hex_color("#6c63ff")   # purple accent
    C_ACCENT2   = hex_color("#00d4aa")   # teal
    C_WHITE     = colors.white
    C_LIGHT     = hex_color("#f0f2ff")   # very light lavender page bg
    C_DARK      = hex_color("#1a1d2e")
    C_BODY      = hex_color("#2d3250")
    C_MUTED     = hex_color("#6b7280")
    C_RULE      = hex_color("#e2e4f0")
    C_TAG_BG    = hex_color("#ede9fe")   # light purple tag bg
    C_TAG_TXT   = hex_color("#4c1d95")   # dark purple tag text

    SIDEBAR_W   = 62 * mm
    LEFT_M      = 68 * mm
    RIGHT_M     = 14 * mm
    TOP_M       = 0
    PAGE_W, PAGE_H = A4

    def __init__(self, data: dict, path: str):
        self.d   = data
        self.path = path
        self.W, self.H = A4
        self.c   = canvas.Canvas(path, pagesize=A4)
        self.y   = self.H   # current y cursor (right column)
        self.sy  = self.H   # sidebar y cursor
        self.content_w = self.W - self.LEFT_M - self.RIGHT_M

    # ── drawing helpers ────────────────────────────────────────────────────
    def _font(self, name="Helvetica", size=10):
        self.c.setFont(name, size)

    def _color(self, col):
        self.c.setFillColor(col)

    def _stroke(self, col):
        self.c.setStrokeColor(col)

    def _rect(self, x, y, w, h, fill_color, stroke=False):
        self.c.setFillColor(fill_color)
        if stroke:
            self.c.rect(x, y, w, h, fill=1, stroke=1)
        else:
            self.c.rect(x, y, w, h, fill=1, stroke=0)

    def _text(self, x, y, text, font="Helvetica", size=10, color=None):
        if color:
            self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawString(x, y, str(text))

    def _text_right(self, x, y, text, font="Helvetica", size=10, color=None):
        if color:
            self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawRightString(x, y, str(text))

    def _wrap_text(self, text, max_width, font="Helvetica", size=9):
        """Split text into lines that fit max_width."""
        self.c.setFont(font, size)
        words = str(text).split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            if self.c.stringWidth(test, font, size) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    def _draw_wrapped(self, x, y, text, max_w, font="Helvetica", size=9,
                      color=None, line_h=5*mm):
        """Draw wrapped text, return new y."""
        lines = self._wrap_text(text, max_w, font, size)
        for ln in lines:
            self._text(x, y, ln, font, size, color)
            y -= line_h
        return y

    # ── sidebar section header ─────────────────────────────────────────────
    def _sidebar_section(self, title):
        y = self.sy - 8*mm
        # Teal rule
        self.c.setStrokeColor(self.C_ACCENT2)
        self.c.setLineWidth(1.5)
        self.c.line(6*mm, y, self.SIDEBAR_W - 4*mm, y)
        y -= 5*mm
        self._text(6*mm, y, title.upper(), "Helvetica-Bold", 7,
                   color=self.C_ACCENT2)
        self.sy = y - 5*mm

    # ── main section header ─────────────────────────────────────────────────
    def _main_section(self, title):
        y = self.y - 6*mm
        # accent bar left
        self._rect(self.LEFT_M, y + 1*mm, 3, 6*mm, self.C_ACCENT)
        self._text(self.LEFT_M + 5*mm, y + 1.5*mm, title.upper(),
                   "Helvetica-Bold", 10, color=self.C_ACCENT)
        y -= 2*mm
        # light rule
        self.c.setStrokeColor(self.C_RULE)
        self.c.setLineWidth(0.5)
        self.c.line(self.LEFT_M, y, self.W - self.RIGHT_M, y)
        self.y = y - 5*mm

    # ── bullet point ─────────────────────────────────────────────────────────
    def _bullet(self, x, y, text, max_w, color=None, size=8.5):
        col = color or self.C_BODY
        # draw dot
        self.c.setFillColor(self.C_ACCENT2)
        self.c.circle(x + 2*mm, y + 1.5, 1.2, fill=1, stroke=0)
        y = self._draw_wrapped(x + 5*mm, y, text,
                               max_w - 5*mm, size=size, color=col)
        return y

    # ── skill tag (sidebar) ───────────────────────────────────────────────
    def _skill_tag(self, x, y, text):
        self.c.setFont("Helvetica", 7)
        tw = self.c.stringWidth(text, "Helvetica", 7)
        pad = 3
        bw = tw + pad * 2
        bh = 4.5 * mm
        # rounded rect approximated with rect
        self._rect(x, y, bw, bh, self.C_ACCENT, stroke=False)
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont("Helvetica-Bold", 7)
        self.c.drawString(x + pad, y + 1.5, text)
        return bw + 2*mm   # return width used

    # ══════════════════════════════════════════════════════════════════════
    #  BUILD
    # ══════════════════════════════════════════════════════════════════════
    def build(self):
        d = self.d

        # ── BACKGROUND ──────────────────────────────────────────────────
        # Full page light
        self._rect(0, 0, self.W, self.H, self.C_LIGHT)
        # Left sidebar navy
        self._rect(0, 0, self.SIDEBAR_W, self.H, self.C_PRIMARY)
        # Accent top strip
        self._rect(0, self.H - 3*mm, self.W, 3*mm, self.C_ACCENT)
        # Accent bottom strip
        self._rect(0, 0, self.W, 2*mm, self.C_ACCENT2)

        # ── HEADER (full width top band) ─────────────────────────────────
        header_h = 46 * mm
        self._rect(0, self.H - 3*mm - header_h, self.W, header_h, self.C_DARK)

        # Name
        name = d.get("name", "Your Name")
        self._text(self.LEFT_M, self.H - 3*mm - 14*mm,
                   name, "Helvetica-Bold", 26, color=self.C_WHITE)

        # Job title
        job = d.get("job_title", "")
        if job:
            self._text(self.LEFT_M, self.H - 3*mm - 22*mm,
                       job, "Helvetica-Oblique", 11, color=self.C_ACCENT2)

        # Contact line
        contact_parts = []
        if d.get("email"):    contact_parts.append("✉  " + d["email"])
        if d.get("phone"):    contact_parts.append("✆  " + d["phone"])
        if d.get("location"): contact_parts.append("⊙  " + d["location"])
        contact_str = "   |   ".join(contact_parts)
        self._text(self.LEFT_M, self.H - 3*mm - 30*mm,
                   contact_str, "Helvetica", 8, color=hex_color("#aab0d0"))

        links = []
        if d.get("linkedin"): links.append("in  " + d["linkedin"])
        if d.get("github"):   links.append("⌥  " + d["github"])
        link_str = "   |   ".join(links)
        self._text(self.LEFT_M, self.H - 3*mm - 36*mm,
                   link_str, "Helvetica", 8, color=hex_color("#aab0d0"))

        # Sidebar photo placeholder circle
        cx, cy = self.SIDEBAR_W / 2, self.H - 3*mm - 22*mm
        r = 15 * mm
        self.c.setFillColor(hex_color("#2a2d4e"))
        self.c.setStrokeColor(self.C_ACCENT2)
        self.c.setLineWidth(2)
        self.c.circle(cx, cy, r, fill=1, stroke=1)
        initials = "".join(w[0].upper() for w in name.split()[:2])
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawCentredString(cx, cy - 4, initials)

        # ── SET CURSORS ──────────────────────────────────────────────────
        self.y  = self.H - 3*mm - header_h - 6*mm
        self.sy = self.H - 3*mm - header_h - 4*mm

        # ══════════════════════════════════════════════════════════════
        #  SIDEBAR CONTENT
        # ══════════════════════════════════════════════════════════════

        # ── SKILLS (sidebar) ─────────────────────────────────────────
        skills_raw = d.get("skills", "")
        if skills_raw.strip():
            self._sidebar_section("Skills")
            skill_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
            sx = 6 * mm
            sy = self.sy
            row_x = sx
            for sk in skill_list:
                self.c.setFont("Helvetica", 7)
                tw = self.c.stringWidth(sk, "Helvetica", 7) + 6
                if row_x + tw > self.SIDEBAR_W - 4*mm:
                    row_x = sx
                    sy -= 6.5 * mm
                used = self._skill_tag(row_x, sy, sk)
                row_x += used
            self.sy = sy - 9 * mm

        # ── EDUCATION (sidebar) ──────────────────────────────────────
        edus = d.get("educations", [])
        if any(e.get("institution") for e in edus):
            self._sidebar_section("Education")
            for edu in edus:
                if not edu.get("institution"):
                    continue
                # Institution
                inst_lines = self._wrap_text(edu["institution"],
                                             self.SIDEBAR_W - 10*mm,
                                             "Helvetica-Bold", 8)
                for ln in inst_lines:
                    self._text(6*mm, self.sy, ln, "Helvetica-Bold", 8,
                               color=self.C_WHITE)
                    self.sy -= 4.5*mm
                # Degree
                if edu.get("degree"):
                    deg_lines = self._wrap_text(edu["degree"],
                                                self.SIDEBAR_W - 10*mm,
                                                "Helvetica", 7)
                    for ln in deg_lines:
                        self._text(6*mm, self.sy, ln, "Helvetica", 7,
                                   color=hex_color("#8b92b8"))
                        self.sy -= 4*mm
                if edu.get("dates"):
                    self._text(6*mm, self.sy, edu["dates"],
                               "Helvetica-Oblique", 7, color=self.C_ACCENT2)
                    self.sy -= 3.5*mm
                if edu.get("grade"):
                    self._text(6*mm, self.sy, "CGPA: " + edu["grade"],
                               "Helvetica", 7, color=hex_color("#aab0d0"))
                    self.sy -= 5*mm

        # ── CERTIFICATIONS (sidebar) ─────────────────────────────────
        certs = d.get("certifications", "")
        if certs.strip():
            self._sidebar_section("Certifications")
            for line in certs.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # small bullet
                self.c.setFillColor(self.C_ACCENT2)
                self.c.circle(8*mm, self.sy + 1.5, 1.2, fill=1, stroke=0)
                cert_lines = self._wrap_text(line,
                                             self.SIDEBAR_W - 14*mm,
                                             "Helvetica", 7)
                for ln in cert_lines:
                    self._text(11*mm, self.sy, ln, "Helvetica", 7,
                               color=hex_color("#c8cce8"))
                    self.sy -= 4.5*mm

        # ══════════════════════════════════════════════════════════════
        #  MAIN COLUMN CONTENT
        # ══════════════════════════════════════════════════════════════
        main_max_w = self.W - self.LEFT_M - self.RIGHT_M

        # ── PROFESSIONAL SUMMARY ────────────────────────────────────
        summary = d.get("summary", "")
        if summary.strip():
            self._main_section("Professional Summary")
            self.y = self._draw_wrapped(
                self.LEFT_M, self.y, summary,
                main_max_w, size=9, color=self.C_BODY, line_h=5*mm)
            self.y -= 2*mm

        # ── WORK EXPERIENCE ──────────────────────────────────────────
        exps = d.get("experiences", [])
        if any(e.get("company") or e.get("role") for e in exps):
            self._main_section("Work Experience")
            for exp in exps:
                if not (exp.get("company") or exp.get("role")):
                    continue
                # Company + dates row
                company = exp.get("company", "")
                dates   = exp.get("dates", "")
                role    = exp.get("role", "")
                desc    = exp.get("description", "")

                self._text(self.LEFT_M, self.y, company,
                           "Helvetica-Bold", 10, color=self.C_BODY)
                self._text_right(self.W - self.RIGHT_M, self.y, dates,
                                 "Helvetica", 8, color=self.C_MUTED)
                self.y -= 5*mm

                if role:
                    # pill badge for role
                    self.c.setFont("Helvetica-Oblique", 8.5)
                    rw = self.c.stringWidth(role, "Helvetica-Oblique", 8.5)
                    self._rect(self.LEFT_M, self.y - 1, rw + 8, 5*mm,
                               self.C_TAG_BG)
                    self._text(self.LEFT_M + 4, self.y + 1, role,
                               "Helvetica-Oblique", 8.5, color=self.C_ACCENT)
                    self.y -= 6.5*mm

                for line in desc.split("\n"):
                    line = line.strip().lstrip("•").strip()
                    if not line:
                        continue
                    self.y = self._bullet(self.LEFT_M, self.y, line,
                                          main_max_w, color=self.C_BODY)
                    self.y -= 1*mm
                self.y -= 3*mm

        # ── PROJECTS ────────────────────────────────────────────────
        projs = d.get("projects", [])
        if any(p.get("name") for p in projs):
            self._main_section("Projects")
            for proj in projs:
                if not proj.get("name"):
                    continue
                name_str = proj["name"]
                tech = proj.get("tech", "")
                link = proj.get("link", "")
                desc = proj.get("description", "")

                # Project name + tech stack
                self._text(self.LEFT_M, self.y, name_str,
                           "Helvetica-Bold", 10, color=self.C_BODY)
                if tech:
                    self._text_right(self.W - self.RIGHT_M, self.y,
                                     tech, "Helvetica", 7.5,
                                     color=self.C_ACCENT)
                self.y -= 5*mm

                if link:
                    self._text(self.LEFT_M, self.y, link,
                               "Helvetica-Oblique", 7.5,
                               color=self.C_MUTED)
                    self.y -= 4.5*mm

                for line in desc.split("\n"):
                    line = line.strip().lstrip("•").strip()
                    if not line:
                        continue
                    self.y = self._bullet(self.LEFT_M, self.y, line,
                                          main_max_w, color=self.C_BODY)
                    self.y -= 0.5*mm
                self.y -= 3*mm

        # ── footer rule ──────────────────────────────────────────────
        self.c.setStrokeColor(self.C_RULE)
        self.c.setLineWidth(0.5)
        self.c.line(self.LEFT_M, 8*mm, self.W - self.RIGHT_M, 8*mm)
        self._text(self.LEFT_M, 4.5*mm,
                   d.get("email", "") + "  |  " + d.get("github", ""),
                   "Helvetica", 7, color=self.C_MUTED)

        self.c.save()
        return self.path


# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS (same dark-theme pattern you love)
# ══════════════════════════════════════════════════════════════════════════════

def labeled_entry(parent, label, placeholder="", row=0, col=0, colspan=1):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid(row=row, column=col, columnspan=colspan,
               padx=10, pady=(6, 2), sticky="ew")
    ctk.CTkLabel(frame, text=label, text_color=TEXT_SEC,
                 font=("Segoe UI", 11), anchor="w").pack(anchor="w")
    entry = ctk.CTkEntry(
        frame, placeholder_text=placeholder, height=36,
        fg_color=BG_INPUT, border_color=BORDER,
        text_color=TEXT_PRI, placeholder_text_color=TEXT_SEC,
        font=("Segoe UI", 11), corner_radius=8
    )
    entry.pack(fill="x", expand=True)
    return entry

def labeled_textbox(parent, label, height=80, row=0, col=0, colspan=1):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid(row=row, column=col, columnspan=colspan,
               padx=10, pady=(6, 2), sticky="ew")
    ctk.CTkLabel(frame, text=label, text_color=TEXT_SEC,
                 font=("Segoe UI", 11), anchor="w").pack(anchor="w")
    tb = ctk.CTkTextbox(
        frame, height=height,
        fg_color=BG_INPUT, border_color=BORDER,
        text_color=TEXT_PRI, font=("Segoe UI", 11),
        corner_radius=8, border_width=1
    )
    tb.pack(fill="x", expand=True)
    return tb

def section_card(parent, title, row=0):
    card = ctk.CTkFrame(parent, fg_color=BG_CARD,
                        corner_radius=14, border_color=BORDER, border_width=1)
    card.grid(row=row, column=0, padx=20, pady=(0, 14), sticky="ew")
    card.columnconfigure(0, weight=1)
    card.columnconfigure(1, weight=1)
    title_bar = ctk.CTkFrame(card, fg_color=BG_DARK, corner_radius=10)
    title_bar.grid(row=0, column=0, columnspan=2,
                   sticky="ew", padx=12, pady=(12, 4))
    ctk.CTkLabel(title_bar, text=f"  {title}",
                 font=("Segoe UI", 13, "bold"),
                 text_color=ACCENT).pack(anchor="w", padx=6, pady=6)
    return card


# ── Dynamic blocks ────────────────────────────────────────────────────────────

class ExperienceBlock(ctk.CTkFrame):
    def __init__(self, parent, index=1, on_remove=None, **kw):
        super().__init__(parent, fg_color="#12151f", corner_radius=10,
                         border_width=1, border_color=BORDER, **kw)
        self.on_remove = on_remove
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8,0))
        ctk.CTkLabel(hdr, text=f"Experience #{index}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=ACCENT2).pack(side="left")
        if on_remove:
            ctk.CTkButton(hdr, text="✕ Remove", width=80, height=24,
                          fg_color="#2a1f2f", hover_color="#ff6b6b",
                          text_color="#ff6b6b", font=("Segoe UI", 10),
                          corner_radius=6, command=on_remove).pack(side="right")
        self.e_company = labeled_entry(self, "Company", row=1, col=0)
        self.e_role    = labeled_entry(self, "Role", row=1, col=1)
        self.e_dates   = labeled_entry(self, "Dates", row=2, col=0)
        self.e_desc    = labeled_textbox(self, "Bullet points (one per line)",
                                        height=70, row=3, col=0, colspan=2)

    def get_data(self):
        return {
            "company":     self.e_company.get().strip(),
            "role":        self.e_role.get().strip(),
            "dates":       self.e_dates.get().strip(),
            "description": self.e_desc.get("1.0", "end").strip(),
        }


class EducationBlock(ctk.CTkFrame):
    def __init__(self, parent, index=1, on_remove=None, **kw):
        super().__init__(parent, fg_color="#12151f", corner_radius=10,
                         border_width=1, border_color=BORDER, **kw)
        self.on_remove = on_remove
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8,0))
        ctk.CTkLabel(hdr, text=f"Education #{index}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=ACCENT2).pack(side="left")
        if on_remove:
            ctk.CTkButton(hdr, text="✕ Remove", width=80, height=24,
                          fg_color="#2a1f2f", hover_color="#ff6b6b",
                          text_color="#ff6b6b", font=("Segoe UI", 10),
                          corner_radius=6, command=on_remove).pack(side="right")
        self.e_inst   = labeled_entry(self, "Institution", row=1, col=0)
        self.e_degree = labeled_entry(self, "Degree", row=1, col=1)
        self.e_dates  = labeled_entry(self, "Years", row=2, col=0)
        self.e_grade  = labeled_entry(self, "Grade / CGPA", row=2, col=1)

    def get_data(self):
        return {
            "institution": self.e_inst.get().strip(),
            "degree":      self.e_degree.get().strip(),
            "dates":       self.e_dates.get().strip(),
            "grade":       self.e_grade.get().strip(),
        }


class ProjectBlock(ctk.CTkFrame):
    def __init__(self, parent, index=1, on_remove=None, **kw):
        super().__init__(parent, fg_color="#12151f", corner_radius=10,
                         border_width=1, border_color=BORDER, **kw)
        self.on_remove = on_remove
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8,0))
        ctk.CTkLabel(hdr, text=f"Project #{index}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=ACCENT2).pack(side="left")
        if on_remove:
            ctk.CTkButton(hdr, text="✕ Remove", width=80, height=24,
                          fg_color="#2a1f2f", hover_color="#ff6b6b",
                          text_color="#ff6b6b", font=("Segoe UI", 10),
                          corner_radius=6, command=on_remove).pack(side="right")
        self.e_name = labeled_entry(self, "Project Name", row=1, col=0)
        self.e_tech = labeled_entry(self, "Tech Stack", row=1, col=1)
        self.e_link = labeled_entry(self, "GitHub / Live Link",
                                    row=2, col=0, colspan=2)
        self.e_desc = labeled_textbox(self, "Description (one point per line)",
                                      height=65, row=3, col=0, colspan=2)

    def get_data(self):
        return {
            "name":        self.e_name.get().strip(),
            "tech":        self.e_tech.get().strip(),
            "link":        self.e_link.get().strip(),
            "description": self.e_desc.get("1.0", "end").strip(),
        }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

class ResumePDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✨ Beautiful Resume PDF Generator")
        self.geometry("1100x820")
        self.minsize(900, 700)
        self.configure(fg_color=BG_DARK)
        self._exp_blocks  = []
        self._edu_blocks  = []
        self._proj_blocks = []
        self._build_ui()
        self._load_demo()

    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=BG_CARD, width=220,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = ctk.CTkFrame(self.sidebar, fg_color=BG_DARK, corner_radius=12)
        logo.pack(fill="x", padx=16, pady=(20, 12))
        ctk.CTkLabel(logo, text="📄", font=("Segoe UI", 28)).pack(pady=(10,0))
        ctk.CTkLabel(logo, text="Resume\nGenerator",
                     font=("Segoe UI", 13, "bold"),
                     text_color=ACCENT).pack(pady=(2, 10))

        for label, y_frac in [
            ("👤  Personal", 0.0),
            ("💼  Experience", 0.15),
            ("🎓  Education", 0.38),
            ("⚡  Skills", 0.54),
            ("🚀  Projects", 0.62),
            ("🏅  Certifications", 0.86),
        ]:
            ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                fg_color="transparent", hover_color=BG_INPUT,
                text_color=TEXT_SEC, font=("Segoe UI", 12),
                height=38, corner_radius=8,
                command=lambda f=y_frac: self.main_frame._parent_canvas.yview_moveto(f)
            ).pack(fill="x", padx=12, pady=2)

        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True)

        ctk.CTkButton(
            self.sidebar, text="⬇  Generate PDF", height=46,
            fg_color=ACCENT, hover_color="#5a52d5",
            font=("Segoe UI", 13, "bold"), corner_radius=12,
            command=self._generate
        ).pack(fill="x", padx=16, pady=(0,16))

        # Main
        self.main_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG_DARK, scrollbar_fg_color=BG_CARD)
        self.main_frame.pack(side="left", fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        topbar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        ctk.CTkLabel(topbar, text="Build Your Resume",
                     font=("Segoe UI", 22, "bold"),
                     text_color=TEXT_PRI).pack(side="left")
        ctk.CTkLabel(topbar, text="✨ Modern two-column design",
                     font=("Segoe UI", 11),
                     text_color=TEXT_SEC).pack(side="left", padx=16)

        self.status_var = ctk.StringVar(value="")
        self.status_lbl = ctk.CTkLabel(
            self.main_frame, textvariable=self.status_var,
            font=("Segoe UI", 11), text_color=SUCCESS)
        self.status_lbl.grid(row=1, column=0, sticky="w", padx=24)

        self._build_personal(row=2)
        self._build_experience(row=3)
        self._build_education(row=4)
        self._build_skills(row=5)
        self._build_projects(row=6)
        self._build_certs(row=7)

        ctk.CTkButton(
            self.main_frame, text="⬇   Generate Beautiful Resume PDF",
            height=52, fg_color=ACCENT, hover_color="#5a52d5",
            font=("Segoe UI", 14, "bold"), corner_radius=14,
            command=self._generate
        ).grid(row=8, column=0, padx=20, pady=(10,30), sticky="ew")

    def _build_personal(self, row):
        c = section_card(self.main_frame, "👤  Personal Information", row=row)
        self.e_name     = labeled_entry(c, "Full Name *", row=1, col=0)
        self.e_title    = labeled_entry(c, "Job Title", row=1, col=1)
        self.e_email    = labeled_entry(c, "Email *", row=2, col=0)
        self.e_phone    = labeled_entry(c, "Phone", row=2, col=1)
        self.e_location = labeled_entry(c, "Location", row=3, col=0)
        self.e_linkedin = labeled_entry(c, "LinkedIn", row=3, col=1)
        self.e_github   = labeled_entry(c, "GitHub", row=4, col=0)
        self.e_summary  = labeled_textbox(c, "Professional Summary",
                                          height=75, row=5, col=0, colspan=2)

    def _build_experience(self, row):
        self.exp_card = section_card(self.main_frame, "💼  Work Experience", row=row)
        self.exp_card.columnconfigure(0, weight=1)
        self.exp_container = ctk.CTkFrame(self.exp_card, fg_color="transparent")
        self.exp_container.grid(row=1, column=0, columnspan=2,
                                sticky="ew", padx=10, pady=4)
        self.exp_container.columnconfigure(0, weight=1)
        ctk.CTkButton(
            self.exp_card, text="+ Add Experience", height=36,
            fg_color=BG_INPUT, hover_color=BORDER,
            text_color=ACCENT2, font=("Segoe UI", 12),
            border_color=ACCENT2, border_width=1,
            corner_radius=8, command=self._add_exp
        ).grid(row=2, column=0, padx=12, pady=(4,12), sticky="w")

    def _add_exp(self):
        idx = len(self._exp_blocks) + 1
        b = ExperienceBlock(self.exp_container, index=idx,
                            on_remove=lambda bl=None: self._rm(
                                self._exp_blocks, b, self.exp_container))
        b.grid(row=idx-1, column=0, sticky="ew", pady=(0,8))
        self._exp_blocks.append(b)

    def _build_education(self, row):
        self.edu_card = section_card(self.main_frame, "🎓  Education", row=row)
        self.edu_card.columnconfigure(0, weight=1)
        self.edu_container = ctk.CTkFrame(self.edu_card, fg_color="transparent")
        self.edu_container.grid(row=1, column=0, columnspan=2,
                                sticky="ew", padx=10, pady=4)
        self.edu_container.columnconfigure(0, weight=1)
        ctk.CTkButton(
            self.edu_card, text="+ Add Education", height=36,
            fg_color=BG_INPUT, hover_color=BORDER,
            text_color=ACCENT2, font=("Segoe UI", 12),
            border_color=ACCENT2, border_width=1,
            corner_radius=8, command=self._add_edu
        ).grid(row=2, column=0, padx=12, pady=(4,12), sticky="w")

    def _add_edu(self):
        idx = len(self._edu_blocks) + 1
        b = EducationBlock(self.edu_container, index=idx,
                           on_remove=lambda bl=None: self._rm(
                               self._edu_blocks, b, self.edu_container))
        b.grid(row=idx-1, column=0, sticky="ew", pady=(0,8))
        self._edu_blocks.append(b)

    def _build_skills(self, row):
        c = section_card(self.main_frame, "⚡  Skills", row=row)
        ctk.CTkLabel(c, text="Comma-separated skills — shown as coloured tags",
                     text_color=TEXT_SEC, font=("Segoe UI", 10)
                     ).grid(row=1, column=0, padx=16, pady=(0,2), sticky="w")
        self.e_skills = ctk.CTkTextbox(
            c, height=70, fg_color=BG_INPUT, border_color=BORDER,
            text_color=TEXT_PRI, font=("Segoe UI", 11),
            corner_radius=8, border_width=1)
        self.e_skills.grid(row=2, column=0, padx=14, pady=(0,14), sticky="ew")

    def _build_projects(self, row):
        self.proj_card = section_card(self.main_frame, "🚀  Projects", row=row)
        self.proj_card.columnconfigure(0, weight=1)
        self.proj_container = ctk.CTkFrame(self.proj_card, fg_color="transparent")
        self.proj_container.grid(row=1, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=4)
        self.proj_container.columnconfigure(0, weight=1)
        ctk.CTkButton(
            self.proj_card, text="+ Add Project", height=36,
            fg_color=BG_INPUT, hover_color=BORDER,
            text_color=ACCENT2, font=("Segoe UI", 12),
            border_color=ACCENT2, border_width=1,
            corner_radius=8, command=self._add_proj
        ).grid(row=2, column=0, padx=12, pady=(4,12), sticky="w")

    def _add_proj(self):
        idx = len(self._proj_blocks) + 1
        b = ProjectBlock(self.proj_container, index=idx,
                         on_remove=lambda bl=None: self._rm(
                             self._proj_blocks, b, self.proj_container))
        b.grid(row=idx-1, column=0, sticky="ew", pady=(0,8))
        self._proj_blocks.append(b)

    def _build_certs(self, row):
        c = section_card(self.main_frame, "🏅  Certifications & Awards", row=row)
        ctk.CTkLabel(c, text="One per line",
                     text_color=TEXT_SEC, font=("Segoe UI", 10)
                     ).grid(row=1, column=0, padx=16, pady=(0,2), sticky="w")
        self.e_certs = ctk.CTkTextbox(
            c, height=80, fg_color=BG_INPUT, border_color=BORDER,
            text_color=TEXT_PRI, font=("Segoe UI", 11),
            corner_radius=8, border_width=1)
        self.e_certs.grid(row=2, column=0, padx=14, pady=(0,14), sticky="ew")

    def _rm(self, lst, block, container):
        if block in lst:
            lst.remove(block)
            block.destroy()
            for i, b in enumerate(lst):
                b.grid(row=i, column=0, sticky="ew", pady=(0,8))

    def _collect(self):
        return {
            "name":           self.e_name.get().strip(),
            "job_title":      self.e_title.get().strip(),
            "email":          self.e_email.get().strip(),
            "phone":          self.e_phone.get().strip(),
            "location":       self.e_location.get().strip(),
            "linkedin":       self.e_linkedin.get().strip(),
            "github":         self.e_github.get().strip(),
            "summary":        self.e_summary.get("1.0","end").strip(),
            "experiences":    [b.get_data() for b in self._exp_blocks],
            "educations":     [b.get_data() for b in self._edu_blocks],
            "skills":         self.e_skills.get("1.0","end").strip(),
            "projects":       [b.get_data() for b in self._proj_blocks],
            "certifications": self.e_certs.get("1.0","end").strip(),
        }

    def _generate(self):
        data = self._collect()
        if not data["name"]:
            self.status_var.set("⚠  Full Name is required.")
            self.status_lbl.configure(text_color=ERROR)
            return
        if not data["email"] or not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            self.status_var.set("⚠  Valid email is required.")
            self.status_lbl.configure(text_color=ERROR)
            return

        default = re.sub(r"[^a-zA-Z0-9_]","_",data["name"]) + "_Resume.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files","*.pdf")],
            initialfile=default, title="Save Resume PDF"
        )
        if not path:
            return

        self.status_var.set("⏳  Building your beautiful PDF…")
        self.status_lbl.configure(text_color=TEXT_SEC)

        def worker():
            try:
                BeautifulResumePDF(data, path).build()
                self.after(0, lambda: self._ok(path))
            except Exception as ex:
                self.after(0, lambda: self._err(str(ex)))

        threading.Thread(target=worker, daemon=True).start()

    def _ok(self, path):
        self.status_var.set(f"✅  Saved → {os.path.basename(path)}")
        self.status_lbl.configure(text_color=SUCCESS)
        messagebox.showinfo("Done!", f"Resume saved:\n{path}")

    def _err(self, msg):
        self.status_var.set(f"❌  {msg}")
        self.status_lbl.configure(text_color=ERROR)
        messagebox.showerror("Error", msg)

    def _load_demo(self):
        self.e_name.insert(0, "Jainam Shah")
        self.e_title.insert(0, "Full-Stack Developer & Data Scientist")
        self.e_email.insert(0, "jainam@example.com")
        self.e_phone.insert(0, "+91 98765 43210")
        self.e_location.insert(0, "Ahmedabad, Gujarat, India")
        self.e_linkedin.insert(0, "linkedin.com/in/jainam259")
        self.e_github.insert(0, "github.com/Jainam259")
        self.e_summary.insert("1.0",
            "Motivated BCA student at GLS University with hands-on experience in "
            "full-stack web development, Python desktop tools, and AI/ML integration. "
            "Passionate about building polished, user-friendly applications backed by "
            "clean, maintainable code.")

        self._add_exp()
        b = self._exp_blocks[-1]
        b.e_company.insert(0, "Way to Web — Internship")
        b.e_role.insert(0, "Web Development Intern")
        b.e_dates.insert(0, "Jan 2025 – Mar 2025")
        b.e_desc.insert("1.0",
            "Built and deployed responsive Flask web applications with clean dark-themed UIs\n"
            "Developed RESTful APIs and integrated third-party data sources\n"
            "Collaborated with senior developers on code reviews and feature planning")

        self._add_edu()
        e = self._edu_blocks[-1]
        e.e_inst.insert(0, "GLS University")
        e.e_degree.insert(0, "Bachelor of Computer Applications (BCA)")
        e.e_dates.insert(0, "2022 – 2025")
        e.e_grade.insert(0, "8.5 / 10")

        self.e_skills.insert("1.0",
            "Python, Flask, Django, JavaScript, React, HTML5, CSS3, "
            "CustomTkinter, ReportLab, SQL, MongoDB, Git, Docker, "
            "Machine Learning, OpenCV, Pandas, NumPy, Streamlit, REST APIs")

        self._add_proj()
        p = self._proj_blocks[-1]
        p.e_name.insert(0, "Air Quality Monitoring Dashboard")
        p.e_tech.insert(0, "Flask, Chart.js, Python, Jinja2")
        p.e_link.insert(0, "github.com/Jainam259/air-quality-monitor")
        p.e_desc.insert("1.0",
            "Real-time AQI monitoring web app with dark-themed dashboard and interactive charts\n"
            "Integrated OpenWeatherMap & AQICN APIs for live pollutant data\n"
            "Responsive UI with animated gauge indicators and city-level heatmaps")

        self._add_proj()
        p2 = self._proj_blocks[-1]
        p2.e_name.insert(0, "Image Caption Generator")
        p2.e_tech.insert(0, "Flask, Salesforce BLIP, Python, PIL")
        p2.e_link.insert(0, "github.com/Jainam259/image-caption-generator")
        p2.e_desc.insert("1.0",
            "AI-powered caption generator supporting multilingual output via BLIP model\n"
            "Drag-and-drop image upload with instant caption preview\n"
            "REST API for third-party integration and batch processing")

        self.e_certs.insert("1.0",
            "Udemy: The Complete Python Bootcamp – 2024\n"
            "Coursera: Machine Learning Specialization (Andrew Ng) – 2024\n"
            "HackerRank: Python (Gold Badge) – 2023")


if __name__ == "__main__":
    app = ResumePDFApp()
    app.mainloop()
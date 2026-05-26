import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from PIL import Image, ImageTk, ImageFilter
from rembg import remove
import io
import os

# ================= COLORS =================
BG = "#0D0D0D"
SURFACE = "#161616"
CARD = "#1E1E1E"
ACCENT = "#00E5A0"
ACCENT2 = "#00B37A"
TEXT = "#F0F0F0"
SUBTEXT = "#888888"
BTN_DIS = "#2E2E2E"
TXT_DIS = "#555555"
BORDER = "#2A2A2A"

FONT_HEAD = ("Georgia", 22, "bold")
FONT_SUB = ("Georgia", 10, "italic")
FONT_BTN = ("Helvetica", 11, "bold")

class BGRemoverApp:

    def __init__(self, root):

        self.root = root
        self.root.title("AI BG Eraser - HD Quality")
        self.root.geometry("1200x850")
        self.root.configure(bg=BG)

        self.original_image = None
        self.result_image = None
        self.source_path = ""

        self.create_ui()


    ##########################
    # UI
    ##########################

    def create_ui(self):

        header = tk.Frame(
            self.root,
            bg=SURFACE,
            height=80
        )

        header.pack(fill="x")

        tk.Label(
            header,
            text="✦ BG ERASER",
            font=FONT_HEAD,
            bg=SURFACE,
            fg=ACCENT
        ).pack(side="left", padx=30)

        tk.Label(
            header,
            text="Realistic AI Background Removal • HD Quality",
            font=FONT_SUB,
            bg=SURFACE,
            fg=SUBTEXT
        ).pack(side="left")


        body = tk.Frame(
            self.root,
            bg=BG
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )


        self.left = self.make_card(
            body,
            "ORIGINAL IMAGE"
        )

        self.left.pack(
            side="left",
            expand=True,
            fill="both",
            padx=10
        )

        self.right = self.make_card(
            body,
            "RESULT"
        )

        self.right.pack(
            side="right",
            expand=True,
            fill="both",
            padx=10
        )


        self.canvas1 = self.make_canvas(self.left)
        self.canvas2 = self.make_canvas(self.right)


        toolbar = tk.Frame(
            self.root,
            bg=SURFACE,
            height=100
        )

        toolbar.pack(
            fill="x"
        )


        tk.Button(
            toolbar,
            text="UPLOAD IMAGE",
            command=self.upload,
            bg="#2A2A2A",
            fg="white",
            font=FONT_BTN,
            width=18,
            height=2
        ).pack(
            side="left",
            padx=20,
            pady=20
        )


        self.remove_btn = tk.Button(
            toolbar,
            text="REMOVE BACKGROUND",
            command=self.start_remove,
            bg=ACCENT,
            fg="black",
            font=FONT_BTN,
            width=20,
            height=2,
            state="disabled"
        )

        self.remove_btn.pack(
            side="left",
            padx=20
        )


        self.download_btn = tk.Button(
            toolbar,
            text="DOWNLOAD",
            command=self.download,
            bg="#FFD166",
            fg="black",
            font=FONT_BTN,
            width=15,
            height=2,
            state="disabled"
        )

        self.download_btn.pack(
            side="left"
        )


        self.status = tk.Label(
            toolbar,
            text="Upload image",
            bg=SURFACE,
            fg="white"
        )

        self.status.pack(
            side="right",
            padx=20
        )


    def make_card(self,parent,title):

        frame = tk.Frame(
            parent,
            bg=CARD
        )

        tk.Label(
            frame,
            text=title,
            bg=CARD,
            fg="white"
        ).pack(anchor="nw")

        return frame


    def make_canvas(self,parent):

        canvas = tk.Canvas(
            parent,
            bg="#111111"
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        canvas.bind(
            "<Configure>",
            lambda e:self.redraw()
        )

        return canvas


    #############################
    # Upload
    #############################

    def upload(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Images","*.png *.jpg *.jpeg")
            ]
        )

        if not path:
            return


        self.source_path = path

        self.original_image = Image.open(
            path
        ).convert("RGBA")


        self.show(
            self.canvas1,
            self.original_image
        )


        self.remove_btn.config(
            state="normal"
        )

        self.status.config(
            text="Image loaded"
        )



    ##############################
    # Remove BG
    ##############################

    def start_remove(self):

        threading.Thread(
            target=self.remove_bg,
            daemon=True
        ).start()



    def remove_bg(self):

        try:

            buffer = io.BytesIO()

            self.original_image.save(
                buffer,
                format="PNG"
            )

            output = remove(

                buffer.getvalue(),

                alpha_matting=True,

                alpha_matting_foreground_threshold=240,

                alpha_matting_background_threshold=10,

                alpha_matting_erode_size=10

            )


            fg = Image.open(
                io.BytesIO(output)
            ).convert("RGBA")


            fg = fg.filter(
                ImageFilter.SMOOTH_MORE
            )


            fg = fg.filter(
                ImageFilter.SHARPEN
            )


            white = Image.new(
                "RGBA",
                fg.size,
                (255,255,255,255)
            )


            white.paste(
                fg,
                mask=fg.split()[3]
            )


            self.result_image = white.convert(
                "RGB"
            )


            self.root.after(
                0,
                self.finish
            )


        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


    def finish(self):

        self.show(
            self.canvas2,
            self.result_image
        )


        self.download_btn.config(
            state="normal"
        )


        self.status.config(
            text="Background Removed ✓"
        )



    ##################################
    # Show Image
    ##################################

    def show(self,canvas,img):

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        iw,ih = img.size


        scale = min(
            cw/iw,
            ch/ih
        )


        nw = int(iw*scale)
        nh = int(ih*scale)


        image = img.resize(

            (nw,nh),

            Image.LANCZOS

        )


        photo = ImageTk.PhotoImage(
            image
        )


        canvas.delete(
            "all"
        )


        canvas.image = photo


        canvas.create_image(

            cw/2,

            ch/2,

            image=photo

        )


    ##################################

    def redraw(self):

        if self.original_image:

            self.show(
                self.canvas1,
                self.original_image
            )


        if self.result_image:

            self.show(
                self.canvas2,
                self.result_image
            )



    ##################################
    # Save
    ##################################

    def download(self):

        path = filedialog.asksaveasfilename(

            defaultextension=".png",

            filetypes=[

                ("PNG","*.png"),

                ("JPEG","*.jpg")

            ]

        )


        if not path:

            return


        ext = path.split(".")[-1]


        if ext == "jpg":

            self.result_image.save(

                path,

                quality=100,

                subsampling=0

            )

        else:

            self.result_image.save(

                path,

                compress_level=0,

                optimize=False

            )


        messagebox.showinfo(

            "Saved",

            "Image Saved Successfully"

        )



##########################

root = tk.Tk()

app = BGRemoverApp(root)

root.mainloop()
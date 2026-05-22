# Image ↔ PDF Converter and Also PDF to Image Converter

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import fitz
import img2pdf
import os


root = tk.Tk()
root.title("Image ↔ PDF Converter")
root.geometry("600x450")
root.configure(bg="#1E1E2E")


title = tk.Label(
    root,
    text="Image ↔ PDF Converter",
    font=("Arial",24,"bold"),
    fg="white",
    bg="#1E1E2E"
)
title.pack(pady=20)


status = tk.Label(
    root,
    text="Select Option",
    font=("Arial",12),
    fg="lightgreen",
    bg="#1E1E2E"
)
status.pack()


####################
# IMAGE → PDF
####################

def image_to_pdf():

    files = filedialog.askopenfilenames(
        filetypes=[
            ("Images","*.jpg *.jpeg *.png")
        ]
    )

    if not files:
        return


    save = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF","*.pdf")]
    )

    if not save:
        return


    try:

        with open(save,"wb") as f:
            f.write(img2pdf.convert(files))

        messagebox.showinfo(
            "Success",
            "PDF Saved Successfully"
        )


    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )



####################
# PDF → IMAGE
####################

def pdf_to_image():

    pdf = filedialog.askopenfilename(
        filetypes=[("PDF","*.pdf")]
    )

    if not pdf:
        return


    folder = filedialog.askdirectory()

    if not folder:
        return


    try:

        doc = fitz.open(pdf)


        for page_num in range(len(doc)):

            page = doc.load_page(page_num)


            # Higher DPI (5 = very HD)
            zoom = 5
            matrix = fitz.Matrix(
                zoom,
                zoom
            )

            pix = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )


            output = os.path.join(
                folder,
                f"page_{page_num+1}.jpg"
            )


            img = Image.frombytes(
                "RGB",
                [pix.width,pix.height],
                pix.samples
            )


            img.save(
                output,
                quality=100,
                subsampling=0
            )


        messagebox.showinfo(
            "Success",
            "HD Images Saved Successfully"
        )


    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )



btn1 = tk.Button(
    root,
    text="Image → PDF",
    font=("Arial",15),
    width=25,
    bg="#4CAF50",
    fg="white",
    command=image_to_pdf
)

btn1.pack(
    pady=30
)



btn2 = tk.Button(
    root,
    text="PDF → Image",
    font=("Arial",15),
    width=25,
    bg="#2196F3",
    fg="white",
    command=pdf_to_image
)

btn2.pack()


root.mainloop()
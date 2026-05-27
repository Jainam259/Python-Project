# PDF Merger ana Splitter tool

import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
import os


class PDFTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merge & Split Tool")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f4f8")

        title = tk.Label(
            root,
            text="📄 PDF Merge & Split Tool",
            font=("Arial", 24, "bold"),
            bg="#f0f4f8",
            fg="#1a237e"
        )
        title.pack(pady=20)

        subtitle = tk.Label(
            root,
            text="Merge Multiple PDFs or Split One PDF Easily",
            font=("Arial", 12),
            bg="#f0f4f8"
        )
        subtitle.pack()

        frame = tk.Frame(root, bg="white", bd=2, relief="ridge")
        frame.pack(pady=30, padx=30, fill="both", expand=True)

        merge_btn = tk.Button(
            frame,
            text="📑 Merge PDFs",
            font=("Arial",16,"bold"),
            bg="#4CAF50",
            fg="white",
            width=25,
            command=self.merge_pdf
        )
        merge_btn.pack(pady=25)

        split_btn = tk.Button(
            frame,
            text="✂ Split PDF",
            font=("Arial",16,"bold"),
            bg="#2196F3",
            fg="white",
            width=25,
            command=self.split_pdf
        )
        split_btn.pack(pady=25)

        exit_btn = tk.Button(
            frame,
            text="❌ Exit",
            font=("Arial",16,"bold"),
            bg="#f44336",
            fg="white",
            width=25,
            command=root.quit
        )
        exit_btn.pack(pady=25)

        self.status = tk.Label(
            root,
            text="Ready",
            bg="#f0f4f8",
            font=("Arial",12)
        )
        self.status.pack(pady=10)

    #################################
    # Merge PDFs
    #################################

    def merge_pdf(self):

        files = filedialog.askopenfilenames(
            title="Select PDFs",
            filetypes=[("PDF Files","*.pdf")]
        )

        if not files:
            return

        writer = PdfWriter()

        try:
            for pdf in files:

                reader = PdfReader(pdf)

                for page in reader.pages:
                    writer.add_page(page)

            save_file = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF","*.pdf")],
                title="Save Merged PDF"
            )

            if save_file:

                with open(save_file,"wb") as f:
                    writer.write(f)

                self.status.config(
                    text="Merged Successfully!"
                )

                messagebox.showinfo(
                    "Success",
                    f"PDF saved:\n{save_file}"
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )


    #################################
    # Split PDF
    #################################

    def split_pdf(self):

        file = filedialog.askopenfilename(
            filetypes=[("PDF","*.pdf")]
        )

        if not file:
            return


        folder = filedialog.askdirectory(
            title="Select Folder To Save Split PDFs"
        )

        if not folder:
            return


        try:

            reader = PdfReader(file)

            total = len(reader.pages)

            for i in range(total):

                writer = PdfWriter()

                writer.add_page(
                    reader.pages[i]
                )

                output = os.path.join(
                    folder,
                    f"Page_{i+1}.pdf"
                )

                with open(output,"wb") as f:
                    writer.write(f)


            self.status.config(
                text="Split Successfully!"
            )

            messagebox.showinfo(
                "Done",
                f"{total} PDFs created"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)


            )


root = tk.Tk()

app = PDFTool(root)

root.mainloop()
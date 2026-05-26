# Advanced Text Editor App with Tkinter

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font

# ===== Functions =====
def new_file():
    text.delete(1.0, tk.END)
    root.title("Untitled - Text Editor")

def open_file():
    file_path = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, 'r') as file:
            text.delete(1.0, tk.END)
            text.insert(tk.END, file.read())
        root.title(f"{file_path} - Text Editor")

def save_file():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if file_path:
        with open(file_path, 'w') as file:
            file.write(text.get(1.0, tk.END))
        messagebox.showinfo("Info", "File Saved Successfully!")
        root.title(f"{file_path} - Text Editor")

def exit_app():
    if messagebox.askyesno("Exit", "Do you really want to exit?"):
        root.quit()

def cut():
    text.event_generate("<<Cut>>")

def copy():
    text.event_generate("<<Copy>>")

def paste():
    text.event_generate("<<Paste>>")

def undo():
    text.event_generate("<<Undo>>")

def redo():
    text.event_generate("<<Redo>>")

def find_text():
    query = simpledialog.askstring("Find", "Enter text to find:")
    if query:
        start = "1.0"
        while True:
            pos = text.search(query, start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            text.tag_add("highlight", pos, end)
            text.tag_config("highlight", background="yellow", foreground="red")
            start = end

def replace_text():
    find_str = simpledialog.askstring("Replace", "Enter text to find:")
    replace_str = simpledialog.askstring("Replace", "Enter replacement text:")
    if find_str and replace_str is not None:
        content = text.get(1.0, tk.END)
        new_content = content.replace(find_str, replace_str)
        text.delete(1.0, tk.END)
        text.insert(tk.END, new_content)

def toggle_wrap():
    if text.cget("wrap") == tk.WORD:
        text.config(wrap=tk.NONE)
        wrap_menu.entryconfig(0, label="Enable Word Wrap")
    else:
        text.config(wrap=tk.WORD)
        wrap_menu.entryconfig(0, label="Disable Word Wrap")

def change_font():
    size = simpledialog.askinteger("Font Size", "Enter font size:", minvalue=8, maxvalue=50)
    if size:
        text.config(font=("Helvetica", size))

def update_status(event=None):
    row, col = text.index(tk.INSERT).split(".")
    status_bar.config(text=f"Line {row}, Column {col}")

# ===== Main Window =====
root = tk.Tk()
root.title("Simple Text Editor")
root.geometry("900x600")

# ===== Menu Bar =====
menu = tk.Menu(root)
root.config(menu=menu)

# File Menu
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
file_menu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_app)

# Edit Menu
edit_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Undo", command=undo, accelerator="Ctrl+Z")
edit_menu.add_command(label="Redo", command=redo, accelerator="Ctrl+Y")
edit_menu.add_separator()
edit_menu.add_command(label="Cut", command=cut, accelerator="Ctrl+X")
edit_menu.add_command(label="Copy", command=copy, accelerator="Ctrl+C")
edit_menu.add_command(label="Paste", command=paste, accelerator="Ctrl+V")
edit_menu.add_separator()
edit_menu.add_command(label="Find", command=find_text, accelerator="Ctrl+F")
edit_menu.add_command(label="Replace", command=replace_text, accelerator="Ctrl+H")

# Format Menu
wrap_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Format", menu=wrap_menu)
wrap_menu.add_command(label="Disable Word Wrap", command=toggle_wrap)
wrap_menu.add_command(label="Change Font Size", command=change_font)

# ===== Text Area with Scrollbars =====
frame = tk.Frame(root)
frame.pack(expand=tk.YES, fill=tk.BOTH)

scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

text = tk.Text(
    frame, wrap=tk.WORD, font=("Helvetica", 14), undo=True,
    yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set
)
text.pack(expand=tk.YES, fill=tk.BOTH)

scrollbar_y.config(command=text.yview)
scrollbar_x.config(command=text.xview)

# ===== Status Bar =====
status_bar = tk.Label(root, text="Line 1, Column 0", anchor="w")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

text.bind("<KeyRelease>", update_status)
text.bind("<ButtonRelease>", update_status)

# ===== Keyboard Shortcuts =====
root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-f>", lambda e: find_text())
root.bind("<Control-h>", lambda e: replace_text())

root.mainloop()

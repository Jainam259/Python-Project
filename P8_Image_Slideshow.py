import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk

# -------------------------
# Configuration
# -------------------------
IMAGE_PATHS = [
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\5d2350be21a8612d236e24fa.webp",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\2360c073539b13761358392ddd89b71d.jpg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\f797f81aa1ec783d80491fd516e306c7.jpg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\images.jpeg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\desktop-wallpaper-the-most-beautiful-girls-in-the-world-indian-beauty-women.jpg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\c92142f2ef427934cef9c66bafdc6191.jpg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\Top-10-Growing-Smart-Cities_Hero.jpg",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\Aishwarya_Rai_Cannes_2017.webp",
    r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\istockphoto-1147803899-612x612.jpg",
]

IMAGE_SIZE = (700, 700)
DELAY = 1500  # milliseconds between slides

# -------------------------
# Setup Window
# -------------------------
root = tk.Tk()
root.title("📸 Image Slideshow Viewer")
root.geometry("800x850")
root.configure(bg="#222")

# -------------------------
# Load and Resize Images
# -------------------------
images = []
for path in IMAGE_PATHS:
    img = Image.open(path).resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
    images.append(ImageTk.PhotoImage(img))

# Create a cycle for looping
slideshow_images = cycle(images)

# -------------------------
# UI Elements
# -------------------------
label = tk.Label(root, bg="#222")
label.pack(pady=20)

btn_frame = tk.Frame(root, bg="#222")
btn_frame.pack(pady=10)

# -------------------------
# Variables
# -------------------------
is_running = False
current_index = 0
after_id = None

# -------------------------
# Functions
# -------------------------
def show_image(index):
    """Display image by index."""
    global current_index
    current_index = index % len(images)
    label.config(image=images[current_index])

def show_next_image():
    """Show next image and schedule next."""
    global current_index, after_id
    if not is_running:
        return
    current_index = (current_index + 1) % len(images)
    label.config(image=images[current_index])
    after_id = root.after(DELAY, show_next_image)

def start_slideshow():
    """Start slideshow."""
    global is_running
    if not is_running:
        is_running = True
        start_button.config(state="disabled")
        pause_button.config(state="normal")
        end_button.config(state="normal")
        show_next_image()

def pause_slideshow():
    """Pause slideshow."""
    global is_running, after_id
    if is_running:
        is_running = False
        if after_id:
            root.after_cancel(after_id)
        start_button.config(state="normal")
        pause_button.config(state="disabled")

def end_slideshow():
    """Stop and reset to first image."""
    global is_running, after_id, current_index
    is_running = False
    if after_id:
        root.after_cancel(after_id)
    current_index = 0
    show_image(current_index)
    start_button.config(state="normal")
    pause_button.config(state="disabled")
    end_button.config(state="disabled")

# -------------------------
# Buttons
# -------------------------
start_button = tk.Button(btn_frame, text="▶ Start", command=start_slideshow,
                         bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), width=10)
start_button.grid(row=0, column=0, padx=10)

pause_button = tk.Button(btn_frame, text="⏸ Pause", command=pause_slideshow,
                         bg="#FFC107", fg="black", font=("Arial", 12, "bold"), width=10, state="disabled")
pause_button.grid(row=0, column=1, padx=10)

end_button = tk.Button(btn_frame, text="⏹ End", command=end_slideshow,
                       bg="#F44336", fg="white", font=("Arial", 12, "bold"), width=10, state="disabled")
end_button.grid(row=0, column=2, padx=10)

# -------------------------
# Show first image initially
# -------------------------
show_image(0)

# -------------------------
# Run the GUI
# -------------------------
root.mainloop()






































# from itertools import cycle
# from PIL import Image, ImageTk
# import time
# import tkinter as tk

# root = tk.Tk()
# root.title("Image Slideshow Viewer")

# # List of image file path
# image_paths = [
#     r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\5d2350be21a8612d236e24fa.webp",
#     r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\2360c073539b13761358392ddd89b71d.jpg",
#     r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\f797f81aa1ec783d80491fd516e306c7.jpg",
#     r"C:\Users\Jainam J Shah\Pictures\Saved Pictures\images.jpeg"
# ]

# image_size = (1080,1080)
# images = [Image.open(path).resize(image_size) for path in image_paths]
# photo_images = [ImageTk.PhotoImage(img) for img in images]

# label = tk.Label(root)
# label.pack()

# def update_image():
#     for photo_image in photo_images:
#         label.config(image=photo_image)
#         label.update()
#         time.sleep(1)
    
# sldieshow = cycle(photo_images)

# def start_slideshow():
#     for _ in range(len(image_paths)):
#         update_image()

# play_button = tk.Button(root, text="Start Slideshow", command=start_slideshow)
# play_button.pack()

# root.mainloop()
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import time
import threading
from .draggable_object import DraggableObject
from .export import export_jpg, start_recording, stop_recording, save_video_to_path

# Constants
max_width, max_height = 800, 800
padding = 20  # Padding around canvas content

# Global variables
recording = False
record_start_time = None

def create_sidebar_icon(parent_frame, canvas, images, hotkey=None):
    thumbnail = images[0].resize((48, 48))
    thumbnail_tk = ImageTk.PhotoImage(thumbnail)

    def on_click(event):
        DraggableObject(canvas, images, x=150, y=150, hotkey=hotkey)

    label = tk.Label(parent_frame, image=thumbnail_tk, bg="lightgray", cursor="hand2")
    label.image = thumbnail_tk
    label.pack(pady=10)
    label.bind("<Button-1>", on_click)

def update_recording_status(status_label):
    if recording:
        elapsed = int(time.time() - record_start_time)
        blink = "●" if elapsed % 2 == 0 else " "
        status_label.config(text=f"{blink} Recording... {elapsed}s")
        status_label.after(500, lambda: update_recording_status(status_label))
    else:
        status_label.config(text="")

def on_key_press(event, canvas):
    if event.keysym == "Delete" and DraggableObject.selected_object:
        DraggableObject.selected_object.delete()
    elif event.keysym == "space" and DraggableObject.selected_object:
        DraggableObject.selected_object.toggle_state()
    elif event.keysym.lower() == "l" and DraggableObject.selected_object:
        DraggableObject.selected_object.toggle_lock()
    # Handle character hotkeys
    elif event.keysym in ["1", "2"]:
        obj = DraggableObject.get_by_hotkey(event.keysym)
        if obj:
            obj.set_selected()

def delete_selected():
    if DraggableObject.selected_object:
        DraggableObject.selected_object.delete()

def record_loop():
    while recording:
        export_jpg(max_width, max_height, padding)
        time.sleep(0.1)

def toggle_recording(status_label, record_btn):
    global recording, record_start_time
    recording = not recording
    if recording:
        record_start_time = time.time()
        update_recording_status(status_label)
        start_recording(max_width, max_height, padding)
        threading.Thread(target=record_loop).start()
        record_btn.config(text="Stop")
    else:
        update_recording_status(status_label)
        stop_recording()
        record_btn.config(text="Record")
        status_label.config(text="Recording stopped")

def export_video(status_label):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
        title="Save Recording As"
    )
    if file_path:
        if save_video_to_path(file_path):
            status_label.config(text=f"Recording saved to {file_path}")
        else:
            status_label.config(text="Error saving recording")
    else:
        status_label.config(text="Export cancelled")

def setup_ui(root):
    # Create main window
    root.geometry("1400x800")
    root.title("Mini Animation Tool")

    # Create sidebar
    sidebar = tk.Frame(root, width=200, bg="lightgray")
    sidebar.pack(side="left", fill="y")

    # Create canvas
    canvas = tk.Canvas(root, width=max_width, height=max_height, bg="white")
    canvas.pack(side="right", fill="both", expand=True)
    canvas.create_rectangle(padding, padding, max_width - padding, max_height - padding, outline="gray")

    # Create status label
    status_label = tk.Label(canvas, text="", fg="red", font=("Arial", 12), bg="white")
    status_label.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

    # Create button frame
    button_frame = tk.Frame(sidebar, bg="lightgray")
    button_frame.pack(pady=10)

    # Create buttons
    record_btn = tk.Button(button_frame, text="Record", 
                          command=lambda: toggle_recording(status_label, record_btn))
    record_btn.pack(padx=10, pady=5)

    export_btn = tk.Button(button_frame, text="Export Video", 
                          command=lambda: export_video(status_label))
    export_btn.pack(padx=10, pady=5)

    # Bind keyboard events
    root.bind("<Key>", lambda e: on_key_press(e, canvas))

    return root, sidebar, canvas, status_label 
import tkinter as tk
from PIL import Image, ImageTk, ImageOps

class DraggableObject:
    selected_object = None

    def __init__(self, canvas, images, x=100, y=100):
        self.canvas = canvas
        self.original_images = images  # Keep originals for rotation
        self.rotation = 0
        self.images = images
        self.tk_images = [ImageTk.PhotoImage(img) for img in self.images]
        self.state = 0
        self.id = canvas.create_image(x, y, image=self.tk_images[self.state], anchor="nw")
        self.pos = (x, y)
        self.drag_offset = (0, 0)
        self.is_dragging = False
        self.resizing = False
        self.resize_handle = None
        self.resize_origin = None

        self.menu = tk.Menu(canvas, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete)
        self.menu.add_command(label="Resize +", command=lambda: self.resize(1.2))
        self.menu.add_command(label="Resize −", command=lambda: self.resize(0.8))
        self.menu.add_command(label="Rotate Clockwise", command=lambda: self.rotate(15))
        self.menu.add_command(label="Rotate Counterclockwise", command=lambda: self.rotate(-15))
        self.menu.add_separator()
        self.menu.add_command(label="Bring to Front", command=self.bring_to_front)
        self.menu.add_command(label="Send to Back", command=self.send_to_back)

        canvas.tag_bind(self.id, "<Button-1>", self.on_click)
        canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_release)
        canvas.tag_bind(self.id, "<Button-3>", self.on_right_click)

    def on_click(self, event):
        self.set_selected()
        if len(self.tk_images) > 1:
            self.toggle_state()
        self.is_dragging = True
        self.drag_offset = (event.x - self.pos[0], event.y - self.pos[1])

    def set_selected(self):
        if DraggableObject.selected_object and DraggableObject.selected_object != self:
            DraggableObject.selected_object.remove_resize_handle()
        DraggableObject.selected_object = self
        self.add_resize_handle()

    def add_resize_handle(self):
        if self.resize_handle:
            return
        x, y = self.canvas.coords(self.id)
        w, h = self.tk_images[self.state].width(), self.tk_images[self.state].height()
        self.resize_handle = self.canvas.create_rectangle(
            x + w - 10, y + h - 10, x + w, y + h,
            fill="blue", outline="black", tags="resize"
        )
        self.canvas.tag_bind(self.resize_handle, "<Button-1>", self.start_resize)
        self.canvas.tag_bind(self.resize_handle, "<B1-Motion>", self.do_resize)
        self.canvas.tag_bind(self.resize_handle, "<ButtonRelease-1>", self.end_resize)

    def remove_resize_handle(self):
        if self.resize_handle:
            self.canvas.delete(self.resize_handle)
            self.resize_handle = None

    def start_resize(self, event):
        self.resizing = True
        self.resize_origin = (event.x, event.y)

    def do_resize(self, event):
        if not self.resizing:
            return
        dx = event.x - self.resize_origin[0]
        dy = event.y - self.resize_origin[1]
        scale = 1 + max(dx, dy) / 100
        self.resize(scale)
        self.resize_origin = (event.x, event.y)

    def end_resize(self, event):
        self.resizing = False

    def on_drag(self, event):
        if self.is_dragging:
            new_x = event.x - self.drag_offset[0]
            new_y = event.y - self.drag_offset[1]
            self.canvas.coords(self.id, new_x, new_y)
            self.pos = (new_x, new_y)
            self.update_resize_handle()

    def update_resize_handle(self):
        if self.resize_handle:
            x, y = self.canvas.coords(self.id)
            w, h = self.tk_images[self.state].width(), self.tk_images[self.state].height()
            self.canvas.coords(self.resize_handle, x + w - 10, y + h - 10, x + w, y + h)

    def on_release(self, event):
        self.is_dragging = False

    def on_right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_state(self):
        self.state = (self.state + 1) % len(self.tk_images)
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()

    def resize(self, scale):
        self.images = [img.resize((int(img.width * scale), int(img.height * scale))) for img in self.images]
        self.tk_images = [ImageTk.PhotoImage(img) for img in self.images]
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.images = [img.rotate(self.rotation, expand=True) for img in self.original_images]
        self.tk_images = [ImageTk.PhotoImage(img) for img in self.images]
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()

    def delete(self):
        self.canvas.delete(self.id)
        if self.resize_handle:
            self.canvas.delete(self.resize_handle)
        if DraggableObject.selected_object == self:
            DraggableObject.selected_object = None

    def bring_to_front(self):
        self.canvas.tag_raise(self.id)
        if self.resize_handle:
            self.canvas.tag_raise(self.resize_handle)

    def send_to_back(self):
        self.canvas.tag_lower(self.id)
        if self.resize_handle:
            self.canvas.tag_lower(self.resize_handle)


def create_sidebar_icon(parent_frame, canvas, images):
    thumbnail = images[0].resize((48, 48))
    thumbnail_tk = ImageTk.PhotoImage(thumbnail)

    def on_click(event):
        DraggableObject(canvas, images, x=150, y=150)

    label = tk.Label(parent_frame, image=thumbnail_tk, bg="lightgray", cursor="hand2")
    label.image = thumbnail_tk
    label.pack(pady=10)
    label.bind("<Button-1>", on_click)

# --- UI SETUP ---
root = tk.Tk()
root.geometry("1400x800")
root.title("Mini Animation Tool")

sidebar = tk.Frame(root, width=200, bg="lightgray")
sidebar.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=1200, height=1200, bg="white")
canvas.pack(side="right", fill="both", expand=True)

metadata = {
    'mlephy': ['mlephy1.png', 'mlephy2.png'], 
    'pixpi': ['pixpi1.png', 'pixpi2.png'], 
    'scenario': ['scenario.png'], 
    'table': ['table.png']
}

for key, values in metadata.items():
    images = []
    for value in values:
        img = Image.open(f"src/{value}")
        max_width, max_height = 1200, 1200
        if img.width > max_width or img.height > max_height:
            scale = min(max_width / img.width, max_height / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        images.append(img)
    create_sidebar_icon(sidebar, canvas, images)

root.mainloop()

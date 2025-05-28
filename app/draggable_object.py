import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import threading

class DraggableObject:
    selected_object = None
    instances = []  # Track all instances

    def __init__(self, canvas, images, x=100, y=100):
        self.canvas = canvas
        self.original_images = images  # keep originals
        self.current_scale = 1.0
        self.rotation = 0
        self.state = 0
        self.locked = False
        self.original_pos = (x, y)
        self.is_shaking = False
        self.is_resizing = False  # Track if we're resizing via shift+drag

        self.tk_images = self._generate_tk_images()

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
        self.menu.add_separator()
        self.menu.add_command(label="Lock Position", command=self.toggle_lock)
        self.lock_menu_index = self.menu.index("end")

        canvas.tag_bind(self.id, "<Button-1>", self.on_click)
        canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_release)
        canvas.tag_bind(self.id, "<Button-3>", self.on_right_click)
        # Bind shift key events
        canvas.bind_all("<Shift-Key>", self.on_shift_press)
        canvas.bind_all("<KeyRelease-Shift_L>", self.on_shift_release)
        canvas.bind_all("<KeyRelease-Shift_R>", self.on_shift_release)

        DraggableObject.instances.append(self)

    def _generate_tk_images(self):
        images = [img.rotate(self.rotation, expand=True).resize(
            (int(img.width * self.current_scale), int(img.height * self.current_scale)),
            Image.Resampling.LANCZOS) for img in self.original_images]
        return [ImageTk.PhotoImage(img) for img in images]

    def on_shift_press(self, event):
        if self.is_dragging:
            self.is_resizing = True
            self.resize_origin = (event.x, event.y)

    def on_shift_release(self, event):
        self.is_resizing = False

    def on_click(self, event):
        self.set_selected()
        if not self.locked:
            self.is_dragging = True
            self.drag_offset = (event.x - self.pos[0], event.y - self.pos[1])
            # Check if shift is pressed
            if event.state & 0x1:  # Check if Shift key is pressed
                self.is_resizing = True
                self.resize_origin = (event.x, event.y)

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
        # Change color based on lock status
        fill_color = "red" if self.locked else "blue"
        self.resize_handle = self.canvas.create_rectangle(
            x + w - 10, y + h - 10, x + w, y + h,
            fill=fill_color, outline="black", tags="resize"
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
        if self.locked:
            return
            
        if self.is_resizing:
            # Calculate scale based on drag distance
            dx = event.x - self.resize_origin[0]
            dy = event.y - self.resize_origin[1]
            # Use the larger of dx or dy for more intuitive scaling
            scale = 1 + max(dx, dy) / 100
            self.resize(scale)
            self.resize_origin = (event.x, event.y)
        elif self.is_dragging:
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
            # Update color based on lock status
            fill_color = "red" if self.locked else "blue"
            self.canvas.itemconfig(self.resize_handle, fill=fill_color)

    def on_release(self, event):
        self.is_dragging = False
        self.is_resizing = False

    def on_right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def toggle_state(self):
        self.state = (self.state + 1) % len(self.tk_images)
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()
        
        # Add random shake with 0.3 probability
        if random.random() < 0.3:
            self.shake()

    def resize(self, scale):
        self.current_scale *= scale
        self.tk_images = self._generate_tk_images()
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()

    def rotate(self, angle):
        self.rotation = (self.rotation + angle) % 360
        self.tk_images = self._generate_tk_images()
        self.canvas.itemconfig(self.id, image=self.tk_images[self.state])
        self.update_resize_handle()

    def delete(self):
        # Unbind shift key events
        self.canvas.unbind_all("<Shift-Key>")
        self.canvas.unbind_all("<KeyRelease-Shift_L>")
        self.canvas.unbind_all("<KeyRelease-Shift_R>")
        # Continue with normal deletion
        self.canvas.delete(self.id)
        if self.resize_handle:
            self.canvas.delete(self.resize_handle)
        if DraggableObject.selected_object == self:
            DraggableObject.selected_object = None
        if self in DraggableObject.instances:
            DraggableObject.instances.remove(self)

    def bring_to_front(self):
        self.canvas.tag_raise(self.id)
        if self.resize_handle:
            self.canvas.tag_raise(self.resize_handle)

    def send_to_back(self):
        self.canvas.tag_lower(self.id)
        if self.resize_handle:
            self.canvas.tag_lower(self.resize_handle)

    def toggle_lock(self):
        self.locked = not self.locked
        if self.locked:
            self.original_pos = self.pos
            self.menu.entryconfig(self.lock_menu_index, label="Unlock Position")
        else:
            self.menu.entryconfig(self.lock_menu_index, label="Lock Position")
        # Update resize handle color
        if self.resize_handle:
            fill_color = "red" if self.locked else "blue"
            self.canvas.itemconfig(self.resize_handle, fill=fill_color)

    def shake(self):
        if self.is_shaking:
            return
        
        self.is_shaking = True
        original_x, original_y = self.pos
        
        def shake_animation():
            # Random offset between -5 and 5 pixels
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            
            # Move to offset position
            self.canvas.coords(self.id, original_x + offset_x, original_y + offset_y)
            self.pos = (original_x + offset_x, original_y + offset_y)
            self.update_resize_handle()
            
            # Wait a short time
            time.sleep(0.1)
            
            # Return to original position
            self.canvas.coords(self.id, original_x, original_y)
            self.pos = (original_x, original_y)
            self.update_resize_handle()
            
            self.is_shaking = False

        # Run shake animation in a separate thread
        threading.Thread(target=shake_animation).start() 
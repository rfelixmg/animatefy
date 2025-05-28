import os
from PIL import Image
from .draggable_object import DraggableObject

def export_jpg(max_width, max_height, padding):
    # Create exports directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")
    
    # Generate filename
    filename = f"exports/canvas.1.jpg"
    
    # Create a new image with canvas dimensions
    img = Image.new('RGB', (max_width - 2*padding, max_height - 2*padding), 'white')
    
    # Get all objects from the canvas
    for obj in DraggableObject.instances:
        # Get object position and image
        x, y = obj.pos
        # Adjust position by padding
        x -= padding
        y -= padding
        # Get the current image state
        current_img = obj.original_images[obj.state]
        # Resize according to current scale
        current_img = current_img.resize(
            (int(current_img.width * obj.current_scale), 
             int(current_img.height * obj.current_scale)),
            Image.Resampling.LANCZOS
        )
        # Rotate if needed
        if obj.rotation != 0:
            current_img = current_img.rotate(obj.rotation, expand=True)
        # Paste onto the main image
        img.paste(current_img, (int(x), int(y)), current_img if current_img.mode == 'RGBA' else None)
    
    # Save as JPG
    img.save(filename, "JPEG", quality=95)
    print(f"Canvas exported as {filename}")

def export_video():
    print(NotImplementedError("export_video")) 
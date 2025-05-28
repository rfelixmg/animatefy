import os
import cv2
import numpy as np
from PIL import Image
from .draggable_object import DraggableObject

# Video writer instance
video_writer = None
temp_video_path = 'exports/temp_recording.mp4'

def export_jpg(max_width:int = 800, max_height:int = 800, padding:int = 20):
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
    
    # Convert PIL Image to OpenCV format
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # If we're recording, write the frame to video
    global video_writer
    if video_writer is not None:
        video_writer.write(cv_img)
    
    return cv_img
    # print(f"Canvas exported as {filename}")

def start_recording(max_width, max_height, padding):
    global video_writer
    if video_writer is not None:
        stop_recording()
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 10  # frames per second
    size = (max_width - 2*padding, max_height - 2*padding)
    video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, size)

def stop_recording():
    global video_writer
    if video_writer is not None:
        video_writer.release()
        video_writer = None
        return True
    return False

def save_video_to_path(target_path):
    """Save the temporary video to the specified path"""
    if os.path.exists(temp_video_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        # Copy the file
        os.replace(temp_video_path, target_path)
        return True
    return False

def export_video():
    print(NotImplementedError("export_video")) 
import os
import cv2
import numpy as np
from PIL import Image
from .draggable_object import DraggableObject
import time
import threading
import queue

# Video recording state
is_paused = False
pause_start_time = None
temp_video_path = 'exports/temp_recording.mp4'
FPS = 30  # Fixed FPS

# Thread-safe queue for frames
frame_queue = queue.Queue()
recording_thread = None
should_stop_recording = False
frames_written = 0
frames_captured = 0

def frame_writer_worker():
    global should_stop_recording, frames_written
    video_writer = None
    
    while not should_stop_recording or not frame_queue.empty():
        try:
            # Get frame with timeout to allow checking should_stop_recording
            frame = frame_queue.get(timeout=0.1)
            
            # Initialize video writer with first frame
            if video_writer is None and frame is not None:
                height, width = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(temp_video_path, fourcc, FPS, (width, height))
            
            if video_writer is not None and frame is not None:
                video_writer.write(frame)
                frames_written += 1
                if frames_written % 30 == 0:  # Log every second (at 30fps)
                    print(f"Frames written: {frames_written}, Queue size: {frame_queue.qsize()}, seconds: {frames_written/FPS}")
                
            frame_queue.task_done()
            
        except queue.Empty:
            continue
    
    if video_writer is not None:
        video_writer.release()
        print(f"Recording complete. Total frames written: {frames_written}")

def export_jpg(max_width:int = 800, max_height:int = 800, padding:int = 20):
    # Create exports directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")
    
    # Create a new image with canvas dimensions
    img = Image.new('RGB', (max_width - 2*padding, max_height - 2*padding), 'white')
    
    # Sort objects by their canvas order (bottom to top)
    sorted_objects = sorted(DraggableObject.instances, key=lambda obj: obj.get_canvas_order())
    
    # Get all objects from the canvas in correct order
    for obj in sorted_objects:
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
    
    # If we're recording and not paused, add frame to queue
    global is_paused, frames_captured
    if not is_paused:
        frame_queue.put(cv_img.copy())
        frames_captured += 1
        # if frames_captured % 30 == 0:  # Log every second (at 30fps)
            # print(f"Frames captured: {frames_captured}")
    
    return cv_img
    # print(f"Canvas exported as {filename}")

def start_recording(max_width=800, max_height=800, padding=20):
    global recording_thread, should_stop_recording, frames_written, frames_captured
    should_stop_recording = False
    frames_written = 0
    frames_captured = 0
    
    # Start frame writer thread
    recording_thread = threading.Thread(target=frame_writer_worker)
    recording_thread.daemon = True  # Thread will exit when main program exits
    recording_thread.start()
    print("Recording started")

def stop_recording():
    global recording_thread, should_stop_recording, frames_written, frames_captured
    if recording_thread is None:
        return False
    
    print(f"Stopping recording. Frames captured: {frames_captured}, Frames written: {frames_written} | seconds: {frames_captured/FPS}")
    
    # Signal thread to stop
    should_stop_recording = True
    
    # Wait for thread to finish
    recording_thread.join()
    recording_thread = None
    
    return True

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

def toggle_pause():
    global is_paused, pause_start_time
    is_paused = not is_paused
    if is_paused:
        pause_start_time = time.time()
    return is_paused

def is_recording_paused():
    return is_paused

def get_pause_duration():
    if is_paused and pause_start_time:
        return time.time() - pause_start_time
    return 0 
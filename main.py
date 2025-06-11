import tkinter as tk
from PIL import Image
from app.ui import setup_ui, create_sidebar_icon

MAX_WIDTH, MAX_HEIGHT = 1920, 1080

def load_character_images(character_name):
    """Load all images for a character from the src directory"""
    images = []
    # Load both states of the character
    for i in range(1, 3):  # Assuming each character has 2 states
        img_path = f"src/{character_name}{i}.png"
        try:
            img = Image.open(img_path)
            # Resize if too large
            if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                scale = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
                new_size = (int(img.width * scale * 0.9), int(img.height * scale * 0.9))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            images.append(img)
        except FileNotFoundError:
            print(f"Warning: Could not find image {img_path}")
    return images

def main():
    # Create root window
    root = tk.Tk()
    
    # Setup UI
    root, sidebar, canvas, status_label = setup_ui(root)
    
    # Load character images
    mlephy_images = load_character_images("mlephy")
    pixpi_images = load_character_images("pixpi")

    # Create sidebar icons with hotkeys
    create_sidebar_icon(sidebar, canvas, mlephy_images, hotkey="1")
    create_sidebar_icon(sidebar, canvas, pixpi_images, hotkey="2")

    for img_path in [
        'src/scenario.png', 
        'src/table.png', 
        'src/scenario2.png', 
        'src/scenario3.jpg', 
        'src/scenario4.jpg',
        'src/scenario5.jpg'
    ]:
        img = Image.open(img_path)
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            scale = min(MAX_WIDTH / img.width, MAX_HEIGHT / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        create_sidebar_icon(sidebar, canvas, [img])


    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 
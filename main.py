import tkinter as tk
from PIL import Image
from app.ui import setup_ui, create_sidebar_icon

def main():
    # Create root window
    root = tk.Tk()
    
    # Setup UI
    root, sidebar, canvas, status_label = setup_ui(root)
    
    # Load and setup images
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
            if img.width > 800 or img.height > 800:
                scale = min(800 / img.width, 800 / img.height)
                new_size = (int(img.width * scale * 0.9), int(img.height * scale * 0.9))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            images.append(img)
        create_sidebar_icon(sidebar, canvas, images)

    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main() 
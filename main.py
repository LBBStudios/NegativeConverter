import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance

# Function to correct the orange mask of color negatives
def correct_orange_mask(image):
    # This is a placeholder function (soz)
    return image

# Function to invert colors
def invert_colors(image):
    return ImageOps.invert(image)

# Function to update image
def update_image(*args):
    global img, img_display, canvas, scale_brightness, scale_contrast, enhanced_img
    # Apply brightness and contrast adjustments
    # These values can be tweaked to match the needed adjustments for the negative
    brightness = scale_brightness.get()
    contrast = scale_contrast.get()
    
    # Perform corrections and update image
    corrected_img = correct_orange_mask(invert_colors(orig_img))
    enhanced_img = ImageOps.autocontrast(corrected_img, cutoff=contrast)

    # Assuming enhanced_img is an Image object and brightness is a float value
    enhancer = ImageEnhance.Brightness(enhanced_img)
    enhanced_img = enhancer.enhance(brightness)
    ImageEnhance.Contrast(enhanced_img)

    copy = enhanced_img.copy()

    #resize the copy to fit the canvas, letterboxing if necessary
    copy.thumbnail((600, 400), Image.ADAPTIVE)

    img = ImageTk.PhotoImage(copy)
    canvas.itemconfig(img_display, image=img)

# Function to load an image
def load_image():
    global orig_img, img, img_display
    file_path = filedialog.askopenfilename()
    if file_path:
        orig_img = Image.open(file_path)
        update_image()

# Function to save the image
def save_image():
    global enhanced_img
    file_path = filedialog.asksaveasfilename(defaultextension=".png")
    if file_path:
        enhanced_img.save(file_path)

# Create main window
root = tk.Tk()

root.title('Film Negative Converter')

# Create canvas for image display
canvas = tk.Canvas(root, width=800, height=400)
canvas.pack()

# Load and display image button
btn_load = tk.Button(root, text='Load Image', command=load_image)
btn_load.pack()

# Save image button
btn_save = tk.Button(root, text='Save Image', command=save_image)
btn_save.pack()

# Create sliders for brightness and contrast
scale_brightness = tk.Scale(root, label='Brightness', from_=0, to=2, resolution=0.1, orient=tk.HORIZONTAL, command=update_image)
scale_brightness.set(1)  # Default value
scale_brightness.pack()

scale_contrast = tk.Scale(root, label='Contrast', from_=0, to=20, orient=tk.HORIZONTAL, command=update_image)
scale_contrast.set(4)  # Default value
scale_contrast.pack()

# Main loop
orig_img = None
img = None
img_display = canvas.create_image(300, 200, image=img)
root.mainloop()

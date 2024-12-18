import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class FilmNegativeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title('Film Negative Converter')
        self.root.geometry('900x750')

        # Create main container
        self.container = ttk.Frame(root, padding=20)
        self.container.pack(fill=BOTH, expand=True)

        # Image display canvas
        self.canvas = ttk.Canvas(self.container, width=800, height=500)
        self.canvas.pack(pady=10)

        # Image control frame
        self.control_frame = ttk.Frame(self.container)
        self.control_frame.pack(fill=X, pady=10)

        # Load and Save buttons
        self.btn_frame = ttk.Frame(self.control_frame)
        self.btn_frame.pack(side=TOP, fill=X)

        self.btn_load = ttk.Button(
            self.btn_frame, 
            text='Load Image', 
            command=self.load_image, 
            bootstyle='primary'
        )
        self.btn_load.pack(side=LEFT, padx=5)

        self.btn_save = ttk.Button(
            self.btn_frame, 
            text='Save Image', 
            command=self.save_image, 
            bootstyle='success'
        )
        self.btn_save.pack(side=LEFT, padx=5)

        # Checkboxes frame
        self.checkbox_frame = ttk.Frame(self.control_frame)
        self.checkbox_frame.pack(side=TOP, fill=X, pady=5)

        # Invert colors checkbox
        self.invert_var = ttk.BooleanVar(value=True)
        self.chk_invert = ttk.Checkbutton(
            self.checkbox_frame, 
            text='Invert Colors', 
            variable=self.invert_var,
            bootstyle='primary',
            command=self.update_image
        )
        self.chk_invert.pack(side=LEFT, padx=10)

        # Auto white balance checkbox
        self.auto_wb_var = ttk.BooleanVar(value=True)
        self.chk_auto_wb = ttk.Checkbutton(
            self.checkbox_frame, 
            text='Auto White Balance', 
            variable=self.auto_wb_var,
            bootstyle='primary',
            command=self.update_image
        )
        self.chk_auto_wb.pack(side=LEFT, padx=10)

        # Sliders frame
        self.slider_frame = ttk.Frame(self.control_frame)
        self.slider_frame.pack(side=TOP, fill=X, pady=10)

        # Brightness slider
        self.label_brightness = ttk.Label(self.slider_frame, text='Brightness')
        self.label_brightness.pack()
        self.scale_brightness = ttk.Scale(
            self.slider_frame, 
            from_=0, 
            to=2, 
            value=1, 
            bootstyle='primary',
            command=self.update_image
        )
        self.scale_brightness.pack(fill=X, padx=20)

        # Contrast slider
        self.label_contrast = ttk.Label(self.slider_frame, text='Contrast')
        self.label_contrast.pack()
        self.scale_contrast = ttk.Scale(
            self.slider_frame, 
            from_=0, 
            to=20, 
            value=4, 
            bootstyle='primary',
            command=self.update_image
        )
        self.scale_contrast.pack(fill=X, padx=20)

        # Initialize variables
        self.orig_img = None
        self.enhanced_img = None
        self.img = None
        self.img_display = self.canvas.create_image(400, 250, image=self.img)

    def remove_orange_cast(self, image):
        """
        Remove orange cast from film negatives using a simple color balancing technique.
        
        This method:
        1. Converts image to numpy array
        2. Calculates mean RGB values
        3. Adjusts color channels to neutralize orange cast
        """
        # Convert PIL Image to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Separate color channels
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Calculate mean values
        r_mean, g_mean, b_mean = r.mean(), g.mean(), b.mean()
        
        # Adjust channels to neutralize orange cast
        # Reduce red and green channels more aggressively
        r_adjusted = r * (b_mean / r_mean)
        g_adjusted = g * (b_mean / g_mean)
        
        # Recombine channels
        img_array[:,:,0] = np.clip(r_adjusted, 0, 255)
        img_array[:,:,1] = np.clip(g_adjusted, 0, 255)
        
        # Convert back to PIL Image
        return Image.fromarray(np.uint8(img_array))

    def auto_white_balance(self, image):
        """
        Simple auto white balance using gray world assumption
        """
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Calculate mean values for each channel
        r_mean = img_array[:,:,0].mean()
        g_mean = img_array[:,:,1].mean()
        b_mean = img_array[:,:,2].mean()
        
        # Calculate scaling factors
        gray_world_mean = (r_mean + g_mean + b_mean) / 3
        
        # Scale each channel
        r_scaled = img_array[:,:,0] * (gray_world_mean / r_mean)
        g_scaled = img_array[:,:,1] * (gray_world_mean / g_mean)
        b_scaled = img_array[:,:,2] * (gray_world_mean / b_mean)
        
        # Recombine and clip
        balanced_array = np.stack([
            np.clip(r_scaled, 0, 255),
            np.clip(g_scaled, 0, 255),
            np.clip(b_scaled, 0, 255)
        ], axis=-1)
        
        return Image.fromarray(np.uint8(balanced_array))

    def update_image(self, *args):
        if self.orig_img is None:
            return

        # Start with original image
        processed_img = self.orig_img.copy()

        # Remove orange cast
        processed_img = self.remove_orange_cast(processed_img)

        # Invert colors if checked
        if self.invert_var.get():
            processed_img = ImageOps.invert(processed_img)

        # Apply brightness and contrast adjustments
        brightness = self.scale_brightness.get()
        contrast = self.scale_contrast.get()

        # Enhance contrast
        processed_img = ImageOps.autocontrast(processed_img, cutoff=contrast)
        
        # Enhance brightness
        enhancer = ImageEnhance.Brightness(processed_img)
        processed_img = enhancer.enhance(brightness)

        # Apply auto white balance if checked
        if self.auto_wb_var.get():
            processed_img = self.auto_white_balance(processed_img)
        
        # Store the enhanced image
        self.enhanced_img = processed_img
        
        # Resize and display
        copy = processed_img.copy()
        copy.thumbnail((800, 500), Image.ADAPTIVE)
        self.img = ImageTk.PhotoImage(copy)
        self.canvas.itemconfig(self.img_display, image=self.img)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ('Image files', '*.jpg *.jpeg *.png *.bmp *.tiff'),
                ('All files', '*.*')
            ]
        )
        if file_path:
            self.orig_img = Image.open(file_path).convert('RGB')
            self.update_image()

    def save_image(self):
        if self.enhanced_img is None:
            tk.messagebox.showwarning('Warning', 'No image to save')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ('PNG', '*.png'),
                ('JPEG', '*.jpg'),
                ('BMP', '*.bmp'),
                ('TIFF', '*.tiff')
            ]
        )
        if file_path:
            self.enhanced_img.save(file_path)

def main():
    # Use ttkbootstrap for modern theming
    root = ttk.Window(themename="superhero")
    app = FilmNegativeConverter(root)
    root.mainloop()

if __name__ == '__main__':
    main()
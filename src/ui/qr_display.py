import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import platform
import os
import tempfile

class QRDisplayWindow:
    def __init__(self, parent, qr_image: Image.Image, summary_data: dict, qr_id: str):
        self.parent = parent
        self.qr_image = qr_image
        self.summary_data = summary_data
        self.qr_id = qr_id
        
        self.window = tk.Toplevel(parent)
        self.window.title("Recycling Receipt")
        self.window.geometry("400x550")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all UI widgets for QR display"""
        # Display QR code
        tk_img = ImageTk.PhotoImage(self.qr_image)
        qr_label = tk.Label(self.window, image=tk_img)
        qr_label.image = tk_img  # Keep reference
        qr_label.pack(pady=10)
        
        # Display QR ID
        qr_id_label = tk.Label(
            self.window,
            text=f"QR ID: {self.qr_id}",
            font=('Helvetica', 10),
            fg='gray'
        )
        qr_id_label.pack(pady=5)
        
        # Display summary
        summary_text = (f"Plastic Bottles: {self.summary_data.get('plastic_count', 0)}\n"
                       f"Cans: {self.summary_data.get('can_count', 0)}\n"
                       f"Total Items: {self.summary_data.get('total_count', 0)}")
        
        summary_label = tk.Label(
            self.window, 
            text=summary_text, 
            font=('Helvetica', 12)
        )
        summary_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=15)
        
        # Print button
        print_btn = tk.Button(
            button_frame,
            text="Print Receipt",
            command=self.print_receipt,
            width=15,
            height=2
        )
        print_btn.pack(side=tk.LEFT, padx=10)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            width=15,
            height=2
        )
        close_btn.pack(side=tk.LEFT, padx=10)
    
    def print_receipt(self):
        """Cross-platform printing of receipt with QR ID"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_path = tmp.name
                self.qr_image.save(temp_path)
                
                # Platform-specific printing
                system = platform.system()
                if system == "Windows":
                    os.startfile(temp_path, "print")
                elif system == "Darwin":  # macOS
                    os.system(f"lpr -o fit-to-page {temp_path}")
                else:  # Linux
                    os.system(f"xdg-open {temp_path}")
                
                # Queue file for deletion after printing
                self.window.after(10000, lambda: os.unlink(temp_path))
                
                # Show success message
                messagebox.showinfo(
                    "Printing",
                    f"Receipt with QR ID {self.qr_id} sent to printer"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Print Error",
                f"Could not print receipt:\n{str(e)}"
            )
    
    def on_close(self):
        """Clean up when window is closed"""
        self.window.destroy()
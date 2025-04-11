import tkinter as tk
from tkinter import messagebox, ttk
from queue import Queue
import threading
from PIL import Image

from ui.qr_display import QRDisplayWindow

class RVMachineUI:
    def __init__(self, command_queue: Queue, response_queue: Queue):
        self.command_queue = command_queue
        self.response_queue = response_queue
        self.root = tk.Tk()
        self.root.title("Reverse Vending Machine")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configure window size and position
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # System state
        self.session_active = False
        self.processing_item = False
        
        # Create UI elements
        self.create_widgets()
        
        # Start the UI update thread
        self.update_thread = threading.Thread(target=self.update_ui, daemon=True)
        self.update_thread.start()
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            main_frame, 
            text="Reverse Vending Machine", 
            font=('Helvetica', 16, 'bold')
        )
        header.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Waiting for user...", 
            font=('Helvetica', 12)
        )
        self.status_label.pack()
        
        # Instructions
        self.instructions_label = ttk.Label(
            main_frame,
            text="Please place your recyclable item (plastic bottle or can) in the machine",
            wraplength=400,
            justify=tk.CENTER
        )
        self.instructions_label.pack(pady=10)
        
        # Session info frame
        info_frame = ttk.LabelFrame(main_frame, text="Current Session", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Session counters
        self.plastic_count = ttk.Label(info_frame, text="Plastic Bottles: 0")
        self.plastic_count.pack(anchor=tk.W)
        
        self.can_count = ttk.Label(info_frame, text="Cans: 0")
        self.can_count.pack(anchor=tk.W)

        self.reject_count = ttk.Label(info_frame, text="Rejected Items: 0")
        self.reject_count.pack(anchor=tk.W)
        
        self.total_count = ttk.Label(info_frame, text="Total Items: 0")
        self.total_count.pack(anchor=tk.W)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Session", 
            command=self.start_session
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.end_button = ttk.Button(
            button_frame, 
            text="End Session", 
            command=self.end_session,
            state=tk.DISABLED
        )
        self.end_button.pack(side=tk.LEFT, padx=5)
        
        # Detection result
        self.detection_result = ttk.Label(
            main_frame,
            text="",
            font=('Helvetica', 10),
            foreground="green"
        )
        self.detection_result.pack(pady=5)
    
    def start_session(self):
        """Handle start session button click"""
        self.command_queue.put("START_SESSION")
        self.start_button.config(state=tk.DISABLED)
        self.end_button.config(state=tk.NORMAL)
        self.status_label.config(text="Session active - please insert items")
        self.session_active = True
    
    def end_session(self):
        """Handle end session button click"""
        self.command_queue.put("END_SESSION")
        self.start_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        self.status_label.config(text="Session ended - waiting for user")
        self.session_active = False
    
    def update_ui(self):
        """Continuously update UI based on responses from main controller"""
        while True:
            try:
                # Check for messages from main controller
                message = self.response_queue.get(timeout=0.1)
                
                if message.startswith("DETECTION_RESULT:"):
                    result = message.split(":")[1]
                    self.detection_result.config(text=result)
                    self.root.after(3000, lambda: self.detection_result.config(text=""))
                
                elif message.startswith("SESSION_DATA:"):
                    try:
                        data_str = message.split("SESSION_DATA:")[1]
                        data = eval(data_str)  # Safe because we control the input
                        
                        # Update all counters
                        self.plastic_count.config(text=f"Plastic Bottles: {data.get('plastic_count', 0)}")
                        self.can_count.config(text=f"Cans: {data.get('can_count', 0)}")
                        self.reject_count.config(text=f"Rejected Items: {data.get('rejected_count', 0)}")
                        self.total_count.config(text=f"Total Items: {data.get('total_count', 0)}")
                        
                        # Flash the background to show update
                        self._flash_background()
                        
                    except Exception as e:
                        print(f"Error processing session data: {e}")
                
                elif message == "DISPLAY_QR":
                    # Get the next item from queue which contains the QR data
                    qr_data = self.response_queue.get()
                    if len(qr_data) == 3:  # Ensure we have all three components
                        qr_image, counts, qr_id = qr_data
                        self.display_qr_window(qr_image, counts, qr_id)
                    else:
                        self.logger.error("Invalid QR data received")
                
                elif message == "SHOW_QR":
                    # For backward compatibility
                    qr_path = self.response_queue.get()
                    self.show_qr_message(qr_path)
                
                elif message == "QR_GENERATION_FAILED":
                    messagebox.showerror(
                        "Error",
                        "Failed to generate QR code for your session."
                    )
                
                elif message == "SESSION_STARTED":
                    # Reset the session counters
                    self.plastic_count.config(text="Plastic Bottles: 0")
                    self.can_count.config(text="Cans: 0")
                    self.total_count.config(text="Total Items: 0")
                    self.detection_result.config(text="")
                
                elif message == "SYSTEM_SHUTDOWN":
                    self.root.after(0, lambda: messagebox.showinfo(
                        "System Shutting Down",
                        "The system is shutting down. Please complete your session."
                    ))
            
            except Exception as e:
                continue
    
    def display_qr_window(self, qr_image: Image.Image, counts: dict, qr_id: str):
        """Display QR code in a new window"""
        QRDisplayWindow(self.root, qr_image, counts, qr_id)

    def _flash_background(self):
        """Flash the background to visually indicate update"""
        original_bg = self.plastic_count.cget('background')
        for widget in [self.plastic_count, self.can_count, self.total_count]:
            widget.config(background='light green')
            self.root.after(100, lambda w=widget, bg=original_bg: w.config(background=bg))
    
    def show_qr_message(self, qr_path):
        """Show message with QR code information"""
        messagebox.showinfo(
            "Session Complete",
            f"Thank you for recycling!\n\nQR code saved to:\n{qr_path}"
        )
    
    def on_close(self):
        """Handle window close event"""
        self.command_queue.put("QUIT")
        self.root.quit()
    
    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()
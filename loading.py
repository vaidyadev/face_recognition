from tkinter import Toplevel, Label, Canvas
from PIL import Image, ImageTk
from utils import resource_path

class LoadingSplash:
    def __init__(self, root, message="Loading... Please Wait"):
        self.root = root
        self.window = Toplevel(root)
        self.window.title(message)
        self.window.attributes('-topmost', True)
        self.window.geometry("350x200")
        
        # Center the window
        x = root.winfo_x() + (root.winfo_width() // 2) - 175
        y = root.winfo_y() + (root.winfo_height() // 2) - 100
        self.window.geometry(f"+{x}+{y}")
        self.window.overrideredirect(True) # Remove title bar
        self.window.config(bg='#1A1A2E') # Dark modern background
        
        # Border frame to give it a neat look
        self.border_frame = Canvas(self.window, bg='#16213E', highlightthickness=1, highlightbackground='#0F3460')
        self.border_frame.pack(fill='both', expand=True, padx=2, pady=2)

        # Message Label
        self.msg_label = Label(self.border_frame, text=message, font=("Helvetica", 13, "bold"), bg="#16213E", fg="white")
        self.msg_label.pack(pady=(30, 10))
        
        # Canvas for custom spinner
        self.canvas = Canvas(self.border_frame, width=100, height=100, bg='#16213E', highlightthickness=0)
        self.canvas.pack()
        
        self.angle = 0
        self.running = True
        self.after_id = None
        self.draw_spinner()
        
        self.sub_msg = Label(self.border_frame, text="Initializing components...", font=("Helvetica", 10), bg="#16213E", fg="#A0A0A0")
        self.sub_msg.pack(side='bottom', pady=(10, 20))
        
        self.window.update_idletasks()
        self.window.update()

    def draw_spinner(self):
        if not self.running: return
        self.canvas.delete("spinner")
        
        x0, y0, x1, y1 = 25, 25, 75, 75
        width = 4
        
        # Draw background circle
        self.canvas.create_oval(x0, y0, x1, y1, outline="#0F3460", width=width, tags="spinner")
        
        # Draw animated arc (tail)
        start_angle = self.angle
        extent = 120  # Arc length
        self.canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=extent, outline="#E94560", width=width, style="arc", tags="spinner")
        
        # Update angle
        self.angle = (self.angle - 15) % 360
        
        # Schedule next frame
        if self.window.winfo_exists():
            self.after_id = self.window.after(30, self.draw_spinner)

    def update_message(self, msg):
        if hasattr(self, 'msg_label') and self.msg_label.winfo_exists():
            self.msg_label.config(text=msg)
        if hasattr(self, 'sub_msg') and self.sub_msg.winfo_exists():
            self.sub_msg.config(text=msg)
            self.window.update()

    def destroy(self):
        self.running = False
        if hasattr(self, 'after_id') and self.after_id is not None:
            try:
                self.window.after_cancel(self.after_id)
            except: pass
        try:
            if self.window.winfo_exists():
                self.window.destroy()
        except:
            pass

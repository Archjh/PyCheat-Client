import os
import platform
from tkinter import *
from collections import deque

class FPSHUDDisplay:
    def __init__(self):
        # Initialize the GUI window
        self.window = Tk()
        self.window.overrideredirect(True)
        self.window.config(bg='#000000')
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.85)
        
        # Window dimensions
        self.width = 100
        self.height = 50
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position (top center)
        x_pos = (screen_width // 2) - (self.width // 2)  # Centered horizontally
        y_pos = 10  # Top margin
        
        # Set window geometry
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas
        self.canvas = Canvas(self.window, highlightthickness=0, bg='#000000')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # FPS display elements
        self.fps_text = None
        self.fps_value = "0"
        
        # File path to monitor
        self.file_path = self.get_minecraft_path('fps_display.txt')
        
        # Start the update loop
        self.update_fps_display()
        
        # Start the GUI
        self.window.mainloop()
    
    def get_minecraft_path(self, filename):
        """Get the .minecraft path based on OS"""
        system = platform.system()
        
        if system == "Windows":
            return os.path.join(os.getenv('APPDATA'), '.minecraft', filename)
        elif system == "Darwin":  # Mac
            return os.path.expanduser(f'~/Library/Application Support/minecraft/{filename}')
        else:  # Linux and others
            return os.path.expanduser(f'~/.minecraft/{filename}')
    
    def get_fps_color(self, fps):
        """Return color based on FPS value"""
        try:
            fps_num = int(fps)
            if fps_num >= 60:
                return '#00FF00'  # Green - good performance
            elif fps_num >= 30:
                return '#FFFF00'  # Yellow - acceptable
            else:
                return '#FF0000'  # Red - poor performance
        except:
            return '#FFFFFF'  # Default white
    
    def update_fps_display(self):
        """Check the FPS file and update the display"""
        try:
            # Clear existing display
            if self.fps_text:
                self.canvas.delete(self.fps_text)
            
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    fps = f.readline().strip()
                    self.fps_value = fps if fps else "0"
            
            # Create FPS display text
            color = self.get_fps_color(self.fps_value)
            self.fps_text = self.canvas.create_text(
                self.width // 2, self.height // 2,
                text=f"FPS: {self.fps_value}",
                fill=color,
                font=('Arial', 14, 'bold'),
                anchor=CENTER
            )
            
        except Exception as e:
            print(f"Error updating FPS display: {e}")
        
        # Schedule next update
        self.window.after(500, self.update_fps_display)

# Start the application
if __name__ == "__main__":
    FPSHUDDisplay()

import os
import platform
from tkinter import *

class TargetHUDDisplay:
    def __init__(self):
        # Initialize the GUI window
        self.window = Tk()
        self.window.title("Minecraft Target HUD")
        self.window.overrideredirect(True)
        self.window.config(bg='black')
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.85)
        
        # Window dimensions
        self.width = 150
        self.height = 80
        
        # Get screen dimensions
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        # Position in bottom right corner (with some margin)
        x_pos = self.screen_width - self.width - 20  # Right margin
        y_pos = self.screen_height - self.height - 20  # Bottom margin
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas
        self.canvas = Canvas(self.window, highlightthickness=0, bg='black')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # File path to monitor
        self.file_path = self.get_minecraft_path('target_info.txt')
        print(f"Monitoring file at: {self.file_path}")
        
        # Draw initial display
        self.draw_background()
        self.update_target_status()
        
        # Start the GUI
        self.window.mainloop()
    
    def get_minecraft_path(self, filename):
        """Get the .minecraft path based on OS"""
        system = platform.system()
        
        if system == "Windows":
            path = os.path.join(os.getenv('APPDATA'), '.minecraft', filename)
        elif system == "Darwin":  # Mac
            path = os.path.expanduser(f'~/Library/Application Support/minecraft/{filename}')
        else:  # Linux and others
            path = os.path.expanduser(f'~/.minecraft/{filename}')
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
    
    def draw_background(self):
        """Draw a semi-transparent background with border"""
        # Main background (using window alpha for transparency)
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill='#222222', outline='')
        # Border lines
        self.canvas.create_rectangle(0, 0, self.width, 1, fill='#555555', outline='')
        self.canvas.create_rectangle(0, self.height-1, self.width, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(0, 0, 1, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(self.width-1, 0, self.width, self.height, fill='#555555', outline='')
    
    def get_health_color(self, health_percent):
        """Return color based on health percentage"""
        if health_percent > 0.6:
            return '#00FF00'
        elif health_percent > 0.3:
            return '#FFFF00'
        return '#FF0000'
    
    def update_target_status(self):
        """Check the target status file and update the display"""
        try:
            self.canvas.delete("all")
            self.draw_background()
            
            # Default values if file doesn't exist or can't be read
            name = "No Target"
            health_text = "HP: 0.0/0.0"
            distance = "距离: 0.0"
            health_color = '#FFFFFF'
            
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                if len(lines) >= 3:
                    name = lines[0]
                    health_text = lines[1]
                    distance = lines[2]
                    
                    # Health color calculation
                    try:
                        health_info = health_text.split('/')
                        current_health = float(health_info[0].split(': ')[1])
                        max_health = float(health_info[1])
                        health_percent = current_health / max_health
                        health_color = self.get_health_color(health_percent)
                    except Exception as e:
                        print(f"Health parse error: {e}")
            
            # Draw elements
            self.canvas.create_rectangle(5, 5, 35, 35, fill='#333333', outline='#555555')
            self.canvas.create_text(20, 20, text="👤", font=('Arial', 12))
            self.canvas.create_text(45, 10, text=name, anchor=NW, fill='white', font=('Arial', 10, 'bold'))
            self.canvas.create_text(45, 30, text=health_text, anchor=NW, fill=health_color, font=('Arial', 9))
            self.canvas.create_text(45, 50, text=distance, anchor=NW, fill='#AAAAAA', font=('Arial', 9))
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Schedule next update
        self.window.after(300, self.update_target_status)

if __name__ == "__main__":
    TargetHUDDisplay()

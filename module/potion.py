import os
import platform
from tkinter import *
from collections import deque

class PotionHUDDisplay:
    def __init__(self):
        # Initialize the GUI window
        self.window = Tk()
        self.window.overrideredirect(True)
        self.window.config(bg='#000000')
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.85)
        
        # Window will resize based on content
        self.width = 200
        self.min_height = 30
        self.current_height = self.min_height
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position (left side, centered vertically)
        x_pos = 10  # Left margin
        y_pos = (screen_height // 2) - (self.current_height // 2)
        
        # Set window geometry
        self.window.geometry(f'{self.width}x{self.current_height}+{x_pos}+{y_pos}')
        
        # Create canvas
        self.canvas = Canvas(self.window, highlightthickness=0, bg='#000000')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # Potion effect elements
        self.potion_effects = []
        
        # File path to monitor
        self.file_path = self.get_minecraft_path('potion_hud.txt')
        
        # Start the update loop
        self.update_potion_status()
        
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
    
    def get_potion_color(self, potion_name):
        """Return color based on potion type"""
        potion_name = potion_name.lower()
        
        # Standard potion colors
        if 'speed' in potion_name or 'haste' in potion_name:
            return '#7CAFC6'  # Light blue
        elif 'slowness' in potion_name:
            return '#5A6C81'  # Dark blue
        elif 'strength' in potion_name or 'damage' in potion_name:
            return '#932423'  # Red
        elif 'jump' in potion_name:
            return '#22FF33'  # Bright green
        elif 'regeneration' in potion_name:
            return '#CD5CAB'  # Pink
        elif 'fire resistance' in potion_name:
            return '#E49E3A'  # Orange
        elif 'water breathing' in potion_name:
            return '#2E5299'  # Dark blue
        elif 'invisibility' in potion_name:
            return '#7F8392'  # Gray
        elif 'night vision' in potion_name:
            return '#1F1FA1'  # Dark blue
        elif 'poison' in potion_name:
            return '#4E9331'  # Green
        elif 'weakness' in potion_name:
            return '#484D48'  # Dark gray
        elif 'wither' in potion_name:
            return '#352A27'  # Brown
        elif 'health boost' in potion_name:
            return '#F87D23'  # Orange
        elif 'absorption' in potion_name:
            return '#F8B71D'  # Gold
        
        return '#FFFFFF'  # Default white
    
    def update_potion_status(self):
        """Check the potion status file and update the display"""
        try:
            # Clear existing effects
            for effect in self.potion_effects:
                self.canvas.delete(effect['name_text'])
                self.canvas.delete(effect['duration_text'])
            self.potion_effects = []
            
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                # Calculate new window height based on number of effects
                num_effects = len(lines)
                self.current_height = max(self.min_height, 30 + (num_effects * 40))
                
                # Update window size and position
                screen_height = self.window.winfo_screenheight()
                y_pos = (screen_height // 2) - (self.current_height // 2)
                self.window.geometry(f'{self.width}x{self.current_height}+10+{y_pos}')
                
                # Process each potion effect
                for i, line in enumerate(lines):
                    parts = line.split(';')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        duration = parts[1].strip()
                        color = self.get_potion_color(name)
                        
                        # Create text elements for this potion
                        name_text = self.canvas.create_text(
                            10, 15 + i*40, 
                            text=name, 
                            anchor=NW, 
                            fill=color, 
                            font=('Arial', 10, 'bold')
                        )
                        
                        duration_text = self.canvas.create_text(
                            10, 35 + i*40, 
                            text=duration, 
                            anchor=NW, 
                            fill='#AAAAAA', 
                            font=('Arial', 9)
                        )
                        
                        self.potion_effects.append({
                            'name_text': name_text,
                            'duration_text': duration_text
                        })
            
        except Exception as e:
            print(f"Error updating potion status: {e}")
        
        # Schedule next update
        self.window.after(500, self.update_potion_status)

# Start the application
if __name__ == "__main__":
    PotionHUDDisplay()

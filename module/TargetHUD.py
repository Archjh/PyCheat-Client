import os
import platform
from tkinter import *
from flask import Flask, request
import threading

class TargetHUDDisplay:
    def __init__(self):
        # Initialize thread lock and latest data storage
        self.latest_target_data = {
            "name": "No Target",
            "health": 0,
            "max_health": 0,
            "distance": 0
        }
        self.data_lock = threading.Lock()
        
        # Initialize the GUI window
        self.window = Tk()
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
        
        # Position in middle-left of the screen
        x_pos = int(self.screen_width * 0.25 - self.width / 2)  # 25% from left
        y_pos = int(self.screen_height / 2 - self.height / 2)  # Centered vertically
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas
        self.canvas = Canvas(self.window, highlightthickness=0, bg='black')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # Start Flask server
        self.start_flask_server()
        
        # Draw initial display
        self.draw_background()
        self.update_target_status()
        
        # Start the GUI
        self.window.mainloop()
    
    def draw_background(self):
        """Draw a semi-transparent background with border"""
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill='#222222', outline='')
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
        """Update display with latest target data"""
        with self.data_lock:
            target_data = self.latest_target_data
        
        try:
            self.canvas.delete("all")
            self.draw_background()
            
            name = target_data["name"]
            health = target_data["health"]
            max_health = target_data["max_health"]
            distance = target_data["distance"]
            
            # Calculate health percentage and color
            health_percent = health / max_health if max_health > 0 else 0
            health_color = self.get_health_color(health_percent)
            health_text = f"HP: {health:.1f}/{max_health:.1f}"
            distance_text = f"距离: {distance:.1f}"
            
            # Draw elements
            self.canvas.create_rectangle(5, 5, 35, 35, fill='#333333', outline='#555555')
            self.canvas.create_text(20, 20, text="👤", font=('Arial', 12))
            self.canvas.create_text(45, 10, text=name, anchor=NW, fill='white', font=('Arial', 10, 'bold'))
            self.canvas.create_text(45, 30, text=health_text, anchor=NW, fill=health_color, font=('Arial', 9))
            self.canvas.create_text(45, 50, text=distance_text, anchor=NW, fill='#AAAAAA', font=('Arial', 9))
            
        except Exception as e:
            print(f"Error updating target display: {e}")
        
        # Schedule next update
        self.window.after(300, self.update_target_status)
        
    def start_flask_server(self):
        app = Flask(__name__)
        
        @app.route('/update_target', methods=['POST'])
        def update_target():
            data = request.json.get("target_data", {})
            with self.data_lock:
                self.latest_target_data = {
                    "name": data.get("name", "No Target"),
                    "health": data.get("health", 0),
                    "max_health": data.get("max_health", 0),
                    "distance": data.get("distance", 0)
                }
            return "OK"
        
        # Run Flask server in background thread
        self.flask_thread = threading.Thread(
            target=lambda: app.run(host='localhost', port=5003, debug=False, use_reloader=False)
        )
        self.flask_thread.daemon = True
        self.flask_thread.start()

if __name__ == "__main__":
    TargetHUDDisplay()

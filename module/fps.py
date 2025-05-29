import os
import platform
from tkinter import *
from flask import Flask, request
import threading

class FPSHUDDisplay:
    def __init__(self):
        # Initialize thread lock and latest data storage
        self.latest_fps = 0
        self.data_lock = threading.Lock()
        
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
        x_pos = (screen_width // 2) - (self.width // 2)
        y_pos = 10
        
        # Set window geometry
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas
        self.canvas = Canvas(self.window, highlightthickness=0, bg='#000000')
        self.canvas.pack(fill=BOTH, expand=True)
        
        # FPS display elements
        self.fps_text = None
        
        # Start Flask server
        self.start_flask_server()
        
        # Start the update loop
        self.update_fps_display()
        
        # Start the GUI
        self.window.mainloop()
    
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
        """Update display with latest FPS data"""
        with self.data_lock:
            fps = self.latest_fps
        
        # Clear existing display
        if self.fps_text:
            self.canvas.delete(self.fps_text)
        
        # Create FPS display text
        color = self.get_fps_color(fps)
        self.fps_text = self.canvas.create_text(
            self.width // 2, self.height // 2,
            text=f"FPS: {fps}",
            fill=color,
            font=('Arial', 14, 'bold'),
            anchor=CENTER
        )
        
        # Schedule next update
        self.window.after(500, self.update_fps_display)
        
    def start_flask_server(self):
        app = Flask(__name__)
        
        @app.route('/update_fps', methods=['POST'])
        def update_fps():
            data = request.json
            with self.data_lock:
                self.latest_fps = data.get('fps', 0)
            return "OK"
        
        # Run Flask server in background thread
        self.flask_thread = threading.Thread(
            target=lambda: app.run(host='localhost', port=5002, debug=False, use_reloader=False)
        )
        self.flask_thread.daemon = True
        self.flask_thread.start()

# Start the application
if __name__ == "__main__":
    FPSHUDDisplay()

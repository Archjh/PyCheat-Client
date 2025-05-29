import os
import time
from tkinter import *
from collections import deque
from flask import Flask, request
import threading

class PotionStatusDisplay:
    def __init__(self):
        # Initialize thread lock and latest data storage
        self.latest_potion_data = []
        self.data_lock = threading.Lock()
        
        # Initialize the GUI window
        self.window = Tk()
        self.window.overrideredirect(True)
        self.window.config(bg='#222222')  # Matching style with ArmorHUD
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.85)
        
        # Window dimensions and position (top-right corner, below armor display)
        self.width = 180
        self.height = 150  # Adjusted for potion display
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position (top-right corner, below armor display)
        x_pos = screen_width - self.width - 1750
        y_pos = 110  # Below armor display
        
        # Set window geometry
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas with matching style
        self.canvas = Canvas(self.window, highlightthickness=0, bg='#222222')
        self.canvas.place(width=self.width, height=self.height)
        
        # Draw border like ArmorHUD
        self.canvas.create_rectangle(0, 0, self.width, 1, fill='#555555', outline='')
        self.canvas.create_rectangle(0, self.height-1, self.width, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(0, 0, 1, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(self.width-1, 0, self.width, self.height, fill='#555555', outline='')
        
        # Title label
        self.canvas.create_text(self.width//2, 15, 
                               text="药水效果", 
                               fill='white', 
                               font=('Arial', 12, 'bold'),
                               anchor='center')
        
        # Potion effect elements
        self.potion_texts = []
        self.potion_duration_bars = []
        
        # Create UI elements for potion effects
        for i in range(5):  # Support up to 5 potion effects
            # Potion effect name and amplifier
            text = self.canvas.create_text(10, 35 + i*25, 
                                        text='', 
                                        fill='white', 
                                        font=('Arial', 10),
                                        anchor='w')
            
            # Potion duration bar background
            bar_bg = self.canvas.create_rectangle(10, 45 + i*25, self.width-10, 50 + i*25, 
                                                fill='#444444', outline='')
            
            # Potion duration bar foreground
            bar_fg = self.canvas.create_rectangle(10, 45 + i*25, 10, 50 + i*25, 
                                                fill='#55FF55', outline='')
            
            self.potion_texts.append(text)
            self.potion_duration_bars.append((bar_bg, bar_fg))
        
        # Start Flask server
        self.start_flask_server()
        
        # Start the update loop
        self.update_potion_status()
        
        # Start the GUI
        self.window.mainloop()
    
    def get_potion_color(self, potion_name):
        """Return color based on potion type"""
        potion_name = potion_name.lower()
        
        if 'speed' in potion_name or 'haste' in potion_name:
            return '#55FF55'  # Green for speed
        elif 'strength' in potion_name or 'damage' in potion_name:
            return '#FF5555'  # Red for strength
        elif 'jump' in potion_name:
            return '#FFAA00'  # Orange for jump boost
        elif 'regeneration' in potion_name:
            return '#FF00FF'  # Pink for regeneration
        elif 'resistance' in potion_name or 'protection' in potion_name:
            return '#AAAAAA'  # Light gray for resistance
        elif 'water' in potion_name or 'breathing' in potion_name:
            return '#00FFFF'  # Cyan for water breathing
        elif 'invisibility' in potion_name:
            return '#999999'  # Gray for invisibility
        elif 'night' in potion_name or 'vision' in potion_name:
            return '#1F1F9F'  # Dark blue for night vision
        elif 'fire' in potion_name:
            return '#FF6600'  # Orange-red for fire resistance
        else:
            return '#FFFFFF'  # White for others
    
    def update_potion_status(self):
        """Update display with latest potion data"""
        with self.data_lock:
            potion_effects = self.latest_potion_data
    
        # Clear all potion displays first
        for i in range(5):
            self.canvas.itemconfig(self.potion_texts[i], text='')
            self.canvas.coords(self.potion_duration_bars[i][1], 10, 45 + i*25, 10, 50 + i*25)
    
        # Update with current potion effects
        for i, effect in enumerate(potion_effects[:5]):  # Only show first 5 effects
            parts = effect.split('|')
            if len(parts) >= 3:
                name = parts[0]
                amplifier = parts[1]
                duration_str = parts[2]
             
                # Set text with amplifier (I, II, III, etc.)
                display_text = f"{name} {amplifier}"
                color = self.get_potion_color(name)
            
                self.canvas.itemconfig(self.potion_texts[i], text=display_text, fill=color)
            
                # Update duration bar (如果是 "Instant"，进度条显示 100%)
                if duration_str == "Instant":
                    bar_width = self.width - 20
                else:
                    # 解析 MM:SS 时间（示例逻辑，需根据实际需求调整）
                    try:
                        minutes, seconds = map(int, duration_str.split(':'))
                        total_seconds = minutes * 60 + seconds
                        # 假设最大持续时间为 3 分钟（仅示例，实际应根据药水类型调整）
                        max_seconds = 180
                        progress = min(1.0, max(0.0, total_seconds / max_seconds))
                        bar_width = (self.width - 20) * progress
                    except:
                        bar_width = 0
               
                self.canvas.coords(self.potion_duration_bars[i][1], 
                                  10, 45 + i*25, 
                                  10 + bar_width, 50 + i*25)
                self.canvas.itemconfig(self.potion_duration_bars[i][1], fill=color)
    
        # Continue periodic updates
        self.window.after(500, self.update_potion_status)
        
    def start_flask_server(self):
        app = Flask(__name__)
        
        @app.route('/update_potions', methods=['POST'])
        def update_potions():
            data = request.json
            with self.data_lock:
                self.latest_potion_data = data.get('potion_data', [])
            return "OK"
        
        # Run Flask server in background thread
        self.flask_thread = threading.Thread(
            target=lambda: app.run(host='localhost', port=5001, debug=False, use_reloader=False)
        )
        self.flask_thread.daemon = True
        self.flask_thread.start()

# Start the application
if __name__ == "__main__":
    PotionStatusDisplay()

import os
import time
from tkinter import *
from collections import deque
from flask import Flask, request
import threading

class ArmorStatusDisplay:
    def __init__(self):
        # 初始化线程锁和最新数据存储
        self.latest_armor_data = ["empty,0"] * 4
        self.data_lock = threading.Lock()
        
        # Initialize the GUI window
        self.window = Tk()
        self.window.overrideredirect(True)
        self.window.config(bg='#222222')  # Changed to match TargetHUD
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.85)  # Matched alpha with TargetHUD
        
        # Window dimensions and position (top-right corner)
        self.width = 180  # Slightly wider for better text display
        self.height = 100
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate position (top-right corner)
        x_pos = screen_width - self.width - 1750
        y_pos = 0
        
        # Set window geometry
        self.window.geometry(f'{self.width}x{self.height}+{x_pos}+{y_pos}')
        
        # Create canvas with matching style
        self.canvas = Canvas(self.window, highlightthickness=0, bg='#222222')
        self.canvas.place(width=self.width, height=self.height)
        
        # Draw border like TargetHUD
        self.canvas.create_rectangle(0, 0, self.width, 1, fill='#555555', outline='')
        self.canvas.create_rectangle(0, self.height-1, self.width, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(0, 0, 1, self.height, fill='#555555', outline='')
        self.canvas.create_rectangle(self.width-1, 0, self.width, self.height, fill='#555555', outline='')
        
        # Armor slots (boots, leggings, chestplate, helmet - in reverse order)
        self.slot_rects = []
        self.slot_texts = []
        
        # Create UI elements for each armor slot in correct order
        for i in range(4):
            # Armor slot rectangle
            rect = self.canvas.create_rectangle(10, 10 + i*22, 30, 30 + i*22, fill='gray', outline='#555555')
            
            # Armor info text with consistent formatting
            text = self.canvas.create_text(90, 20 + i*22, 
                                        text='None, 0%', 
                                        fill='white', 
                                        font=('Arial', 10),  # Changed to Arial for consistency
                                        anchor='center')
            self.slot_rects.append(rect)
            self.slot_texts.append(text)
        
        # Labels for each slot in correct order (头盔->胸甲->护腿->靴子)
        slot_labels = ['头盔:', '胸甲:', '护腿:', '靴子:']
        for i, label in enumerate(slot_labels):
            self.canvas.create_text(45, 20 + i*22, 
                                  text=label, 
                                  fill='white', 
                                  font=('Arial', 10),  # Changed to Arial
                                  anchor='e')  # Right-aligned
            
        # File path to monitor
        self.file_path = os.path.expanduser('~/.minecraft/armor_status.txt')
        
        # 启动Flask服务器
        self.start_flask_server()
        
        # Start the update loop
        self.update_armor_status()
        
        # Start the GUI
        self.window.mainloop()
    
    def get_armor_color(self, armor_type):
        """Return color based on armor type and material"""
        armor_type = armor_type.lower()
        
        # First check material
        if 'leather' in armor_type:
            return '#A0522D'  # 棕色 for leather
        elif 'iron' in armor_type:
            return '#FFFFFF'  # 白色 for iron
        elif 'chainmail' in armor_type:
            return '#A0A0A0'  # 灰色 for chainmail
        elif 'gold' in armor_type:
            return '#FFD700'  # 黄色 for gold
        elif 'diamond' in armor_type:
            return '#00FFFF'  # 蓝绿色 for diamond
        
        # Then check armor type if material not specified
        if 'helmet' in armor_type:
            return '#FFAA00'  # Default gold for helmet
        elif 'chestplate' in armor_type:
            return '#FF5555'  # Default red for chestplate
        elif 'leggings' in armor_type:
            return '#5555FF'  # Default blue for leggings
        elif 'boots' in armor_type:
            return '#55FF55'  # Default green for boots
        
        return 'gray'  # Default
    
    def update_armor_status(self):
        """从内存中获取最新数据并更新显示"""
        with self.data_lock:
            lines = self.latest_armor_data
        
        # 处理数据与之前相同
        for i, line in enumerate(reversed(lines[:4])):
            parts = line.strip().split(',')
            if len(parts) >= 2:
                armor_type = parts[0].strip()
                durability = parts[1].strip()
                
                color = self.get_armor_color(armor_type)
                self.canvas.itemconfig(self.slot_rects[i], fill=color)
                
                display_text = f"{armor_type}, {durability}%" if armor_type.lower() != "empty" else "None, 0%"
                self.canvas.itemconfig(self.slot_texts[i], text=display_text)
        
        # 继续定期检查更新
        self.window.after(500, self.update_armor_status)
        
    def start_flask_server(self):
        app = Flask(__name__)
        
        @app.route('/update_armor', methods=['POST'])
        def update_armor():
            data = request.json
            with self.data_lock:
                self.latest_armor_data = data.get('armor_data', ["empty,0"] * 4)
            return "OK"
        
        # 在后台线程中运行Flask服务器
        self.flask_thread = threading.Thread(
            target=lambda: app.run(host='localhost', port=5000, debug=False, use_reloader=False)
        )
        self.flask_thread.daemon = True
        self.flask_thread.start()

# Start the application
if __name__ == "__main__":
    ArmorStatusDisplay()

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QListWidget, QSlider, QListWidgetItem, QCheckBox, QFrame
)
from PyQt6.QtCore import QStandardPaths, Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QPainter, QPen, QBrush
from PyQt6.QtCore import pyqtSignal  # Add this import at the top

class RoundSwitch(QWidget):
    # Add this custom signal
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 30)
        self.state = False
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        bg_color = QColor("#30a856" if self.state else "#e5e5ea")
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # Draw switch
        switch_color = QColor("#ffffff")
        painter.setBrush(QBrush(switch_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        x_pos = self.width() - 20 if self.state else 5
        painter.drawEllipse(x_pos, 5, 20, 20)

    def mousePressEvent(self, event):
        self.toggle()

    def toggle(self):
        self.state = not self.state
        self.update()
        # Emit the signal when toggled
        self.toggled.emit(self.state)
        # Also call parent's toggle_state if it exists
        if hasattr(self.parent(), 'toggle_state'):
            self.parent().toggle_state(self.state)
        
class ModuleItem(QWidget):
    def __init__(self, name, initial_state=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.state = initial_state
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel(name)
        self.switch = RoundSwitch()
        self.switch.state = initial_state
        self.switch.update()
        
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.switch)
        
        self.setLayout(layout)
    
    def toggle_state(self, state):
        self.state = state
        self.switch.state = state
        self.switch.update()

def get_resource_path(relative: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", relative)

def get_data_dir() -> str:
    return os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation), "pycheat")

def ensure_data_dir() -> str:
    data_dir = get_data_dir()
    if not os.path.exists(data_dir):
        Path(data_dir).mkdir(parents=True, exist_ok=True)
    return data_dir

def generate_launch_script(java_path: str, mc_dir: str):
    data_dir = ensure_data_dir()
    if platform.system() == "Windows":
        with open(os.path.join(data_dir, "start.bat"), "w") as f, open(get_resource_path("start.bat.template"), "r") as template_file:
            content = template_file.read().replace("#<java_path>#", java_path).replace("#<mc_dir>#", mc_dir)
            f.write(content)
    else:
        with open(os.path.join(data_dir, "start.sh"), "w") as f, open(get_resource_path("start.sh.template"), "r") as template_file:
            content = template_file.read().replace("#<java_path>#", java_path).replace("#<mc_dir>#", mc_dir).replace("#<home_dir>#", str(Path.home()))
            f.write(content)
        os.chmod(os.path.join(data_dir, "start.sh"), 0o755)

class ModuleManager:
    def __init__(self):
        self.modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "module")
        self.modules = {
            "armorr.py": "Armor Status",
            "fps.py": "FPS Display",
            "potion.py": "Potion Effects",
            "TargetHUD.py": "Target HUD",
            "key.py": "Keystrokes"
        }
        self.running_processes = {}
        
        # Create modules directory if it doesn't exist
        os.makedirs(self.modules_dir, exist_ok=True)
        
        # Move existing modules to the module directory
        for module in self.modules:
            src = os.path.join(os.path.dirname(os.path.abspath(__file__)), module)
            if os.path.exists(src):
                dest = os.path.join(self.modules_dir, module)
                if not os.path.exists(dest):
                    os.rename(src, dest)

    def get_module_display_name(self, module_file):
        """获取模块的显示名称"""
        return self.modules.get(module_file, module_file)
    
    def get_module_state(self):
        """Get the saved state of modules"""
        config_path = os.path.join(ensure_data_dir(), "modules.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {module: False for module in self.modules}
    
    def save_module_state(self, state):
        """Save the state of modules"""
        config_path = os.path.join(ensure_data_dir(), "modules.json")
        with open(config_path, "w") as f:
            json.dump(state, f)
    
    def start_module(self, module_name):
        """Start a module"""
        if module_name in self.running_processes:
            return
            
        module_path = os.path.join(self.modules_dir, module_name)
        if os.path.exists(module_path):
            try:
                if platform.system() == "Windows":
                    # On Windows, use pythonw.exe to avoid console windows
                    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                    if not os.path.exists(pythonw):
                        pythonw = sys.executable
                    process = subprocess.Popen([pythonw, module_path], creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    process = subprocess.Popen([sys.executable, module_path])
                
                self.running_processes[module_name] = process
                return True
            except Exception as e:
                print(f"Error starting module {module_name}: {e}")
                return False
        return False
    
    def stop_module(self, module_name):
        """Stop a running module"""
        if module_name in self.running_processes:
            try:
                self.running_processes[module_name].terminate()
                self.running_processes[module_name].wait()
                del self.running_processes[module_name]
                return True
            except Exception as e:
                print(f"Error stopping module {module_name}: {e}")
                return False
        return False
    
    def stop_all_modules(self):
        """Stop all running modules"""
        for module_name in list(self.running_processes.keys()):
            self.stop_module(module_name)

class PyCheat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCheat - Minecraft 1.8.8")
        self.setFixedSize(800, 600)

        # Initialize module manager
        self.module_manager = ModuleManager()

        # Initialize UI
        self.init_ui()

        # Load existing settings
        self.load_settings()

        # Detect Java installations
        self.detect_java()

        # Start modules that were previously enabled
        self.load_and_start_modules()

        # 添加ArrayList窗口（在所有初始化完成后）
        self.array_list_window = ArrayListWindow(self.module_manager)
        self.array_list_window.show()
        self.array_list_window.update_list()

    def on_module_toggle(self, module_name, state):
        """Handle module toggle"""
        if state:  # On
            self.module_manager.start_module(module_name)
        else:  # Off
            self.module_manager.stop_module(module_name)

        # 更新ArrayList
        self.array_list_window.update_list()

        # Save the new state
        module_states = self.module_manager.get_module_state()
        module_states[module_name] = state
        self.module_manager.save_module_state(module_states)

    def closeEvent(self, event):
        """Handle window close event - stop all modules"""
        self.module_manager.stop_all_modules()
        self.array_list_window.close()  # 关闭ArrayList窗口
        event.accept()

    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel for Minecraft settings (keep this the same as before)
        # ... (existing left panel code)
        
        # Right panel for module management
        module_panel = QWidget()
        module_layout = QVBoxLayout()
        module_panel.setLayout(module_layout)
        
        # Add a header with a master switch
        header = QWidget()
        header_layout = QHBoxLayout()
        header.setLayout(header_layout)
        
        self.master_switch_label = QLabel("All Modules:")
        self.master_switch = RoundSwitch()
        self.master_switch.state = False
        self.master_switch.update()
        self.master_switch.toggled.connect(self.toggle_all_modules)
        
        header_layout.addWidget(self.master_switch_label)
        header_layout.addStretch()
        header_layout.addWidget(self.master_switch)
        
        module_layout.addWidget(header)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        module_layout.addWidget(separator)

        # Left panel for Minecraft settings
        settings_panel = QWidget()
        settings_layout = QVBoxLayout()
        settings_panel.setLayout(settings_layout)

        # Java path selection
        java_path_layout = QHBoxLayout()
        java_path_label = QLabel("Java Path:")
        self.java_path_input = QLineEdit()
        java_path_browse = QPushButton("Browse...")
        java_path_browse.clicked.connect(self.browse_java_path)

        java_path_layout.addWidget(java_path_label)
        java_path_layout.addWidget(self.java_path_input)
        java_path_layout.addWidget(java_path_browse)
        settings_layout.addLayout(java_path_layout)

        # Minecraft directory selection
        mc_dir_layout = QHBoxLayout()
        mc_dir_label = QLabel(".minecraft Directory:")
        self.minecraft_dir_input = QLineEdit()
        mc_dir_browse = QPushButton("Browse...")
        mc_dir_browse.clicked.connect(self.browse_minecraft_dir)

        mc_dir_layout.addWidget(mc_dir_label)
        mc_dir_layout.addWidget(self.minecraft_dir_input)
        mc_dir_layout.addWidget(mc_dir_browse)
        settings_layout.addLayout(mc_dir_layout)

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        install_button = QPushButton("Install Client")
        install_button.clicked.connect(self.install_client)
        launch_button = QPushButton("Launch Minecraft")
        launch_button.clicked.connect(self.launch_minecraft)

        button_layout.addWidget(install_button)
        button_layout.addWidget(launch_button)
        settings_layout.addLayout(button_layout)

        # Add some spacing
        settings_layout.addStretch()
        
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e5ea;
                border-radius: 10px;
                background: #f5f5f7;
            }
            QListWidget::item {
                border-bottom: 1px solid #e5e5ea;
            }
            QListWidget::item:last {
                border-bottom: none;
            }
        """)
        
        # Populate module list with new switch style
        module_states = self.module_manager.get_module_state()
        all_enabled = all(module_states.values())
        self.master_switch.state = all_enabled
        self.master_switch.update()
        
        for module_file, module_name in self.module_manager.modules.items():
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, module_file)
            
            widget = ModuleItem(
                module_name, 
                initial_state=module_states.get(module_file, False),
                parent=self
            )
            widget.switch.toggled.connect(
                lambda state, m=module_file: self.on_module_toggle(m, state)
            )

            self.module_list.addItem(item)
            self.module_list.setItemWidget(item, widget)
            item.setSizeHint(widget.sizeHint())
        
        module_layout.addWidget(self.module_list)
        
        # Add panels to main layout
        main_layout.addWidget(settings_panel, stretch=1)
        main_layout.addWidget(module_panel, stretch=1)

    def toggle_all_modules(self, state):
        """Toggle all modules on/off"""
        for i in range(self.module_list.count()):
            item = self.module_list.item(i)
            widget = self.module_list.itemWidget(item)
            module_name = item.data(Qt.ItemDataRole.UserRole)

            widget.toggle_state(state)
            self.on_module_toggle(module_name, state)
        # 切换所有模块状态后更新ArrayList
        self.array_list_window.update_list()
    
    # ... (keep all other existing methods the same)

    def on_module_toggle(self, module_name, state):
        """Handle module toggle"""
        if state:  # On
            self.module_manager.start_module(module_name)
        else:  # Off
            self.module_manager.stop_module(module_name)

        # Save the new state
        module_states = self.module_manager.get_module_state()
        module_states[module_name] = state
        self.module_manager.save_module_state(module_states)

    def load_and_start_modules(self):
        """Load and start modules that were previously enabled"""
        module_states = self.module_manager.get_module_state()
        for module_name, enabled in module_states.items():
            if enabled:
                self.module_manager.start_module(module_name)

        # 确保ArrayList窗口已创建后再更新
        if hasattr(self, 'array_list_window'):
            self.array_list_window.update_list()
    
    def browse_minecraft_dir(self):
        """Open a dialog to select the .minecraft directory"""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        
        if dialog.exec():
            selected_dir = dialog.selectedFiles()[0]
            self.minecraft_dir_input.setText(selected_dir)
    
    def browse_java_path(self):
        """Open a dialog to select the Java executable"""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if dialog.exec():
            selected_file = dialog.selectedFiles()[0]
            self.java_path_input.setText(selected_file)
    
    def load_settings(self):
        """Load settings from the settings.json file if it exists"""
        data_dir = ensure_data_dir()
        try:
            with open(os.path.join(data_dir, "settings.json"), "r") as f:
                dic = json.load(f)
                self.java_path_input.setText(dic["java_path"])
                self.minecraft_dir_input.setText(dic["mc_dir"])
                
        except FileNotFoundError:
            # Default paths
            default_mc_dir = str(Path.home() / ".minecraft")
            self.minecraft_dir_input.setText(default_mc_dir)
            
            # Try to find default Java
            if platform.system() == "Windows":
                self.java_path_input.setText("java.exe")  # Will look in PATH
            else:
                self.java_path_input.setText("/usr/bin/java")
    
    def detect_java(self):
        """Try to detect Java installations automatically"""
        if not self.java_path_input.text().strip():
            # Try common Java paths
            java_paths = []
            
            if platform.system() == "Windows":
                java_paths.extend([
                    "C:\\Program Files\\Java\\jre1.8.0_*\\bin\\java.exe",
                    "C:\\Program Files (x86)\\Java\\jre1.8.0_*\\bin\\java.exe",
                    "java.exe"  # Try PATH
                ])
            else:  # Linux/macOS
                java_paths.extend([
                    "/usr/bin/java",
                    "/usr/lib/jvm/java-8-openjdk-*/bin/java",
                    "/usr/lib/jvm/jre1.8.0_*/bin/java",
                    "/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java"
                ])
            
            for path_pattern in java_paths:
                # Handle wildcards
                if "*" in path_pattern:
                    matches = list(Path(path_pattern).parent.glob(Path(path_pattern).name))
                    if matches:
                        path = str(matches[0])
                        self.java_path_input.setText(path)
                        break
                elif Path(path_pattern).exists():
                    self.java_path_input.setText(path_pattern)
                    break
    
    def save_settings(self):
        """Save settings to settings.json"""
        mc_dir = self.minecraft_dir_input.text().strip()
        java_path = self.java_path_input.text().strip()
        data_dir = ensure_data_dir()
        
        if not mc_dir or not java_path:
            QMessageBox.warning(self, "Error", "Please specify both Minecraft directory and Java path")
            return False
        
        # Create .minecraft directory if it doesn't exist
        try:
            Path(mc_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create Minecraft directory: {e}")
            return False

        try:
            with open(os.path.join(data_dir, "settings.json"), "w") as f:
                json.dump({"mc_dir": mc_dir, "java_path": java_path}, f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")
            return False
        
        # Update start script
        try:
            generate_launch_script(java_path, mc_dir)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not generate launch script: {e}")
            return False

    def launch_minecraft(self):
        """Launch Minecraft using the configured settings"""
        if not self.save_settings():
            return

        current_os = platform.system()

        try:
            if current_os == "Windows":
                subprocess.Popen([os.path.join(get_data_dir(), "start.bat")], shell=True)
            else:
                if current_os == "Darwin":  # macOS
                    subprocess.Popen(["open", "-a", "Terminal", os.path.join(get_data_dir(), "start.sh")])
                else:  # Linux
                    os.chmod("start.sh", 0o755)
                    subprocess.Popen([os.path.join(get_data_dir(), "start.sh")])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Minecraft: {e}")

    def install_client(self):
        """Install the client version to the Minecraft directory"""
        mc_dir = self.minecraft_dir_input.text().strip()
     
        if not mc_dir:
            QMessageBox.warning(self, "Error", "Please specify Minecraft directory first")
            return
    
        # Check if client directory exists
        client_dir = Path(__file__).parent / "pycheat"
        if not client_dir.exists():
            QMessageBox.critical(self, "Error", "Client files not found in pycheat directory")
            return
    
        # Determine the command to run based on OS
        current_os = platform.system()
        script_path = Path(__file__).parent / "install_client.py"
    
        try:
            if current_os == "Windows":
                subprocess.run([sys.executable, str(script_path), mc_dir], check=True)
            else:
                subprocess.run([sys.executable, str(script_path), mc_dir], check=True)
        
            QMessageBox.information(self, "Success", "Client installed successfully!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Installation failed: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event - stop all modules"""
        self.module_manager.stop_all_modules()
        event.accept()

    # 添加新的ArrayListWindow类
class ArrayListWindow(QWidget):
    def __init__(self, module_manager, parent=None):
        super().__init__(parent)
        self.module_manager = module_manager
        self.setWindowTitle("Active Modules")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 300)

        # 设置窗口位置在屏幕右上角
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(screen_geometry.width() - 220, 50)

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
                border: 1px solid #555;
            }
            QLabel {
                color: white;
                padding: 5px;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)

        # 标题
        self.title_label = QLabel("Active Modules")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # 分隔线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setStyleSheet("color: #555;")
        self.layout.addWidget(self.separator)

        # 模块列表容器
        self.modules_container = QWidget()
        self.modules_layout = QVBoxLayout()
        self.modules_layout.setSpacing(5)
        self.modules_container.setLayout(self.modules_layout)
        self.layout.addWidget(self.modules_container)

        # 初始更新
        self.update_list()

    def update_list(self):
        """更新显示的模块列表"""
         # 清除现有模块显示
        for i in reversed(range(self.modules_layout.count())):
            item = self.modules_layout.itemAt(i)
            if item is not None and item.widget() is not None:
                item.widget().setParent(None)

        # 获取当前启用的模块
        module_states = self.module_manager.get_module_state()
        active_modules = [name for name, state in module_states.items() if state]

        # 按模块名称排序
        active_modules.sort()

        # 添加每个启用的模块
        for module_file in active_modules:
            module_name = self.module_manager.get_module_display_name(module_file)
            label = QLabel(f"• {module_name}")
            label.setStyleSheet("font-size: 12px;")
            self.modules_layout.addWidget(label)

        # 如果没有启用的模块，显示提示
        if not active_modules:
            label = QLabel("No active modules")
            label.setStyleSheet("font-size: 12px; color: #888;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.modules_layout.addWidget(label)

        # 添加伸缩空间
        self.modules_layout.addStretch()

def main():
    app = QApplication(sys.argv)
    launcher = PyCheat()
    launcher.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

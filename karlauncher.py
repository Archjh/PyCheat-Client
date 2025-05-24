import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QStandardPaths

def get_resource_path(relative: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", relative)

def get_data_dir() -> str:
    return os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation), "karlauncher")

def ensure_data_dir() -> str:
    data_dir = get_data_dir()
    if not os.path.exists(data_dir):
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        pass
    return data_dir

def generate_launch_script(java_path: str, mc_dir: str):
    data_dir = ensure_data_dir()
    if platform.system() == "Windows":
        with open(os.path.join(data_dir, "start.bat"), "w") as f, open(get_resource_path("start.bat.template"), "r") as template_file:
            content = template_file.read().replace("#<java_path>#", java_path).replace("#<mc_dir>#", mc_dir)
            f.write(content)
        pass
    else:
        with open(os.path.join(data_dir, "start.sh"), "w") as f, open(get_resource_path("start.sh.template"), "r") as template_file:
            content = template_file.read().replace("#<java_path>#", java_path).replace("#<mc_dir>#", mc_dir).replace("#<home_dir>#", str(Path.home()))
            f.write(content)
        os.chmod(os.path.join(data_dir, "start.sh"), 0o755)

class Karlauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karlauncher - Minecraft 1.8.8")
        self.setFixedSize(500, 300)
        
        # Initialize UI
        self.init_ui()
        
        # Load existing settings
        self.load_settings()
        
        # Detect Java installations
        self.detect_java()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
    
        # Minecraft directory
        self.minecraft_dir_label = QLabel("Minecraft Directory:")
        self.minecraft_dir_input = QLineEdit()
        self.minecraft_dir_input.setPlaceholderText("Path to .minecraft folder")
        self.minecraft_dir_browse = QPushButton("Browse...")
        self.minecraft_dir_browse.clicked.connect(self.browse_minecraft_dir)
    
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.minecraft_dir_input)
        dir_layout.addWidget(self.minecraft_dir_browse)
    
        # Java executable
        self.java_path_label = QLabel("Java Path:")
        self.java_path_input = QLineEdit()
        self.java_path_input.setPlaceholderText("Path to java executable")
        self.java_path_browse = QPushButton("Browse...")
        self.java_path_browse.clicked.connect(self.browse_java_path)
    
        java_layout = QHBoxLayout()
        java_layout.addWidget(self.java_path_input)
        java_layout.addWidget(self.java_path_browse)
    
        # Create Install button first
        self.install_button = QPushButton("Install Client")
        self.install_button.clicked.connect(self.install_client)
    
        # Launch button
        self.launch_button = QPushButton("Launch Minecraft 1.8.8")
        self.launch_button.clicked.connect(self.launch_minecraft)
      
        # Add widgets to main layout in correct order
        layout.addWidget(self.minecraft_dir_label)
        layout.addWidget(self.minecraft_dir_input)
        layout.addWidget(self.minecraft_dir_browse)
        layout.addWidget(self.java_path_label)
        layout.addWidget(self.java_path_input)
        layout.addWidget(self.java_path_browse)
        layout.addStretch()
        layout.addWidget(self.install_button)  # Now this will work
        layout.addWidget(self.launch_button)

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
        """Load settings from the start.sh script if it exists"""
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
        """Save settings to the start.sh script"""
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
        
        # Update start.sh script
        try:
            generate_launch_script(java_path, mc_dir)
            # Make start.sh executable on Unix-like systems
            if platform.system() != "Windows":
                os.chmod("start.sh", 0o755)
            
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
                # On Windows, use the batch file
                subprocess.Popen([os.path.join(get_data_dir(), "start.bat")], shell=True)
            else:
                # On Linux/macOS, use the shell script
                if current_os == "Darwin":  # macOS
                    subprocess.Popen(["open", "-a", "Terminal", os.path.join(get_data_dir(), "start.sh")])
                else:  # Linux
                    os.chmod("start.sh", 0o755)
                    subprocess.Popen([os.path.join(get_data_dir(), "start.sh")])
            
            # Close the launcher
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Minecraft: {e}")

    # Add this new method to the Karlauncher class:     
    def install_client(self):
        """Install the client version to the Minecraft directory"""
        mc_dir = self.minecraft_dir_input.text().strip()
     
        if not mc_dir:
            QMessageBox.warning(self, "Error", "Please specify Minecraft directory first")
            return
    
        # Check if client directory exists
        client_dir = Path(__file__).parent / "ArchLibman"
        if not client_dir.exists():
            QMessageBox.critical(self, "Error", "Client files not found in ArchLibman directory")
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

def main():
    app = QApplication(sys.argv)
    launcher = Karlauncher()
    launcher.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import re  # Import regex for settings parsing
    main()

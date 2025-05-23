import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QProcess


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
        
        # Launch button
        self.launch_button = QPushButton("Launch Minecraft 1.8.8")
        self.launch_button.clicked.connect(self.launch_minecraft)
        
        # Add widgets to main layout
        layout.addWidget(self.minecraft_dir_label)
        layout.addWidget(self.minecraft_dir_input)
        layout.addWidget(self.minecraft_dir_browse)
        layout.addWidget(self.java_path_label)
        layout.addWidget(self.java_path_input)
        layout.addWidget(self.java_path_browse)
        layout.addStretch()
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
        try:
            with open("start.sh", "r") as f:
                content = f.read()
                
                # Extract Minecraft directory
                mc_dir_match = re.search(r'export INST_MC_DIR=(.+?)\n', content)
                if mc_dir_match:
                    self.minecraft_dir_input.setText(mc_dir_match.group(1).strip('"'))
                
                # Extract Java path
                java_match = re.search(r'export INST_JAVA=(.+?)\n', content)
                if java_match:
                    self.java_path_input.setText(java_match.group(1).strip('"'))
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
        
        if not mc_dir or not java_path:
            QMessageBox.warning(self, "Error", "Please specify both Minecraft directory and Java path")
            return False
        
        # Create .minecraft directory if it doesn't exist
        try:
            Path(mc_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create Minecraft directory: {e}")
            return False
        
        # Update start.sh script
        try:
            with open("start.sh", "w") as f:
                f.write(f"""#!/usr/bin/env bash
export INST_NAME=ArchLibman
export INST_ID=ArchLibman
export INST_DIR={mc_dir}/versions/ArchLibman
export INST_MC_DIR={mc_dir}
export INST_JAVA={java_path}
cd {mc_dir}
{java_path} -Xmx7637m -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 -Djava.rmi.server.useCodebaseOnly=true -Dcom.sun.jndi.rmi.object.trustURLCodebase=false -Dcom.sun.jndi.cosnaming.object.trustURLCodebase=false -Dlog4j2.formatMsgNoLookups=true -Dlog4j.configurationFile={mc_dir}/versions/ArchLibman/log4j2.xml -Dminecraft.client.jar={mc_dir}/versions/ArchLibman/ArchLibman.jar -Duser.home={Path.home()} -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32m -XX:-UseAdaptiveSizePolicy -XX:-OmitStackTraceInFastThrow -XX:-DontCompileHugeMethods -Dfml.ignoreInvalidMinecraftCertificates=true -Dfml.ignorePatchDiscrepancies=true -Djava.library.path={mc_dir}/versions/ArchLibman/natives-linux-x86_64 -Dminecraft.launcher.brand=HMCL -Dminecraft.launcher.version=3.6.12 -cp {mc_dir}/libraries/com/mojang/netty/1.8.8/netty-1.8.8.jar:{mc_dir}/libraries/oshi-project/oshi-core/1.1/oshi-core-1.1.jar:{mc_dir}/libraries/net/java/dev/jna/jna/3.4.0/jna-3.4.0.jar:{mc_dir}/libraries/net/java/dev/jna/platform/3.4.0/platform-3.4.0.jar:{mc_dir}/libraries/com/ibm/icu/icu4j-core-mojang/51.2/icu4j-core-mojang-51.2.jar:{mc_dir}/libraries/net/sf/jopt-simple/jopt-simple/4.6/jopt-simple-4.6.jar:{mc_dir}/libraries/com/paulscode/codecjorbis/20101023/codecjorbis-20101023.jar:{mc_dir}/libraries/com/paulscode/codecwav/20101023/codecwav-20101023.jar:{mc_dir}/libraries/com/paulscode/libraryjavasound/20101123/libraryjavasound-20101123.jar:{mc_dir}/libraries/com/paulscode/librarylwjglopenal/20100824/librarylwjglopenal-20100824.jar:{mc_dir}/libraries/com/paulscode/soundsystem/20120107/soundsystem-20120107.jar:{mc_dir}/libraries/io/netty/netty-all/4.0.23.Final/netty-all-4.0.23.Final.jar:{mc_dir}/libraries/com/google/guava/guava/17.0/guava-17.0.jar:{mc_dir}/libraries/org/apache/commons/commons-lang3/3.3.2/commons-lang3-3.3.2.jar:{mc_dir}/libraries/commons-io/commons-io/2.4/commons-io-2.4.jar:{mc_dir}/libraries/commons-codec/commons-codec/1.9/commons-codec-1.9.jar:{mc_dir}/libraries/net/java/jinput/jinput/2.0.5/jinput-2.0.5.jar:{mc_dir}/libraries/net/java/jutils/jutils/1.0.0/jutils-1.0.0.jar:{mc_dir}/libraries/com/google/code/gson/gson/2.2.4/gson-2.2.4.jar:{mc_dir}/libraries/com/mojang/authlib/1.5.21/authlib-1.5.21.jar:{mc_dir}/libraries/com/mojang/realms/1.7.39/realms-1.7.39.jar:{mc_dir}/libraries/org/apache/commons/commons-compress/1.8.1/commons-compress-1.8.1.jar:{mc_dir}/libraries/org/apache/httpcomponents/httpclient/4.3.3/httpclient-4.3.3.jar:{mc_dir}/libraries/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar:{mc_dir}/libraries/org/apache/httpcomponents/httpcore/4.3.2/httpcore-4.3.2.jar:{mc_dir}/libraries/org/apache/logging/log4j/log4j-api/2.0-beta9/log4j-api-2.0-beta9.jar:{mc_dir}/libraries/org/apache/logging/log4j/log4j-core/2.0-beta9/log4j-core-2.0-beta9.jar:{mc_dir}/libraries/org/lwjgl/lwjgl/lwjgl/2.9.4-nightly-20150209/lwjgl-2.9.4-nightly-20150209.jar:{mc_dir}/libraries/org/lwjgl/lwjgl/lwjgl_util/2.9.4-nightly-20150209/lwjgl_util-2.9.4-nightly-20150209.jar:{mc_dir}/libraries/tv/twitch/twitch/6.5/twitch-6.5.jar:{mc_dir}/versions/ArchLibman/ArchLibman.jar net.minecraft.client.main.Main --username GNUiannjh --version ArchLibman --gameDir {mc_dir} --assetsDir {mc_dir}/assets --assetIndex 1.8 --uuid 8356f0a7d17e47dcbf2f4a198aec6bca --accessToken eyJraWQiOiIwNDkxODEiLCJhbGciOiJSUzI1NiJ9.eyJ4dWlkIjoiMjUzNTQ0NTE4NTEwNTEzNiIsImFnZyI6IkFkdWx0Iiwic3ViIjoiM2U3N2E2ZDQtYTU5Ny00MmUxLWIwYTAtMzM5MjNlM2VjYTQzIiwiYXV0aCI6IlhCT1giLCJucyI6ImRlZmF1bHQiLCJyb2xlcyI6W10sImlzcyI6ImF1dGhlbnRpY2F0aW9uIiwiZmxhZ3MiOlsib3JkZXJzXzIwMjIiLCJtdWx0aXBsYXllciIsInR3b2ZhY3RvcmF1dGgiLCJtc2FtaWdyYXRpb25fc3RhZ2U0Il0sInByb2ZpbGVzIjp7Im1jIjoiODM1NmYwYTctZDE3ZS00N2RjLWJmMmYtNGExOThhZWM2YmNhIn0sInBsYXRmb3JtIjoiVU5LTk9XTiIsInl1aWQiOiIzNzI4NzFjOGFiNzhkZGE2MDllY2M0ODVjN2ZjN2Y2YSIsIm5iZiI6MTc0NzkyNDM3MSwiZXhwIjoxNzQ4MDEwNzcxLCJpYXQiOjE3NDc5MjQzNzF9.gOnayPk4U_gxAnkZhrFEpEpG6rMOre8v66TgVqhhBIM-7gXy-iqqIHtSLQFJtiecP9ubq7H0_jV12iGda_aDCDAhs67HDvYNcuwwaTrUJPWdq9zWezYSrFjfj9xmNBSS5U790GEGNi5jJzmZtgMvjjQo13fsBf-IUPzhSJ_V4BV0AQNssJNtH2uBot0PXYxhPuh3CF1YAxv-qS5A8N8hb8KFusufwPxdb2UPyiv-hEvngvggLM9w1fQhXgkPlrWXDNSiNYpB0siMpezT2j_83o7xM4dDoTuXTKZcdlNKCJZlUFrzNJdPeFTA-TXqWu1D9A0VKPesEuHHcd5VDm3x4Q --userProperties "{{}}" --userType msa --width 854 --height 480
""")
            
            # Make start.sh executable on Unix-like systems
            if platform.system() != "Windows":
                os.chmod("start.sh", 0o755)
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")
            return False

    
    def launch_minecraft(self):
        """Launch Minecraft using the configured settings"""
        if not self.save_settings():
            return
        
        current_os = platform.system()
        
        try:
            if current_os == "Windows":
                # On Windows, use the batch file
                subprocess.Popen(["start.bat"], shell=True)
            else:
                # On Linux/macOS, use the shell script
                if current_os == "Darwin":  # macOS
                    subprocess.Popen(["open", "-a", "Terminal", "start.sh"])
                else:  # Linux
                    os.chmod("start.sh", 0o755)
                    subprocess.Popen(["./start.sh"])
            
            # Close the launcher
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Minecraft: {e}")

def main():
    app = QApplication(sys.argv)
    launcher = Karlauncher()
    launcher.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import re  # Import regex for settings parsing
    main()

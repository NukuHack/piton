import sys
import psutil
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit,
                             QMessageBox, QGroupBox)
from PyQt5.QtCore import QTimer, Qt

class MemoryMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("App Memory Monitor")
        self.setGeometry(100, 100, 600, 500)
        
        # Configuration
        self.STORAGE_FILE = "monitored_apps.json"
        self.currently_monitoring = None
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_memory_usage)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        
        # Create left panel (app list and controls)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # App input section
        self.app_input_group = QGroupBox("Monitor Application")
        self.app_input_layout = QVBoxLayout()
        
        self.app_name_label = QLabel("Enter application name:")
        self.app_name_input = QLineEdit()
        self.app_name_input.setPlaceholderText("e.g., chrome.exe")
        
        self.monitor_button = QPushButton("Start Monitoring")
        self.monitor_button.clicked.connect(self.start_monitoring)
        
        self.add_to_monitored_button = QPushButton("Add to Monitored Apps")
        self.add_to_monitored_button.clicked.connect(self.add_to_monitored)
        self.add_to_monitored_button.setEnabled(False)
        
        self.app_input_layout.addWidget(self.app_name_label)
        self.app_input_layout.addWidget(self.app_name_input)
        self.app_input_layout.addWidget(self.monitor_button)
        self.app_input_layout.addWidget(self.add_to_monitored_button)
        self.app_input_group.setLayout(self.app_input_layout)
        
        # Monitored apps list
        self.monitored_apps_group = QGroupBox("Monitored Apps")
        self.monitored_apps_layout = QVBoxLayout()
        
        self.monitored_apps_list = QListWidget()
        self.monitored_apps_list.itemDoubleClicked.connect(self.monitor_selected_app)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_monitored_app)
        
        self.monitored_apps_layout.addWidget(self.monitored_apps_list)
        self.monitored_apps_layout.addWidget(self.remove_button)
        self.monitored_apps_group.setLayout(self.monitored_apps_layout)
        
        # Add groups to left panel
        self.left_layout.addWidget(self.app_input_group)
        self.left_layout.addWidget(self.monitored_apps_group)
        
        # Create right panel (memory display)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        self.memory_display_group = QGroupBox("Memory Usage")
        self.memory_display_layout = QVBoxLayout()
        
        self.app_name_display = QLabel("Not currently monitoring any app")
        self.app_name_display.setAlignment(Qt.AlignCenter)
        self.app_name_display.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.memory_usage_display = QLabel()
        self.memory_usage_display.setAlignment(Qt.AlignCenter)
        self.memory_usage_display.setStyleSheet("font-size: 24px; color: #2E86C1;")
        
        self.detailed_memory_display = QTextEdit()
        self.detailed_memory_display.setReadOnly(True)
        self.detailed_memory_display.setStyleSheet("font-family: monospace;")
        
        self.process_count_display = QLabel()
        self.process_count_display.setAlignment(Qt.AlignCenter)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        
        self.memory_display_layout.addWidget(self.app_name_display)
        self.memory_display_layout.addWidget(self.memory_usage_display)
        self.memory_display_layout.addWidget(self.detailed_memory_display)
        self.memory_display_layout.addWidget(self.process_count_display)
        self.memory_display_layout.addWidget(self.stop_button)
        self.memory_display_group.setLayout(self.memory_display_layout)
        
        self.right_layout.addWidget(self.memory_display_group)
        
        # Add panels to main layout
        self.main_layout.addWidget(self.left_panel, 1)
        self.main_layout.addWidget(self.right_panel, 2)
        
        # Load monitored apps
        self.load_monitored_apps()
        self.update_monitored_apps_list()
        
    def convert_bytes(self, bytes_num):
        """Convert bytes to human-readable format (GB, MB, KB, B)"""
        gb = bytes_num // (1024 ** 3)
        remaining = bytes_num % (1024 ** 3)
        mb = remaining // (1024 ** 2)
        remaining %= (1024 ** 2)
        kb = remaining // 1024
        b = remaining % 1024
        return gb, mb, kb, b
    
    def format_memory(self, gb, mb, kb, b):
        """Format memory components into a readable string"""
        parts = []
        if gb > 0:
            parts.append(f"{gb} GB")
        if mb > 0:
            parts.append(f"{mb} MB")
        if kb > 0:
            parts.append(f"{kb} KB")
        if b > 0 or not parts:
            parts.append(f"{b} B")
        return " ".join(parts)
    
    def find_process_by_name(self, name):
        """Find all processes matching the given name"""
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                if name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return matching_processes
    
    def get_total_memory(self, processes):
        """Calculate total memory usage for a list of processes"""
        total = 0
        for proc in processes:
            try:
                total += proc.info['memory_info'].rss  # Resident Set Size
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return total
    
    def load_monitored_apps(self):
        """Load the list of monitored apps from file"""
        self.monitored_apps = []
        if not Path(self.STORAGE_FILE).exists():
            return
        
        with open(self.STORAGE_FILE, 'r') as f:
            try:
                self.monitored_apps = json.load(f)
            except json.JSONDecodeError:
                pass
    
    def save_monitored_apps(self):
        """Save the list of monitored apps to file"""
        with open(self.STORAGE_FILE, 'w') as f:
            json.dump(self.monitored_apps, f)
    
    def update_monitored_apps_list(self):
        """Update the list widget with monitored apps"""
        self.monitored_apps_list.clear()
        for app in self.monitored_apps:
            self.monitored_apps_list.addItem(app)
    
    def add_to_monitored(self):
        """Add the current app to monitored list"""
        app_name = self.app_name_input.text().strip()
        if not app_name:
            QMessageBox.warning(self, "Error", "Please enter an application name")
            return
        
        if app_name not in self.monitored_apps:
            self.monitored_apps.append(app_name)
            self.save_monitored_apps()
            self.update_monitored_apps_list()
            QMessageBox.information(self, "Success", f"'{app_name}' has been added to monitored apps.")
        else:
            QMessageBox.information(self, "Info", f"'{app_name}' is already being monitored.")
    
    def remove_monitored_app(self):
        """Remove the selected app from monitored list"""
        selected_items = self.monitored_apps_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select an app to remove")
            return
        
        app_name = selected_items[0].text()
        self.monitored_apps.remove(app_name)
        self.save_monitored_apps()
        self.update_monitored_apps_list()
        
        if self.currently_monitoring == app_name:
            self.stop_monitoring()
    
    def monitor_selected_app(self, item):
        """Start monitoring the selected app from the list"""
        app_name = item.text()
        self.app_name_input.setText(app_name)
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring the specified app"""
        app_name = self.app_name_input.text().strip()
        if not app_name:
            QMessageBox.warning(self, "Error", "Please enter an application name")
            return
        
        processes = self.find_process_by_name(app_name)
        if not processes:
            reply = QMessageBox.question(
                self, "App Not Found",
                f"No running processes found for '{app_name}'. Do you want to keep trying?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Start a timer to check periodically
                self.currently_monitoring = app_name
                self.app_name_display.setText(f"Waiting for '{app_name}'...")
                self.monitoring_timer.start(2000)  # Check every 2 seconds
                self.stop_button.setEnabled(True)
                self.monitor_button.setEnabled(False)
                self.add_to_monitored_button.setEnabled(True)
            return
        
        # If we found the app, start monitoring
        self.currently_monitoring = app_name
        self.app_name_display.setText(f"Monitoring: {app_name}")
        self.monitoring_timer.start(1000)  # Update every second
        self.stop_button.setEnabled(True)
        self.monitor_button.setEnabled(False)
        self.add_to_monitored_button.setEnabled(True)
        
        # Update display immediately
        self.update_memory_usage()
    
    def stop_monitoring(self):
        """Stop the current monitoring session"""
        self.monitoring_timer.stop()
        self.currently_monitoring = None
        self.app_name_display.setText("Not currently monitoring any app")
        self.memory_usage_display.clear()
        self.detailed_memory_display.clear()
        self.process_count_display.clear()
        self.stop_button.setEnabled(False)
        self.monitor_button.setEnabled(True)
    
    def update_memory_usage(self):
        """Update the memory usage display"""
        if not self.currently_monitoring:
            return
        
        processes = self.find_process_by_name(self.currently_monitoring)
        
        if not processes:
            # If we were monitoring but the app closed
            if self.monitoring_timer.isActive():
                self.app_name_display.setText(f"Waiting for '{self.currently_monitoring}'...")
                self.memory_usage_display.setText("App not currently running")
                self.detailed_memory_display.clear()
                self.process_count_display.clear()
            return
        
        total_memory = self.get_total_memory(processes)
        gb, mb, kb, b = self.convert_bytes(total_memory)
        
        # Update displays
        self.app_name_display.setText(f"Monitoring: {self.currently_monitoring}")
        self.memory_usage_display.setText(self.format_memory(gb, mb, kb, b))
        
        detailed_text = f"""Memory Breakdown:
{gb} GB
{mb} MB
{kb} KB
{b} B

Total Bytes: {total_memory:,}"""
        self.detailed_memory_display.setText(detailed_text)
        
        self.process_count_display.setText(f"Processes: {len(processes)}")
        
        # Enable add button if not already monitored
        if self.currently_monitoring not in self.monitored_apps:
            self.add_to_monitored_button.setEnabled(True)
        else:
            self.add_to_monitored_button.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryMonitorApp()
    window.show()
    sys.exit(app.exec_())
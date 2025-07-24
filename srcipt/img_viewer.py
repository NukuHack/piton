import sys
import os  # Added missing import
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                             QVBoxLayout, QWidget, QPushButton, QLabel,
                             QHBoxLayout)
from PyQt5.QtGui import QPixmap, QKeySequence, QColor, QPalette, QImage
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QGuiApplication
from skimage.measure import label
import cv2

class ImageProcessor(QObject):
    finished = pyqtSignal(QImage)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def process(self):
        """Process only large bright areas (>5% of image)"""
        try:
            if not os.path.exists(self.file_path):
                self.error_occurred.emit("Error: File does not exist")
                return
                
            image = QImage(self.file_path)
            if image.isNull():
                self.error_occurred.emit("Error: Unable to load image")
                return
            
            if image.format() != QImage.Format_RGBA8888:
                image = image.convertToFormat(QImage.Format_RGBA8888)
            
            width, height = image.width(), image.height()
            buffer = image.constBits().asstring(image.byteCount())
            arr = np.frombuffer(buffer, dtype=np.uint8).copy().reshape(height, width, 4)
            
            # Bright pixel mask (threshold 230)
            bright_mask = ((arr[:, :, :3] > 230).all(axis=2)).astype(np.uint8)
            
            # Find contours of bright areas
            contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Minimum area threshold (5% of image)
            min_area = width * height * 0.05
            
            # Create mask for only large bright areas
            large_mask = np.zeros_like(bright_mask)
            for cnt in contours:
                if cv2.contourArea(cnt) >= min_area:
                    cv2.drawContours(large_mask, [cnt], -1, 1, -1)
            
            # Apply color change only to large bright areas
            arr[large_mask.astype(bool), 0:3] = [50, 0, 80]
            
            processed_image = QImage(arr.data, width, height, image.bytesPerLine(), QImage.Format_RGBA8888)
            processed_image.ndarray = arr
            self.finished.emit(processed_image.copy())
            
        except Exception as e:
            self.error_occurred.emit(f"Processing error: {str(e)}")

class ImageViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initial path settings
        self.base_path = r"B:\my stuff\pics\image"
        self.current_number = 1
        self.file_extension = ".jpg"
        
        # Set up the main window
        self.setWindowTitle("Image Viewer")
        
        # Get screen dimensions and set window size
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height())
        
        # Apply dark theme using both palette and stylesheet
        self.set_dark_theme()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create horizontal layout for path and buttons
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        
        # Previous button with blue hover effect
        self.prev_button = QPushButton("◀")
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #5a9bd5;
                font-size: 16px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: #7ab7f5;
                border: 1px solid #555;
            }
        """)
        self.prev_button.clicked.connect(self.prev_image)
        path_layout.addWidget(self.prev_button)
        
        # Path input field
        self.path_input = QLineEdit()
        self.path_input.setFixedHeight(40)
        self.path_input.editingFinished.connect(self.update_path_from_input)
        path_layout.addWidget(self.path_input, stretch=1)
        
        # Next button with blue hover effect
        self.next_button = QPushButton("▶")
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #5a9bd5;
                font-size: 16px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                color: #7ab7f5;
                border: 1px solid #555;
            }
        """)
        self.next_button.clicked.connect(self.next_image)
        path_layout.addWidget(self.next_button)
        
        main_layout.addLayout(path_layout)
        
        # Create the image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            border: 1px solid #444;
            background: #252525;
        """)
        main_layout.addWidget(self.image_label)
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Initialize with default path
        self.update_path_display()
        self.load_image()
    
    def set_dark_theme(self):
        """Set a comprehensive dark theme that actually works"""        
        # Create dark palette
        dark_palette = QPalette()
        
        # Base colors
        dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.black)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Disabled colors
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        
        # Apply the palette
        self.setPalette(dark_palette)
        
        # Additional stylesheet for elements not fully covered by palette
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                selection-background-color: #3a6ea5;
            }
            QLabel {
                color: white;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
            }
            QMenu::item:selected {
                background-color: #3a6ea5;
            }
        """)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts for navigation"""
        # Navigation
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.prev_image)
        QShortcut(QKeySequence(Qt.Key_A), self).activated.connect(self.prev_image)
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.next_image)
        QShortcut(QKeySequence(Qt.Key_D), self).activated.connect(self.next_image)
    
    def update_path_display(self):
        """Update the path display with current number"""
        # Try both underscore and hyphen separated formats
        path1 = f"{self.base_path}_{self.current_number}{self.file_extension}"
        path2 = f"{self.base_path}-{self.current_number}{self.file_extension}"
        path3 = f"{self.base_path}.{self.current_number}{self.file_extension}"
        path4 = f"{self.base_path}({self.current_number}){self.file_extension}"
        
        # Use the first format that exists, or default to underscore
        if os.path.exists(path2):
            self.path_input.setText(path2)
        elif os.path.exists(path3):
            self.path_input.setText(path3)
        elif os.path.exists(path4):
            self.path_input.setText(path4)
        else:
            self.path_input.setText(path1)  # default to underscore format

    def update_path_from_input(self):
        """Update the path components when user edits the field"""
        full_path = self.path_input.text()
        
        # Try different patterns to extract base path and number
        patterns = [
            (r'(.+)[-_](\d+)\.(\w+)$', 1, 2),  # name-number.ext or name_number.ext
            (r'(.+)\.(\d+)\.(\w+)$', 1, 2),    # name.number.ext
            (r'(.+)\((\d+)\)\.(\w+)$', 1, 2)   # name(number).ext
        ]
        
        for pattern, base_group, num_group in patterns:
            import re
            match = re.match(pattern, full_path)
            if match:
                self.base_path = match.group(base_group)
                self.current_number = int(match.group(num_group))
                self.file_extension = f".{match.group(3)}"
                self.load_image()
                return
        
        # If no pattern matched, try to find a number elsewhere in the path
        match = re.search(r'(\d+)\.\w+$', full_path)
        if match:
            num = match.group(1)
            self.base_path = full_path[:match.start(1)-1]
            self.current_number = int(num)
            self.load_image()
        else:
            # If no number found, just use the path as is
            self.base_path = full_path.rsplit('.', 1)[0]
            self.current_number = 0
            self.load_image()

    def load_image(self):
        """Load image using background thread for processing"""
        try:
            # Validate input path first
            path = self.path_input.text().strip()
            if not path:
                self.image_label.setText("Please enter an image path")
                return
                
            # Show loading indicator
            self.image_label.setText("Loading...")
            QApplication.processEvents()  # Force UI update
            
            # Clean up any existing thread
            if hasattr(self, 'worker_thread'):
                self.worker_thread.quit()
                self.worker_thread.wait()
                if hasattr(self, 'processor'):
                    self.processor.deleteLater()
                self.worker_thread.deleteLater()
                del self.worker_thread
                if hasattr(self, 'processor'):
                    del self.processor
            
            # Create and start worker thread
            self.worker_thread = QThread()
            self.processor = ImageProcessor(path)
            self.processor.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker_thread.started.connect(self.processor.process)
            self.processor.finished.connect(self.on_image_processed)
            self.processor.finished.connect(self.worker_thread.quit)
            self.processor.finished.connect(self.processor.deleteLater)
            
            # Use a dedicated method for thread cleanup
            self.worker_thread.finished.connect(self.cleanup_thread)
            
            self.processor.error_occurred.connect(self.handle_processing_error)
            
            # Start the thread
            self.worker_thread.start()
        except Exception as e:
            self.image_label.setText(f"Error loading image: {str(e)}")

    def cleanup_thread(self):
        """Clean up the thread resources"""
        if hasattr(self, 'worker_thread'):
            self.worker_thread.deleteLater()
            del self.worker_thread

    def handle_processing_error(self, error_msg):
        """Handle processing errors from the worker thread"""
        self.image_label.setText(error_msg)
        if hasattr(self, 'worker_thread'):
            self.worker_thread.quit()
            self.worker_thread.wait(1000)  # Wait up to 1 second
            self.worker_thread.deleteLater()
            del self.worker_thread

    def on_image_processed(self, image):
        """Handle the processed image from background thread"""
        try:
            if image and not image.isNull():
                pixmap = QPixmap.fromImage(image)
                if not pixmap.isNull():
                    # Calculate available space while maintaining aspect ratio
                    available_width = self.image_label.width() - 20  # Account for borders
                    available_height = self.image_label.height() - 20
                    
                    scaled_pixmap = pixmap.scaled(
                        available_width, available_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    self.image_label.setText("Error: Invalid pixmap conversion")
            else:
                self.image_label.setText("Error: Processed image is invalid")
        except Exception as e:
            self.image_label.setText(f"Error displaying image: {str(e)}")
    
    def prev_image(self):
        """Load the previous image in sequence"""
        self.current_number -= 1
        if self.current_number < 0:
            self.current_number = 0
        self.update_path_display()
        self.load_image()
    
    def next_image(self):
        """Load the next image in sequence"""
        self.current_number += 1
        self.update_path_display()
        self.load_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Force Fusion style for better dark theme support
    app.setStyle("Fusion")
    
    window = ImageViewerApp()
    window.show()
    sys.exit(app.exec_())
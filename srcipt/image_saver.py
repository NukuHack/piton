import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, 
                             QVBoxLayout, QWidget, QShortcut, QLabel,
                             QHBoxLayout, QSpinBox)
from PyQt5.QtGui import QPixmap, QImage, QKeySequence, QClipboard
from PyQt5.QtCore import Qt

class ImageDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initial save path
        self.base_path = r"B:\my stuff\pics\image"
        self.save_counter = 0
        
        # Set up the main window with fixed size
        self.setWindowTitle("Image Display & Save")
        self.setFixedSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Create horizontal layout for path and counter
        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)
        
        # Create the path input field (editable)
        self.path_input = QLineEdit(self.base_path + ".jpg")
        self.path_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px; 
                border: 1px solid #ccc;
                background: #f0f0f0;
                padding: 2px;
            }
        """)
        self.path_input.setFixedHeight(40)
        self.path_input.editingFinished.connect(self.update_base_path)
        self.path_input.setFocusPolicy(Qt.StrongFocus)  # Allow normal focus behavior
        path_layout.addWidget(self.path_input, stretch=1)
        
        # Create counter label
        counter_label = QLabel("Save #:")
        counter_label.setStyleSheet("font-size: 14px;")
        path_layout.addWidget(counter_label)
        
        # Create counter input (spin box)
        self.counter_input = QSpinBox()
        self.counter_input.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                border: 1px solid #ccc;
                background: #f0f0f0;
                padding: 2px;
            }
        """)
        self.counter_input.setFixedWidth(60)
        self.counter_input.setFixedHeight(40)
        self.counter_input.setMinimum(0)
        self.counter_input.setMaximum(9999)
        self.counter_input.setValue(0)
        self.counter_input.setFocusPolicy(Qt.StrongFocus)  # Allow normal focus behavior
        self.counter_input.valueChanged.connect(self.update_counter)
        path_layout.addWidget(self.counter_input)
        
        main_layout.addLayout(path_layout)
        
        # Create the image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            border: 1px solid #ccc;
            background: #f8f8f8;
        """)
        self.image_label.setFocusPolicy(Qt.StrongFocus)  # Allow focus for pasting
        main_layout.addWidget(self.image_label)
        
        # Set up clipboard
        self.clipboard = QApplication.clipboard()
        
        # Shortcuts - now attached to the window, not individual widgets
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.handle_paste)
        
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_current_image)
        
        # Current image storage
        self.current_image = None
        
        # Set initial focus to image label
        self.image_label.setFocus()
        
    def update_base_path(self):
        """Update the base path when user edits the field"""
        full_path = self.path_input.text()
        
        # Split into path parts
        parts = full_path.rsplit('_', 1)
        
        # Check if the last part before extension is a number
        if len(parts) > 1:
            last_part = parts[1].split('.')[0]  # Remove extension if present
            if last_part.isdigit():
                # Update both the base path and the counter
                self.base_path = parts[0]
                self.save_counter = int(last_part)
                self.counter_input.setValue(self.save_counter)
                return
        
        # If no counter found, just update the base path without the extension
        self.base_path = full_path.rsplit(".", 1)[0]
        self.update_path_display()
    
    def update_counter(self, value):
        """Update the save counter when spin box changes"""
        self.save_counter = value
        self.update_path_display()
    
    def handle_paste(self):
        """Handle clipboard paste (Ctrl+V)"""
        if self.counter_input.hasFocus():
            # Let the spin box handle the paste operation normally
            return
        elif not self.path_input.hasFocus():
            self.paste_from_clipboard()
    
    def paste_from_clipboard(self):
        """Handle image paste from clipboard"""
        clipboard_image = self.clipboard.image()
        if not clipboard_image.isNull():
            self.current_image = clipboard_image
            self.display_image()
            self.save_counter = 0
            self.update_path_display()
    
    def save_current_image(self):
        """Handle save (Ctrl+S)"""
        # Only save if focus isn't on the path or counter inputs
        if not (self.path_input.hasFocus() or self.counter_input.hasFocus()):
            if self.current_image and not self.current_image.isNull():
                # Use the counter from the spin box
                counter = self.counter_input.value()
                
                # Determine filename
                if counter == 0:
                    save_path = f"{self.base_path}.jpg"
                else:
                    save_path = f"{self.base_path}_{counter}.jpg"
                
                # Save image
                if self.current_image.save(save_path, "JPG", quality=90):
                    print(f"Image saved to {save_path}")
                    # Auto-increment the counter for next save
                    self.counter_input.setValue(counter + 1)
                else:
                    print("Failed to save image")
    
    def display_image(self):
        """Display the current image"""
        if self.current_image and not self.current_image.isNull():
            scaled_image = self.current_image.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(QPixmap.fromImage(scaled_image))
    
    def update_path_display(self):
        """Update the path display with current save path"""
        counter = self.counter_input.value()
        if counter == 0:
            self.path_input.setText(f"{self.base_path}.jpg")
        else:
            self.path_input.setText(f"{self.base_path}_{counter}.jpg")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDisplayApp()
    window.show()
    sys.exit(app.exec_())
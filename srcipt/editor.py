import sys
import os
import struct
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                              QVBoxLayout, QWidget, QFileDialog, QSpinBox, 
                              QComboBox, QMessageBox, QSlider, QHBoxLayout)
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtCore import Qt

class KTX2Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KTX Texture Editor")
        self.setGeometry(100, 100, 800, 600)
        
        # Current texture data
        self.image_data = None
        self.image_width = 0
        self.image_height = 0
        self.current_file = None
        
        # UI Elements
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(512, 512)
        self.image_label.setStyleSheet("background-color: #333; border: 1px solid #555;")
        layout.addWidget(self.image_label)
        
        # Controls
        control_layout = QHBoxLayout()
        
        # Create/Edit buttons
        self.new_btn = QPushButton("New Texture")
        self.new_btn.clicked.connect(self.create_new_texture)
        control_layout.addWidget(self.new_btn)
        
        self.open_btn = QPushButton("Open KTX2")
        self.open_btn.clicked.connect(self.open_ktx2)
        control_layout.addWidget(self.open_btn)
        
        self.save_btn = QPushButton("Save KTX2")
        self.save_btn.clicked.connect(self.save_ktx2)
        self.save_btn.setEnabled(False)
        control_layout.addWidget(self.save_btn)
        
        layout.addLayout(control_layout)
        
        # Texture properties
        prop_layout = QHBoxLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 512)
        self.width_spin.setValue(256)
        self.width_spin.setEnabled(False)
        prop_layout.addWidget(QLabel("Width:"))
        prop_layout.addWidget(self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 512)
        self.height_spin.setValue(256)
        self.height_spin.setEnabled(False)
        prop_layout.addWidget(QLabel("Height:"))
        prop_layout.addWidget(self.height_spin)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["RGB", "RGBA", "sRGB", "sRGBA"])
        prop_layout.addWidget(QLabel("Format:"))
        prop_layout.addWidget(self.format_combo)
        
        layout.addLayout(prop_layout)
        
        # Color picker for editing
        color_layout = QHBoxLayout()
        
        self.color_btn = QPushButton("Set Color")
        self.color_btn.clicked.connect(self.set_solid_color)
        color_layout.addWidget(self.color_btn)
        
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setRange(0, 255)
        self.red_slider.setValue(255)
        color_layout.addWidget(QLabel("R:"))
        color_layout.addWidget(self.red_slider)
        
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setRange(0, 255)
        self.green_slider.setValue(255)
        color_layout.addWidget(QLabel("G:"))
        color_layout.addWidget(self.green_slider)
        
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setRange(0, 255)
        self.blue_slider.setValue(255)
        color_layout.addWidget(QLabel("B:"))
        color_layout.addWidget(self.blue_slider)
        
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(255)
        color_layout.addWidget(QLabel("A:"))
        color_layout.addWidget(self.alpha_slider)
        
        layout.addLayout(color_layout)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
    def create_new_texture(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        
        # Create a blank RGBA image
        self.image_data = np.zeros((height, width, 4), dtype=np.uint8)
        self.image_data.fill(255)  # White
        self.image_width = width
        self.image_height = height
        self.current_file = None
        
        self.update_image_display()
        self.save_btn.setEnabled(True)
        
    
    def set_solid_color(self):
        if self.image_data is None:
            return
            
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        a = self.alpha_slider.value()
        
        # Fill image with the selected color
        self.image_data[..., 0] = r
        self.image_data[..., 1] = g
        self.image_data[..., 2] = b
        self.image_data[..., 3] = a
        
        self.update_image_display()
    


    def open_ktx(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                # Check file identifier
                identifier = f.read(12)
                if identifier != b'\xABKTX 11\xBB\r\n\x1A\n':
                    raise ValueError("Not a valid KTX file")
                
                # Read header
                endianness = struct.unpack('<I', f.read(4))[0]
                gl_type = struct.unpack('<I', f.read(4))[0]
                gl_format = struct.unpack('<I', f.read(4))[0]
                gl_internal_format = struct.unpack('<I', f.read(4))[0]
                self.image_width = struct.unpack('<I', f.read(4))[0]
                self.image_height = struct.unpack('<I', f.read(4))[0]
                
                # Skip remaining header fields
                f.seek(64)  # KTX header is fixed at 64 bytes
                
                # Read image data
                image_size = struct.unpack('<I', f.read(4))[0]
                data = f.read(image_size)
                
                # Convert to numpy array (assuming 8-bit per channel)
                if gl_format == 0x1907:  # GL_RGB
                    self.image_data = np.frombuffer(data, dtype=np.uint8).reshape(
                        (self.image_height, self.image_width, 3))
                elif gl_format == 0x1908:  # GL_RGBA
                    self.image_data = np.frombuffer(data, dtype=np.uint8).reshape(
                        (self.image_height, self.image_width, 4))
                else:
                    raise ValueError("Unsupported format")
                
                self.current_file = file_path
                return True
                
        except Exception as e:
            print(f"Error reading KTX file: {str(e)}")
            return False

    def save_ktx(self, file_path):
        try:
            with open(file_path, 'wb') as f:
                # Write header
                f.write(b'\xABKTX 11\xBB\r\n\x1A\n')  # Identifier
                f.write(struct.pack('<I', 0x04030201))  # Endianness
                
                # Determine format from UI
                format_str = self.format_combo.currentText()
                if format_str == "RGB":
                    gl_format = 0x1907  # GL_RGB
                    gl_internal_format = 0x8051  # GL_RGB8
                    channels = 3
                elif format_str == "RGBA":
                    gl_format = 0x1908  # GL_RGBA
                    gl_internal_format = 0x8058  # GL_RGBA8
                    channels = 4
                
                f.write(struct.pack('<I', 0))  # glType (0 for compressed)
                f.write(struct.pack('<I', gl_format))
                f.write(struct.pack('<I', gl_internal_format))
                f.write(struct.pack('<I', self.image_width))
                f.write(struct.pack('<I', self.image_height))
                f.write(struct.pack('<I', 0))  # Depth
                f.write(struct.pack('<I', 0))  # Array elements
                f.write(struct.pack('<I', 0))  # Faces
                f.write(struct.pack('<I', 1))  # Mipmap levels
                f.write(struct.pack('<I', 0))  # Key/value data
                
                # Write image data
                image_data = self.image_data[:,:,:channels].tobytes()
                f.write(struct.pack('<I', len(image_data)))
                f.write(image_data)
                
            return True
        except Exception as e:
            print(f"Error writing KTX file: {str(e)}")
            return False

    def open_ktx2(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open KTX File", "", "KTX Files (*.ktx *.ktx2)")
            
        if file_path and self.open_ktx(file_path):
            self.width_spin.setValue(self.image_width)
            self.height_spin.setValue(self.image_height)
            self.update_image_display()
            self.save_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", "Failed to open KTX file")

    def save_ktx2(self):
        if self.image_data is None:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save KTX File", self.current_file or "texture.ktx", 
            "KTX Files (*.ktx)")
            
        if file_path:
            if self.save_ktx(file_path):
                self.current_file = file_path
                QMessageBox.information(self, "Success", "KTX file saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save KTX file")

    def update_image_display(self):
        if self.image_data is None:
            return
            
        # Convert numpy array to QImage
        height, width, channels = self.image_data.shape
        if channels == 3:
            fmt = QImage.Format_RGB888
        else:
            fmt = QImage.Format_RGBA8888
            
        bytes_per_line = width * channels
        qimage = QImage(self.image_data.data, width, height, bytes_per_line, fmt)
        
        # Scale to fit display
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        self.image_label.setPixmap(scaled_pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = KTX2Editor()
    editor.show()
    sys.exit(app.exec())
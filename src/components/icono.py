from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class IconoApp(QWidget):
    def __init__(self, icono: str, texto: str, color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 90)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botón con icono
        self.boton = QPushButton()
        self.boton.setFixedSize(64, 64)
        self.boton.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 15px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
        """)
        
        # Cargar imagen o emoji
        ruta_icono = os.path.join("assets", f"{icono}.png")
        if os.path.exists(ruta_icono):
            pixmap = QPixmap(ruta_icono).scaled(40, 40, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.boton.setIcon(QIcon(pixmap))
        else:
            self.boton.setText("📁")  # Fallback
        
        # Texto
        label = QLabel(texto)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 10px;")
        
        layout.addWidget(self.boton)
        layout.addWidget(label)

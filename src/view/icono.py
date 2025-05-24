from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os


class IconoApp(QWidget):
    def __init__(self, icon_path, texto, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
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

        # Cargar imagen del icono (64x64 recomendado)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            icon = QLabel()
            icon.setPixmap(pixmap)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Layout para centrar la imagen en el botón
            btn_layout = QVBoxLayout(self.boton)
            btn_layout.addWidget(icon)
        else:
            self.boton.setText("📁")
            self.boton.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 15px;
                    border: none;
                    font-size: 24px;
                }}
                QPushButton:hover {{
                    background-color: {color}DD;
                }}
            """)

        # Texto debajo del icono
        texto_label = QLabel(texto)
        texto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texto_label.setStyleSheet("""
            font-size: 10px; 
            color: black;
            background-color: transparent;
        """)

        layout.addWidget(self.boton)
        layout.addWidget(texto_label)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os


class IconoApp(QWidget):
    def __init__(self, icon_path, texto, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 120)  # Aumentado el tamaño del widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Estilo del fondo con gradiente
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #232526, stop:1 #414345);
            }
        """)

        # Botón con icono
        self.boton = QPushButton()
        self.boton.setFixedSize(80, 80)  # Aumentado el tamaño del botón
        self.boton.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 24px;
                border: none;
                box-shadow: 0px 4px 16px rgba(0,0,0,0.25);
                transition: background 0.3s, box-shadow 0.3s;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
                box-shadow: 0px 8px 24px rgba(0,0,0,0.35);
            }}
        """)

        # Cargar imagen del icono (64x64 recomendado)
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(
                56, 56,
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
                    border-radius: 20px;
                    border: none;
                    font-size: 32px;
                }}
                QPushButton:hover {{
                    background-color: {color}DD;
                }}
            """)

        # Texto debajo del icono
        texto_label = QLabel(texto)
        texto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        texto_label.setStyleSheet("""
            font-size: 13px; 
            color: white;
            background-color: transparent;
        """)

        layout.addWidget(self.boton)
        layout.addWidget(texto_label)






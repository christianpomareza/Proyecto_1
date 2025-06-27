# src/view/screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AppScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        # Título genérico que las pantallas hijas pueden sobrescribir
        self.titulo = QLabel("Forencell: Obtén evidencia digital al instante. Preserva, analiza y actúa con precisión.")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.titulo)

        # Un QWidget para el contenido principal, para que las subclases añadan sus layouts
        self.contenido = QWidget()
        self.contenido.setLayout(QVBoxLayout()) # Asegúrate de que tenga un layout
        self.main_layout.addWidget(self.contenido)

        self.main_layout.addStretch() # Empuja el contenido hacia arriba

        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #232526, stop:1 #414345);
            }
            QLabel#titulo {
                color: white;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 1px;
                margin-bottom: 18px;
                text-shadow: 0px 2px 8px #00000088;
            }
            QFrame, QWidget#contenido {
                background: rgba(30, 30, 30, 0.7);
                border-radius: 18px;
                box-shadow: 0px 4px 24px rgba(0,0,0,0.25);
            }
        """)
        self.titulo.setObjectName("titulo")
        self.contenido.setObjectName("contenido")
# src/view/screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AppScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        # Título genérico que las pantallas hijas pueden sobrescribir
        self.titulo = QLabel("Título de la Pantalla")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        self.main_layout.addWidget(self.titulo)

        # Un QWidget para el contenido principal, para que las subclases añadan sus layouts
        self.contenido = QWidget()
        self.contenido.setLayout(QVBoxLayout()) # Asegúrate de que tenga un layout
        self.main_layout.addWidget(self.contenido)

        self.main_layout.addStretch() # Empuja el contenido hacia arriba
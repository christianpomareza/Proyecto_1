from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class AppScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Barra superior con título y botón de regreso
        self.barra_superior = QFrame()
        self.barra_superior.setStyleSheet(
            "background-color: rgba(255, 255, 255, 150); border-radius: 15px;")
        barra_layout = QHBoxLayout(self.barra_superior)
        barra_layout.setContentsMargins(5, 5, 5, 5)

        self.btn_regresar = QPushButton("←")
        self.btn_regresar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                font-size: 18px;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,0.1);
                border-radius: 10px;
            }
        """)
        self.btn_regresar.setFixedSize(30, 30)

        self.titulo = QLabel()
        self.titulo.setStyleSheet("font-size: 16px; font-weight: bold;")

        barra_layout.addWidget(self.btn_regresar)
        barra_layout.addWidget(self.titulo, 1)
        barra_layout.addStretch()

        self.layout.addWidget(self.barra_superior)

        # Área de contenido
        self.contenido = QWidget()
        self.layout.addWidget(self.contenido, 1)

        # Conectar botón de regreso
        self.btn_regresar.clicked.connect(self.regresar)

    def regresar(self):
        if hasattr(self.parent(), 'mostrar_menu_principal'):
            self.parent().mostrar_menu_principal()

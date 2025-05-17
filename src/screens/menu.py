from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import Qt, QTimer
from components.fondo import FondoOndulado
from components.icono import IconoApp
import time

class MenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()
        self.init_reloj()

    def init_ui(self):
        layout = QVBoxLayout(self)
        fondo = FondoOndulado()
        layout.addWidget(fondo)
        
        # Barra de búsqueda y reloj
        self.barra = QHBoxLayout()
        self.busqueda = QLineEdit(placeholderText="🔍 Buscar")
        self.reloj = QLabel()
        self.barra.addWidget(self.busqueda)
        self.barra.addWidget(self.reloj)
        
        # Grid de iconos
        self.grid = QGridLayout()
        apps = [
            ("playstore", "Play Store", "#8BC34A", self.parent_app.mostrar_apps),
            ("settings", "Ajustes", "#9E9E9E", self.parent_app.mostrar_ajustes),
            ("phone", "Llamadas", "#2196F3", self.parent_app.mostrar_llamadas)
        ]
        
        for i, (icono, texto, color, funcion) in enumerate(apps):
            btn = IconoApp(icono, texto, color)
            btn.boton.clicked.connect(funcion)
            self.grid.addWidget(btn, i // 3, i % 3)
        
        fondo_layout = QVBoxLayout(fondo)
        fondo_layout.addLayout(self.barra)
        fondo_layout.addLayout(self.grid)

    def init_reloj(self):
        self.actualizar_reloj()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(1000)

    def actualizar_reloj(self):
        self.reloj.setText(time.strftime("%H:%M"))

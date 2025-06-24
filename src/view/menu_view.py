from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import datetime

from .screen import AppScreen
from .fondo import FondoOndulado
from .icono import IconoApp

class MenuView(AppScreen):
    icon_clicked = pyqtSignal(str)  # Señal para notificar clics en iconos

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titulo.setText("Menú Principal")
        self.init_ui()
        self._start_clock()

    def init_ui(self):
        """Configura la interfaz gráfica del menú"""
        fondo = FondoOndulado()
        self.main_layout.insertWidget(0, fondo)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Layout para el contenido principal
        self.menu_content_layout = self.contenido.layout()
        self.menu_content_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_content_layout.setSpacing(10)

        # Barra superior con búsqueda y reloj
        barra_superior = QFrame()
        barra_superior.setStyleSheet("background-color: rgba(255, 255, 255, 150); border-radius: 15px;")
        barra_superior.setMaximumHeight(50)
        barra_superior_layout = QHBoxLayout(barra_superior)
        barra_superior_layout.setContentsMargins(15, 5, 15, 5)

        self.barra_busqueda = QLineEdit()
        self.barra_busqueda.setPlaceholderText("🔍 Buscar apps...")
        self.barra_busqueda.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 12px;
                border: none;
            }
        """)

        self.reloj = QLabel()
        self.reloj.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
        self.reloj.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.reloj.setMinimumWidth(60)

        barra_superior_layout.addWidget(self.barra_busqueda)
        barra_superior_layout.addWidget(self.reloj)
        self.menu_content_layout.addWidget(barra_superior)

        # Grid para iconos de apps
        iconos_frame = QFrame()
        iconos_frame.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(iconos_frame)
        self.grid_layout.setSpacing(15)
        self.menu_content_layout.addWidget(iconos_frame)

    def _start_clock(self):
        """Inicia el reloj que se actualiza cada segundo"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)
        self.actualizar_hora()

    def actualizar_hora(self):
        """Actualiza la hora mostrada"""
        self.reloj.setText(datetime.datetime.now().strftime('%H:%M'))

    def populate_icons(self, app_icons_data, _):
        """Carga los iconos en el grid y conecta sus señales"""
        # Limpiar iconos existentes
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget)
            widget.deleteLater()

        # Añadir nuevos iconos
        row, col = 0, 0
        for app in app_icons_data:
            icon = IconoApp(app["img"], app["text"], app["color"])
            icon.boton.clicked.connect(
                lambda _, sn=app["screen_name"]: self.icon_clicked.emit(sn)
            )
            self.grid_layout.addWidget(icon, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
# src/view/menu_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer # Importamos QTimer
import datetime # Para el reloj

from .screen import AppScreen     # Importamos la clase base AppScreen
from .fondo import FondoOndulado  # Asegúrate de que FondoOndulado.py exista en src/view/
from .icono import IconoApp       # Asegúrate de que IconoApp.py exista en src/view/

class MenuView(AppScreen): # Hereda de AppScreen
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titulo.setText("Menú Principal") # Personaliza el título de esta pantalla
        self.init_ui()
        self._start_clock() # Inicia el reloj al crear la vista

    def init_ui(self):
        """
        Inicializa los widgets específicos de la vista del menú.
        Usa self.contenido.layout() para añadir widgets al área de contenido definida en AppScreen.
        """
        # El layout principal de AppScreen ya está en self.main_layout.
        # El fondo se añade al main_layout, asegurando que cubra toda la ventana.
        fondo = FondoOndulado()
        self.main_layout.insertWidget(0, fondo) # Inserta el fondo al inicio del layout principal
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Acceder al layout del QWidget de contenido de AppScreen para añadir elementos del menú
        self.menu_content_layout = self.contenido.layout() 
        self.menu_content_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_content_layout.setSpacing(10)

        # Barra superior con búsqueda y reloj
        barra_superior = QFrame()
        barra_superior.setStyleSheet(
            "background-color: rgba(255, 255, 255, 150); border-radius: 15px;")
        barra_superior.setMaximumHeight(50)
        barra_superior_layout = QHBoxLayout(barra_superior)
        barra_superior_layout.setContentsMargins(15, 5, 15, 5) # Pequeños márgenes internos

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
        self.reloj.setMinimumWidth(60) # Asegura espacio para la hora

        barra_superior_layout.addWidget(self.barra_busqueda)
        barra_superior_layout.addWidget(self.reloj)

        self.menu_content_layout.addWidget(barra_superior)

        # Área para los iconos de aplicaciones (QGridLayout)
        iconos_frame = QFrame()
        iconos_frame.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(iconos_frame)
        self.grid_layout.setSpacing(15) # Espacio entre iconos

        self.menu_content_layout.addWidget(iconos_frame)
        self.menu_content_layout.addStretch() # Esto empuja el contenido hacia arriba

    def _start_clock(self):
        """Inicia un QTimer para actualizar la hora cada segundo."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000) # Actualiza cada 1000 ms (1 segundo)
        self.actualizar_hora() # Llama una vez al inicio para mostrar la hora inmediatamente

    def actualizar_hora(self):
        """Actualiza el QLabel del reloj con la hora actual."""
        self.reloj.setText(datetime.datetime.now().strftime('%H:%M'))

    def populate_icons(self, app_icons_data, icon_clicked_callback):
        """
        Llena el grid de iconos con los datos proporcionados y conecta sus botones.
        :param app_icons_data: Lista de diccionarios con 'img', 'text', 'color', 'screen_name'.
        :param icon_clicked_callback: Una función (del controlador principal) a la que se conectará
                                    el clicked de cada botón. Debe aceptar un argumento (screen_name).
        """
        # Limpiar cualquier icono existente antes de repoblar (importante si el menú se recarga)
        # Eliminar widgets del layout en orden inverso para evitar problemas
        for i in reversed(range(self.grid_layout.count())): 
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None) # Desvincular el widget

        row, col = 0, 0
        for app in app_icons_data:
            icon = IconoApp(app["img"], app["text"], app["color"])
            # Conecta la señal `clicked` del botón del icono a la `icon_clicked_callback`
            # Pasamos el `screen_name` de esta app como argumento.
            icon.boton.clicked.connect(lambda checked, target_screen=app["screen_name"]: icon_clicked_callback(target_screen))
            self.grid_layout.addWidget(icon, row, col)
            col += 1
            if col > 3: # 4 columnas por fila (0, 1, 2, 3)
                col = 0
                row += 1
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QMessageBox, QWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt, QTime
import datetime


from .menu_controller import MenuController

# Módulo de Llamadas (Modelo, Vista, Controlador)
# Importación relativa corregida
from ..model.llamadas_model import CallLogModel

# Importación relativa CORREGIDA: era CallLogView
from ..view.llamadas_view import LlamadasView

# Importación relativa: ahora importa LlamadasController
from .llamadas_controller import LlamadasController


# Módulo de Ajustes (Modelo, Vista, Controlador)
# Importación relativa corregida
from ..model.ajustes_model import AjustesModel
# Importación relativa corregida
from ..view.ajustes_view import AjustesView
# Importación relativa corregida
from .ajustes_controller import AjustesController


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Tipo Celular")
        # Tamaño y posición de la ventana principal
        self.setGeometry(100, 100, 320, 600)

        # Contenedor principal de la ventana (para el layout general)
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        # Espacio entre widgets del layout principal
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.main_container)

        # Widget central con pila de pantallas (StackedWidget)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Historial de vistas para el botón de retroceso
        self.view_history = []

        # Barra de navegación inferior (botón atrás y home)
        self._init_navigation_bar()
        self.main_layout.addWidget(self.nav_bar)

        # Inicializar todos los controladores y sus vistas, y añadirlos al stacked_widget
        self._init_controllers()

        # Conectar las señales base (navegación)
        self._connect_base_signals()

        # Mostrar la pantalla inicial (Menú Principal)
        self._show_initial_screen()

        # Actualizar estado de botones de navegación al inicio
        self._update_nav_button_state()

    def _init_navigation_bar(self):
        """
        Inicializa y configura la barra de navegación inferior.
        """
        self.nav_bar = QFrame(self)
        self.nav_bar.setStyleSheet(
            "background-color: #333333; border-top: 1px solid #555555;")
        self.nav_bar_layout = QHBoxLayout(self.nav_bar)
        self.nav_bar_layout.setContentsMargins(10, 5, 10, 5)
        # Espacio entre los botones de navegación
        self.nav_bar_layout.setSpacing(20)

        # Botón de retroceso
        self.nav_back_button = QPushButton("← Atrás")
        self.nav_back_button.setStyleSheet(
            "QPushButton { background-color: #555555; color: white; border-radius: 8px; padding: 5px 10px; }"
            "QPushButton:pressed { background-color: #777777; }"
            "QPushButton:disabled { background-color: #444444; color: #888888; }"
        )
        self.nav_back_button.setFixedSize(80, 30)  # Tamaño fijo para el botón
        self.nav_bar_layout.addWidget(self.nav_back_button)

        # Espaciador para centrar el botón Home (si se desea)
        self.nav_bar_layout.addSpacerItem(QSpacerItem(
            20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Botón de inicio (Home)
        self.nav_home_button = QPushButton("🏠 Inicio")
        self.nav_home_button.setStyleSheet(
            "QPushButton { background-color: #555555; color: white; border-radius: 8px; padding: 5px 10px; }"
            "QPushButton:pressed { background-color: #777777; }"
        )
        self.nav_home_button.setFixedSize(80, 30)  # Tamaño fijo para el botón
        self.nav_bar_layout.addWidget(self.nav_home_button)

        # Espaciador
        self.nav_bar_layout.addSpacerItem(QSpacerItem(
            20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    def _connect_base_signals(self):
        """
        Conecta las señales de los botones de navegación.
        """
        self.nav_back_button.clicked.connect(self.go_back)
        self.nav_home_button.clicked.connect(self.go_home)

    def _init_controllers(self):
        """
        Inicializa los controladores para las diferentes pantallas de la aplicación.
        Cada controlador MVC se encargará de su vista y modelo.
        """
        self.controllers = {
            # Diccionario para almacenar los controladores (o placeholders) por nombre
        }

        # 1. Controlador del Menú Principal
        # El MenuController recibe el MainController para poder usar change_screen
        self.menu_controller = MenuController(self)
        self.stacked_widget.addWidget(self.menu_controller.get_view())
        self.controllers["menu"] = self.menu_controller

        # 2. Módulo de Llamadas (MVC)
        self.call_log_model = CallLogModel()
        # VVVVVVVV CAMBIO AQUÍ VVVVVVVV
        # Le pasamos 'self' (MainController) como parent
        self.call_log_view = LlamadasView(self)
        self.call_log_controller = LlamadasController(
            self.call_log_model, self.call_log_view)
        # ^^^^^^^^ CAMBIO AQUÍ ^^^^^^^^
        # Añade la vista del controlador de llamadas
        self.stacked_widget.addWidget(self.call_log_controller.get_view())
        self.controllers["llamadas"] = self.call_log_controller

        # 3. Módulo de Ajustes (MVC)
        self.ajustes_model = AjustesModel()
        # Le pasamos 'self' (MainController) como parent
        self.ajustes_view = AjustesView(self)
        self.ajustes_controller = AjustesController(
            self.ajustes_model, self.ajustes_view)
        # Añade la vista del controlador de ajustes
        self.stacked_widget.addWidget(self.ajustes_controller.get_view())
        self.controllers["ajustes"] = self.ajustes_controller

        # 4. Placeholders para otras pantallas (si aún no tienen MVC)
        # Reemplaza estos placeholders con la inicialización de sus controladores MVC
        # cuando los implementes.

        self.apps_placeholder = QWidget()
        layout_apps = QVBoxLayout(self.apps_placeholder)
        layout_apps.addWidget(
            QLabel("<h1>Pantalla de Aplicaciones (En construcción)</h1>"))
        layout_apps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(self.apps_placeholder)
        self.controllers["apps"] = self.apps_placeholder

        self.info_placeholder = QWidget()
        layout_info = QVBoxLayout(self.info_placeholder)
        layout_info.addWidget(QLabel("<h1>Información (Placeholder)</h1>"))
        layout_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stacked_widget.addWidget(self.info_placeholder)
        self.controllers["info"] = self.info_placeholder

    def _show_initial_screen(self):
        """
        Muestra la pantalla inicial de la aplicación (el menú principal).
        """
        self.stacked_widget.setCurrentWidget(self.menu_controller.get_view())

    def change_screen(self, screen_name):
        """
        Cambia a la pantalla deseada y gestiona el historial de navegación.
        :param screen_name: El nombre lógico de la pantalla (ej: "menu", "llamadas", "ajustes").
        """
        if screen_name not in self.controllers:
            QMessageBox.critical(self, "Error de Navegación",
                                 f"La pantalla '{screen_name}' no está registrada en MainController.")
            return

        target_widget = None
        screen_entry = self.controllers[screen_name]

        if isinstance(screen_entry, QWidget):
            target_widget = screen_entry
        else:
            target_controller = screen_entry
            target_widget = target_controller.get_view()

            if screen_name == "llamadas":
                target_controller.load_call_logs()
            elif screen_name == "ajustes":
                # Esta línea es crucial para cargar los ajustes y datos ADB
                target_controller.load_initial_settings()

        current_widget = self.stacked_widget.currentWidget()
        # Solo añade al historial si NO es la pantalla actual y NO estamos volviendo al menú desde el menú
        if current_widget is not None and current_widget != target_widget and screen_name != "menu":
            self.view_history.append(current_widget)

        self.stacked_widget.setCurrentWidget(target_widget)
        self._update_nav_button_state()

    def go_back(self):
        """
        Vuelve a la pantalla anterior en el historial de navegación.
        """
        if self.view_history:
            previous_widget = self.view_history.pop()
            self.stacked_widget.setCurrentWidget(previous_widget)
            self._update_nav_button_state()
        else:
            # Asegura que el botón esté deshabilitado
            self.nav_back_button.setEnabled(False)

    def go_home(self):
        """
        Vuelve directamente a la pantalla del menú principal y limpia el historial.
        """
        if self.stacked_widget.currentWidget() != self.menu_controller.get_view():
            self.view_history = []
            self.stacked_widget.setCurrentWidget(
                self.menu_controller.get_view())
        self._update_nav_button_state()

    def _update_nav_button_state(self):
        """
        Actualiza el estado de los botones de navegación (habilitado/deshabilitado).
        """
        self.nav_back_button.setEnabled(len(self.view_history) > 0)
        self.nav_home_button.setEnabled(
            self.stacked_widget.currentWidget() != self.menu_controller.get_view())

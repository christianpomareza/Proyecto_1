from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QTimer
import time

from controller.menu_controller import MenuController
from controller.ajustes_controller import AjustesController
from controller.llamadas_controller import LlamadasController
from controller.apps_controller import AppsController

from PyQt6.QtWidgets import QMessageBox


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Tipo Celular")
        self.setGeometry(100, 100, 320, 600)

        self.pila_pantallas = QStackedWidget()
        self.setCentralWidget(self.pila_pantallas)

        # Crear controladores
        self.menu_controller = MenuController(self)
        self.ajustes_controller = AjustesController(self)
        self.llamadas_controller = LlamadasController(self)
        self.apps_controller = AppsController(self)

        # Crear pantallas y añadir a pila
        self.crear_menu_principal()
        self.crear_pantalla_ajustes()
        self.crear_pantalla_llamadas()
        self.crear_pantalla_apps()

        self.mostrar_menu_principal()

    def crear_menu_principal(self):
        self.menu_principal, self.reloj = self.menu_controller.crear_menu_principal()
        self.pila_pantallas.addWidget(self.menu_principal)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)

    def crear_pantalla_ajustes(self):
        pantalla = self.ajustes_controller.crear_pantalla_ajustes()
        self.pila_pantallas.addWidget(pantalla)

    def crear_pantalla_llamadas(self):
        pantalla = self.llamadas_controller.crear_pantalla_llamadas()
        self.pila_pantallas.addWidget(pantalla)

    def crear_pantalla_apps(self):
        pantalla = self.apps_controller.crear_pantalla_apps()
        self.pila_pantallas.addWidget(pantalla)

    def mostrar_menu_principal(self):
        self.pila_pantallas.setCurrentWidget(self.menu_principal)

    def mostrar_pantalla_ajustes(self):
        self.pila_pantallas.setCurrentWidget(self.ajustes_controller.pantalla_ajustes)

    def mostrar_pantalla_llamadas(self):
        self.pila_pantallas.setCurrentWidget(self.llamadas_controller.pantalla_llamadas)

    def mostrar_pantalla_apps(self):
        self.pila_pantallas.setCurrentWidget(self.apps_controller.pantalla_apps)

    def mostrar_info(self):
        QMessageBox.information(self, "Información", "Esta es una app simulada para la demostración.")

    def actualizar_hora(self):
        self.reloj.setText(time.strftime('%H:%M'))

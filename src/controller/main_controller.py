from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QTimer
from view import *
import time


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Tipo Celular")
        self.setGeometry(100, 100, 320, 600)

        # Widget central con pila de pantallas
        self.pila_pantallas = QStackedWidget()
        self.setCentralWidget(self.pila_pantallas)

        # Crear pantallas
        self.crear_menu_principal()
        self.crear_pantalla_ajustes()
        self.crear_pantalla_llamadas()
        self.crear_pantalla_apps()

        # Mostrar menú principal al inicio
        self.mostrar_menu_principal()

    def crear_menu_principal(self):
        self.menu_principal, self.reloj = crear_menu_principal(self)

        # Configurar temporizador para actualizar el reloj
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)

        # Añadir a la pila de pantallas
        self.pila_pantallas.addWidget(self.menu_principal)

    def crear_pantalla_ajustes(self):
        self.pantalla_ajustes = crear_pantalla_ajustes(self)
        self.pila_pantallas.addWidget(self.pantalla_ajustes)

    def crear_pantalla_llamadas(self):
        self.pantalla_llamadas = crear_pantalla_llamadas(self)
        self.pila_pantallas.addWidget(self.pantalla_llamadas)

    def crear_pantalla_apps(self):
        self.pantalla_apps = crear_pantalla_apps(self)
        self.pila_pantallas.addWidget(self.pantalla_apps)

    def mostrar_menu_principal(self):
        self.pila_pantallas.setCurrentWidget(self.menu_principal)

    def mostrar_pantalla_ajustes(self):
        self.pila_pantallas.setCurrentWidget(self.pantalla_ajustes)

    def mostrar_pantalla_llamadas(self):
        self.pila_pantallas.setCurrentWidget(self.pantalla_llamadas)

    def mostrar_pantalla_apps(self):
        self.pila_pantallas.setCurrentWidget(self.pantalla_apps)

    def mostrar_info(self):
        # Puedes crear una pantalla específica para información o usar un QMessageBox
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Información", "Esta es una app simulada para la demostración.")

    def actualizar_hora(self):
        self.reloj.setText(time.strftime('%H:%M'))

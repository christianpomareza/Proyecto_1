from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from screens.menu import MenuScreen
from screens.ajustes import AjustesScreen
from screens.llamadas import LlamadasScreen
from screens.apps import AppsScreen

class MiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz Celular")
        self.setGeometry(100, 100, 320, 600)
        
        self.pila_pantallas = QStackedWidget()
        self.setCentralWidget(self.pila_pantallas)
        
        # Pantallas
        self.menu = MenuScreen(self)
        self.ajustes = AjustesScreen(self)
        self.llamadas = LlamadasScreen(self)
        self.apps = AppsScreen(self)
        
        # Agregar a pila
        self.pila_pantallas.addWidget(self.menu)
        self.pila_pantallas.addWidget(self.ajustes)
        self.pila_pantallas.addWidget(self.llamadas)
        self.pila_pantallas.addWidget(self.apps)
        
        self.mostrar_menu()

    def mostrar_menu(self):
        self.pila_pantallas.setCurrentWidget(self.menu)
    
    def mostrar_ajustes(self):
        self.pila_pantallas.setCurrentWidget(self.ajustes)
    
    def mostrar_llamadas(self):
        self.pila_pantallas.setCurrentWidget(self.llamadas)
    
    def mostrar_apps(self):
        self.pila_pantallas.setCurrentWidget(self.apps)

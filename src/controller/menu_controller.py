from model.menu_model import obtener_apps_menu
from view.menu import crear_menu_principal

class MenuController:
    def __init__(self, parent):
        self.parent = parent
        self.menu_principal = None
        self.reloj = None

    def crear_menu_principal(self):
        lista_apps = obtener_apps_menu()

        funciones = {
            "mostrar_pantalla_apps": self.parent.mostrar_pantalla_apps,
            "mostrar_info": self.parent.mostrar_info,
            "mostrar_pantalla_ajustes": self.parent.mostrar_pantalla_ajustes,
            "mostrar_pantalla_llamadas": self.parent.mostrar_pantalla_llamadas,
        }

        self.menu_principal, self.reloj = crear_menu_principal(self.parent, lista_apps, funciones)
        return self.menu_principal, self.reloj

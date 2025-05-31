from view.apps import crear_pantalla_apps
from model.apps_model import obtener_apps_instaladas

class AppsController:
    def __init__(self, parent):
        self.parent = parent
        self.pantalla_apps = None

    def crear_pantalla_apps(self):
        apps, error = obtener_apps_instaladas()
        self.pantalla_apps = crear_pantalla_apps(self.parent, apps, error)
        return self.pantalla_apps

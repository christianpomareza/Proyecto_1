from model.llamadas_model import obtener_llamadas
from view.llamadas import crear_pantalla_llamadas

class LlamadasController:
    def __init__(self, parent):
        self.parent = parent
        self.pantalla_llamadas = None

    def crear_pantalla_llamadas(self):
        llamadas = obtener_llamadas()
        self.pantalla_llamadas = crear_pantalla_llamadas(self.parent, llamadas)
        return self.pantalla_llamadas

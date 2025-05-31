from model.ajustes_model import actualizar_info_adb
from view.ajustes import crear_pantalla_ajustes

class AjustesController:
    def __init__(self, parent):
        self.parent = parent
        self.pantalla_ajustes = None
        self.boton_refrescar = None
        self.lista_dispositivos = None

    def crear_pantalla_ajustes(self):
        dispositivos = actualizar_info_adb()
        self.pantalla_ajustes, self.boton_refrescar, self.lista_dispositivos = crear_pantalla_ajustes(self.parent, dispositivos)
        self.boton_refrescar.clicked.connect(self.refrescar_info_adb)
        return self.pantalla_ajustes

    def refrescar_info_adb(self):
        dispositivos = actualizar_info_adb()
        self.lista_dispositivos.clear()
        if dispositivos:
            self.lista_dispositivos.addItems(dispositivos)
        else:
            self.lista_dispositivos.addItem("No hay dispositivos conectados")

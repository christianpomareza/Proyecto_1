import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from ..model.menu_model import MenuModel
from ..view.menu_view import MenuView
from ..view.icono import IconoApp
from ..controller.reportes_controller import ReportesController

class MenuController:
    def __init__(self, main_app_controller):
        self.main_app_controller = main_app_controller
        self.model = MenuModel()
        self.view = MenuView(main_app_controller)
        self.reporte_controller = ReportesController(self.view)
        self._connect_signals()
        self._populate_menu_icons()

    def _connect_signals(self):
        self.view.icon_clicked.connect(self._handle_icon_click)
        self.view.barra_busqueda.textChanged.connect(self._filtrar_iconos)

    def _handle_icon_click(self, screen_name):
        if screen_name == "whatsapp":
            self._launch_external_app("main7.py", "WhatsApp Viewer")
        elif screen_name == "mensajes": # Esta condición ya existía y es la que necesitas
            self._launch_external_app("mensajes.py", "Visor de Mensajes")
        else:
            self.main_app_controller.change_screen(screen_name)

    def _launch_external_app(self, filename, app_name):
        """Método genérico para lanzar apps externas"""
        try:
            base_dir = Path(__file__).parent.parent
            app_path = base_dir / filename
            
            if app_path.exists():
                subprocess.Popen(["python", str(app_path)])
            else:
                QMessageBox.critical(
                    self.view,
                    "Error",
                    f"¡Archivo {filename} no encontrado!\nRuta esperada: {app_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Error al abrir {app_name}:\n{str(e)}"
            )

    def _filtrar_iconos(self, texto):
        texto = texto.lower().strip()
        iconos = self.model.get_app_icons_data()
        if texto:
            iconos = [icono for icono in iconos if texto in icono["text"].lower()]
        self.view.populate_icons(iconos, None)
        # Vuelve a agregar el botón de reportes si existe
        self.view.add_custom_icon(self._crear_boton_reportes())

    def _crear_boton_reportes(self):
        btn_reportes = IconoApp(
            icon_path="resources/assets/report.png",
            texto="Reportes",
            color="#4CAF50"
        )
        btn_reportes.boton.clicked.connect(self.reporte_controller.generar_reporte)
        return btn_reportes

    def _populate_menu_icons(self):
        # Cargar íconos normales desde el modelo
        self.view.populate_icons(self.model.get_app_icons_data(), None)
        self.view.add_custom_icon(self._crear_boton_reportes())

    def get_view(self):
        return self.view
import subprocess
import os
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from ..model.menu_model import MenuModel
from ..view.menu_view import MenuView

class MenuController:
    def __init__(self, main_app_controller):
        self.main_app_controller = main_app_controller
        self.model = MenuModel()
        self.view = MenuView(main_app_controller)
        self._connect_signals()
        self._populate_menu_icons()

    def _connect_signals(self):
        self.view.icon_clicked.connect(self._handle_icon_click)

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

    def _populate_menu_icons(self):
        """Carga los íconos en la vista"""
        self.view.populate_icons(self.model.get_app_icons_data(), None)

    def get_view(self):
        return self.view
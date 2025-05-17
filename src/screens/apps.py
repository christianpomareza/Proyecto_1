from PyQt6.QtWidgets import QVBoxLayout, QTextBrowser, QPushButton
from components.screen import AppScreen
import subprocess

class AppsScreen(AppScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.titulo.setText("Aplicaciones")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.contenido)
        
        # Botón para actualizar
        btn_actualizar = QPushButton("Actualizar lista")
        btn_actualizar.clicked.connect(self.actualizar_apps)
        
        # Área de texto para mostrar apps
        self.texto_apps = QTextBrowser()
        self.texto_apps.setStyleSheet("font-family: monospace;")
        
        layout.addWidget(btn_actualizar)
        layout.addWidget(self.texto_apps)
        self.actualizar_apps()

    def actualizar_apps(self):
        try:
            # Obtener apps instaladas (requiere ADB)
            result = subprocess.run(
                ['adb', 'shell', 'pm', 'list', 'packages'],
                capture_output=True,
                text=True
            )
            apps = result.stdout.replace('package:', '• ') if result.stdout else "No se detectaron apps"
            self.texto_apps.setPlainText(apps)
        except Exception as e:
            self.texto_apps.setPlainText(f"Error al obtener apps:\n{str(e)}")

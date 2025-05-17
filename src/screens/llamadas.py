from PyQt6.QtWidgets import QVBoxLayout, QTextBrowser, QLabel
from components.screen import AppScreen
import subprocess

class LlamadasScreen(AppScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.titulo.setText("Llamadas")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.contenido)
        
        try:
            # Obtener registro de llamadas (requiere ADB)
            result = subprocess.run(
                ['adb', 'shell', 'content', 'query', '--uri', 'content://call_log/calls'],
                capture_output=True,
                text=True
            )
            llamadas = QTextBrowser()
            llamadas.setPlainText(result.stdout if result.stdout else "No hay llamadas recientes")
        except Exception as e:
            llamadas = QLabel(f"Error al obtener llamadas:\n{str(e)}")
        
        layout.addWidget(llamadas)

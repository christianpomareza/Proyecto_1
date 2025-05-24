from PyQt6.QtWidgets import QVBoxLayout, QTextBrowser, QLabel
import subprocess
from .screen import AppScreen


def crear_pantalla_llamadas(parent):
    pantalla_llamadas = AppScreen(parent)
    pantalla_llamadas.titulo.setText("Llamadas")

    # Contenido de llamadas
    contenido = QVBoxLayout(pantalla_llamadas.contenido)

    # Ejemplo de registro de llamadas
    try:
        resultado = subprocess.check_output(
            ['adb', 'shell', 'content', 'query',
                '--uri', 'content://call_log/calls'],
            text=True,
            stderr=subprocess.STDOUT
        )

        llamadas = QTextBrowser()
        llamadas.setPlainText(
            resultado.strip() if resultado.strip() else "No hay llamadas recientes")
        contenido.addWidget(llamadas)
    except Exception as e:
        # Crear registros de ejemplo en caso de error
        llamadas = QTextBrowser()
        llamadas.setStyleSheet(
            "background-color: rgba(255, 255, 255, 150); border-radius: 10px;")
        ejemplos = """
        Registro de Llamadas:
        
        ► Juan Pérez - Móvil
           15:30 - Llamada saliente (2:15)
        
        ► María García - Casa
           14:22 - Llamada entrante (0:45)
        
        ► Oficina
           12:10 - Llamada perdida
        
        ► Servicio Técnico
           Ayer - Llamada saliente (5:30)
        
        ► Ana López - Móvil
           Ayer - Llamada entrante (1:20)
        """
        llamadas.setPlainText(ejemplos)
        contenido.addWidget(llamadas)

        # Mensaje de error (solo para desarrolladores)
        error_msg = QLabel(
            f"Nota para desarrolladores: No se pudo conectar con ADB: {str(e)}")
        error_msg.setStyleSheet("color: gray; font-size: 10px;")
        contenido.addWidget(error_msg)

    return pantalla_llamadas

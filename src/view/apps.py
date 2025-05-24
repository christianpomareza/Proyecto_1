
from PyQt6.QtWidgets import QVBoxLayout, QTextBrowser, QLabel
import subprocess
from .screen import AppScreen

def crear_pantalla_apps(parent):
    pantalla_apps = AppScreen(parent)
    pantalla_apps.titulo.setText("Aplicaciones")
    
    # Contenido de apps
    contenido = QVBoxLayout(pantalla_apps.contenido)

    # Ejemplo de lista de apps
    try:
        resultado = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], text=True)
        apps = QTextBrowser()
        apps.setPlainText(resultado.strip())
        contenido.addWidget(apps)
    except Exception as e:
        # Crear lista de apps de ejemplo en caso de error
        apps = QTextBrowser()
        apps.setStyleSheet("background-color: rgba(255, 255, 255, 150); border-radius: 10px;")
        ejemplos = """
        Aplicaciones Instaladas:
        
        • Mensajes
        • Teléfono
        • Contactos
        • Cámara
        • Galería
        • Reloj
        • Calculadora
        • Navegador
        • Maps
        • YouTube
        • Instagram
        • WhatsApp
        • Facebook
        • Twitter
        • Netflix
        • Spotify
        • Gmail
        • Drive
        • Fotos
        • Calendario
        """
        apps.setPlainText(ejemplos)
        contenido.addWidget(apps)
        
        # Mensaje de error (solo para desarrolladores)
        error_msg = QLabel(f"Nota para desarrolladores: No se pudo conectar con ADB: {str(e)}")
        error_msg.setStyleSheet("color: gray; font-size: 10px;")
        contenido.addWidget(error_msg)
    
    return pantalla_apps

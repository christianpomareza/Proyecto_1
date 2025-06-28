from PyQt6.QtWidgets import QVBoxLayout, QTextBrowser, QLabel
from .screen import AppScreen

def crear_pantalla_apps(parent, lista_apps, error_msg=None):
    pantalla_apps = AppScreen(parent)
    pantalla_apps.titulo.setText("Aplicaciones")

    contenido = QVBoxLayout(pantalla_apps.contenido)

    apps_widget = QTextBrowser()
    apps_widget.setPlainText('\n'.join(lista_apps))
    contenido.addWidget(apps_widget)

    if error_msg:
        etiqueta_error = QLabel(f"Nota para desarrolladores: No se pudo conectar con ADB: {error_msg}")
        etiqueta_error.setStyleSheet("color: gray; font-size: 10px;")
        contenido.addWidget(etiqueta_error)

    return pantalla_apps

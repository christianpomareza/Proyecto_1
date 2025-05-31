from PyQt6.QtWidgets import QTextBrowser, QVBoxLayout
from .screen import AppScreen

def crear_pantalla_llamadas(parent, lista_llamadas):
    pantalla = AppScreen(parent)
    pantalla.titulo.setText("Llamadas")

    layout = QVBoxLayout(pantalla.contenido)
    log = QTextBrowser()
    log.setPlainText('\n'.join(lista_llamadas))
    layout.addWidget(log)

    return pantalla

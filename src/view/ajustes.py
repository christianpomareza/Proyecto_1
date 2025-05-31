from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget


def crear_pantalla_ajustes(parent, dispositivos_adb):
    """
    Crea y devuelve el widget de la pantalla Ajustes.

    Args:
        parent: QWidget padre.
        dispositivos_adb: lista de strings con dispositivos ADB conectados.

    Returns:
        pantalla: QWidget principal de ajustes.
        boton_refrescar: QPushButton para actualizar info.
        lista_dispositivos: QListWidget que muestra dispositivos.
    """
    pantalla = QWidget(parent)
    layout = QVBoxLayout(pantalla)

    # Título
    titulo = QLabel("Pantalla de Ajustes")
    titulo.setStyleSheet("font-weight: bold; font-size: 16px;")
    layout.addWidget(titulo)

    # Lista dispositivos conectados
    lista_dispositivos = QListWidget()
    if dispositivos_adb:
        lista_dispositivos.addItems(dispositivos_adb)
    else:
        lista_dispositivos.addItem("No hay dispositivos conectados")
    layout.addWidget(lista_dispositivos)

    # Botón para refrescar la información
    boton_refrescar = QPushButton("Refrescar Dispositivos")
    layout.addWidget(boton_refrescar)

    # Aquí puedes añadir más widgets para otros ajustes si quieres

    return pantalla, boton_refrescar, lista_dispositivos

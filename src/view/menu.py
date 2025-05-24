from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt

from .fondo import FondoOndulado
from .icono import IconoApp


def crear_menu_principal(parent):
    # Pantalla del menú principal
    menu_principal = QWidget()
    layout = QVBoxLayout(menu_principal)
    layout.setContentsMargins(0, 0, 0, 0)

    # Fondo ondulado
    fondo = FondoOndulado()
    layout.addWidget(fondo)

    main_layout = QVBoxLayout(fondo)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(10)

    # Barra superior con búsqueda y reloj
    barra_superior = QFrame()
    barra_superior.setStyleSheet(
        "background-color: rgba(255, 255, 255, 150); border-radius: 15px;")
    barra_superior_layout = QHBoxLayout(barra_superior)
    barra_superior.setMaximumHeight(50)

    barra_busqueda = QLineEdit()
    barra_busqueda.setPlaceholderText("🔍 Buscar apps...")
    barra_busqueda.setStyleSheet("""
        QLineEdit {
            background-color: rgba(255, 255, 255, 180);
            border-radius: 15px;
            padding: 8px 15px;
            font-size: 12px;
            border: none;
        }
    """)

    reloj = QLabel()
    reloj.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
    reloj.setAlignment(Qt.AlignmentFlag.AlignRight |
                       Qt.AlignmentFlag.AlignVCenter)
    reloj.setMinimumWidth(60)

    barra_superior_layout.addWidget(barra_busqueda)
    barra_superior_layout.addWidget(reloj)

    # Grid de iconos
    iconos_frame = QFrame()
    iconos_frame.setStyleSheet("background-color: transparent;")
    grid_layout = QGridLayout(iconos_frame)
    grid_layout.setSpacing(15)

    # Definir aplicaciones con rutas corregidas para assets/
    app_icons = [
        {"img": "assets/playstore.png", "text": "Play Store",
            "color": "#8BC34A", "func": parent.mostrar_pantalla_apps},
        {"img": "assets/chrome.png", "text": "Chrome",
            "color": "#00BCD4", "func": parent.mostrar_info},
        {"img": "assets/settings.png", "text": "Ajustes",
            "color": "#9E9E9E", "func": parent.mostrar_pantalla_ajustes},
        {"img": "assets/phone.png", "text": "Llamadas",
            "color": "#2196F3", "func": parent.mostrar_pantalla_llamadas},
        {"img": "assets/games.png", "text": "Juegos",
            "color": "#FF9800", "func": parent.mostrar_info},
        {"img": "assets/amongus.png", "text": "NN",
            "color": "#F44336", "func": parent.mostrar_info},
        {"img": "assets/memory.png", "text": "Memoria",
            "color": "#3F51B5", "func": parent.mostrar_info},
        {"img": "assets/cod.png", "text": "NN",
            "color": "#FFC107", "func": parent.mostrar_info},
        {"img": "assets/music.png", "text": "Música",
            "color": "#9C27B0", "func": parent.mostrar_info},
        {"img": "assets/freefire.png", "text": "NN",
            "color": "#FF5722", "func": parent.mostrar_info},
        {"img": "assets/battery.png", "text": "Energía",
            "color": "#673AB7", "func": parent.mostrar_info}
    ]

    # Crear iconos
    row, col = 0, 0
    for app in app_icons:
        icon = IconoApp(app["img"], app["text"], app["color"])
        icon.boton.clicked.connect(app["func"])
        grid_layout.addWidget(icon, row, col)
        col += 1
        if col > 3:
            col = 0
            row += 1

    # Barra inferior
    dock_inferior = QFrame()
    dock_inferior.setStyleSheet(
        "background-color: rgba(255, 255, 255, 180); border-radius: 20px;")
    dock_layout = QHBoxLayout(dock_inferior)
    dock_inferior.setMaximumHeight(60)

    nav_home = QPushButton("🏠")
    nav_home.setStyleSheet(
        "background-color: transparent; font-size: 24px; border: none;")
    nav_back = QPushButton("⬅️")
    nav_back.setStyleSheet(
        "background-color: transparent; font-size: 24px; border: none;")
    nav_menu = QPushButton("☰")
    nav_menu.setStyleSheet(
        "background-color: transparent; font-size: 24px; border: none;")

    dock_layout.addWidget(nav_back)
    dock_layout.addWidget(nav_home)
    dock_layout.addWidget(nav_menu)

    # Organizar layout principal
    main_layout.addWidget(barra_superior)
    main_layout.addWidget(iconos_frame, 1)
    main_layout.addWidget(dock_inferior)

    return menu_principal, reloj


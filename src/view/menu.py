from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from .fondo import FondoOndulado
from .icono import IconoApp


def crear_menu_principal(parent, lista_apps, funciones):
    menu_principal = QWidget()
    layout = QVBoxLayout(menu_principal)
    layout.setContentsMargins(0, 0, 0, 0)

    fondo = FondoOndulado()
    layout.addWidget(fondo)

    main_layout = QVBoxLayout(fondo)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(10)

    barra_superior = QFrame()
    barra_superior.setStyleSheet("background-color: rgba(255, 255, 255, 150); border-radius: 15px;")
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
    reloj.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    reloj.setMinimumWidth(60)

    barra_superior_layout.addWidget(barra_busqueda)
    barra_superior_layout.addWidget(reloj)

    iconos_frame = QFrame()
    iconos_frame.setStyleSheet("background-color: transparent;")
    grid_layout = QGridLayout(iconos_frame)
    grid_layout.setSpacing(15)

    # Crear iconos con funciones conectadas
    row, col = 0, 0
    for app in lista_apps:
        icon = IconoApp(app["img"], app["text"], app["color"])
        func = funciones.get(app["func_name"])
        if func:
            icon.boton.clicked.connect(func)
        grid_layout.addWidget(icon, row, col)
        col += 1
        if col > 3:
            col = 0
            row += 1

    dock_inferior = QFrame()
    dock_inferior.setStyleSheet("background-color: rgba(255, 255, 255, 180); border-radius: 20px;")
    dock_layout = QHBoxLayout(dock_inferior)
    dock_inferior.setMaximumHeight(60)

    nav_home = QPushButton("🏠")
    nav_home.setStyleSheet("background-color: transparent; font-size: 24px; border: none;")
    nav_back = QPushButton("⬅️")
    nav_back.setStyleSheet("background-color: transparent; font-size: 24px; border: none;")
    nav_menu = QPushButton("☰")
    nav_menu.setStyleSheet("background-color: transparent; font-size: 24px; border: none;")

    dock_layout.addWidget(nav_back)
    dock_layout.addWidget(nav_home)
    dock_layout.addWidget(nav_menu)

    main_layout.addWidget(barra_superior)
    main_layout.addWidget(iconos_frame, 1)
    main_layout.addWidget(dock_inferior)

    return menu_principal, reloj

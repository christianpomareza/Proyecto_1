# src/main.py
from PyQt6.QtWidgets import QApplication
import sys
import os
from src.controller.main_controller import MainController # Importación absoluta para el script principal

if __name__ == "__main__":

    # Esto es un bloque para verificar y crear la carpeta 'assets'
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Crea una carpeta 'assets' y coloca allí los iconos de las aplicaciones")
        print("Nombres esperados: playstore.png, chrome.png, settings.png, phone.png, etc.")

    app = QApplication(sys.argv)
    ventana = MainController()
    ventana.show()
    app.exec()
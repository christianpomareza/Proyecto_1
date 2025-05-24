from PyQt6.QtWidgets import QApplication
import sys
import os
from controller.main_controller import MainController

if __name__ == "__main__":

    """ El código solo verifica que existe la carpeta assets, pero no agrega imágenes
    # Verificar y crear directorio de imágenes
    if not os.path.exists("assets"):
        os.makedirs("assets")
        # link:playstore.png
        # Función que rellene los datos faltantes
        print("Crea una carpeta 'assets' y coloca allí los iconos de las aplicaciones")
        print("Nombres esperados: playstore.png, chrome.png, settings.png, phone.png, etc.") """

    app = QApplication(sys.argv)
    ventana = MainController()
    ventana.show()
    app.exec()


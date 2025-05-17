import sys
from PyQt6.QtWidgets import QApplication
from src.app import MiApp

if __name__ == "__main__":
    # Verificar assets (opcional)
    import os
    if not os.path.exists("assets"):
        print("⚠️ Crea una carpeta 'assets' con los archivos PNG necesarios")
        print("Nombres requeridos: playstore.png, chrome.png, settings.png, phone.png, etc.")
    
    # Iniciar app
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Mejor rendimiento visual
    ventana = MiApp()
    ventana.show()
    sys.exit(app.exec())

from PyQt6.QtWidgets import QApplication
from controller.main_controller import MainController

if __name__ == "__main__":
    app = QApplication([])
    window = MainController()
    window.show()
    app.exec()

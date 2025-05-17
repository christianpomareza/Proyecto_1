from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class AppScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout(self)
        
        # Barra superior
        self.barra = QWidget()
        barra_layout = QHBoxLayout(self.barra)
        
        self.btn_atras = QPushButton("←")
        self.titulo = QLabel("Título")
        
        barra_layout.addWidget(self.btn_atras)
        barra_layout.addWidget(self.titulo)
        self.layout.addWidget(self.barra)
        
        # Área principal
        self.contenido = QWidget()
        self.layout.addWidget(self.contenido)
        
        self.btn_atras.clicked.connect(self.regresar)
    
    def regresar(self):
        if self.parent_app:
            self.parent_app.mostrar_menu()

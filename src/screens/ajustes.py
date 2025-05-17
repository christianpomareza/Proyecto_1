from PyQt6.QtWidgets import QVBoxLayout, QLabel, QSlider, QCheckBox
from components.screen import AppScreen

class AjustesScreen(AppScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.titulo.setText("Ajustes")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.contenido)
        
        # Configuración de brillo
        lbl_brillo = QLabel("Brillo: 80%")
        slider_brillo = QSlider(Qt.Orientation.Horizontal)
        slider_brillo.setRange(0, 100)
        slider_brillo.setValue(80)
        slider_brillo.valueChanged.connect(lambda v: lbl_brillo.setText(f"Brillo: {v}%"))
        
        # Configuración de sonido
        check_sonido = QCheckBox("Sonido activado")
        check_sonido.setChecked(True)
        
        # Configuración de tema
        lbl_tema = QLabel("Tema oscuro")
        check_tema = QCheckBox()
        
        layout.addWidget(lbl_brillo)
        layout.addWidget(slider_brillo)
        layout.addSpacing(20)
        layout.addWidget(check_sonido)
        layout.addSpacing(20)
        layout.addWidget(lbl_tema)
        layout.addWidget(check_tema)
        layout.addStretch()

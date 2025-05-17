from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPainterPath, QLinearGradient, QColor, QBrush
from PyQt6.QtCore import Qt

class FondoOndulado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Gradiente
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(240, 240, 255))
        gradient.setColorAt(1, QColor(200, 230, 255))
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Ondas
        path = QPainterPath()
        path.moveTo(0, self.height() * 0.7)
        path.cubicTo(
            self.width() * 0.3, self.height() * 0.5,
            self.width() * 0.7, self.height() * 0.9,
            self.width(), self.height() * 0.6
        )
        path.lineTo(self.width(), self.height())
        path.lineTo(0, self.height())
        painter.fillPath(path, QColor(170, 220, 230, 80))

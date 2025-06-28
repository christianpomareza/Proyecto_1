from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt


class FondoOndulado(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradiente de fondo
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(240, 240, 255))
        gradient.setColorAt(0.3, QColor(230, 245, 255))
        gradient.setColorAt(0.7, QColor(200, 230, 255))
        gradient.setColorAt(1.0, QColor(225, 235, 255))

        painter.fillRect(0, 0, self.width(), self.height(), QBrush(gradient))

        # Onda principal
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(170, 220, 230, 80))
        path = QPainterPath()
        path.moveTo(0, self.height() * 0.5)
        path.cubicTo(
            self.width() * 0.25, self.height() * 0.35,
            self.width() * 0.75, self.height() * 0.65,
            self.width(), self.height() * 0.45
        )
        path.lineTo(self.width(), self.height())
        path.lineTo(0, self.height())
        path.closeSubpath()
        painter.drawPath(path)

        # Segunda onda
        painter.setBrush(QColor(150, 200, 240, 60))
        path2 = QPainterPath()
        path2.moveTo(0, self.height() * 0.7)
        path2.cubicTo(
            self.width() * 0.35, self.height() * 0.5,
            self.width() * 0.65, self.height() * 0.8,
            self.width(), self.height() * 0.6
        )
        path2.lineTo(self.width(), self.height())
        path2.lineTo(0, self.height())
        path2.closeSubpath()
        painter.drawPath(path2)

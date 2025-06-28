from PyQt6.QtWidgets import QMessageBox

class ReportesView:
    def __init__(self, parent=None):
        self.parent = parent

    def mostrar_mensaje_hash(self, archivo, hash_valor):
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Reporte generado")
        msg.setText(f"✅ PDF generado en:\n{archivo}\n\n🔐 El código hash es:\n{hash_valor}")
        msg.exec()

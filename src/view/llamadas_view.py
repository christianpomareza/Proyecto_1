# src/view/llamadas_view.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QLabel, QLineEdit,
    QFileDialog
)
from PyQt6.QtCore import Qt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from openpyxl import Workbook

# Importa tu clase AppScreen real. Ajusta la ruta si es necesario.
# Asumo que 'screen.py' está en la misma carpeta 'view'.
try:
    from .screen import AppScreen
except ImportError:
    # Definición de respaldo si no se encuentra AppScreen
    class AppScreen(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.titulo = QLabel("Título de la Pantalla")
            self.contenido = QWidget()
            # ESTO ES LO CRÍTICO: SOLO SE ASIGNA UN LAYOUT UNA VEZ.
            # AppScreen ya debe tener un layout en self.contenido.
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.titulo)
            main_layout.addWidget(self.contenido)
            # Asegúrate de que self.contenido tenga un layout inicializado por AppScreen
            # o inicialízalo aquí si AppScreen no lo hace.
            if not self.contenido.layout(): # Agregado para robustez
                self.contenido.setLayout(QVBoxLayout())


class LlamadasView(AppScreen): # Hereda de AppScreen
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titulo.setText("Historial de Llamadas")
        self.init_ui()

    def init_ui(self):
        """
        Inicializa los widgets específicos de la vista del menú.
        Usa self.contenido.layout() para añadir widgets al área de contenido definida en AppScreen.
        """
        # Obtener el layout existente de self.contenido que fue configurado por AppScreen
        content_layout = self.contenido.layout()
        if content_layout is None:
            # Esto NO debería suceder si AppScreen está bien, pero es una fallback.
            content_layout = QVBoxLayout(self.contenido)
            self.contenido.setLayout(content_layout)

        # Campo de búsqueda
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, número o tipo...")
        search_layout.addWidget(self.search_input)
        content_layout.addLayout(search_layout) # Añade este layout al layout principal de contenido

        # Botón para cargar historial (mantenerlo para la acción manual)
        self.load_button = QPushButton("Obtener y Mostrar Historial")
        content_layout.addWidget(self.load_button)

        # Tabla para mostrar el historial de llamadas
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5) # Nombre, Número, Duración, Fecha y Hora, Tipo de Llamada
        self.table_widget.setHorizontalHeaderLabels([
            "Nombre", "Número", "Duración", "Fecha y Hora", "Tipo de Llamada"
        ])
        # Ajustar el tamaño de las columnas al contenido
        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True) # La última columna estira

        content_layout.addWidget(self.table_widget)

        # Botones de exportación
        export_buttons_layout = QHBoxLayout()
        self.export_pdf_button = QPushButton("Exportar a PDF")
        self.export_excel_button = QPushButton("Exportar a Excel")
        export_buttons_layout.addWidget(self.export_pdf_button)
        export_buttons_layout.addWidget(self.export_excel_button)
        content_layout.addLayout(export_buttons_layout)


    def set_table_data(self, data: list[dict], column_order: list[str]):
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(column_order))
        self.table_widget.setHorizontalHeaderLabels(column_order)

        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(column_order):
                item = QTableWidgetItem(str(row_data.get(col_name, '')))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Hacer la celda no editable
                self.table_widget.setItem(row_idx, col_idx, item)

        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setStretchLastSection(True)

    def get_search_term(self) -> str:
        return self.search_input.text()


    def show_info_message(self, title, message, show_popup: bool = True):
        if show_popup:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
        else:
            print(f"[INFO - {title}] {message}")

    def show_warning_message(self, title, message, show_popup: bool = True):
        if show_popup:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
        else:
            print(f"[WARNING - {title}] {message}")

    def show_critical_message(self, title, message, show_popup: bool = True):
        if show_popup:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()
        else:
            print(f"[CRITICAL - {title}] {message}")


    def export_to_pdf(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.parent(), "Guardar como PDF", "", "Archivos PDF (*.pdf)")
            if not filename:
                return False

            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []

            # Headers
            headers = [self.table_widget.horizontalHeaderItem(
                col).text() for col in range(self.table_widget.columnCount())]

            # Data
            data = [headers]
            for row in range(self.table_widget.rowCount()):
                row_data = []
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    row_data.append(item.text() if item else '')
                data.append(row_data)

            table = Table(data)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(style)
            elements.append(table)
            self.show_info_message("Exportación Exitosa", f"Se exportó el historial a {filename}", show_popup=True)
            return True

        except Exception as e:
            self.show_critical_message("Error al Exportar", f"Error: {e}", show_popup=True)
            return False

    def export_to_excel(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self.parent(), "Guardar como Excel", "", "Archivos Excel (*.xlsx)")
            if not filename:
                return False

            workbook = Workbook()
            sheet = workbook.active

            headers = [self.table_widget.horizontalHeaderItem(
                col).text() for col in range(self.table_widget.columnCount())]
            sheet.append(headers)

            for row in range(self.table_widget.rowCount()):
                row_data = []
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    row_data.append(item.text() if item else '')
                sheet.append(row_data)

            workbook.save(filename)
            self.show_info_message("Exportación Exitosa", f"Se exportó el historial a {filename}", show_popup=True)
            return True

        except Exception as e:
            self.show_critical_message("Error al Exportar", f"Error: {e}", show_popup=True)
            return False
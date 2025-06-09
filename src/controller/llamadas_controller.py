# src/controller/llamadas_controller.py

from ..model.llamadas_model import CallLogModel
from ..view.llamadas_view import LlamadasView
# No necesitamos QMessageBox aquí directamente, ya que la vista lo maneja
# from PyQt6.QtWidgets import QMessageBox

class LlamadasController:
    def __init__(self, model: CallLogModel, view: LlamadasView):
        self.model = model
        self.view = view
        self._all_call_data = [] # Para almacenar los datos completos para filtrar

        # Conectar señales de la vista a slots del controlador
        self.view.load_button.clicked.connect(self.load_call_logs)
        self.view.export_pdf_button.clicked.connect(self.export_pdf)
        self.view.export_excel_button.clicked.connect(self.export_excel)

        # Conectar el campo de búsqueda para filtrar la tabla dinámicamente
        self.view.search_input.textChanged.connect(self.filter_call_logs)


    def get_view(self):
        return self.view

    def load_call_logs(self):
        self.view.table_widget.setRowCount(0) # Limpiar tabla antes de cargar nuevos datos
        self._all_call_data = [] # Limpiar datos internos del controlador

        # Mensaje de carga discreto (solo en consola)
        self.view.show_info_message("Cargando...", "Obteniendo historial de llamadas del dispositivo...", show_popup=False)

        xml_data = self.model.get_call_log_xml_from_device()

        if xml_data is None:
            # Si xml_data es None, significa que hubo un problema en el modelo (no se encontró archivo, ADB falló, etc.)
            # El modelo ya imprimió un mensaje DEBUG en la consola. Aquí mostramos un QMessageBox al usuario.
            self.view.show_critical_message("Error al Cargar Llamadas",
                                     "No se pudo obtener el historial de llamadas del dispositivo. "
                                     "Posibles razones:\n"
                                     "- El celular no está conectado o la depuración USB no está activa.\n"
                                     "- El archivo XML no existe en el dispositivo o la ruta/nombre no coincide con el patrón esperado (`/sdcard/extraer/` y `calls-YYYYMMDDHHMMSS.xml`).\n"
                                     "Revisa la consola de Python para ver los mensajes de depuración de ADB más detallados.",
                                     show_popup=True) # <-- Mostrar este mensaje como popup
            return # Salir de la función si no hay XML

        parsed_calls = self.model.parse_call_log_xml(xml_data)

        if not parsed_calls:
            # Esto ocurre si el XML se obtuvo pero está vacío o mal formado.
            self.view.show_warning_message("No hay datos",
                                  "No se encontraron llamadas en el historial o hubo un problema al parsear el XML."
                                  "\nVerifica que el archivo XML en el dispositivo esté bien formado y contenga datos.",
                                  show_popup=True) # <-- Mostrar este mensaje como popup
            return

        self._all_call_data = parsed_calls # Guardar los datos completos y originales
        self._display_filtered_data(self._all_call_data) # Mostrar todos los datos inicialmente

        # Mensaje de carga completa discreto (solo en consola)
        self.view.show_info_message("Carga Completa",
                               f"Se cargaron {len(self._all_call_data)} llamadas desde el dispositivo.",
                               show_popup=False)


    def filter_call_logs(self):
        search_term = self.view.get_search_term().lower().strip()

        if not self._all_call_data:
            # No mostrar warning box si no hay datos y se intenta filtrar.
            # Simplemente la tabla estará vacía o no cambiará.
            self._display_filtered_data([])
            return

        if not search_term:
            self._display_filtered_data(self._all_call_data)
            return

        filtered_calls = [
            call for call in self._all_call_data
            if search_term in call.get('Nombre', '').lower() or
               search_term in call.get('Número', '').lower() or
               search_term in call.get('Tipo de Llamada', '').lower()
        ]
        self._display_filtered_data(filtered_calls)

    def _display_filtered_data(self, data_to_display):
        column_order = ['Nombre', 'Número', 'Duración', 'Fecha y Hora', 'Tipo de Llamada']
        self.view.set_table_data(data_to_display, column_order)

    def export_pdf(self):
        self.view.export_to_pdf()

    def export_excel(self):
        self.view.export_to_excel()
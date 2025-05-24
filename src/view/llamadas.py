import sys
import subprocess
import xml.etree.ElementTree as ET
import datetime # Necesario para parsear las fechas

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt

# Asegúrate de que 'AppScreen' esté correctamente importada desde '.screen'
# Si AppScreen está en el mismo archivo, simplemente comenta o elimina esta línea y asegúrate de que AppScreen
# esté definida antes de crear_pantalla_llamadas.
# Si AppScreen es una clase base simple, aquí hay un ejemplo básico si no la tienes definida:
# class AppScreen(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.titulo = QLabel("Título de la Pantalla")
#         self.contenido = QWidget() # Contenedor para el contenido principal
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.titulo)
#         layout.addWidget(self.contenido)
#         self.contenido.setLayout(QVBoxLayout()) # Establecer un layout para el contenido

from .screen import AppScreen # Mantengo tu import original

# --- Configuración de ADB y Rutas de Archivos ---
# Asegúrate de que adb.exe esté en tu PATH del sistema,
# o especifica la ruta completa a adb.exe (ej: r"C:\platform-tools\adb.exe")
ADB_COMMAND = "adb"

# Nombre del archivo XML en tu celular (¡Usa el nombre exacto de TU archivo!)
CALL_LOG_FILENAME = "calls-20250523211835.xml"
# Ruta en el almacenamiento interno de tu celular donde está el archivo
CALL_LOG_PATH_ON_DEVICE = f"/sdcard/extraer/{CALL_LOG_FILENAME}"

# --- Funciones para ADB y Parseo XML ---
def get_call_log_xml_from_device():
    """
    Ejecuta el comando ADB para obtener el contenido XML del historial de llamadas
    directamente desde el dispositivo.
    """
    try:
        command = [ADB_COMMAND, "shell", "cat", CALL_LOG_PATH_ON_DEVICE]
        # print(f"Ejecutando comando ADB: {' '.join(command)}") # Para depuración
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', timeout=60) # Añadir timeout

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error ADB (código {result.returncode}): {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando ADB: {e}")
        print(f"Salida de error: {e.stderr}")
        # Retornar None para indicar fallo en la UI
        return None
    except FileNotFoundError:
        print(f"Error: '{ADB_COMMAND}' no encontrado. Asegúrate de que ADB esté en tu PATH o especifica la ruta completa a adb.exe.")
        return None
    except subprocess.TimeoutExpired:
        print("El comando ADB tardó demasiado en responder y se ha cancelado.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al obtener XML de ADB: {e}")
        return None

def parse_call_log_xml(xml_string):
    """
    Parse un string XML del historial de llamadas y extrae los datos relevantes.
    """
    calls_list = []
    if not xml_string:
        return calls_list # Retorna lista vacía si no hay XML

    try:
        root = ET.fromstring(xml_string)
        for call_element in root.findall('call'):
            number = call_element.get('number', 'N/A')
            # Si contact_name no existe o está vacío, usa el número
            name = call_element.get('contact_name')
            if not name:
                name = number
            else:
                name = name.strip() # Limpiar espacios en blanco

            duration_seconds = int(call_element.get('duration', '0'))
            duration_minutes = duration_seconds // 60
            duration_remaining_seconds = duration_seconds % 60
            duration_formatted = f"{duration_minutes}m {duration_remaining_seconds}s"

            # El timestamp 'date' está en milisegundos desde la época (epoch)
            timestamp_ms = int(call_element.get('date', '0'))
            # Convertir a segundos antes de crear el objeto datetime
            call_datetime = datetime.datetime.fromtimestamp(timestamp_ms / 1000)

            # Formato de fecha y hora legible
            call_time = call_datetime.strftime('%Y-%m-%d %H:%M:%S')

            # Tipo de llamada: 1=entrante, 2=saliente, 3=perdida, 4=buzón, 5=rechazada, 6=bloqueada
            call_type_code = int(call_element.get('type', '0'))
            call_type_map = {
                1: 'Entrante',
                2: 'Saliente',
                3: 'Perdida',
                4: 'Buzón de voz',
                5: 'Rechazada',
                6: 'Bloqueada',
                # Otros tipos que puedan aparecer en algunas versiones de Android/app
                7: 'Respondida corta',
                8: 'Llamada de vuelta',
                9: 'Reenviada',
                0: 'Desconocido'
            }
            call_type = call_type_map.get(call_type_code, f'Tipo {call_type_code}')

            calls_list.append({
                'Nombre': name,
                'Número': number,
                'Duración': duration_formatted,
                'Fecha y Hora': call_time,
                'Tipo de Llamada': call_type
            })
    except ET.ParseError as e:
        print(f"Error al parsear el XML: {e}")
        # Puedes mostrar un QMessageBox aquí en la UI si lo deseas
    except Exception as e:
        print(f"Ocurrió un error inesperado al parsear el XML: {e}")
        # Puedes mostrar un QMessageBox aquí en la UI si lo deseas
    return calls_list

# --- Función para cargar datos en la tabla (se llamará al hacer clic en el botón) ---
def load_call_logs_into_table(table_widget, parent_window):
    table_widget.setRowCount(0) # Limpiar tabla antes de cargar nuevos datos

    # 1. Obtener XML del dispositivo usando ADB
    xml_data = get_call_log_xml_from_device()

    if not xml_data:
        # El error ya se imprimió en la consola desde get_call_log_xml_from_device
        QMessageBox.critical(parent_window, "Error de ADB",
                             "No se pudo obtener el historial de llamadas del dispositivo. "
                             "Asegúrate de que el celular esté conectado, la depuración USB activada, "
                             "y que la APK haya guardado el archivo en la ruta esperada. "
                             "Revisa la consola (donde ejecutas Python) para más detalles de ADB.")
        return

    # 2. Parsear el XML
    parsed_calls = parse_call_log_xml(xml_data)

    if not parsed_calls:
        QMessageBox.warning(parent_window, "No hay datos", "No se encontraron llamadas en el historial o hubo un problema al parsear el XML.")
        return

    # 3. Llenar la tabla
    table_widget.setRowCount(len(parsed_calls))
    # Definir el orden de las columnas que queremos mostrar
    column_order = ['Nombre', 'Número', 'Duración', 'Fecha y Hora', 'Tipo de Llamada']
    table_widget.setColumnCount(len(column_order))
    table_widget.setHorizontalHeaderLabels(column_order)


    for row_idx, call_data in enumerate(parsed_calls):
        for col_idx, col_name in enumerate(column_order):
            item = QTableWidgetItem(str(call_data.get(col_name, '')))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Hacer las celdas no editables
            table_widget.setItem(row_idx, col_idx, item)

    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    table_widget.horizontalHeader().setStretchLastSection(True) # Para que la última columna use el espacio restante
    QMessageBox.information(parent_window, "Carga Completa", f"Se cargaron {len(parsed_calls)} llamadas desde el dispositivo.")


# --- Función principal para crear la pantalla de llamadas ---
def crear_pantalla_llamadas(parent):
    pantalla_llamadas = AppScreen(parent)
    pantalla_llamadas.titulo.setText("Historial de Llamadas del Dispositivo")

    contenido_layout = QVBoxLayout(pantalla_llamadas.contenido)

    # Botón para cargar datos
    # Le pasamos la referencia a la tabla y a la ventana padre para los QMessageBox
    load_button = QPushButton("Obtener y Mostrar Historial de Llamadas")
    load_button.clicked.connect(lambda: load_call_logs_into_table(pantalla_llamadas.table_widget, parent))
    contenido_layout.addWidget(load_button)

    # Tabla para mostrar los datos
    # Asumiendo que AppScreen no tiene una QTableWidget predefinida, la creamos aquí
    pantalla_llamadas.table_widget = QTableWidget()
    pantalla_llamadas.table_widget.setColumnCount(5) # Nombre, Número, Duración, Fecha y Hora, Tipo de Llamada
    pantalla_llamadas.table_widget.setHorizontalHeaderLabels([
        "Nombre", "Número", "Duración", "Fecha y Hora", "Tipo de Llamada"
    ])
    pantalla_llamadas.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    pantalla_llamadas.table_widget.horizontalHeader().setStretchLastSection(True)
    contenido_layout.addWidget(pantalla_llamadas.table_widget)

    return pantalla_llamadas

# --- Bloque para ejecutar la aplicación si este es el script principal ---
if __name__ == "__main__":
    # Esto es solo un ejemplo si quieres probar esta pantalla de forma independiente
    # Si tu aplicación principal ya tiene un QApplication, no lo crees aquí de nuevo.
    app = QApplication(sys.argv)

    # Mini AppScreen de ejemplo si no tienes el archivo .screen
    class MockAppScreen(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.titulo = QLabel("Título de la Pantalla")
            self.contenido = QWidget()
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.titulo)
            main_layout.addWidget(self.contenido)
            self.contenido.setLayout(QVBoxLayout()) # Importante para que el layout interno funcione

    # Crea una instancia de tu ventana principal (o la MockAppScreen para probar)
    main_window = MockAppScreen() # O tu clase principal si tienes una
    # Llama a la función para crear la pantalla de llamadas y añádela a tu ventana principal
    call_screen = crear_pantalla_llamadas(main_window)

    main_window.contenido.layout().addWidget(call_screen)
    main_window.setWindowTitle("Aplicación de Historial de Llamadas (Prueba)")
    main_window.setGeometry(100, 100, 900, 700)
    main_window.show()

    sys.exit(app.exec())

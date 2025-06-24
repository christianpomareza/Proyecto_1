import sys
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
import re

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox,
    QFileDialog, QSizePolicy, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# --- Hilo para la operación ADB (para no congelar la interfaz) ---
class AdbPullThread(QThread):
    finished = pyqtSignal(str, str, str) # Signal to emit (status, message, path_to_load)
    progress = pyqtSignal(str) # Signal to emit progress updates

    def __init__(self, adb_path, device_base_path, local_target_dir):
        super().__init__()
        self.adb_path = adb_path
        self.device_base_path = device_base_path
        self.local_target_dir = local_target_dir

    def run(self):
        try:
            self.progress.emit("Buscando archivos SMS en el dispositivo...")
            
            if not self.device_base_path.endswith('/'):
                self.device_base_path += '/'

            ls_command = [self.adb_path, 'shell', f'ls -1 {self.device_base_path}sms-*.xml']
            ls_process = subprocess.run(ls_command, capture_output=True, text=True, check=True,
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                        timeout=30)

            output_lines = ls_process.stdout.strip().split('\n')
            
            recent_file_on_device = None
            max_timestamp_value = -1

            filename_regex = re.compile(r'sms-(\d{14})\.xml$')

            for line in output_lines:
                full_device_path = line.strip()
                if not full_device_path:
                    continue

                filename = os.path.basename(full_device_path)
                match = filename_regex.search(filename)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        current_timestamp_value = int(timestamp_str)
                        
                        if current_timestamp_value > max_timestamp_value:
                            max_timestamp_value = current_timestamp_value
                            recent_file_on_device = full_device_path
                            
                    except ValueError:
                        continue

            if not recent_file_on_device:
                self.finished.emit("error", f"No se encontraron archivos SMS válidos (sms-YYYYMMDDHHMMSS.xml) en:\n{self.device_base_path}", "")
                return

            recent_filename = os.path.basename(recent_file_on_device)
            self.progress.emit(f"Archivo SMS más reciente encontrado: {recent_filename}. Extrayendo...")

            target_local_path = os.path.join(self.local_target_dir, recent_filename)
            pull_command = [self.adb_path, 'pull', recent_file_on_device, target_local_path]
            pull_process = subprocess.run(pull_command, capture_output=True, text=True, check=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                          timeout=60)

            if pull_process.returncode == 0:
                self.finished.emit("success", f"Archivo extraído exitosamente a:\n{target_local_path}", target_local_path)
            else:
                self.finished.emit("error", f"Fallo al extraer el archivo:\n{pull_process.stderr}", "")

        except FileNotFoundError:
            self.finished.emit("error", f"ADB no encontrado en la ruta especificada: '{self.adb_path}'.", "")
        except subprocess.TimeoutExpired:
             self.finished.emit("error", "El comando ADB excedió el tiempo límite. Asegúrate de que el dispositivo esté conectado y la depuración USB activada.", "")
        except subprocess.CalledProcessError as e:
            if "No such file or directory" in e.stderr or "Permission denied" in e.stderr:
                self.finished.emit("error", f"La ruta de la carpeta en el celular no existe o no tiene permisos: '{self.device_base_path}'.\nDetalles: {e.stderr}", "")
            else:
                self.finished.emit("error", f"Error al ejecutar el comando ADB:\n{e.stderr}", "")
        except Exception as e:
            self.finished.emit("error", f"Ocurrió un error inesperado durante la extracción:\n{e}", "")

# --- Clase Principal de la Aplicación ---
class SMSViewerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.adb_thread = None
        self.progress_dialog = None

    def initUI(self):
        self.setWindowTitle("Visor de Mensajes SMS/MMS (PyQt6)")
        self.setGeometry(100, 100, 900, 700)

        # --- Aplicar estilos CSS a la ventana principal ---
        # Paleta de colores más suave y moderna
        self.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA; /* Blanco muy suave, casi gris claro */
                color: #343A40; /* Gris oscuro para el texto principal */
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }
            QLabel {
                color: #495057; /* Gris un poco más claro para etiquetas */
                padding-left: 5px;
            }
            QLineEdit {
                background-color: #FFFFFF; /* Blanco puro para campos de texto */
                border: 1px solid #CED4DA; /* Borde gris claro */
                border-radius: 6px; /* Más redondeado */
                padding: 8px; /* Más padding */
                color: #343A40;
            }
            QPushButton {
                background-color: #007BFF; /* Azul suave (podemos cambiarlo) */
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px; /* Más padding */
                font-weight: bold;
                transition: background-color 0.2s ease; /* Transición suave al pasar el ratón */
            }
            QPushButton:hover {
                background-color: #0056b3; /* Azul un poco más oscuro al pasar el ratón */
            }
            QPushButton:pressed {
                background-color: #004085; /* Azul aún más oscuro al presionar */
            }
            QTextEdit {
                background-color: #E9ECEF; /* Gris muy claro para el área de mensajes */
                border: 1px solid #DEE2E6; /* Borde suave */
                border-radius: 8px; /* Más redondeado */
                padding: 10px;
                color: #343A40; /* Texto oscuro */
            }
            QMessageBox {
                background-color: #FFFFFF;
                color: #343A40;
            }
            QProgressDialog {
                background-color: #FFFFFF;
                color: #343A40;
            }
            /* Estilos específicos para QLineEdit que son solo rutas para que se vean un poco diferente */
            #entry_adb_path, #entry_device_base_path, #entry_local_folder {
                font-family: 'Consolas', 'Courier New', monospace; /* Fuente monoespaciada para rutas */
                font-size: 9pt;
            }
        """)


        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- Sección de ADB ---
        adb_layout = QHBoxLayout()
        main_layout.addLayout(adb_layout)

        self.label_adb_path = QLabel("Ruta ADB:")
        adb_layout.addWidget(self.label_adb_path)

        self.entry_adb_path = QLineEdit()
        self.entry_adb_path.setObjectName("entry_adb_path") # Asignar un ID para CSS
        self.entry_adb_path.setText(self.find_adb_path())
        adb_layout.addWidget(self.entry_adb_path)

        self.label_device_base_path = QLabel("Carpeta XML en Celular:")
        adb_layout.addWidget(self.label_device_base_path)

        self.entry_device_base_path = QLineEdit()
        self.entry_device_base_path.setObjectName("entry_device_base_path") # Asignar un ID para CSS
        self.entry_device_base_path.setPlaceholderText("/storage/emulated/0/extraer/")
        self.entry_device_base_path.setText("/storage/emulated/0/extraer/")
        adb_layout.addWidget(self.entry_device_base_path)

        self.btn_pull_adb = QPushButton("Extraer XML más Reciente con ADB")
        self.btn_pull_adb.clicked.connect(self.pull_most_recent_xml_with_adb)
        adb_layout.addWidget(self.btn_pull_adb)

        # --- Sección de Carga de Archivo Local ---
        file_layout = QHBoxLayout()
        main_layout.addLayout(file_layout)

        self.label_local_folder = QLabel("Carpeta Local de XMLs:")
        file_layout.addWidget(self.label_local_folder)

        self.entry_local_folder = QLineEdit(os.getcwd())
        self.entry_local_folder.setObjectName("entry_local_folder") # Asignar un ID para CSS
        file_layout.addWidget(self.entry_local_folder)

        self.btn_browse_local_folder = QPushButton("Buscar Carpeta")
        self.btn_browse_local_folder.clicked.connect(self.browse_local_folder)
        file_layout.addWidget(self.btn_browse_local_folder)

        self.btn_load_most_recent_local = QPushButton("Cargar XML más Reciente Local")
        self.btn_load_most_recent_local.clicked.connect(self.load_most_recent_local_xml)
        file_layout.addWidget(self.btn_load_most_recent_local)


        # --- Área de Visualización de Mensajes ---
        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        # Los estilos CSS del QWidget principal se aplican aquí, pero podemos sobreescribir específicos
        main_layout.addWidget(self.messages_display)


    def find_adb_path(self):
        """Intenta encontrar la ruta de ADB si está en el PATH del sistema."""
        try:
            process = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                                     timeout=5)
            if "daemon not running" in process.stderr or "List of devices attached" in process.stdout:
                return "adb"
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return ""
        return ""

    def browse_local_folder(self):
        """Permite al usuario seleccionar una carpeta local para buscar XMLs."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta con Archivos XML", self.entry_local_folder.text()
        )
        if folder_path:
            self.entry_local_folder.setText(folder_path)
            self.load_most_recent_local_xml()

    def find_most_recent_sms_xml(self, directory):
        """Busca el archivo sms-YYYYMMDDHHMMSS.xml más reciente en un directorio dado."""
        if not os.path.isdir(directory):
            return None

        recent_file = None
        max_timestamp_value = -1
        filename_regex = re.compile(r'sms-(\d{14})\.xml$')

        for filename in os.listdir(directory):
            match = filename_regex.search(filename)
            if match:
                timestamp_str = match.group(1)
                try:
                    current_timestamp_value = int(timestamp_str)
                    if current_timestamp_value > max_timestamp_value:
                        max_timestamp_value = current_timestamp_value
                        recent_file = os.path.join(directory, filename)
                except ValueError:
                    continue

        return recent_file

    def load_most_recent_local_xml(self):
        """Carga y muestra el archivo SMS XML más reciente de la carpeta local especificada."""
        local_folder = self.entry_local_folder.text().strip()
        if not local_folder:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una carpeta local.")
            return

        recent_xml_path = self.find_most_recent_sms_xml(local_folder)

        if recent_xml_path:
            QMessageBox.information(self, "Archivo Encontrado", f"Cargando el archivo local más reciente:\n{os.path.basename(recent_xml_path)}")
            self.load_and_display_messages(recent_xml_path)
        else:
            QMessageBox.warning(self, "No Encontrado", f"No se encontró ningún archivo SMS XML (sms-YYYYMMDDHHMMSS.xml) en:\n{local_folder}")
            self.update_messages_display(f"<p style='color: #DC3545;'>No se encontró ningún archivo SMS XML en '{local_folder}'.</p>", clear=True) # Rojo para error

    def pull_most_recent_xml_with_adb(self):
        """Inicia la extracción del archivo XML más reciente del dispositivo Android usando ADB."""
        adb_path = self.entry_adb_path.text().strip()
        device_base_path = self.entry_device_base_path.text().strip()

        if not adb_path:
            QMessageBox.critical(self, "Error ADB", "Por favor, especifica la ruta a ADB (ej. 'adb' si está en PATH, o la ruta completa).")
            return
        if not device_base_path:
            QMessageBox.critical(self, "Error ADB", "Por favor, ingresa la ruta de la CARPETA donde están los XML en el celular (ej. /storage/emulated/0/extraer/).")
            return

        local_target_dir = os.getcwd()

        self.progress_dialog = QProgressDialog("Buscando y extrayendo archivo SMS...", "Cancelar", 0, 0, self)
        self.progress_dialog.setWindowTitle("Progreso ADB")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setCancelButton(None)

        self.adb_thread = AdbPullThread(adb_path, device_base_path, local_target_dir)
        self.adb_thread.finished.connect(self.handle_adb_pull_finished)
        self.adb_thread.progress.connect(self.progress_dialog.setLabelText)
        self.adb_thread.start()
        self.progress_dialog.show()

    def handle_adb_pull_finished(self, status, message, path_to_load):
        """Maneja el resultado de la operación ADB."""
        if self.progress_dialog:
            self.progress_dialog.close()

        if status == "success":
            QMessageBox.information(self, "Éxito ADB", message)
            self.entry_local_folder.setText(os.path.dirname(path_to_load))
            self.load_and_display_messages(path_to_load)
        else:
            QMessageBox.critical(self, "Error ADB", message)
            self.update_messages_display(f"<p style='color: #DC3545;'>Error: {message}</p>", clear=True)

    def load_and_display_messages(self, xml_file_path):
        """Carga y muestra los mensajes desde el archivo XML."""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            messages = []
            
            for sms in root.findall('sms'):
                msg_type = sms.get('type')
                address = sms.get('address')
                body = sms.get('body')
                timestamp_ms = sms.get('date')
                readable_date = sms.get('readable_date')
                contact_name = sms.get('contact_name')

                timestamp_int = 0
                if timestamp_ms:
                    try:
                        timestamp_int = int(timestamp_ms)
                    except ValueError:
                        pass

                if not readable_date and timestamp_int > 0:
                    try:
                        dt_object = datetime.fromtimestamp(timestamp_int / 1000)
                        readable_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        readable_date = "Fecha/Hora no disponible"
                elif not readable_date:
                    readable_date = "Fecha/Hora no disponible"


                messages.append({
                    'type': msg_type,
                    'address': address,
                    'body': body if body else "[Mensaje vacío]",
                    'timestamp': timestamp_int,
                    'readable_date': readable_date,
                    'contact_name': contact_name
                })

            messages.sort(key=lambda x: x['timestamp'])

            html_content = []

            # --- Estilos CSS para las burbujas de chat ---
            html_content.append("""
                <style>
                    body {
                        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                        background-color: #E9ECEF; /* Fondo del área de mensajes, un gris muy claro */
                        color: #343A40;
                        margin: 0;
                        padding: 10px;
                    }
                    .message-bubble {
                        max-width: 70%; /* Las burbujas no ocupan todo el ancho */
                        padding: 10px 15px;
                        border-radius: 18px; /* Más redondeado para un look moderno */
                        margin-bottom: 12px;
                        word-wrap: break-word; /* Para mensajes largos */
                        box-shadow: 0 1px 1px rgba(0,0,0,0.1); /* Sombra sutil */
                        line-height: 1.4;
                    }
                    .sender-bubble {
                        background-color: #DCF8C6; /* Verde pastel claro (WhatsApp like) */
                        float: right; /* Alineado a la derecha */
                        margin-left: auto; /* Empuja a la derecha */
                        clear: both; /* Asegura que no flote al lado de la anterior */
                    }
                    .receiver-bubble {
                        background-color: #FFFFFF; /* Blanco puro para recibidos */
                        float: left; /* Alineado a la izquierda */
                        margin-right: auto; /* Empuja a la izquierda */
                        clear: both;
                        border: 1px solid #E0E0E0; /* Borde sutil */
                    }
                    .info-text {
                        font-weight: bold;
                        color: #6C757D; /* Gris medio para el nombre/número */
                        font-size: 0.85em;
                        margin-bottom: 3px;
                    }
                    .message-text {
                        color: #343A40; /* Gris oscuro para el cuerpo del mensaje */
                        font-size: 1em;
                        margin-top: 0;
                        margin-bottom: 5px;
                    }
                    .timestamp-text {
                        font-size: 0.7em;
                        color: #ADB5BD; /* Gris muy claro para la marca de tiempo */
                        text-align: right; /* La hora alineada a la derecha dentro de la burbuja */
                        margin-top: 5px;
                    }
                    .sender-bubble .timestamp-text {
                        text-align: right;
                    }
                    .receiver-bubble .timestamp-text {
                        text-align: left;
                    }
                    .clear-float {
                        clear: both; /* Para asegurar que el siguiente elemento no flote */
                        height: 0; /* No ocupa espacio visible */
                    }
                </style>
            """)

            for msg in messages:
                message_text = msg['body']
                contact_display_name = msg['contact_name'] if msg['contact_name'] else msg['address']

                if msg['type'] == '1': # Recibido (INBOX)
                    html_content.append(f"<div class='message-bubble receiver-bubble'>")
                    html_content.append(f"<p class='info-text'>{contact_display_name}</p>")
                    html_content.append(f"<p class='message-text'>{message_text}</p>")
                    html_content.append(f"<p class='timestamp-text'>{msg['readable_date']}</p>")
                    html_content.append("</div>")
                    html_content.append("<div class='clear-float'></div>") # Limpia el float
                elif msg['type'] == '2': # Enviado (SENT)
                    html_content.append(f"<div class='message-bubble sender-bubble'>")
                    html_content.append(f"<p class='info-text'>Tú (a {contact_display_name})</p>")
                    html_content.append(f"<p class='message-text'>{message_text}</p>")
                    html_content.append(f"<p class='timestamp-text'>{msg['readable_date']}</p>")
                    html_content.append("</div>")
                    html_content.append("<div class='clear-float'></div>") # Limpia el float
                else:
                    # Otros tipos de mensajes o desconocidos
                    html_content.append(f"<div class='message-bubble' style='background-color: #E0E0E0;'>") # Gris neutro
                    html_content.append(f"<p class='info-text'>Tipo: {msg['type']} (Dirección: {msg['address']})</p>")
                    html_content.append(f"<p class='message-text'>{message_text}</p>")
                    html_content.append(f"<p class='timestamp-text'>{msg['readable_date']}</p>")
                    html_content.append("</div>")
                    html_content.append("<div class='clear-float'></div>")

            self.messages_display.setHtml("".join(html_content))
            # Asegurarse de que el scroll esté al final para ver los últimos mensajes
            self.messages_display.verticalScrollBar().setValue(self.messages_display.verticalScrollBar().maximum())


        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Archivo no encontrado: {xml_file_path}")
            self.messages_display.clear()
            self.messages_display.append(f"<p style='color: #DC3545;'>Error: Archivo no encontrado en '{xml_file_path}'</p>")
        except ET.ParseError:
            QMessageBox.critical(self, "Error XML", "Error al parsear el archivo XML. Asegúrate de que sea un XML válido.")
            self.messages_display.clear()
            self.messages_display.append("<p style='color: #DC3545;'>Error: El archivo no es un XML válido o tiene un formato inesperado.</p>")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado al cargar los mensajes:\n{e}")
            self.messages_display.clear()
            self.messages_display.append(f"<p style='color: #DC3545;'>Error inesperado al cargar: {e}</p>")

    def update_messages_display(self, text, clear=False):
        """Actualiza el área de texto de mensajes con HTML si es necesario."""
        if clear:
            self.messages_display.clear()
        self.messages_display.append(text)

# --- Ejecutar la aplicación ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SMSViewerApp()
    ex.show()
    sys.exit(app.exec())
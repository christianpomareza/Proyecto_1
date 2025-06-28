import sys
import os
import zipfile
import re
import shutil
import time

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QFileDialog, QScrollArea,
                             QLabel, QFrame, QMessageBox, QListWidget, QListWidgetItem,
                             QStackedWidget, QSizePolicy, QScrollBar, QLineEdit,
                             QDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QSize
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices

# Intentar importar rarfile. Si falla, el soporte para .rar no estará disponible.
try:
    import rarfile
    RAR_SUPPORT = True
except ImportError:
    RAR_SUPPORT = False
    print("Advertencia: 'rarfile' no encontrado. No se podrá abrir archivos .rar directamente.")
    print("Para añadir soporte .rar, instala: pip install rarfile")
    print("Y asegúrate de tener la herramienta 'unrar' instalada en tu sistema (ej: brew install unrar en macOS, sudo apt install unrar en Linux, o WinRAR/UnRAR.exe en Windows).")

# Regex para detectar adjuntos de WhatsApp
MEDIA_ATTACHMENT_PATTERN = re.compile(r'<adjunto:\s*([^>]+)>')

class ImageLoader(QThread):
    image_loaded = pyqtSignal(str, QPixmap, str)

    def __init__(self, image_path, target_size=None):
        super().__init__()
        self.image_path = image_path
        self.target_size = target_size if target_size else QSize(400, 400)

    def run(self):
        pixmap = QPixmap()
        error_msg = ""

        if not os.path.exists(self.image_path):
            error_msg = f"Archivo no encontrado: {os.path.basename(self.image_path)}"
            self.image_loaded.emit(self.image_path, pixmap, error_msg)
            return

        try:
            pixmap.load(self.image_path)

            if pixmap.isNull():
                error_msg = f"Error al cargar la imagen: {os.path.basename(self.image_path)}. Puede que el formato no sea compatible."
            else:
                pixmap = pixmap.scaled(self.target_size,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            error_msg = f"Excepción al procesar imagen {os.path.basename(self.image_path)}: {str(e)}"
            pixmap = QPixmap()

        self.image_loaded.emit(self.image_path, pixmap, error_msg)


class ChatParser(QThread):
    message_parsed = pyqtSignal(dict)
    parsing_finished = pyqtSignal()
    chat_info_parsed = pyqtSignal(str, str, str, str)

    def __init__(self, file_path, base_media_dir):
        super().__init__()
        self.file_path = file_path
        self.base_media_dir = base_media_dir

    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            lines = content.split('\n')

            file_name_without_ext = os.path.splitext(os.path.basename(self.file_path))[0]
            display_contact_name = file_name_without_ext
            your_name_in_chat = "Tú"

            sender_counts = {}
            for line in lines:
                if " - " in line and ":" in line and "Los mensajes y las llamadas están cifrados" not in line:
                    try:
                        sender_part = line.split(" - ")[1]
                        if ": " in sender_part:
                            sender = sender_part.split(":")[0].strip()
                            sender_counts[sender] = sender_counts.get(sender, 0) + 1
                    except IndexError:
                        continue

            sorted_senders = sorted(sender_counts.items(), key=lambda item: item[1], reverse=True)

            if sorted_senders:
                if len(sorted_senders) >= 2:
                    if sorted_senders[0][0] == file_name_without_ext:
                        your_name_in_chat = sorted_senders[1][0]
                    elif sorted_senders[1][0] == file_name_without_ext:
                        your_name_in_chat = sorted_senders[0][0]
                    else:
                        your_name_in_chat = sorted_senders[0][0]
                elif len(sorted_senders) == 1:
                    your_name_in_chat = sorted_senders[0][0]

            self.chat_info_parsed.emit(display_contact_name, your_name_in_chat, self.file_path, self.base_media_dir)

            for line in lines:
                line = line.strip()
                if not line or "Los mensajes y las llamadas están cifrados" in line:
                    continue

                if " - " in line and ":" in line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        datetime_part, msg_part = parts
                        if ": " in msg_part:
                            sender, message = msg_part.split(": ", 1)
                            date_str, time_str = datetime_part.split(", ")

                            time_24 = time_str.replace("a.m.", "").replace("p.m.", "").replace("a. m.", "").replace("p. m.", "").strip()
                            try:
                                hour, minute = map(int, time_24.split(":"))
                                if ("p.m." in time_str or "p. m." in time_str) and hour != 12:
                                    hour = hour % 12 + 12
                                elif ("a.m." in time_str or "a. m." in time_str) and hour == 12:
                                    hour = 0
                                time_24 = f"{hour:02d}:{minute:02d}"
                            except ValueError:
                                time_24 = time_str

                            message_data = {
                                'date': date_str,
                                'time': time_24,
                                'sender': sender.strip(),
                                'message': message.strip(),
                                'raw': line,
                                'message_type': 'text',
                                'media_filename': None
                            }

                            match = MEDIA_ATTACHMENT_PATTERN.search(message_data['message'])
                            if match:
                                media_filename_full = match.group(1).strip()
                                # --- MODIFICACIÓN CLAVE AQUÍ ---
                                # Limpiar caracteres invisibles o de control del nombre del archivo.
                                # Por ejemplo, eliminar Left-to-Right Mark (U+200E) y otros similares.
                                # El rango \u200b-\u200f incluye el LRM (U+200E).
                                media_filename_full = re.sub(r'[\u200e\u200f\u061c\u200b-\u200f\u202a-\u202e\u2066-\u2069]', '', media_filename_full).strip()
                                # -------------------------------

                                message_data['media_filename'] = media_filename_full
                                message_data['message_type'] = 'media'
                                message_data['message'] = message_data['message'].replace(match.group(0), '').strip()
                                if not message_data['message']:
                                    message_data['message'] = f"[{media_filename_full}]"

                            self.message_parsed.emit(message_data)

        except Exception as e:
            print(f"Error al parsear {self.file_path}: {str(e)}")

        self.parsing_finished.emit()

class SelectableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                   Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self._plain_text = text  # Almacena el texto plano
    
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        
        # Reemplazar la acción de copiar con una que copie texto plano
        for action in menu.actions():
            if action.text().lower() == "copiar" or action.text().lower() == "copy":
                menu.removeAction(action)
                break
                
        copy_action = menu.addAction("Copiar")
        copy_action.triggered.connect(self.copyPlainText)
        menu.exec(event.globalPos())
    
    def copyPlainText(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self._plain_text)

class MessageWidget(QFrame):
    def __init__(self, message_data, is_own_message=False, base_media_dir=None):
        super().__init__()
        self.message_data = message_data
        self.is_own_message = is_own_message
        self.base_media_dir = base_media_dir
        self.full_media_path = None
        self.image_loader_thread = None

        self.image_display_container = None
        self.filename_label = None
        self.image_preview_label = None

        self.setup_ui()

    def setup_ui(self):
        self.setMaximumWidth(400)
        # Cambia el fondo de los mensajes enviados a verde claro y los recibidos a blanco
        if self.is_own_message:
            self.setStyleSheet("""
                QFrame {
                    background-color: #D4F8E8;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                    border: 1px solid #B2DFDB;
                    color: #222;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 2px;
                    border: 1px solid #E0E0E0;
                    color: #222;
                }
            """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        if self.message_data['message_type'] == 'text':
            msg_label = SelectableLabel(self.message_data['message'])
            msg_label.setWordWrap(True)
            msg_label.setStyleSheet("font-size: 14px;")
            msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                    Qt.TextInteractionFlag.TextSelectableByKeyboard)
            msg_label.setProperty("text", self.message_data['message'])  # Almacenar texto plano
            layout.addWidget(msg_label)
        elif self.message_data['message_type'] == 'media':
            media_filename = self.message_data['media_filename']

            found_path = None
            # Search for the media file within the chat's specific media directory
            # This is more efficient than os.walk starting from a high level.
            if self.base_media_dir:
                for root, _, files in os.walk(self.base_media_dir):
                    if media_filename in files:
                        found_path = os.path.join(root, media_filename)
                        break

            self.full_media_path = found_path

            if self.full_media_path and os.path.exists(self.full_media_path):
                file_extension = os.path.splitext(media_filename)[1].lower()

                if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    self.image_display_container = QStackedWidget()
                    self.image_display_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

                    self.filename_label = QLabel(f'<u>🖼️ {media_filename}</u>')
                    self.filename_label.setToolTip("Haz clic para ver/ocultar la imagen")
                    self.filename_label.setCursor(Qt.CursorShape.PointingHandCursor)
                    self.filename_label.setStyleSheet("color: blue; font-size: 13px; font-style: italic;")
                    self.filename_label.mousePressEvent = self.show_image_in_place
                    self.image_display_container.addWidget(self.filename_label)

                    self.image_preview_label = QLabel("Cargando imagen...")
                    self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.image_preview_label.setStyleSheet("color: #999; font-style: italic; background-color: #F0F0F0; border-radius: 5px; min-width: 100px; min-height: 100px;")
                    self.image_preview_label.setToolTip("Haz clic para ocultar la imagen")
                    self.image_preview_label.setCursor(Qt.CursorShape.PointingHandCursor)
                    self.image_preview_label.mousePressEvent = self.hide_image_in_place
                    self.image_display_container.addWidget(self.image_preview_label)

                    self.image_display_container.setCurrentWidget(self.filename_label)
                    layout.addWidget(self.image_display_container)

                elif file_extension in ['.mp4', '.avi', '.mov', '.3gp', '.mkv']:
                    video_link = QLabel(f'<a href="{self.full_media_path}" style="color: blue;">▶️ {media_filename}</a>')
                    video_link.setOpenExternalLinks(True)
                    video_link.setToolTip(f"Haz clic para abrir '{media_filename}' con la aplicación predeterminada")
                    layout.addWidget(video_link)
                elif file_extension in ['.mp3', '.aac', '.ogg', '.opus']:
                    audio_link = QLabel(f'<a href="{self.full_media_path}" style="color: blue;">🎵 {media_filename}</a>')
                    audio_link.setOpenExternalLinks(True)
                    audio_link.setToolTip(f"Haz clic para abrir '{media_filename}' con la aplicación predeterminada")
                    layout.addWidget(audio_link)
                else:
                    doc_link = QLabel(f'<a href="{self.full_media_path}" style="color: blue;">📄 {media_filename}</a>')
                    doc_link.setOpenExternalLinks(True)
                    doc_link.setToolTip(f"Haz clic para abrir '{media_filename}' con la aplicación predeterminada")
                    layout.addWidget(doc_link)

                if self.message_data['message'] and self.message_data['message'] != f"[{media_filename}]":
                    msg_label = SelectableLabel(self.message_data['message'])
                    msg_label.setWordWrap(True)
                    msg_label.setStyleSheet("font-size: 14px;")
                    msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                        Qt.TextInteractionFlag.TextSelectableByKeyboard)
                    msg_label.setProperty("text", self.message_data['message'])  # Almacenar texto plano
                    layout.addWidget(msg_label)

            else:
                msg_label = QLabel(f"Archivo adjunto no encontrado: {media_filename}")
                msg_label.setStyleSheet("color: red; font-size: 12px;")
                msg_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                Qt.TextInteractionFlag.TextSelectableByKeyboard)
                msg_label.setProperty("text", f"Archivo adjunto no encontrado: {media_filename}")
                layout.addWidget(msg_label)
            if self.message_data['message']:
                msg_label_orig = QLabel(self.message_data['message'])
                msg_label_orig.setWordWrap(True)
                msg_label_orig.setStyleSheet("font-size: 14px;")
                msg_label_orig.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                          Qt.TextInteractionFlag.TextSelectableByKeyboard)
                msg_label_orig.setProperty("text", self.message_data['message'])
                layout.addWidget(msg_label_orig)

        time_layout = QHBoxLayout()
        time_layout.addStretch()

        time_label = QLabel(self.message_data['time'])
        time_label.setStyleSheet("font-size: 11px; color: #666666;")
        time_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | 
                                 Qt.TextInteractionFlag.TextSelectableByKeyboard)
        time_label.setProperty("text", self.message_data['time'])
        time_layout.addWidget(time_label)

        if self.is_own_message:
            checks = QLabel("✓✓")
            checks.setStyleSheet("color: #4FC3F7; font-size: 11px;")
            time_layout.addWidget(checks)

        layout.addLayout(time_layout)

    def show_image_in_place(self, event=None):
        if self.image_display_container and self.image_preview_label and self.full_media_path and os.path.exists(self.full_media_path):
            self.image_display_container.setCurrentWidget(self.image_preview_label)
            self.image_preview_label.setText("Cargando imagen...")

            if self.image_loader_thread and self.image_loader_thread.isRunning():
                self.image_loader_thread.quit()
                self.image_loader_thread.wait()

            self.image_loader_thread = ImageLoader(self.full_media_path)
            self.image_loader_thread.image_loaded.connect(self.update_in_place_image)
            self.image_loader_thread.start()
        elif self.image_preview_label:
             self.image_preview_label.setText(f"Error: No se puede cargar {os.path.basename(self.full_media_path) if self.full_media_path else 'imagen'}.")
             self.image_display_container.setCurrentWidget(self.image_preview_label)

    def hide_image_in_place(self, event=None):
        if self.image_display_container and self.filename_label:
            if self.image_loader_thread and self.image_loader_thread.isRunning():
                self.image_loader_thread.quit()
                self.image_loader_thread.wait()
            self.image_display_container.setCurrentWidget(self.filename_label)
            self.image_preview_label.clear()


    def update_in_place_image(self, original_path, pixmap, error_msg):
        if not pixmap.isNull():
            self.image_preview_label.setPixmap(pixmap)
            self.image_preview_label.setFixedSize(pixmap.size())
            self.image_preview_label.setText("")
            self.image_preview_label.setStyleSheet("")
            self.image_preview_label.setToolTip(f"Archivo: {os.path.basename(original_path)}\nHaz clic para ocultar")
            self.image_preview_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        else:
            self.image_preview_label.setText(f"Error al cargar: {error_msg}")
            self.image_preview_label.setStyleSheet("color: red; font-style: italic; background-color: #FFDDDD; border-radius: 5px;")
            self.image_preview_label.setFixedSize(200, 70)
            self.image_preview_label.setWordWrap(True)
            self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if self.image_display_container.currentWidget() != self.image_preview_label:
            self.image_display_container.setCurrentWidget(self.image_preview_label)


class ChatHeader(QWidget):
    # New signal for initiating a file search in the currently active chat's extracted archives
    file_search_requested = pyqtSignal(str)

    def __init__(self, contact_name=""):
        super().__init__()
        self.contact_name_label = QLabel(contact_name)
        self.search_bar_file = QLineEdit() # This is the search bar for files within the current chat
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #075E54;
                padding: 10px;
            }
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #128C7E;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.contact_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.contact_name_label, 1)

        # Search bar for *files* within the currently loaded chat's extracted content
        self.search_bar_file.setPlaceholderText("Buscar archivo en este chat...")
        self.search_bar_file.setClearButtonEnabled(True)
        # We connect to editingFinished, so search is triggered when user presses Enter or leaves the field
        self.search_bar_file.editingFinished.connect(self._on_file_search_editing_finished)
        layout.addWidget(self.search_bar_file, 1)

    def _on_file_search_editing_finished(self):
        search_term = self.search_bar_file.text().strip()
        if search_term:
            self.file_search_requested.emit(search_term) # Emit the new signal

    def set_contact_name(self, name):
        self.contact_name_label.setText(name)
        # Clear search bar when changing chat, as the search scope changes
        self.search_bar_file.clear()

# New class for file search results dialog
class FileSearchResultsDialog(QDialog):
    def __init__(self, search_term, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Resultados de búsqueda para: '{search_term}'")
        self.setGeometry(200, 200, 800, 500)

        layout = QVBoxLayout(self)

        if not results:
            no_results_label = QLabel("No se encontraron archivos que coincidan con la búsqueda en este chat.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_results_label)
        else:
            self.table_widget = QTableWidget()
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(["Nombre del archivo", "Ruta original (en el ZIP)", "Ubicación temporal"])
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.table_widget.doubleClicked.connect(self._open_selected_file) # Open on double click

            self.table_widget.setRowCount(len(results))
            for row_idx, result in enumerate(results):
                # result is (original_zip_path, extracted_full_path)
                file_name = os.path.basename(result[0])
                original_path_in_zip = result[0]
                temp_full_path = result[1]

                self.table_widget.setItem(row_idx, 0, QTableWidgetItem(file_name))
                self.table_widget.setItem(row_idx, 1, QTableWidgetItem(original_path_in_zip))
                self.table_widget.setItem(row_idx, 2, QTableWidgetItem(temp_full_path))

            layout.addWidget(self.table_widget)

            # Buttons for actions
            buttons_layout = QHBoxLayout()
            open_btn = QPushButton("Abrir Archivo")
            open_btn.clicked.connect(self._open_selected_file)

            open_folder_btn = QPushButton("Abrir Carpeta")
            open_folder_btn.clicked.connect(self._open_selected_folder)

            close_btn = QPushButton("Cerrar")
            close_btn.clicked.connect(self.accept)

            buttons_layout.addStretch()
            buttons_layout.addWidget(open_btn)
            buttons_layout.addWidget(open_folder_btn)
            buttons_layout.addWidget(close_btn)
            buttons_layout.addStretch()

            layout.addLayout(buttons_layout)

    def _get_selected_file_path(self):
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            temp_path_item = self.table_widget.item(row, 2)
            if temp_path_item:
                return temp_path_item.text()
        return None

    def _open_selected_file(self):
        file_path = self._get_selected_file_path()
        if file_path and os.path.exists(file_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            except Exception as e:
                QMessageBox.warning(self, "Error al abrir archivo", f"No se pudo abrir el archivo: {e}")
        else:
            QMessageBox.warning(self, "Archivo no encontrado", "Por favor, selecciona un archivo válido.")

    def _open_selected_folder(self):
        file_path = self._get_selected_file_path()
        if file_path and os.path.exists(file_path):
            folder_path = os.path.dirname(file_path)
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            except Exception as e:
                QMessageBox.warning(self, "Error al abrir carpeta", f"No se pudo abrir la carpeta: {e}")
        else:
            QMessageBox.warning(self, "Archivo no encontrado", "Por favor, selecciona un archivo válido.")


# New thread for searching files
class FileSearcher(QThread):
    search_completed = pyqtSignal(str, list) # search_term, list of (original_zip_path, extracted_full_path)

    def __init__(self, search_term, extracted_files_map_for_current_chat):
        super().__init__()
        # --- MODIFICACIÓN CLAVE AQUÍ ---
        # Limpiar caracteres invisibles o de control del término de búsqueda
        self.search_term = re.sub(r'[\u200e\u200f\u061c\u200b-\u200f\u202a-\u202e\u2066-\u2069]', '', search_term).strip().lower()
        # -------------------------------
        # This map now only contains files relevant to the current chat
        self.extracted_files_map = extracted_files_map_for_current_chat

    def run(self):
        results = []
        for original_zip_path, extracted_full_path in self.extracted_files_map.items():
            file_name = os.path.basename(original_zip_path).lower() # Search by filename
            # The file_name from original_zip_path also needs to be cleaned for a reliable comparison,
            # in case the original ZIP entry itself contains these characters (less common, but possible).
            # --- MODIFICACIÓN CLAVE AQUÍ (también se limpia el nombre de archivo del ZIP) ---
            cleaned_file_name = re.sub(r'[\u200e\u200f\u061c\u200b-\u200f\u202a-\u202e\u2066-\u2069]', '', file_name).strip()
            # ---------------------------------------------------------------------------------

            if self.search_term in cleaned_file_name: # Compare cleaned search term with cleaned filename
                results.append((original_zip_path, extracted_full_path))
        self.search_completed.emit(self.search_term, results)


class ChatViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chats = {} # Stores chat data and associated temp_media_dir
        self.current_chat_file_path = None
        self.parser_threads = []
        self.all_temp_dirs_created = []

        # New: Store extracted files specific to each chat's media directory
        # {chat_file_path: {original_zip_member_path: extracted_full_path_on_disk}}
        self.chat_extracted_files_map = {}
        self.file_searcher_thread = None # To hold the FileSearcher thread
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("WhatsApp Viewer")
        self.setGeometry(100, 100, 800, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)

        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)
        left_panel_layout.setContentsMargins(5, 5, 5, 5)
        left_panel_layout.setSpacing(5)

        self.import_zip_btn = QPushButton("📦 Importar chat(s) desde archivo comprimido")
        self.import_zip_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #222;
                border: 1px solid #d0d0d0;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.import_zip_btn.clicked.connect(self.import_compressed_dialog)
        left_panel_layout.addWidget(self.import_zip_btn)

        # --- Search Bar (Buscador de contactos) ---
        self.search_bar_contact = QLineEdit()
        self.search_bar_contact.setPlaceholderText("Buscar chats por nombre...")
        self.search_bar_contact.setClearButtonEnabled(True)
        self.search_bar_contact.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                font-size: 14px;
                background-color: #fff;
                color: #222;
            }
            QLineEdit:focus {
                border: 1.5px solid #128C7E;
            }
        """)
        self.search_bar_contact.textChanged.connect(self.filter_chat_list)
        left_panel_layout.addWidget(self.search_bar_contact)
        # --- End Search Bar (Buscador de contactos) ---

        self.chat_list_widget = QListWidget()
        self.chat_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                background-color: #FAFAFA;
                color: #222;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #EDEDED;
            }
            QListWidget::item:selected {
                background-color: #e0f7fa;
                color: #222;
            }
        """)
        self.chat_list_widget.itemClicked.connect(self.display_selected_chat)
        left_panel_layout.addWidget(self.chat_list_widget)

        main_h_layout.addWidget(left_panel_widget, 2)

        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(right_panel_widget)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)

        self.header = ChatHeader("")
        right_panel_layout.addWidget(self.header)
        self.header.file_search_requested.connect(self.start_file_search_for_current_chat)

        self.chat_stacked_widget = QStackedWidget()
        right_panel_layout.addWidget(self.chat_stacked_widget, 1)

        no_chat_selected_widget = QWidget()
        no_chat_layout = QVBoxLayout(no_chat_selected_widget)
        no_chat_label = QLabel("Selecciona un chat de la lista o impórtalo.")
        no_chat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_chat_label.setStyleSheet("color: #222; font-size: 16px; background-color: #fff;")
        no_chat_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # Hacer texto seleccionable
        no_chat_layout.addWidget(no_chat_label)
        self.chat_stacked_widget.addWidget(no_chat_selected_widget)

        main_h_layout.addWidget(right_panel_widget, 5)

        # Cambia el fondo general de la ventana principal y paneles
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #FFFFFF;
                color: #222;
            }
            QScrollArea {
                background: #F9F9F9;
            }
        """)

    def start_file_search_for_current_chat(self, search_term):
        if not self.current_chat_file_path:
            QMessageBox.information(self, "No hay chat seleccionado", "Por favor, selecciona un chat para buscar archivos en él.")
            return

        # Get the extracted files map specific to the current chat
        files_to_search = self.chat_extracted_files_map.get(self.current_chat_file_path, {})

        if not files_to_search:
            QMessageBox.information(self, "No hay archivos en este chat", "No se encontraron archivos extraídos para este chat.")
            return

        if self.file_searcher_thread and self.file_searcher_thread.isRunning():
            QMessageBox.warning(self, "Búsqueda en progreso", "Ya hay una búsqueda en curso. Por favor, espera a que termine.")
            return

        self.file_searcher_thread = FileSearcher(search_term, files_to_search)
        self.file_searcher_thread.search_completed.connect(self.show_file_search_results)
        self.file_searcher_thread.start()
        QMessageBox.information(self, "Buscando archivos...", f"Buscando '{search_term}' en los archivos de este chat. Esto puede tardar unos segundos...")

    def show_file_search_results(self, search_term, results):
        dialog = FileSearchResultsDialog(search_term, results, self)
        dialog.exec()

    def filter_chat_list(self, text):
        """Filters the chat list based on the search bar text (for contact names)."""
        search_text = text.lower()
        for i in range(self.chat_list_widget.count()):
            item = self.chat_list_widget.item(i)
            if item:
                if search_text in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    def import_compressed_dialog(self):
        file_filters = ["Archivos ZIP (*.zip *.ZIP)"]
        if RAR_SUPPORT:
            file_filters.append("Archivos RAR (*.rar *.RAR)")
        file_filters.append("Todos los archivos (*.*)")

        filter_string = ";;".join(file_filters)

        compressed_paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivo(s) comprimido(s)", "", filter_string
        )
        if compressed_paths:
            for compressed_path in compressed_paths:
                self.handle_compressed_file(compressed_path)

    def handle_compressed_file(self, compressed_path):
        temp_dir_base = "temp_whatsapp_chats"
        temp_dir_name = os.path.splitext(os.path.basename(compressed_path))[0]
        temp_dir_name = re.sub(r'[^\w\-_\.]', '_', temp_dir_name)
        temp_dir_name += "_" + str(int(time.time()))

        temp_dir = os.path.join(temp_dir_base, temp_dir_name)

        os.makedirs(temp_dir, exist_ok=True)
        self.all_temp_dirs_created.append(temp_dir)

        file_extension = os.path.splitext(compressed_path)[1].lower()

        try:
            txt_files_found = []
            extracted_files_for_this_archive = {} # {original_zip_member_path: extracted_full_path_on_disk}

            if file_extension == '.zip':
                with zipfile.ZipFile(compressed_path, 'r') as compressed_file:
                    txt_files_found, extracted_files_for_this_archive = self._extract_files(compressed_file, temp_dir)
            elif file_extension == '.rar' and RAR_SUPPORT:
                with rarfile.RarFile(compressed_path, 'r') as compressed_file:
                    txt_files_found, extracted_files_for_this_archive = self._extract_files(compressed_file, temp_dir)
            else:
                if file_extension == '.rar' and not RAR_SUPPORT:
                    QMessageBox.critical(self, "Error de soporte RAR",
                                         f"El archivo '{os.path.basename(compressed_path)}' es un archivo RAR y no se detecta soporte para RAR.\n"
                                         "Por favor, instala la librería 'rarfile' (pip install rarfile) y la herramienta 'unrar' en tu sistema operativo.")
                else:
                    QMessageBox.warning(self, "Formato no soportado",
                                         f"El archivo '{os.path.basename(compressed_path)}' tiene un formato no soportado. "
                                         "Solo se admiten archivos .zip y (opcionalmente) .rar.")
                return

            if not txt_files_found:
                QMessageBox.warning(self, "Advertencia",
                                         f"No se encontraron archivos .txt en '{os.path.basename(compressed_path)}'. Asegúrate de que contenga archivos .txt de chat.")
                # Even if no .txt files, we might still have media files, so we might want to keep the temp_dir.
                # If you want to delete temp_dir if no .txt, add:
                # self.cleanup_temp_dir(temp_dir)
                # self.all_temp_dirs_created.remove(temp_dir)
                return

            for txt_file_path in txt_files_found:
                # Associate the extracted files with this specific chat file
                self.chat_extracted_files_map[txt_file_path] = extracted_files_for_this_archive
                self.start_parsing(txt_file_path, temp_dir)

        except (zipfile.BadZipFile, rarfile.BadRarFile) as e:
            file_type = "ZIP" if isinstance(e, zipfile.BadZipFile) else "RAR"
            QMessageBox.critical(self, f"Error de archivo {file_type}",
                                 f"El archivo '{os.path.basename(compressed_path)}' no es un archivo {file_type} válido o está corrupto. Por favor, verifica su integridad o recréalo.")
        except Exception as e:
            QMessageBox.critical(self, "Error al abrir archivo comprimido",
                                 f"Ocurrió un error inesperado al procesar '{os.path.basename(compressed_path)}': {str(e)}")

    def _extract_files(self, archive_file, dest_dir):
        txt_files_extracted = []
        extracted_files_map = {} # {original_path_in_zip: extracted_full_path}
        for member in archive_file.namelist():
            if not member.endswith('/'): # Skip directories
                try:
                    # Prevent path traversal vulnerabilities
                    safe_member_path = os.path.normpath(member)
                    if os.path.isabs(safe_member_path) or ".." in safe_member_path:
                        print(f"Skipping potentially malicious path in archive: {member}")
                        continue

                    extracted_path = archive_file.extract(member, path=dest_dir)
                    extracted_files_map[member] = extracted_path # Store for global search
                    if member.lower().endswith('.txt'):
                        txt_files_extracted.append(extracted_path)
                except Exception as e:
                    print(f"Error al extraer '{member}': {e}")
        return txt_files_extracted, extracted_files_map

    def cleanup_temp_dir(self, temp_dir):
        """Intenta eliminar un único directorio temporal."""
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"Directorio temporal '{temp_dir}' limpiado.")
            except OSError as e:
                print(f"Error al eliminar el directorio temporal {temp_dir}: {e}")
                print("Por favor, asegúrate de que ningún otro programa esté usando los archivos en este directorio.")

    def cleanup_all_temp_dirs(self):
        """Elimina todos los directorios temporales registrados al cerrar la aplicación."""
        print("Limpiando todos los directorios temporales al salir de la aplicación...")
        for temp_dir in self.all_temp_dirs_created:
            self.cleanup_temp_dir(temp_dir)
        self.all_temp_dirs_created = []


    def start_parsing(self, file_path, base_media_dir):
        if file_path in self.chats:
            QMessageBox.information(self, "Chat ya cargado",
                                    f"El chat '{os.path.basename(file_path)}' ya está cargado en la lista.")
            return

        self.chats[file_path] = {
            'messages': [],
            'contact_name': '',
            'your_name': '',
            'widget_index': -1,
            'messages_layout_ref': None,
            'scroll_area_ref': None,
            'base_media_dir': base_media_dir,
            'current_display_start_index': 0,
            'load_more_button_ref': None
        }

        chat_scroll_area = QScrollArea()
        chat_scroll_area.setWidgetResizable(True)
        chat_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #E5DDD5;
                border: none;
            }
            QScrollBar:vertical {
                width: 8px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #B7B7B7;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        messages_widget = QWidget()
        messages_layout = QVBoxLayout(messages_widget)
        messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        messages_layout.setSpacing(3)
        messages_layout.setContentsMargins(5, 5, 5, 5)
        chat_scroll_area.setWidget(messages_widget)

        index = self.chat_stacked_widget.addWidget(chat_scroll_area)
        self.chats[file_path]['widget_index'] = index
        self.chats[file_path]['messages_layout_ref'] = messages_layout
        self.chats[file_path]['scroll_area_ref'] = chat_scroll_area

        chat_scroll_area.verticalScrollBar().valueChanged.connect(
            lambda value: self._handle_scroll_for_loading(file_path, value)
        )

        parser = ChatParser(file_path, base_media_dir)
        parser.message_parsed.connect(lambda msg: self.add_message_to_chat_data(file_path, msg))
        parser.parsing_finished.connect(lambda: self.parsing_finished_for_chat(file_path))
        parser.chat_info_parsed.connect(lambda contact, your, path, media_dir: self.update_chat_info(contact, your, path, media_dir))
        self.parser_threads.append(parser)
        parser.start()

    def _handle_scroll_for_loading(self, file_path, value):
        chat_data = self.chats.get(file_path)
        if not chat_data:
            return

        scroll_bar = chat_data['scroll_area_ref'].verticalScrollBar()
        # Si el usuario ha subido cerca del tope del scroll (valor 0 o cercano)
        # Y hay más mensajes antiguos por cargar
        if value <= scroll_bar.minimum() + 50 and chat_data['current_display_start_index'] > 0:
            # Solo cargar si no hay un botón de "Cargar más" visible que ya haga lo mismo
            # o si el botón está oculto (porque ya se hizo clic en él)
            if not chat_data['load_more_button_ref'] or chat_data['load_more_button_ref'].isHidden():
                self.load_more_historical_messages(file_path)


    def update_chat_info(self, contact_name, your_name, file_path, base_media_dir):
        if file_path in self.chats:
            self.chats[file_path]['contact_name'] = contact_name
            self.chats[file_path]['your_name'] = your_name
            self.chats[file_path]['base_media_dir'] = base_media_dir

            found_item = False
            for i in range(self.chat_list_widget.count()):
                item = self.chat_list_widget.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == file_path:
                    item.setText(contact_name)
                    found_item = True
                    break
            if not found_item:
                item = QListWidgetItem(contact_name)
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.chat_list_widget.addItem(item)

            if self.chat_list_widget.count() == 1:
                self.chat_list_widget.setCurrentItem(item)
                self.display_selected_chat(item)

    def add_message_to_chat_data(self, file_path, message_data):
        if file_path in self.chats:
            self.chats[file_path]['messages'].append(message_data)
            chat_data = self.chats[file_path]
            total_messages = len(chat_data['messages'])
            batch_size = 30 # AQUI: El tamaño del lote debe coincidir

            if self.current_chat_file_path == file_path:
                # Si el mensaje es uno de los primeros del batch final o si la cantidad total es <= batch_size
                if total_messages > chat_data['current_display_start_index'] or total_messages <= batch_size:
                    self.add_message_to_ui(message_data, chat_data['your_name'],
                                           chat_data['messages_layout_ref'],
                                           chat_data['scroll_area_ref'],
                                           chat_data['base_media_dir'])

                # Si estamos justo en el límite de un lote y el botón de carga más está presente,
                # asegura que los nuevos mensajes se añadan DESPUÉS de él, si aún no está en la posición 0.
                if total_messages == chat_data['current_display_start_index'] + 1 and chat_data['load_more_button_ref'] and \
                   chat_data['messages_layout_ref'].indexOf(chat_data['load_more_button_ref']) != 0:
                    messages_layout = chat_data['messages_layout_ref']
                    messages_layout.insertWidget(0, chat_data['load_more_button_ref'])


    def parsing_finished_for_chat(self, file_path):
        if self.current_chat_file_path == file_path:
            self.display_chat_messages(file_path)

        self.parser_threads = [thread for thread in self.parser_threads if thread.file_path != file_path]


    def display_selected_chat(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and file_path in self.chats:
            # Detener hilos de carga de imagen del chat anterior si había uno
            if self.current_chat_file_path and self.current_chat_file_path in self.chats:
                prev_chat_layout = self.chats[self.current_chat_file_path]['messages_layout_ref']
                if prev_chat_layout:
                    # Clean up existing MessageWidget threads
                    for i in range(prev_chat_layout.count()):
                        widget_item = prev_chat_layout.itemAt(i)
                        if widget_item:
                            widget_container = widget_item.widget()
                            if isinstance(widget_container, QWidget) and widget_container.layout():
                                # Find the MessageWidget within the QHBoxLayout's container
                                message_widget = None
                                for j in range(widget_container.layout().count()):
                                    item_in_container = widget_container.layout().itemAt(j)
                                    if item_in_container and isinstance(item_in_container.widget(), MessageWidget):
                                        message_widget = item_in_container.widget()
                                        break
                                if message_widget and message_widget.image_loader_thread and message_widget.image_loader_thread.isRunning():
                                    message_widget.image_loader_thread.quit()
                                    message_widget.image_loader_thread.wait()


            self.current_chat_file_path = file_path
            chat_data = self.chats[file_path]
            self.header.set_contact_name(chat_data['contact_name'])
            self.setWindowTitle(f"WhatsApp Viewer - {chat_data['contact_name']}")
            self.chat_stacked_widget.setCurrentIndex(chat_data['widget_index'])

            # Clear the file search bar in the header when a new chat is selected
            # This is important as the search scope now changes per chat.
            self.header.search_bar_file.clear()
            self.display_chat_messages(file_path)

    def display_chat_messages(self, file_path):
        chat_data = self.chats.get(file_path)
        if not chat_data:
            return

        messages_layout = chat_data['messages_layout_ref']
        scroll_area = chat_data['scroll_area_ref']
        your_name = chat_data['your_name']
        base_media_dir = chat_data['base_media_dir']

        # Clear existing messages in the UI
        for i in reversed(range(messages_layout.count())):
            widget_item = messages_layout.itemAt(i)
            if widget_item:
                widget = widget_item.widget()
                if widget:
                    widget.setParent(None) # Remove from layout
                    widget.deleteLater()

        all_messages = chat_data['messages']
        total_messages = len(all_messages)
        BATCH_SIZE = 30 # Number of messages to load at once

        # Determine the initial range of messages to display (latest batch)
        end_index = total_messages
        start_index = max(0, total_messages - BATCH_SIZE)
        chat_data['current_display_start_index'] = start_index

        # Add "Load More" button if there are older messages
        if start_index > 0:
            load_more_button = QPushButton("Cargar mensajes anteriores")
            load_more_button.setStyleSheet("""
                QPushButton {
                    background-color: #ECE5DD;
                    color: #555;
                    border: 1px solid #CCC;
                    padding: 8px;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)
            load_more_button.clicked.connect(lambda: self.load_more_historical_messages(file_path))
            messages_layout.addWidget(load_more_button, alignment=Qt.AlignmentFlag.AlignCenter)
            chat_data['load_more_button_ref'] = load_more_button
        else:
            if chat_data['load_more_button_ref']:
                chat_data['load_more_button_ref'].hide()
                chat_data['load_more_button_ref'].deleteLater()
                chat_data['load_more_button_ref'] = None


        # Add the initial batch of messages
        for i in range(start_index, end_index):
            message_data = all_messages[i]
            self.add_message_to_ui(message_data, your_name, messages_layout, scroll_area, base_media_dir)

        # Scroll to the bottom if it's the first load or a new chat
        QTimer.singleShot(100, lambda: scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum()))

    def load_more_historical_messages(self, file_path):
        chat_data = self.chats.get(file_path)
        if not chat_data:
            return

        messages_layout = chat_data['messages_layout_ref']
        scroll_area = chat_data['scroll_area_ref']
        your_name = chat_data['your_name']
        base_media_dir = chat_data['base_media_dir']

        all_messages = chat_data['messages']
        current_start = chat_data['current_display_start_index']
        BATCH_SIZE = 30

        # Calculate the new range of messages to load
        new_end_index = current_start
        new_start_index = max(0, current_start - BATCH_SIZE)

        if new_end_index <= 0: # No more older messages to load
            if chat_data['load_more_button_ref']:
                chat_data['load_more_button_ref'].hide()
                chat_data['load_more_button_ref'].deleteLater()
                chat_data['load_more_button_ref'] = None
            return

        # Store current scroll position to restore after loading
        old_scroll_value = scroll_area.verticalScrollBar().value()
        old_scroll_max = scroll_area.verticalScrollBar().maximum()

        # Remove the "Load More" button temporarily or if no more messages
        if chat_data['load_more_button_ref']:
            # Store its parent and index to re-insert correctly
            button_parent_layout = messages_layout
            button_index = messages_layout.indexOf(chat_data['load_more_button_ref'])
            chat_data['load_more_button_ref'].setParent(None) # Remove from layout
            # Do NOT deleteLater() here, we might reuse it or just hide if no more.


        # Add new messages at the top of the chat area
        added_height = 0
        for i in reversed(range(new_start_index, new_end_index)):
            message_data = all_messages[i]
            is_own = message_data['sender'] == your_name
            msg_widget = MessageWidget(message_data, is_own, base_media_dir)

            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(5, 0, 5, 0)

            if is_own:
                h_layout.addStretch()
                h_layout.addWidget(msg_widget)
            else:
                h_layout.addWidget(msg_widget)
                h_layout.addStretch()

            container = QWidget()
            container.setLayout(h_layout)
            messages_layout.insertWidget(0, container) # Insert at the very top
            added_height += container.sizeHint().height() + messages_layout.spacing()


        chat_data['current_display_start_index'] = new_start_index

        # Re-insert "Load More" button if there are still older messages
        if new_start_index > 0:
            if not chat_data['load_more_button_ref']: # Create if not exists
                load_more_button = QPushButton("Cargar mensajes anteriores")
                load_more_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ECE5DD;
                        color: #555;
                        border: 1px solid #CCC;
                        padding: 8px;
                        border-radius: 5px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #E0E0E0;
                    }
                """)
                load_more_button.clicked.connect(lambda: self.load_more_historical_messages(file_path))
                chat_data['load_more_button_ref'] = load_more_button
            else: # Reuse existing button and ensure it's visible
                chat_data['load_more_button_ref'].show()

            messages_layout.insertWidget(0, chat_data['load_more_button_ref'], alignment=Qt.AlignmentFlag.AlignCenter)
            added_height += chat_data['load_more_button_ref'].sizeHint().height() + messages_layout.spacing()
        else: # No more messages, remove button
            if chat_data['load_more_button_ref']:
                chat_data['load_more_button_ref'].hide()
                chat_data['load_more_button_ref'].deleteLater()
                chat_data['load_more_button_ref'] = None


        # Adjust scrollbar position to maintain view
        QTimer.singleShot(10, lambda: scroll_area.verticalScrollBar().setValue(
            old_scroll_value + (scroll_area.verticalScrollBar().maximum() - old_scroll_max)
        ))


    def add_message_to_ui(self, message_data, your_name, messages_layout, scroll_area, base_media_dir):
        is_own = message_data['sender'] == your_name

        msg_widget = MessageWidget(message_data, is_own, base_media_dir)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(5, 0, 5, 0)

        if is_own:
            h_layout.addStretch()
            h_layout.addWidget(msg_widget)
        else:
            h_layout.addWidget(msg_widget)
            h_layout.addStretch()

        container = QWidget() # Wrap MessageWidget in a QWidget with QHBoxLayout
        container.setLayout(h_layout)
        messages_layout.addWidget(container)

        # Auto-scroll al final solo si ya estamos cerca del final
        if scroll_area.verticalScrollBar().maximum() - scroll_area.verticalScrollBar().value() < 100:
             QTimer.singleShot(10, lambda: scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum()))


def main():
    app = QApplication(sys.argv)
    viewer = ChatViewer()
    viewer.show()
    # Ensure temporary directories are cleaned up on exit
    app.aboutToQuit.connect(viewer.cleanup_all_temp_dirs)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
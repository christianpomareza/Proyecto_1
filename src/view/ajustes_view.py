# src/view/ajustes_view.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QCheckBox, QGroupBox, QSpacerItem, QSizePolicy,
    QTextBrowser, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer # Asegúrate de que QTimer esté importado

from .screen import AppScreen

class AjustesView(AppScreen):
    modo_oscuro_toggled = pyqtSignal(bool)
    notificaciones_toggled = pyqtSignal(bool)
    guardar_clicked = pyqtSignal()
    refresh_adb_info_requested = pyqtSignal()
    reboot_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titulo.setText("Ajustes del Dispositivo y App")

        self.contenido_layout = self.contenido.layout()
        self.contenido_layout.setContentsMargins(10, 10, 10, 10)
        self.contenido_layout.setSpacing(15)

        self.init_general_settings_group()
        self.init_adb_status_group()
        self.init_adb_info_group()
        self.init_action_buttons()
        self.init_version_info()

        # Nuevo QLabel para mensajes de estado discretos
        self.status_message_label = QLabel("")
        self.status_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_message_label.setStyleSheet("color: blue; font-weight: bold;")
        self.contenido_layout.addWidget(self.status_message_label)
        # Opcional: un temporizador para borrar el mensaje después de un tiempo
        self._status_message_timer = QTimer(self)
        self._status_message_timer.setSingleShot(True)
        self._status_message_timer.timeout.connect(lambda: self.status_message_label.setText(""))


        self.contenido_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


    def init_general_settings_group(self):
        general_settings_group = QGroupBox("Ajustes Generales de la App")
        general_layout = QVBoxLayout(general_settings_group)
        general_layout.setSpacing(10)

        self.modo_oscuro_checkbox = QCheckBox("Modo Oscuro")
        self.modo_oscuro_checkbox.setChecked(False)
        self.modo_oscuro_checkbox.toggled.connect(self.modo_oscuro_toggled.emit)
        general_layout.addWidget(self.modo_oscuro_checkbox)

        self.notificaciones_checkbox = QCheckBox("Mostrar Notificaciones")
        self.notificaciones_checkbox.setChecked(True)
        self.notificaciones_checkbox.toggled.connect(self.notificaciones_toggled.emit)
        general_layout.addWidget(self.notificaciones_checkbox)

        self.guardar_button = QPushButton("Guardar Ajustes")
        self.guardar_button.clicked.connect(self.guardar_clicked.emit)
        general_layout.addWidget(self.guardar_button)

        self.contenido_layout.addWidget(general_settings_group)

    def init_adb_status_group(self):
        adb_status_group = QGroupBox("Estado de Conexión y Depuración ADB")
        adb_status_layout = QVBoxLayout(adb_status_group)
        adb_status_layout.setSpacing(10)

        self.usb_debugging_status_label = QLabel("Depuración USB: Desconocido")
        self.adb_connection_status_label = QLabel("Conexión ADB: Desconocido")
        self.device_id_label = QLabel("ID del Dispositivo: N/A")

        adb_status_layout.addWidget(self.usb_debugging_status_label)
        adb_status_layout.addWidget(self.adb_connection_status_label)
        adb_status_layout.addWidget(self.device_id_label)

        self.contenido_layout.addWidget(adb_status_group)

    def init_adb_info_group(self):
        adb_info_group = QGroupBox("Información del Dispositivo (Almacenamiento y Batería)")
        adb_info_layout = QVBoxLayout(adb_info_group)
        adb_info_layout.setSpacing(10)

        adb_info_layout.addWidget(QLabel("Información de Almacenamiento:"))
        self.adb_output_text_browser = QTextBrowser()
        self.adb_output_text_browser.setReadOnly(True)
        self.adb_output_text_browser.setMinimumHeight(80)
        adb_info_layout.addWidget(self.adb_output_text_browser)

        adb_info_layout.addWidget(QLabel("Información de Batería:"))
        self.battery_output_text_browser = QTextBrowser()
        self.battery_output_text_browser.setReadOnly(True)
        self.battery_output_text_browser.setMinimumHeight(60)
        adb_info_layout.addWidget(self.battery_output_text_browser)

        self.refresh_adb_button = QPushButton("Refrescar Información ADB")
        self.refresh_adb_button.clicked.connect(self.refresh_adb_info_requested.emit)
        adb_info_layout.addWidget(self.refresh_adb_button)

        self.contenido_layout.addWidget(adb_info_group)

    def init_action_buttons(self):
        action_buttons_layout = QHBoxLayout()
        self.reboot_button = QPushButton("Reiniciar Dispositivo")
        self.reboot_button.clicked.connect(self.reboot_requested.emit)
        action_buttons_layout.addWidget(self.reboot_button)

        self.shutdown_button = QPushButton("Apagar Dispositivo")
        self.shutdown_button.clicked.connect(self.shutdown_requested.emit)
        action_buttons_layout.addWidget(self.shutdown_button)

        self.contenido_layout.addLayout(action_buttons_layout)

    def init_version_info(self):
        version_layout = QHBoxLayout()
        self.version_label = QLabel("Versión: N/A")
        version_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        version_layout.addWidget(self.version_label)
        version_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.contenido_layout.addLayout(version_layout)

    def display_settings(self, settings: dict):
        self.modo_oscuro_checkbox.setChecked(settings.get("modo_oscuro", False))
        self.notificaciones_checkbox.setChecked(settings.get("mostrar_notificaciones", True))
        self.version_label.setText(f"Versión: {settings.get('version_app', 'N/A')}")

    def update_adb_status(self, usb_debugging_active: bool, adb_connected: bool, device_id: str):
        self.usb_debugging_status_label.setText(
            f"Depuración USB: {'Activada' if usb_debugging_active else 'Desactivada'}")
        self.usb_debugging_status_label.setStyleSheet(
            "color: green;" if usb_debugging_active else "color: red;")

        self.adb_connection_status_label.setText(
            f"Conexión ADB: {'Conectado' if adb_connected else 'Desconectado'}")
        self.adb_connection_status_label.setStyleSheet(
            "color: green;" if adb_connected else "color: red;")

        self.device_id_label.setText(f"ID del Dispositivo: {device_id if device_id else 'N/A'}")
        self.device_id_label.setStyleSheet(
            "color: blue;" if device_id else "color: gray;")

    def update_adb_info(self, storage_info: str):
        self.adb_output_text_browser.setText(storage_info if storage_info else "No disponible.")

    def update_battery_info(self, battery_info: str):
        self.battery_output_text_browser.setText(battery_info if battery_info else "No disponible.")

    def set_status_message(self, message: str, color: str = "blue", timeout_ms: int = 3000):
        """Muestra un mensaje temporal en la etiqueta de estado."""
        self.status_message_label.setText(message)
        self.status_message_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self._status_message_timer.start(timeout_ms)


    def show_message(self, title, message, icon_type="info", show_popup: bool = True):
        """
        Muestra un QMessageBox. Si show_popup es False, simplemente imprime en consola (o ignora).
        """
        if show_popup:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            if icon_type == "info":
                msg_box.setIcon(QMessageBox.Icon.Information)
            elif icon_type == "warning":
                msg_box.setIcon(QMessageBox.Icon.Warning)
            elif icon_type == "critical":
                msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()
        else:
            # Puedes imprimir en la consola o simplemente no hacer nada
            print(f"[{title}] {message}")
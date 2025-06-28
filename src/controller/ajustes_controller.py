# src/controller/ajustes_controller.py

from ..model.ajustes_model import AjustesModel
from ..view.ajustes_view import AjustesView
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox

class AjustesController:
    def __init__(self, model: AjustesModel, view: AjustesView):
        self.model = model
        self.view = view
        self._connect_signals()

        self.refresh_timer = QTimer(self.view)
        # El timeout del timer siempre llama a update_adb_data sin el parámetro 'manual_refresh'
        self.refresh_timer.timeout.connect(lambda: self.update_adb_data(manual_refresh=False))

        self.view.destroyed.connect(self._stop_refresh_timer)

        self.load_initial_settings()
        self._start_refresh_timer() # Inicia el refresco ADB al crear el controlador

    def _connect_signals(self):
        self.view.modo_oscuro_toggled.connect(self._handle_modo_oscuro_toggle)
        self.view.notificaciones_toggled.connect(self._handle_notificaciones_toggle)
        self.view.guardar_clicked.connect(self.save_app_settings)

        # Conectar el botón de refresco para que llame a update_adb_data con manual_refresh=True
        self.view.refresh_adb_info_requested.connect(lambda: self.update_adb_data(manual_refresh=True))
        self.view.reboot_requested.connect(self.handle_reboot_device)
        self.view.shutdown_requested.connect(self.handle_shutdown_device)

    def load_initial_settings(self):
        settings = self.model.get_settings()
        self.view.display_settings(settings)
        self._handle_modo_oscuro_toggle(settings.get("modo_oscuro", False))
        self._handle_notificaciones_toggle(settings.get("mostrar_notificaciones", True))


    def update_adb_data(self, manual_refresh: bool = False):
        """
        Obtiene y actualiza la información de almacenamiento, batería,
        estado de depuración USB y conexión ADB del dispositivo.
        :param manual_refresh: Si es True, muestra mensajes de QMessageBox; si es False (refresco automático), usa QLabel.
        """
        if manual_refresh:
            self.view.set_status_message("Refrescando información ADB...", "blue")
            self.view.show_message("Actualizando ADB", "Obteniendo información del dispositivo...", icon_type="info", show_popup=True)
        else:
            self.view.set_status_message("Actualizando ADB en segundo plano...", "gray", timeout_ms=1000) # Mensaje temporal

        # 1. Verificar estado de la conexión ADB y Depuración USB
        adb_devices = self.model.get_adb_devices()
        adb_connected = bool(adb_devices)
        device_id = adb_devices[0] if adb_connected else ""

        usb_debugging_active = False
        if adb_connected:
            usb_debugging_active = self.model.get_usb_debugging_status(device_id)

        self.view.update_adb_status(usb_debugging_active, adb_connected, device_id)

        # 2. Obtener información de almacenamiento y batería (solo si hay conexión y depuración USB activa)
        storage_info = ""
        battery_info = ""
        if adb_connected and usb_debugging_active:
            storage_info = self.model.get_device_storage_info()
            battery_info = self.model.get_device_battery_info()
            # Limpiar mensajes de error previos de info
            if "Error" in storage_info: storage_info = "Error al obtener almacenamiento."
            if "Error" in battery_info: battery_info = "Error al obtener batería."

        else:
            storage_info = "Dispositivo no conectado o depuración USB desactivada."
            battery_info = "Dispositivo no conectado o depuración USB desactivada."

        self.view.update_adb_info(storage_info)
        self.view.update_battery_info(battery_info)

        # Mostrar mensajes de estado o error en el status_message_label
        if not adb_connected:
            self.view.set_status_message("ERROR: Dispositivo ADB desconectado.", "red")
            if manual_refresh:
                 self.view.show_message("Error ADB", "No se detectó ningún dispositivo ADB conectado. Asegúrate de que el celular esté conectado y la depuración USB activada.", icon_type="critical", show_popup=True)
        elif not usb_debugging_active:
             self.view.set_status_message("ADVERTENCIA: Depuración USB desactivada.", "orange")
             if manual_refresh:
                self.view.show_message("Advertencia ADB", "Dispositivo conectado, pero la Depuración USB no está activada en el celular. Algunos comandos pueden no funcionar.", icon_type="warning", show_popup=True)
        else:
            if manual_refresh:
                self.view.set_status_message("Información de ADB actualizada.", "green")
                self.view.show_message("ADB Actualizado", "Información de ADB actualizada correctamente.", icon_type="info", show_popup=True)
            else:
                self.view.set_status_message("ADB actualizado.", "green", timeout_ms=1500) # Mensaje muy breve

    def _handle_modo_oscuro_toggle(self, checked):
        self.model.set_setting("modo_oscuro", checked)

    def _handle_notificaciones_toggle(self, checked):
        self.model.set_setting("mostrar_notificaciones", checked)

    def save_app_settings(self):
        self.model.save_settings()
        self.view.show_message("Ajustes Guardados", "La configuración de la aplicación ha sido guardada.", show_popup=True)


    def _start_refresh_timer(self):
        self.update_adb_data() # Llama inmediatamente al entrar
        self.refresh_timer.start(self.model.get_refresh_interval() * 1000)

    def _stop_refresh_timer(self):
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            print("Temporizador de refresco de ADB detenido.")


    def handle_reboot_device(self):
        if not self.model.get_adb_devices():
            self.view.show_message("Error de Dispositivo", "No hay dispositivos ADB conectados.", icon_type="critical", show_popup=True)
            return

        reply = QMessageBox.question(
            self.view,
            "Confirmar Reinicio",
            "¿Estás seguro de que quieres reiniciar el dispositivo? Esto podría tardar.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            message = self.model.reboot_device()
            self.view.show_message("Reiniciar Dispositivo", message, icon_type="info", show_popup=True)
            QTimer.singleShot(5000, self.update_adb_data) # Esperar 5 segundos y refrescar


    def handle_shutdown_device(self):
        if not self.model.get_adb_devices():
            self.view.show_message("Error de Dispositivo", "No hay dispositivos ADB conectados.", icon_type="critical", show_popup=True)
            return

        reply = QMessageBox.question(
            self.view,
            "Confirmar Apagado",
            "¿Estás seguro de que quieres apagar el dispositivo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            message = self.model.shutdown_device()
            self.view.show_message("Apagar Dispositivo", message, icon_type="info", show_popup=True)
            QTimer.singleShot(5000, self.update_adb_data)


    def get_view(self):
        return self.view
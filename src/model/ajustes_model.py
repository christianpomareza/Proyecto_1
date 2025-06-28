# src/model/ajustes_model.py

import json
import os
import subprocess
import re
import datetime

class AjustesModel:
    def __init__(self, config_file="config.json", adb_command="adb"):
        self.config_file = config_file
        self.ADB_COMMAND = adb_command
        self.settings = self._load_settings()

    def _load_settings(self):
        """Carga los ajustes desde un archivo JSON o usa valores predeterminados."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    default_settings = self._default_settings()
                    return {**default_settings, **loaded_settings}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al cargar la configuración: {e}. Usando valores predeterminados.")
        return self._default_settings()

    def _default_settings(self):
        """Define los ajustes predeterminados."""
        return {
            # "brillo": 50, # ELIMINADO
            # "volumen": 70, # ELIMINADO
            "modo_oscuro": False,
            "version_app": "1.0.0",
            "mostrar_notificaciones": True,
            "refresh_interval_seconds": 10,
            "last_saved": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_settings(self) -> dict:
        """Devuelve todos los ajustes actuales."""
        return self.settings

    def get_setting(self, key, default=None):
        """Devuelve un ajuste específico."""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Establece un ajuste específico."""
        self.settings[key] = value
        self.settings["last_saved"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_settings(self):
        """Guarda los ajustes actuales en el archivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error al guardar la configuración: {e}")

    def get_refresh_interval(self) -> int:
        """Devuelve el intervalo de refresco de ADB en segundos."""
        return self.settings.get("refresh_interval_seconds", 10)


    # --- Métodos ADB ---
    def _execute_adb_command_sync(self, args: list) -> tuple[int, str, str]:
        """Ejecuta un comando ADB de forma síncrona y devuelve el código de retorno, stdout y stderr."""
        try:
            command = [self.ADB_COMMAND] + args
            result = subprocess.run(command, capture_output=True, text=True,
                                  check=False, encoding='utf-8', timeout=120)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError:
            return 1, "", "Error: 'adb' no encontrado. Asegúrate de que ADB esté instalado y en tu PATH."
        except subprocess.TimeoutExpired:
            return 1, "", "Error: Comando ADB ha excedido el tiempo de espera."
        except Exception as e:
            return 1, "", f"Error desconocido al ejecutar ADB: {e}"

    def get_adb_devices(self) -> list[str]:
        """Obtiene una lista de IDs de dispositivos ADB conectados."""
        returncode, stdout, stderr = self._execute_adb_command_sync(["devices"])
        if returncode == 0:
            devices = []
            lines = stdout.splitlines()
            if len(lines) > 1:
                for line in lines[1:]:
                    if "device" in line and not "offline" in line:
                        device_id = line.split("\t")[0]
                        devices.append(device_id)
            return devices
        else:
            print(f"Error al listar dispositivos ADB: {stderr}")
            return []

    def is_adb_connected(self) -> bool:
        """Verifica si hay al menos un dispositivo ADB conectado."""
        return bool(self.get_adb_devices())

    def get_usb_debugging_status(self, device_id: str) -> bool:
        """
        Verifica si la depuración USB está activa en un dispositivo específico.
        Esto se hace intentando un comando simple que solo funcionaría si la depuración USB está habilitada.
        """
        if not device_id:
            return False
        # Un comando simple para probar si ADB puede comunicarse con el dispositivo.
        # 'getprop ro.build.version.release' es un comando inofensivo.
        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "shell", "getprop", "ro.build.version.release"])
        # Si el comando tiene éxito (returncode == 0) y no hay errores significativos en stderr,
        # asumimos que la depuración USB está activa.
        return returncode == 0 and "error" not in stderr.lower() and "failed" not in stderr.lower()


    def get_device_storage_info(self) -> str:
        """Obtiene información de almacenamiento del dispositivo."""
        devices = self.get_adb_devices()
        if not devices:
            return "No hay dispositivos ADB conectados."
        device_id = devices[0]
        # Comando para ver el uso de espacio en /sdcard (almacenamiento interno)
        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "shell", "df -h /sdcard"])
        if returncode == 0:
            return stdout
        else:
            return f"Error al obtener info de almacenamiento: {stderr}"

    def get_device_battery_info(self) -> str:
        """Obtiene información de la batería del dispositivo."""
        devices = self.get_adb_devices()
        if not devices:
            return "No hay dispositivos ADB conectados."
        device_id = devices[0]
        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "shell", "dumpsys battery"])
        if returncode == 0:
            battery_info = []
            for line in stdout.splitlines():
                # Filtra solo las líneas más relevantes
                if any(keyword in line.lower() for keyword in ["level:", "status:", "temperature:", "voltage:", "health:", "charge counter:"]):
                    battery_info.append(line.strip())
            return "\n".join(battery_info) if battery_info else "Información de batería no disponible o no parseada."
        else:
            return f"Error al obtener info de batería: {stderr}"

    def reboot_device(self) -> str:
        """Reinicia el dispositivo Android."""
        devices = self.get_adb_devices()
        if not devices:
            return "No se encontraron dispositivos ADB conectados para reiniciar."
        device_id = devices[0]
        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "reboot"])
        if returncode == 0:
            return "Comando de reinicio enviado exitosamente."
        else:
            return f"Error al reiniciar: {stderr}"

    def shutdown_device(self) -> str:
        """Apaga el dispositivo Android."""
        devices = self.get_adb_devices()
        if not devices:
            return "No se encontraron dispositivos ADB conectados para apagar."
        device_id = devices[0]
        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "shell", "reboot -p"])
        if returncode == 0:
            return "Comando de apagado enviado exitosamente."
        else:
            return f"Error al apagar: {stderr}"
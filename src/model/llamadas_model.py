# src/model/llamadas_model.py

import subprocess
import xml.etree.ElementTree as ET
import datetime
import re
import os

class CallLogModel:
    def __init__(self):
        self.ADB_COMMAND = "adb"
        self.CALL_LOG_DIR_ON_DEVICE = "/sdcard/extraer/"
        self.CALL_LOG_FILENAME_PATTERN_PYTHON = r"calls-\d{14}\.xml"

    def _execute_adb_command_sync(self, args: list) -> tuple[int, str, str]:
        try:
            command = [self.ADB_COMMAND] + args
            print(f"DEBUG(ADB Command): {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True,
                                  check=False, encoding='utf-8', timeout=120)
            print(f"DEBUG(ADB Output): ReturnCode={result.returncode}, Stdout='{result.stdout.strip()}', Stderr='{result.stderr.strip()}'")
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError:
            return 1, "", "Error: 'adb' no encontrado. Asegúrate de que ADB esté instalado y en tu PATH."
        except subprocess.TimeoutExpired:
            return 1, "", "Error: Comando ADB ha excedido el tiempo de espera."
        except Exception as e:
            return 1, "", f"Error desconocido al ejecutar ADB: {e}"

    def get_adb_devices(self) -> list[str]:
        returncode, stdout, stderr = self._execute_adb_command_sync(["devices"])
        if returncode == 0:
            devices = []
            lines = stdout.splitlines()
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        device_id = parts[0].strip()
                        status = parts[1].strip()
                        if status == "device":
                            devices.append(device_id)
                        elif status == "unauthorized":
                            print(f"DEBUG(LlamadasModel): Dispositivo {device_id} no autorizado. Acepta la depuración USB en tu celular.")
                        elif status == "offline":
                            print(f"DEBUG(LlamadasModel): Dispositivo {device_id} está offline. Revisa la conexión.")
            if not devices:
                print("DEBUG(LlamadasModel): No se encontraron dispositivos ADB conectados y autorizados.")
            return devices
        else:
            print(f"DEBUG(LlamadasModel): Error al listar dispositivos ADB: {stderr}")
            return []

    def get_latest_call_log_filename(self) -> str | None:
        devices = self.get_adb_devices()
        if not devices:
            print("DEBUG(LlamadasModel): No hay dispositivos ADB conectados para listar archivos.")
            return None
        device_id = devices[0]

        command_args = ["-s", device_id, "shell",
                        f"ls -lt {self.CALL_LOG_DIR_ON_DEVICE} 2>/dev/null"]

        returncode, stdout, stderr = self._execute_adb_command_sync(command_args)

        if returncode != 0:
            print(f"DEBUG(LlamadasModel): Error al listar archivos en {self.CALL_LOG_DIR_ON_DEVICE}: {stderr}")
            if "No such file or directory" in stderr or "No such file or directory" in stdout:
                 print(f"DEBUG(LlamadasModel): El directorio '{self.CALL_LOG_DIR_ON_DEVICE}' no existe en el dispositivo o es inaccesible.")
            return None

        file_list_raw = stdout.splitlines()
        
        filename_extract_regex = re.compile(r'\s*([^ ]+)$')

        for line in file_list_raw:
            match = filename_extract_regex.search(line)
            if match:
                filename_on_device = match.group(1).strip()
                
                if filename_on_device.lower() == "total":
                    continue

                if re.fullmatch(self.CALL_LOG_FILENAME_PATTERN_PYTHON, filename_on_device):
                    print(f"DEBUG(LlamadasModel): Coincidencia encontrada: {filename_on_device}")
                    return filename_on_device
                else:
                    print(f"DEBUG(LlamadasModel): Archivo listado '{filename_on_device}' no coincide con patrón de Python '{self.CALL_LOG_FILENAME_PATTERN_PYTHON}'")
            else:
                print(f"DEBUG(LlamadasModel): No se pudo extraer el nombre del archivo de la línea: {line}")

        print(f"DEBUG(LlamadasModel): Después de listar y filtrar en Python, no se encontró ningún archivo XML de historial de llamadas que coincida con el patrón '{self.CALL_LOG_FILENAME_PATTERN_PYTHON}' en {self.CALL_LOG_DIR_ON_DEVICE}")
        return None

    def get_call_log_xml_from_device(self) -> str | None:
        devices = self.get_adb_devices()
        if not devices:
            print("DEBUG(LlamadasModel): No hay dispositivos ADB conectados para obtener XML.")
            return None

        device_id = devices[0]

        latest_filename = self.get_latest_call_log_filename()
        if not latest_filename:
            print("DEBUG(LlamadasModel): No se encontró un nombre de archivo XML válido para descargar. (Esto puede deberse a que no hay archivos en la ruta o no coinciden con el patrón)")
            return None

        full_path_on_device = os.path.join(self.CALL_LOG_DIR_ON_DEVICE, latest_filename).replace("\\", "/")
        print(f"DEBUG(LlamadasModel): Intentando obtener XML de: {full_path_on_device} en dispositivo {device_id}")

        returncode, stdout, stderr = self._execute_adb_command_sync(["-s", device_id, "shell", "cat", full_path_on_device])

        if returncode == 0:
            if not stdout.strip():
                print(f"DEBUG(LlamadasModel): El archivo '{full_path_on_device}' está vacío.")
                return None
            
            # --- GUARDAR XML PARA DEPURACIÓN (eliminar después de verificar) ---
            # debug_xml_filepath = "DEBUG_received_call_log.xml"
            # try:
            #     with open(debug_xml_filepath, "w", encoding="utf-8") as f:
            #         f.write(stdout)
            #     print(f"DEBUG(LlamadasModel): XML recibido guardado en '{debug_xml_filepath}' para inspección.")
            # except Exception as e:
            #     print(f"DEBUG(LlamadasModel): Error al guardar el XML de depuración: {e}")
            # --- FIN DE GUARDAR XML ---

            return stdout
        else:
            print(f"DEBUG(LlamadasModel): Error ADB al leer el archivo (cat {full_path_on_device}): {stderr}")
            if "No such file or directory" in stderr or "No such file or directory" in stdout:
                print("DEBUG(LlamadasModel): El archivo XML no existe en el dispositivo o la ruta/nombre es incorrecta.")
            return None

    def parse_call_log_xml(self, xml_data: str) -> list[dict]:
        calls_list = []
        if not xml_data:
            print("DEBUG(LlamadasModel): No hay datos XML para parsear o el XML está vacío.")
            return []
        try:
            xml_data = xml_data.strip()
            if not xml_data.startswith("<?xml") and "<" in xml_data:
                xml_data = xml_data[xml_data.find("<"):]

            root = ET.fromstring(xml_data)
            for call_element in root.findall('call'):
                # --- CAMBIO AQUÍ: BUSCAMOS 'contact_name' EN LUGAR DE 'name' ---
                number = call_element.get('number', 'Desconocido')
                name = call_element.get('contact_name', 'Desconocido') # <--- LÍNEA MODIFICADA
                
                if not name or name == '(null)' or name.strip() == '':
                    name = 'Desconocido'
                else:
                    name = name.strip()

                duration_seconds = int(call_element.get('duration', '0'))
                duration_minutes = duration_seconds // 60
                duration_remaining_seconds = duration_seconds % 60
                duration_formatted = f"{duration_minutes}m {duration_remaining_seconds}s"

                timestamp_ms = int(call_element.get('date', '0'))
                call_datetime = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
                call_time = call_datetime.strftime('%Y-%m-%d %H:%M:%S')

                call_type_code = int(call_element.get('type', '0'))
                call_type_map = {
                    1: 'Entrante', 2: 'Saliente', 3: 'Perdida', 4: 'Buzón de voz',
                    5: 'Rechazada', 6: 'Bloqueada', 7: 'Respondida corta',
                    8: 'Llamada de vuelta', 9: 'Reenviada', 0: 'Desconocido'
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
            print(f"DEBUG(LlamadasModel): Error al parsear XML de llamadas. El XML podría estar mal formado: {e}")
            print(f"DEBUG(LlamadasModel): Datos XML que causaron el error (primeras 500 chars): {xml_data[:500]}")
            return []
        except Exception as e:
            print(f"DEBUG(LlamadasModel): Error inesperado al procesar el XML de llamadas: {e}")
            return []
        return calls_list
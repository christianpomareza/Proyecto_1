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
            # print(
            #    f"DEBUG(ADB Output): ReturnCode={result.returncode}, Stdout='{result.stdout.strip()}', Stderr='{result.stderr.strip()}'")
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError:
            return 1, "", "Error: 'adb' no encontrado. Asegúrate de que ADB esté instalado y en tu PATH."
        except subprocess.TimeoutExpired:
            return 1, "", "Error: Comando ADB ha excedido el tiempo de espera."
        except Exception as e:
            return 1, "", f"Error desconocido al ejecutar ADB: {e}"

    def get_adb_devices(self) -> list[str]:
        returncode, stdout, stderr = self._execute_adb_command_sync([
                                                                    "devices"])
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
                            print(
                                f"DEBUG(LlamadasModel): Dispositivo {device_id} no autorizado. Acepta la depuración USB en tu celular.")
                        elif status == "offline":
                            print(
                                f"DEBUG(LlamadasModel): Dispositivo {device_id} está offline. Revisa la conexión.")
            if not devices:
                print(
                    "DEBUG(LlamadasModel): No se encontraron dispositivos ADB conectados y autorizados.")
            print(f"-> {devices}")
            return devices
        else:
            print(
                f"DEBUG(LlamadasModel): Error al listar dispositivos ADB: {stderr}")
            return []

    def get_latest_call_log_filename(self, device_id=0) -> str | None:

        command_args = ['shell', 'content', 'query',
                        '--uri', 'content://call_log/calls']

        returncode, stdout, stderr = self._execute_adb_command_sync(
            command_args)

        if returncode != 0:
            return None

        # file_list_raw = stdout.splitlines()
        # filename_extract_regex = re.compile(r'\s*([^ ]+)$')
        return stdout.strip()  # str

    def get_call_log_xml_from_device(self) -> str | None:

        latest_filename = self.get_latest_call_log_filename()
        if not latest_filename:
            print("No se puede acceder a la información de las llamadas")
            return None

        return latest_filename

    def parse_call(self, data):
        fields = {
            "number": r"\bnumber=([^,]+)",
            "name": r"\bname=([^,]+)",
            "duration": r"\bduration=([^,]+)",
            "date": r"\bdate=([^,]+)",
            "type": r"\btype=([^,]+)",
        }

        parse_data = list()
        data = data.split("\n")

        for call in data:
            pattern = re.compile(fields["number"])
            number = pattern.findall(call)[0]

            pattern = re.compile(fields["name"])
            name = pattern.findall(call)
            name = name[0] if len(name) > 0 else "Desconocido"

            pattern = re.compile(fields["duration"])
            duration = pattern.findall(call)[0]

            duration_seconds = int(duration)
            duration_minutes = duration_seconds // 60
            duration_remaining_seconds = duration_seconds % 60
            duration_formatted = f"{duration_minutes}m {duration_remaining_seconds}s"

            pattern = re.compile(fields["date"])
            date = pattern.findall(call)[0]

            timestamp_ms = int(date)
            call_datetime = datetime.datetime.fromtimestamp(
                timestamp_ms / 1000)
            call_time = call_datetime.strftime('%Y-%m-%d %H:%M:%S')

            pattern = re.compile(fields["type"])
            type_call = pattern.findall(call)[0]

            call_type_code = int(type_call)
            call_type_map = {
                1: 'Entrante', 2: 'Saliente', 3: 'Perdida', 4: 'Buzón de voz',
                5: 'Rechazada', 6: 'Bloqueada', 7: 'Respondida corta',
                8: 'Llamada de vuelta', 9: 'Reenviada', 0: 'Desconocido'
            }
            call_type = call_type_map.get(
                call_type_code, f'Tipo {call_type_code}')

            parse_data.append({
                'Nombre': name,
                'Número': number,
                'Duración': duration_formatted,
                'Fecha y Hora': call_time,
                'Tipo de Llamada': call_type
            })

        return parse_data

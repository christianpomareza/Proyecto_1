from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import QTimer
from .screen import AppScreen
import subprocess
import re


def crear_pantalla_ajustes(parent):
    pantalla_ajustes = AppScreen(parent)
    pantalla_ajustes.titulo.setText("Ajustes")

    # Contenido de ajustes
    contenido = QVBoxLayout(pantalla_ajustes.contenido)

    # Estilos
    ajustes_estilo = """
        QLabel {
            padding: 10px;
            background-color: rgba(255, 255, 255, 150);
            border-radius: 10px;
            margin-bottom: 5px;
        }
    """

    # Widget para mostrar información de ADB
    adb_info_title = QLabel("Información de almacenamiento del dispositivo")
    adb_info_title.setStyleSheet(ajustes_estilo)
    contenido.addWidget(adb_info_title)

    # Crear un QTextBrowser para mostrar la salida del comando adb con formato HTML
    adb_output = QTextBrowser()
    adb_output.setReadOnly(True)
    adb_output.setMinimumHeight(300)
    adb_output.setStyleSheet("""
        QTextBrowser {
            padding: 10px;
            background-color: rgba(240, 240, 240, 150);
            border-radius: 10px;
            font-family: Arial, sans-serif;
            border: none;
        }
    """)
    contenido.addWidget(adb_output)

    # Función para ejecutar el comando ADB y actualizar el widget
    def actualizar_info_adb():
        try:
            # Verificar primero si hay dispositivos conectados
            check_devices = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Verificar si hay dispositivos conectados (excluyendo la línea "List of devices attached")
            device_lines = check_devices.stdout.strip().split('\n')[1:]
            devices_connected = [line for line in device_lines if line.strip(
            ) and not line.strip().endswith('unauthorized')]

            if not devices_connected:
                adb_output.setText("No hay dispositivos conectados")
                return

            # Ejecutar el comando df -h
            result = subprocess.run(
                ["adb", "shell", "df", "-h"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Procesar la salida para hacerla más amigable
                output_text = result.stdout
                lines = output_text.strip().split('\n')

                # Ignorar la primera línea (encabezados)
                data_lines = lines[1:] if len(lines) > 1 else []

                # Crear una salida formateada y amigable
                formatted_output = "<style>table {width: 100%; border-collapse: collapse;} th {background-color: #4CAF50; color: white; padding: 10px; text-align: left;} td {padding: 8px; border-bottom: 1px solid #ddd;} tr:nth-child(even) {background-color: #f2f2f2;}</style>"
                formatted_output += "<table>"
                formatted_output += "<tr><th>Unidad de Almacenamiento</th><th>Espacio Total</th><th>Espacio Usado</th><th>Espacio Disponible</th><th>% Usado</th></tr>"

                for line in data_lines:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 6:
                        # Extraer información y adaptarla para que sea más comprensible
                        filesystem = parts[0]
                        size = parts[1]
                        used = parts[2]
                        available = parts[3]
                        percentage = parts[4]
                        mount_point = parts[5]

                        # Simplificar nombre de la unidad según punto de montaje
                        friendly_name = "Desconocido"
                        if "/storage/emulated" in mount_point or "/data" == mount_point:
                            friendly_name = "Almacenamiento Interno"
                        elif "/storage/self" in mount_point:
                            friendly_name = "Almacenamiento Privado"
                        elif "/system" == mount_point:
                            friendly_name = "Sistema"
                        elif "/vendor" == mount_point:
                            friendly_name = "Componentes del Sistema"
                        elif "/cache" == mount_point:
                            friendly_name = "Caché del Sistema"
                        elif "/product" == mount_point:
                            friendly_name = "Aplicaciones del Sistema"
                        elif "/sdcard" in mount_point or "/storage/sdcard" in mount_point:
                            friendly_name = "Tarjeta SD"
                        elif "/mnt" in mount_point:
                            friendly_name = "Almacenamiento Externo"
                        else:
                            friendly_name = f"Otro ({mount_point})"

                        # Añadir color al porcentaje según nivel de uso
                        percentage_value = percentage.strip('%')
                        try:
                            percentage_num = int(percentage_value)
                            if percentage_num >= 90:
                                percentage_cell = f"<td style='color: red; font-weight: bold;'>{percentage}</td>"
                            elif percentage_num >= 75:
                                percentage_cell = f"<td style='color: orange; font-weight: bold;'>{percentage}</td>"
                            else:
                                percentage_cell = f"<td style='color: green;'>{percentage}</td>"
                        except ValueError:
                            percentage_cell = f"<td>{percentage}</td>"

                        # Añadir fila a la tabla
                        formatted_output += f"<tr><td>{friendly_name}</td><td>{size}</td><td>{used}</td><td>{available}</td>{percentage_cell}</tr>"

                formatted_output += "</table>"

                # Si hay pocas líneas, agregar un resumen visual
                if len(data_lines) > 0:
                    formatted_output += "<br><h3>Resumen de Almacenamiento</h3>"
                    formatted_output += "<p>Espacio utilizado por partición:</p>"

                    for line in data_lines:
                        parts = re.split(r'\s+', line.strip())
                        if len(parts) >= 6:
                            mount_point = parts[5]
                            percentage = parts[4].strip('%')
                            try:
                                percentage_num = int(percentage)

                                # Simplificar nombre de la unidad según punto de montaje
                                friendly_name = "Desconocido"
                                if "/storage/emulated" in mount_point or "/data" == mount_point:
                                    friendly_name = "Almacenamiento Interno"
                                elif "/storage/self" in mount_point:
                                    friendly_name = "Almacenamiento Privado"
                                elif "/system" == mount_point:
                                    friendly_name = "Sistema"
                                elif "/vendor" == mount_point:
                                    friendly_name = "Componentes del Sistema"
                                elif "/cache" == mount_point:
                                    friendly_name = "Caché del Sistema"
                                elif "/product" == mount_point:
                                    friendly_name = "Aplicaciones del Sistema"
                                elif "/sdcard" in mount_point or "/storage/sdcard" in mount_point:
                                    friendly_name = "Tarjeta SD"
                                elif "/mnt" in mount_point:
                                    friendly_name = "Almacenamiento Externo"
                                else:
                                    continue  # Omitir particiones desconocidas del resumen visual

                                # Color según nivel de uso
                                if percentage_num >= 90:
                                    color = "red"
                                elif percentage_num >= 75:
                                    color = "orange"
                                else:
                                    color = "green"

                                formatted_output += f"<div style='margin-bottom: 5px;'><b>{friendly_name}</b>: "
                                formatted_output += f"<div style='background-color: #e0e0e0; width: 200px; height: 20px; display: inline-block; margin-left: 10px;'>"
                                formatted_output += f"<div style='background-color: {color}; width: {percentage_num*2}px; height: 20px;'></div></div> {percentage_num}%</div>"
                            except ValueError:
                                pass

                adb_output.setHtml(formatted_output)
            else:
                adb_output.setText(
                    f"Error al ejecutar comando: {result.stderr}")

        except subprocess.TimeoutExpired:
            adb_output.setText(
                "Tiempo de espera agotado al ejecutar comando ADB")
        except Exception as e:
            adb_output.setText(f"Error: {str(e)}")

    # Ejecutar la función cuando se muestra la pantalla
    actualizar_info_adb()

    # Configurar un temporizador para actualizar la información periódicamente (cada 5 segundos)
    refresh_timer = QTimer(pantalla_ajustes)
    refresh_timer.timeout.connect(actualizar_info_adb)
    refresh_timer.start(5000)  # 5000 ms = 5 segundos

    # Asegurarse de que el temporizador se detenga cuando se cierre la pantalla
    pantalla_ajustes.destroyed.connect(lambda: refresh_timer.stop())

    contenido.addStretch()

    return pantalla_ajustes


import subprocess


def llamadas():
    resultado = subprocess.check_output(
        ['adb', 'shell', 'content', 'query',
                '--uri', 'content://call_log/calls'],
        text=True,
        stderr=subprocess.STDOUT
    )

    if type(resultado) == list:
        return resultado
    else:
        pass


def actualizar_info_adb():
    try:
        check_devices = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if check_devices.stdout.strip().split('\n') > 2:
            device_lines = check_devices.stdout.strip().split('\n')[1:]
            devices_connected = [line for line in device_lines if line.strip(
            ) and not line.strip().endswith('unauthorized')]

            if not devices_connected:
                return

        else:
            return
    except FileNotFoundError:
        print("No se puede encontrar el fichero")
        return
    except Exception as e:
        print(f"Error: {e}")
        return


def execute_df_h():

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


def get_information():
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

import subprocess

def actualizar_info_adb():
    """
    Consulta los dispositivos ADB conectados y autorizados.
    Retorna una lista de strings con los identificadores conectados.
    """
    try:
        resultado = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = resultado.stdout.strip().split('\n')

        if len(lines) <= 1:
            return []

        device_lines = lines[1:]
        devices_connected = []
        for line in device_lines:
            if line.strip() and not line.strip().endswith("unauthorized"):
                device_id = line.split()[0]
                devices_connected.append(device_id)

        return devices_connected

    except FileNotFoundError:
        print("Error: no se encontró el comando 'adb'.")
        return []
    except subprocess.TimeoutExpired:
        print("Error: tiempo de espera agotado al consultar dispositivos adb.")
        return []
    except Exception as e:
        print(f"Error inesperado al consultar dispositivos adb: {e}")
        return []

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

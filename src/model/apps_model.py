import subprocess

def obtener_apps_instaladas():
    """
    Ejecuta adb para obtener la lista de paquetes instalados.
    Retorna una lista de strings (cada app).
    En caso de error, retorna una lista de apps de ejemplo y el mensaje de error.
    """
    try:
        result = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], text=True)
        return [line.replace("package:", "").strip() for line in result.splitlines()], None
    except Exception as e:
        fallback = [
            "WhatsApp", "YouTube", "Maps", "Facebook", "Instagram",
            "Galería", "Teléfono", "Calculadora"
        ]
        return fallback, str(e)


import subprocess
import re

def execute_df_h():
    """
    Ejecuta 'adb shell df -h' y devuelve una lista de diccionarios con información del uso de disco.
    """
    try:
        result = subprocess.run(
            ["adb", "shell", "df", "-h"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print("Error ejecutando comando df -h")
            return []

        lines = result.stdout.strip().split('\n')
        data_lines = lines[1:] if len(lines) > 1 else []

        info_list = []
        for line in data_lines:
            parts = re.split(r'\s+', line.strip())
            if len(parts) >= 6:
                info = {
                    "filesystem": parts[0],
                    "size": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percentage": parts[4],
                    "mount_point": parts[5]
                }
                info_list.append(info)

        return info_list

    except subprocess.TimeoutExpired:
        print("Tiempo de espera agotado al ejecutar df -h")
        return []
    except Exception as e:
        print(f"Error inesperado en execute_df_h: {e}")
        return []

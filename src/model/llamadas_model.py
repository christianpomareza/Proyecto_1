import subprocess

def obtener_llamadas():
    """
    Retorna el historial de llamadas como una lista de strings usando ADB.

    Devuelve:
        list[str]: Lista con cada línea del log de llamadas o un mensaje de error.
    """
    try:
        resultado = subprocess.check_output(
            ['adb', 'shell', 'content', 'query', '--uri', 'content://call_log/calls'],
            text=True,
            stderr=subprocess.STDOUT
        )
        return resultado.strip().split('\n')
    except Exception as e:
        print(f"[ERROR] No se pudo obtener el historial de llamadas: {e}")
        return ["No se pudo obtener el registro de llamadas."]

import subprocess
from utils import mostrar_ventana

def abrir_contactos(root):
    try:
        resultado = subprocess.check_output(['adb', 'shell', 'ls', '/sdcard/'], text=True)
        mostrar_ventana(root, "Archivos del celular", resultado)
    except Exception as e:
        mostrar_ventana(root, "Error", str(e))

def abrir_llamadas(root):
    mostrar_ventana(root, "Llamadas", "Has abierto Llamadas")

def abrir_ajustes(root):
    mostrar_ventana(root, "Ajustes", "Has abierto Ajustes")

def abrir_apps(root):
    try:
        resultado = subprocess.check_output(['adb', 'shell', 'pm', 'list', 'packages'], text=True)
        mostrar_ventana(root, "Aplicaciones instaladas", resultado)
    except Exception as e:
        mostrar_ventana(root, "Error", str(e))

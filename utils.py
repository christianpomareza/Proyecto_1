import time
import tkinter as tk

def actualizar_hora(root, reloj):
    hora_actual = time.strftime('%H:%M')
    reloj.config(text=hora_actual)
    root.after(1000, lambda: actualizar_hora(root, reloj))

def mostrar_ventana(root, titulo, mensaje):
    ventana = tk.Toplevel(root)
    ventana.title(titulo)
    ventana.geometry("300x400")
    ventana.configure(bg="white")

    texto = tk.Text(ventana, wrap="word", bg="white", fg="black", font=("Arial", 10))
    texto.insert("1.0", mensaje)
    texto.pack(expand=True, fill="both")

import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import pathlib
import sys

class ReportesModel:
    def generar_reporte_pdf(self, llamadas=None, ajustes=None, apps=None):
        # Obtener la carpeta Descargas real en Windows
        if sys.platform.startswith("win"):
            carpeta = os.path.join(os.environ["USERPROFILE"], "Downloads")
        else:
            carpeta = str(pathlib.Path.home() / "Descargas")
        os.makedirs(carpeta, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = os.path.join(carpeta, f"reporte_{timestamp}.pdf")

        c = canvas.Canvas(archivo, pagesize=letter)
        width, height = letter

        # Hoja 1: Índice
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-60, "Forencell: Reporte final")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height-80, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, height-120, "Índice")
        c.setFont("Helvetica", 11)
        y = height-145
        c.drawString(80, y, "1. Introducción")
        y -= 18
        c.drawString(80, y, "2. Resumen de Llamadas")
        y -= 18
        c.drawString(80, y, "3. Ajustes del Dispositivo")
        y -= 18
        c.drawString(80, y, "4. Aplicaciones Disponibles")
        y -= 18
        c.drawString(80, y, "5. Hash de Integridad")
        c.showPage()

        # Hoja 2: Versión para lectura humana
        y = height-60
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, y, "Forencell: Reporte final")
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(60, y, "1. Introducción")
        y -= 18
        c.setFont("Helvetica", 10)
        intro = (
            "Este reporte ha sido generado automáticamente por Forencell para documentar y preservar evidencia digital obtenida de un dispositivo móvil. "
            "A continuación se presenta un resumen estructurado de la información relevante extraída, incluyendo historial de llamadas, ajustes del dispositivo y aplicaciones disponibles al momento de la adquisición."
        )
        for linea in self._wrap_text(intro, 90):
            c.drawString(80, y, linea)
            y -= 13
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "2. Resumen de Llamadas")
        y -= 18
        c.setFont("Helvetica", 10)
        if llamadas:
            resumen_llamadas = str(llamadas)[:300].replace("\n", " ")
            for linea in self._wrap_text(resumen_llamadas, 90):
                c.drawString(80, y, linea)
                y -= 13
        else:
            c.drawString(80, y, "No se pudo obtener el historial de llamadas.")
            y -= 13
        y -= 5
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "3. Ajustes del Dispositivo")
        y -= 18
        c.setFont("Helvetica", 10)
        if ajustes:
            for k, v in ajustes.items():
                c.drawString(80, y, f"{k.replace('_', ' ').capitalize()}: {v}")
                y -= 13
        else:
            c.drawString(80, y, "No se pudo obtener la configuración del dispositivo.")
            y -= 13
        y -= 5
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "4. Aplicaciones Disponibles")
        y -= 18
        c.setFont("Helvetica", 10)
        if apps:
            apps_str = ", ".join(app['text'] for app in apps)
            for linea in self._wrap_text(apps_str, 90):
                c.drawString(80, y, linea)
                y -= 13
        else:
            c.drawString(80, y, "No se pudo obtener la lista de aplicaciones.")
            y -= 13
        y -= 5
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "5. Hash de Integridad")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(80, y, "El hash SHA-256 del archivo PDF se muestra en la ventana de confirmación al finalizar la generación.")
        c.save()

        with open(archivo, "rb") as f:
            hash_valor = hashlib.sha256(f.read()).hexdigest()

        return archivo, hash_valor

    def _wrap_text(self, text, max_chars):
        # Utilidad para dividir texto largo en líneas de longitud máxima
        palabras = text.split()
        lineas = []
        actual = ""
        for palabra in palabras:
            if len(actual) + len(palabra) + 1 > max_chars:
                lineas.append(actual)
                actual = palabra
            else:
                actual += (" " if actual else "") + palabra
        if actual:
            lineas.append(actual)
        return lineas

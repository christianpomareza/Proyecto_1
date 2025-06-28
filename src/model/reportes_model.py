import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import os
import pathlib
import sys
import xml.etree.ElementTree as ET
import re

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

        def draw_header_footer(page_num):
            # Encabezado
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.HexColor("#1565c0"))
            c.drawString(60, height-40, "Forencell: Reporte final")
            c.setFillColor(colors.black)
            # Pie de página
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.grey)
            c.drawRightString(width-60, 30, f"Página {page_num} - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.setFillColor(colors.black)

        page_num = 1
        # No encabezado en ninguna página
        # draw_header_footer(page_num)  # Línea eliminada para todas las páginas

        # Hoja 1: Índice
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#1565c0"))
        c.drawCentredString(width/2, height-70, "Forencell: Reporte final")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height-90, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, height-130, "Índice")
        c.setFont("Helvetica", 11)
        y = height-160
        c.drawString(80, y, "1. Introducción")
        y -= 18
        c.drawString(80, y, "2. Ajustes del Dispositivo")
        y -= 18
        c.drawString(80, y, "3. Aplicaciones Disponibles")
        y -= 18
        c.drawString(80, y, "4. Resumen de Mensajes")
        y -= 18
        c.drawString(80, y, "5. Hash de Integridad")
        c.showPage()
        page_num += 1
        # No encabezado en la segunda página ni en las siguientes

        # Hoja 2: Versión para lectura humana
        y = height-70
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#1565c0"))
        c.drawCentredString(width/2, y, "Forencell: Reporte final")
        c.setFillColor(colors.black)
        y -= 35

        # Introducción
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1976d2"))
        c.drawString(60, y, "1. Introducción")
        c.setFillColor(colors.black)
        y -= 18
        c.setFont("Helvetica", 10)
        intro = (
            "Este reporte ha sido generado automáticamente por Forencell para documentar y preservar evidencia digital obtenida de un dispositivo móvil. "
            "A continuación se presenta un resumen estructurado de la información relevante extraída, incluyendo ajustes del dispositivo, aplicaciones disponibles y los mensajes SMS más recientes."
        )
        for linea in self._wrap_text(intro, 90):
            c.drawString(80, y, linea)
            y -= 13
        y -= 10
        # Sin líneas separadoras

        # Ajustes del Dispositivo
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1976d2"))
        c.drawString(60, y, "2. Ajustes del Dispositivo")
        c.setFillColor(colors.black)
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
        # Sin líneas separadoras

        # Aplicaciones Disponibles
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1976d2"))
        c.drawString(60, y, "3. Aplicaciones Disponibles")
        c.setFillColor(colors.black)
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
        # Sin líneas separadoras

        # Resumen de Mensajes
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1976d2"))
        c.drawString(60, y, "4. Resumen de Mensajes")
        c.setFillColor(colors.black)
        y -= 18
        mensajes = self._obtener_ultimos_20_mensajes_sms(formato_lista=True)
        if isinstance(mensajes, str):
            c.setFont("Helvetica", 10)
            for linea in self._wrap_text(mensajes, 90):
                c.drawString(80, y, linea)
                y -= 13
        else:
            for m in mensajes:
                c.setFont("Helvetica-Bold", 10)
                c.setFillColor(colors.HexColor("#388e3c") if m['tipo'] == "Enviado" else colors.HexColor("#1565c0"))
                c.drawString(80, y, f"{m['fecha']} - {m['tipo']}")
                c.setFillColor(colors.black)
                y -= 13
                c.setFont("Helvetica-Bold", 10)
                c.drawString(100, y, f"Número: {m['contacto']}")
                # Sin subrayado
                y -= 13
                c.setFont("Helvetica", 10)
                for linea in self._wrap_text(m['body'], 90):
                    c.drawString(120, y, linea)
                    y -= 13
                y -= 13
                if y < 80:
                    c.showPage()
                    page_num += 1
                    # No encabezado en nuevas páginas
                    y = height-70
        y -= 5
        # Sin líneas separadoras

        # Hash de Integridad
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#1976d2"))
        c.drawString(60, y, "5. Hash de Integridad")
        c.setFillColor(colors.black)
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(80, y, "El hash SHA-256 del archivo PDF se muestra en la ventana de confirmación al finalizar la generación.")
        c.save()

        with open(archivo, "rb") as f:
            hash_valor = hashlib.sha256(f.read()).hexdigest()

        return archivo, hash_valor

    def _obtener_ultimos_20_mensajes_sms(self, formato_lista=False):
        # Usa la ruta absoluta a la carpeta Backup_mensajes
        ruta_carpeta_xml = r"C:\Users\HP\Desktop\Proyecto_1\Backup_mensajes"
        recent_file = None
        max_timestamp_value = -1
        filename_regex = re.compile(r'sms-(\d{14})\.xml$')
        if not os.path.isdir(ruta_carpeta_xml):
            return "No se encontró la carpeta de mensajes SMS."
        for filename in os.listdir(ruta_carpeta_xml):
            match = filename_regex.search(filename)
            if match:
                timestamp_str = match.group(1)
                try:
                    current_timestamp_value = int(timestamp_str)
                    if current_timestamp_value > max_timestamp_value:
                        max_timestamp_value = current_timestamp_value
                        recent_file = os.path.join(ruta_carpeta_xml, filename)
                except ValueError:
                    continue
        if not recent_file:
            return "No se encontró archivo de mensajes SMS."

        try:
            tree = ET.parse(recent_file)
            root = tree.getroot()
            mensajes = []
            for sms in root.findall('sms'):
                tipo = sms.get('type')
                address = sms.get('address')
                body = sms.get('body')
                timestamp_ms = sms.get('date')
                contact_name = sms.get('contact_name')
                timestamp_int = 0
                if timestamp_ms:
                    try:
                        timestamp_int = int(timestamp_ms)
                    except ValueError:
                        pass
                if not contact_name:
                    contact_name = address
                if not body:
                    body = "[Mensaje vacío]"
                tipo_str = "Recibido" if tipo == "1" else "Enviado" if tipo == "2" else "Otro"
                fecha = datetime.fromtimestamp(timestamp_int / 1000).strftime('%Y-%m-%d %H:%M:%S') if timestamp_int else "Fecha desconocida"
                mensajes.append({
                    "tipo": tipo_str,
                    "contacto": contact_name,
                    "body": body,
                    "fecha": fecha,
                    "timestamp": timestamp_int
                })
            # Ordenar por fecha (timestamp)
            mensajes = sorted(mensajes, key=lambda x: x["timestamp"])
            ultimos_20 = mensajes[-20:] if len(mensajes) >= 20 else mensajes
            if formato_lista:
                return ultimos_20 if ultimos_20 else "No hay mensajes para mostrar."
            # Si no se pide lista, retorna texto plano
            texto = ""
            for m in ultimos_20:
                texto += f"{m['fecha']} - {m['tipo']} - {m['contacto']}:\n{m['body']}\n\n"
            return texto if texto else "No hay mensajes para mostrar."
        except Exception as e:
            return f"Error al leer mensajes: {e}"

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

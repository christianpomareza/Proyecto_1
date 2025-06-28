from ..model.reportes_model import ReportesModel
from ..view.reportes_view import ReportesView
from ..model.llamadas_model import CallLogModel
from ..model.ajustes_model import AjustesModel
from ..model.menu_model import MenuModel

class ReportesController:
    def __init__(self, parent=None):
        self.modelo = ReportesModel()
        self.vista = ReportesView(parent)
        self.llamadas_model = CallLogModel()
        self.ajustes_model = AjustesModel()
        self.menu_model = MenuModel()

    def generar_reporte(self):
        print("✅ Entró a generar_reporte")  # DEBUG
        # Llamadas
        llamadas = self.llamadas_model.get_call_log_xml_from_device() or "No disponible"
        # Ajustes
        ajustes = self.ajustes_model.get_settings()
        # Apps (menú)
        apps = self.menu_model.get_app_icons_data()
        # Generar PDF con toda la info
        archivo, hash_valor = self.modelo.generar_reporte_pdf(
            llamadas=llamadas,
            ajustes=ajustes,
            apps=apps
        )
        self.vista.mostrar_mensaje_hash(archivo, hash_valor)

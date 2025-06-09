# src/controller/menu_controller.py

from ..model.menu_model import MenuModel # Importamos el modelo
from ..view.menu_view import MenuView    # Importamos la vista

class MenuController:
    def __init__(self, main_app_controller): # Recibe directamente el MainController
        self.main_app_controller = main_app_controller # Guarda la referencia
        self.model = MenuModel() # Instancia del modelo
        self.view = MenuView(main_app_controller) # Le pasamos el main_app_controller a la vista
        self._connect_signals()
        self._populate_menu_icons() # Cargar los iconos al iniciar el controlador

    def _connect_signals(self):
        """
        Conecta las señales de la vista con los slots del controlador.
        """
        # La barra de búsqueda puede conectarse aquí si lo deseas.
        # self.view.barra_busqueda.textChanged.connect(self.filter_apps)
        pass

    def _populate_menu_icons(self):
        """
        Obtiene los datos de los iconos de las aplicaciones del modelo
        y se los pasa a la vista para que los dibuje.
        También proporciona el callback de navegación del MainController a la vista.
        """
        app_icons_data = self.model.get_app_icons_data() # Obtener los datos del modelo

        # Pasamos a la vista los datos de los iconos y la función de navegación (change_screen)
        # que debe ser provista por el MainController (el 'parent' de la vista).
        if hasattr(self.view.parent(), 'change_screen'):
            self.view.populate_icons(app_icons_data, self.view.parent().change_screen)
        else:
            print("Advertencia: El padre de MenuView no tiene el método 'change_screen'. Los iconos no se conectarán para la navegación.")

    def get_view(self):
        """
        Retorna la instancia de la vista del menú.
        MainController usará este método para añadir la vista del menú al QStackedWidget.
        """
        return self.view

    # El método update_clock ya no es necesario aquí porque la vista lo maneja directamente.
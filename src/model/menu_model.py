class MenuModel:
    def __init__(self):
        pass

    def get_app_icons_data(self):
        """
        Retorna los datos de los iconos del menú, incluyendo WhatsApp.
        Estructura de cada icono:
        - img: Ruta del icono (assets/)
        - text: Nombre visible
        - color: Color hexadecimal
        - screen_name: Identificador único para navegación
        """
        return [
            {"img": "assets/whatsapp.png", "text": "WhatsApp", "color": "#25D366", "screen_name": "whatsapp"},
            {"img": "assets/playstore.png", "text": "Play Store", "color": "#8BC34A", "screen_name": "apps"},
            {"img": "assets/chrome.png", "text": "Chrome", "color": "#00BCD4", "screen_name": "info"},
            {"img": "assets/settings.png", "text": "Ajustes", "color": "#9E9E9E", "screen_name": "ajustes"},
            {"img": "assets/phone.png", "text": "Llamadas", "color": "#2196F3", "screen_name": "llamadas"},
            {"img": "assets/games.png", "text": "Juegos", "color": "#FF9800", "screen_name": "info"},
            {"img": "assets/amongus.png", "text": "NN", "color": "#F44336", "screen_name": "info"},
            {"img": "assets/memory.png", "text": "Memoria", "color": "#3F51B5", "screen_name": "info"},
            {"img": "assets/cod.png", "text": "NN", "color": "#FFC107", "screen_name": "info"},
            {"img": "assets/music.png", "text": "Música", "color": "#9C27B0", "screen_name": "info"},
            {"img": "assets/freefire.png", "text": "NN", "color": "#FF5722", "screen_name": "info"},
            {"img": "assets/battery.png", "text": "Energía", "color": "#673AB7", "screen_name": "info"},
            # Esta es la entrada que ya tenías y que usaremos
            {"img": "assets/phone.png", "text": "Mensajes", "color": "#2196F3", "screen_name": "mensajes"}
        ]
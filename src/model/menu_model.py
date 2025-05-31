def obtener_apps_menu():
    """
    Retorna una lista de diccionarios con los datos de las apps del menú principal.
    Cada diccionario contiene: imagen, texto, color y nombre de la función asociada.
    """
    return [
        {"img": "assets/playstore.png", "text": "Play Store", "color": "#8BC34A", "func_name": "mostrar_pantalla_apps"},
        {"img": "assets/chrome.png", "text": "Chrome", "color": "#00BCD4", "func_name": "mostrar_info"},
        {"img": "assets/settings.png", "text": "Ajustes", "color": "#9E9E9E", "func_name": "mostrar_pantalla_ajustes"},
        {"img": "assets/phone.png", "text": "Llamadas", "color": "#2196F3", "func_name": "mostrar_pantalla_llamadas"},
        {"img": "assets/games.png", "text": "Juegos", "color": "#FF9800", "func_name": "mostrar_info"},
        {"img": "assets/amongus.png", "text": "Among Us", "color": "#F44336", "func_name": "mostrar_info"},
        {"img": "assets/memory.png", "text": "Memoria", "color": "#3F51B5", "func_name": "mostrar_info"},
        {"img": "assets/cod.png", "text": "Call of Duty", "color": "#FFC107", "func_name": "mostrar_info"},
        {"img": "assets/music.png", "text": "Música", "color": "#9C27B0", "func_name": "mostrar_info"},
        {"img": "assets/freefire.png", "text": "Free Fire", "color": "#FF5722", "func_name": "mostrar_info"},
        {"img": "assets/battery.png", "text": "Energía", "color": "#673AB7", "func_name": "mostrar_info"}
    ]

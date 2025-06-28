import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from model.menu_model import obtener_apps_menu

class TestMenuModel(unittest.TestCase):
    
    def test_obtener_apps_menu_devuelve_lista(self):
        """
        Verifica que obtener_apps_menu() retorne una lista de elementos.
        """
        items = obtener_apps_menu()
        self.assertIsInstance(items, list)

    def test_lista_no_esta_vacia(self):
        """
        Verifica que la lista contenga al menos un ítem.
        """
        items = obtener_apps_menu()
        self.assertGreater(len(items), 0)

    def test_estructura_de_cada_item(self):
        """
        Verifica que cada elemento del menú tenga las claves necesarias.
        """
        items = obtener_apps_menu()
        for item in items:
            self.assertIn('img', item)
            self.assertIn('text', item)
            self.assertIn('color', item)
            self.assertIn('func_name', item)

if __name__ == '__main__':
    unittest.main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from model.apps_model import obtener_apps_instaladas

class TestAppsModel(unittest.TestCase):
    
    def test_obtener_apps_instaladas_devuelve_lista(self):
        apps, error = obtener_apps_instaladas()
        self.assertIsInstance(apps, list)

    def test_lista_de_apps_tiene_contenido_o_fallback(self):
        apps, error = obtener_apps_instaladas()
        self.assertGreater(len(apps), 0)

    def test_formato_apps_es_string(self):
        apps, error = obtener_apps_instaladas()
        self.assertTrue(all(isinstance(app, str) for app in apps))

if __name__ == '__main__':
    unittest.main()

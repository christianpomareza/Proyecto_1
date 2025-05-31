import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from model.ajustes_model import actualizar_info_adb

class TestAjustesModel(unittest.TestCase):
    
    def test_actualizar_info_adb_retorna_lista(self):
        """
        Verifica que actualizar_info_adb siempre retorne una lista (vacía o con dispositivos).
        """
        dispositivos = actualizar_info_adb()
        self.assertIsInstance(dispositivos, list)

    def test_elementos_son_cadenas(self):
        """
        Si hay dispositivos conectados, todos los elementos deben ser cadenas de texto.
        """
        dispositivos = actualizar_info_adb()
        if dispositivos:  # solo verifica contenido si hay alguno
            self.assertTrue(all(isinstance(d, str) for d in dispositivos))

if __name__ == '__main__':
    unittest.main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from model.llamadas_model import obtener_llamadas

class TestLlamadasModel(unittest.TestCase):
    
    def test_obtener_llamadas_retorna_lista(self):
        """
        Verifica que la función siempre retorne una lista (con o sin datos reales).
        """
        llamadas = obtener_llamadas()
        self.assertIsInstance(llamadas, list)

    def test_elementos_son_cadenas(self):
        """
        Si hay llamadas disponibles, cada una debe ser una cadena de texto.
        """
        llamadas = obtener_llamadas()
        if llamadas:
            self.assertTrue(all(isinstance(c, str) for c in llamadas))

if __name__ == '__main__':
    unittest.main()

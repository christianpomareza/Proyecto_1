import unittest
from unittest.mock import patch
import tkinter as tk
import funciones


class TestFunciones(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    @patch("utils.mostrar_ventana")
    def test_abrir_contactos(self, mock_ventana):
        funciones.abrir_contactos(self.root)
        mock_ventana.assert_called_once()
        args = mock_ventana.call_args[0]
        self.assertEqual(args[1], "Contactos")

    @patch("utils.mostrar_ventana")
    def test_abrir_llamadas(self, mock_ventana):
        funciones.abrir_llamadas(self.root)
        mock_ventana.assert_called_once()
        args = mock_ventana.call_args[0]
        self.assertEqual(args[1], "Llamadas")

    @patch("utils.mostrar_ventana")
    def test_abrir_ajustes(self, mock_ventana):
        funciones.abrir_ajustes(self.root)
        mock_ventana.assert_called_once()
        args = mock_ventana.call_args[0]
        self.assertEqual(args[1], "Ajustes")

    @patch("utils.mostrar_ventana")
    def test_abrir_apps(self, mock_ventana):
        funciones.abrir_apps(self.root)
        mock_ventana.assert_called_once()
        args = mock_ventana.call_args[0]
        self.assertEqual(args[1], "Apps")


if __name__ == "__main__":
    unittest.main()


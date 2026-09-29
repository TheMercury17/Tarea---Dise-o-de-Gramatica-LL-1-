"""
Pruebas Unitarias para el Analizador Semántico y Evaluador (Intérprete)
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import math
import unittest
from src.lexer import Lexer
from src.parser_ll1 import ParserLL1
from src.semantic import SymbolTable, SemanticError
from src.interpreter import Interpreter


class TestSemantic(unittest.TestCase):

    def ejecutar(self, codigo: str) -> Interpreter:
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        interp = Interpreter()
        interp.evaluate(ast)
        return interp

    def test_operaciones_aritmeticas_basicas(self):
        codigo = """
        suma = 15 + 27;
        resta = 50 - 18;
        multi = 6 * 7;
        divi = 100 / 4;
        modulo = 29 % 5;
        """
        interp = self.ejecutar(codigo)
        vars = interp.symbol_table.get_all()
        self.assertEqual(vars["suma"], 42)
        self.assertEqual(vars["resta"], 32)
        self.assertEqual(vars["multi"], 42)
        self.assertEqual(vars["divi"], 25)
        self.assertEqual(vars["modulo"], 4)

    def test_valor_absoluto(self):
        codigo = """
        a = abs(-42);
        b = abs(15);
        c = abs(5 - 20);
        """
        interp = self.ejecutar(codigo)
        vars = interp.symbol_table.get_all()
        self.assertEqual(vars["a"], 42)
        self.assertEqual(vars["b"], 15)
        self.assertEqual(vars["c"], 15)

    def test_funciones_trigonometricas(self):
        codigo = f"""
        pi = {math.pi};
        s0 = sin(0);
        c0 = cos(0);
        t0 = tan(0);
        s_pi_2 = sin(pi / 2);
        c_pi = cos(pi);
        """
        interp = self.ejecutar(codigo)
        vars = interp.symbol_table.get_all()
        self.assertAlmostEqual(vars["s0"], 0.0, places=6)
        self.assertAlmostEqual(vars["c0"], 1.0, places=6)
        self.assertAlmostEqual(vars["t0"], 0.0, places=6)
        self.assertAlmostEqual(vars["s_pi_2"], 1.0, places=6)
        self.assertAlmostEqual(vars["c_pi"], -1.0, places=6)

    def test_asignacion_y_reutilizacion_de_variables(self):
        codigo = """
        radio = 5;
        altura = 10;
        volumen_cilindro = 3.14159265 * (radio * radio) * altura;
        mitad = volumen_cilindro / 2;
        """
        interp = self.ejecutar(codigo)
        vars = interp.symbol_table.get_all()
        esperado_vol = 3.14159265 * 25 * 10
        self.assertAlmostEqual(vars["volumen_cilindro"], esperado_vol, places=4)
        self.assertAlmostEqual(vars["mitad"], esperado_vol / 2, places=4)

    def test_error_semantico_variable_no_definida(self):
        codigo = "y = x + 10;"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        interp = Interpreter()
        with self.assertRaises(SemanticError) as ctx:
            interp.evaluate(ast)
        self.assertIn("La variable 'x' no ha sido definida", str(ctx.exception))

    def test_error_semantico_division_por_cero(self):
        codigo = "x = 10 / (5 - 5);"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        interp = Interpreter()
        with self.assertRaises(SemanticError) as ctx:
            interp.evaluate(ast)
        self.assertIn("División por cero no permitida", str(ctx.exception))

    def test_error_semantico_modulo_por_cero(self):
        codigo = "x = 10 % 0;"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        interp = Interpreter()
        with self.assertRaises(SemanticError) as ctx:
            interp.evaluate(ast)
        self.assertIn("módulo (%) por cero", str(ctx.exception))

    def test_error_semantico_tangente_asintota(self):
        # tan(pi / 2)
        codigo = f"t_indefinida = tan({math.pi / 2});"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        interp = Interpreter()
        with self.assertRaises(SemanticError) as ctx:
            interp.evaluate(ast)
        self.assertIn("asíntota vertical", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

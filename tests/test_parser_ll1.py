"""
Pruebas Unitarias para el Analizador Sintáctico LL(1) y Gramática Formal
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import unittest
from gramatica import crear_gramatica_proyecto
from src.lexer import Lexer
from src.parser_ll1 import ParserLL1, ParserTablaLL1, ParserSyntaxError
from src.ast_nodes import AssignNode, ExprStmtNode, BinaryOpNode, UnaryOpNode, FunctionCallNode


class TestParserLL1(unittest.TestCase):

    def setUp(self):
        self.gramatica = crear_gramatica_proyecto()
        self.primeros = self.gramatica.calcular_primeros()
        self.siguientes = self.gramatica.calcular_siguientes(self.primeros)
        self.predicciones = self.gramatica.calcular_prediccion(self.primeros, self.siguientes)
        self.parser_tabla = ParserTablaLL1(self.gramatica)

    def test_gramatica_condicion_ll1(self):
        """Verifica que la gramática cumpla estrictamente la condición LL(1)."""
        es_ll1, conflictos = self.gramatica.verificar_ll1(self.predicciones)
        self.assertTrue(es_ll1, f"La gramática presenta conflictos LL(1): {conflictos}")
        self.assertEqual(len(conflictos), 0)

    def test_tabla_analisis_sin_conflictos(self):
        """Verifica que la tabla de análisis sintáctico M[A, a] no tenga celdas con doble regla."""
        tabla, conflictos = self.gramatica.construir_tabla_ll1(self.predicciones)
        self.assertEqual(len(conflictos), 0)
        self.assertGreater(len(tabla), 0)

    def test_parser_tabla_predictiva_valido(self):
        """Verifica que el algoritmo con Pila y Tabla reconozca sentencias válidas."""
        casos = [
            "x = 5;",
            "y = x + 10 * 2;",
            "z = abs(-15) % 4;",
            "res = sin(0) + cos(0) + tan(0);",
            "val = - (5 + 2) * 3;",
            "x = 1; y = 2; z = x + y; z;"
        ]
        for caso in casos:
            with self.subTest(caso=caso):
                tokens = Lexer(caso).tokenize()
                traza = self.parser_tabla.analizar_con_traza(tokens)
                self.assertGreater(len(traza), 0)
                # El último paso debe indicar aceptación
                self.assertIn("Aceptar", traza[-1]["accion"])

    def test_parser_ast_asociatividad_izquierda(self):
        """Verifica que '10 - 4 - 2' se agrupe como ((10 - 4) - 2)."""
        codigo = "10 - 4 - 2;"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, ExprStmtNode)

        expr = stmt.expr
        self.assertIsInstance(expr, BinaryOpNode)
        self.assertEqual(expr.op, "-")
        # El subárbol izquierdo debe ser también BinaryOpNode con '-'
        self.assertIsInstance(expr.left, BinaryOpNode)
        self.assertEqual(expr.left.op, "-")

    def test_parser_ast_precedencia_multiplicacion_suma(self):
        """Verifica que '2 + 3 * 4' se agrupe como (2 + (3 * 4))."""
        codigo = "2 + 3 * 4;"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        stmt = ast.statements[0]
        expr = stmt.expr
        self.assertIsInstance(expr, BinaryOpNode)
        self.assertEqual(expr.op, "+")
        self.assertIsInstance(expr.right, BinaryOpNode)
        self.assertEqual(expr.right.op, "*")

    def test_parser_funciones_anidadas(self):
        """Verifica el análisis de funciones matemáticas compuestas."""
        codigo = "val = abs(sin(cos(x + 1)));"
        tokens = Lexer(codigo).tokenize()
        ast = ParserLL1(tokens).parse()
        self.assertIsInstance(ast.statements[0], AssignNode)
        func_abs = ast.statements[0].expr
        self.assertIsInstance(func_abs, FunctionCallNode)
        self.assertEqual(func_abs.func_name, "abs")
        func_sin = func_abs.arg
        self.assertIsInstance(func_sin, FunctionCallNode)
        self.assertEqual(func_sin.func_name, "sin")

    def test_error_sintactico_sin_punto_y_coma(self):
        codigo = "x = 10"
        tokens = Lexer(codigo).tokenize()
        with self.assertRaises(ParserSyntaxError):
            ParserLL1(tokens).parse()

    def test_error_sintactico_parentesis_desbalanceado(self):
        codigo = "x = (5 + 2 * 3;"
        tokens = Lexer(codigo).tokenize()
        with self.assertRaises(ParserSyntaxError):
            ParserLL1(tokens).parse()

    def test_error_sintactico_operador_duplicado(self):
        codigo = "x = 5 + * 2;"
        tokens = Lexer(codigo).tokenize()
        with self.assertRaises(ParserSyntaxError):
            ParserLL1(tokens).parse()


if __name__ == "__main__":
    unittest.main()

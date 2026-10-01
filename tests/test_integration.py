"""
Pruebas de Integración de Extremo a Extremo (Pipeline Completo: Léxico -> Sintáctico -> Semántico)
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import math
import unittest
from src.lexer import Lexer
from src.parser_ll1 import ParserLL1, ParserTablaLL1
from src.interpreter import Interpreter


class TestIntegration(unittest.TestCase):

    def test_pipeline_completo_con_todas_las_caracteristicas(self):
        """
        Prueba completa que integra:
        - Asignaciones de variables
        - Operaciones +, -, *, /, %
        - abs()
        - sin(), cos(), tan()
        - Expresiones evaluadas de forma independiente
        - Validación por tabla predictiva LL(1) con pila
        - Evaluación semántica
        """
        programa = """
        // 1. Asignaciones y Aritmética
        a = 20;
        b = 6;
        suma = a + b;
        resta = a - b;
        prod = a * b;
        divi = a / b;
        mod = a % b;

        // 2. Valor Absoluto y Raíz Cuadrada
        diferencia_negativa = b - a;
        val_abs = abs(diferencia_negativa);
        raiz_c = sqrt(suma + 10);

        // 3. Funciones Trigonométricas
        angulo_cero = 0;
        seno_0 = sin(angulo_cero);
        coseno_0 = cos(angulo_cero);
        tangente_0 = tan(angulo_cero);

        // 4. Expresión Combinada
        resultado_final = (val_abs + mod + raiz_c) * 2 - (coseno_0 * 4);
        resultado_final;
        """

        # Paso 1: Léxico
        lexer = Lexer(programa)
        tokens = lexer.tokenize()
        self.assertGreater(len(tokens), 50)

        # Paso 2: Validación sintáctica con tabla LL(1) formal
        parser_tabla = ParserTablaLL1()
        traza = parser_tabla.analizar_con_traza(tokens)
        self.assertIn("Aceptar", traza[-1]["accion"])

        # Paso 3: Análisis sintáctico con AST y evaluación semántica
        parser_ast = ParserLL1(tokens)
        arbol = parser_ast.parse()
        self.assertEqual(len(arbol.statements), 16)

        interprete = Interpreter()
        resultados = interprete.evaluate(arbol)

        # Paso 4: Verificaciones de valores
        vars_finales = interprete.symbol_table.get_all()
        self.assertEqual(vars_finales["suma"], 26)
        self.assertEqual(vars_finales["resta"], 14)
        self.assertEqual(vars_finales["prod"], 120)
        self.assertAlmostEqual(vars_finales["divi"], 20 / 6, places=4)
        self.assertEqual(vars_finales["mod"], 2)
        self.assertEqual(vars_finales["val_abs"], 14)
        self.assertEqual(vars_finales["raiz_c"], 6)
        self.assertEqual(vars_finales["seno_0"], 0.0)
        self.assertEqual(vars_finales["coseno_0"], 1.0)
        self.assertEqual(vars_finales["tangente_0"], 0.0)

        # resultado_final = (14 + 2 + 6) * 2 - (1.0 * 4) = 22 * 2 - 4 = 44 - 4 = 40
        self.assertEqual(vars_finales["resultado_final"], 40)
        self.assertEqual(resultados[-1], 40)


if __name__ == "__main__":
    unittest.main()

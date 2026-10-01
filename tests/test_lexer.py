"""
Pruebas Unitarias para el Analizador Léxico (Lexer)
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import unittest
from src.tokens import TokenType
from src.lexer import Lexer, LexerError


class TestLexer(unittest.TestCase):

    def test_tokens_aritmeticos_basicos(self):
        codigo = "+ - * / % = ; ( )"
        tokens = Lexer(codigo).tokenize()
        tipos = [t.type for t in tokens]
        esperados = [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.DIV,
            TokenType.MOD,
            TokenType.ASSIGN,
            TokenType.SEMICOLON,
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.EOF
        ]
        self.assertEqual(tipos, esperados)

    def test_numeros_enteros_y_decimales(self):
        codigo = "42 3.14159 0.001 1e3"
        tokens = Lexer(codigo).tokenize()
        valores = [t.value for t in tokens if t.type == TokenType.NUM]
        self.assertEqual(valores, ["42", "3.14159", "0.001", "1e3"])

    def test_palabras_clave_matematicas(self):
        codigo = "abs sqrt raiz sin sen cos tan"
        tokens = Lexer(codigo).tokenize()
        tipos = [t.type for t in tokens if t.type != TokenType.EOF]
        esperados = [
            TokenType.ABS,
            TokenType.SQRT,
            TokenType.SQRT, # 'raiz' mapeado a SQRT
            TokenType.SIN,
            TokenType.SIN,  # 'sen' mapeado a SIN
            TokenType.COS,
            TokenType.TAN
        ]
        self.assertEqual(tipos, esperados)

    def test_identificadores(self):
        codigo = "x mi_variable contador2 alfa_beta"
        tokens = Lexer(codigo).tokenize()
        ids = [(t.type, t.value) for t in tokens if t.type != TokenType.EOF]
        self.assertTrue(all(tipo == TokenType.ID for tipo, _ in ids))
        self.assertEqual([val for _, val in ids], ["x", "mi_variable", "contador2", "alfa_beta"])

    def test_asignacion_con_expresion(self):
        codigo = "x = abs(-5) + sin(3.14) * 2;"
        tokens = Lexer(codigo).tokenize()
        tipos = [t.type for t in tokens]
        esperados = [
            TokenType.ID,
            TokenType.ASSIGN,
            TokenType.ABS,
            TokenType.LPAREN,
            TokenType.MINUS,
            TokenType.NUM,
            TokenType.RPAREN,
            TokenType.PLUS,
            TokenType.SIN,
            TokenType.LPAREN,
            TokenType.NUM,
            TokenType.RPAREN,
            TokenType.MUL,
            TokenType.NUM,
            TokenType.SEMICOLON,
            TokenType.EOF
        ]
        self.assertEqual(tipos, esperados)

    def test_comentarios_ignorados(self):
        codigo = """
        // Este es un comentario de una línea
        x = 10; # Otro comentario con numeral
        y = 20;
        """
        tokens = Lexer(codigo).tokenize()
        valores_no_eof = [t.value for t in tokens if t.type != TokenType.EOF]
        self.assertEqual(valores_no_eof, ["x", "=", "10", ";", "y", "=", "20", ";"])

    def test_error_lexico_caracter_invalido(self):
        codigo = "x = 10 @ 5;"
        with self.assertRaises(LexerError) as ctx:
            Lexer(codigo).tokenize()
        self.assertIn("Carácter no reconocido '@'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

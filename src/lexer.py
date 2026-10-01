"""
Módulo del Analizador Léxico (Lexer)
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import re
from typing import List
from .tokens import Token, TokenType


class LexerError(Exception):
    """Excepción para errores detectados durante el análisis léxico."""
    def __init__(self, mensaje: str, linea: int, columna: int):
        super().__init__(f"Error Léxico [Línea {linea}, Columna {columna}]: {mensaje}")
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna


class Lexer:
    """
    Analizador léxico que convierte el código fuente en un flujo ordenado de Tokens.
    Garantiza el reconocimiento de identificadores, palabras clave (sin, sen, cos, tan, abs),
    números enteros y reales, operadores y signos de puntuación.
    """

    RESERVADAS = {
        "abs": TokenType.ABS,
        "sqrt": TokenType.SQRT,
        "raiz": TokenType.SQRT,  # Soporte de notación en español
        "sin": TokenType.SIN,
        "sen": TokenType.SIN,  # Soporte de notación en español
        "cos": TokenType.COS,
        "tan": TokenType.TAN,
    }

    # Especificación de patrones léxicos
    REGLAS = [
        ("COMMENT_LINE", r'//[^\n]*|#[^\n]*'),       # Comentarios // o #
        ("NUM",          r'\d+(\.\d+)?([eE][+-]?\d+)?'), # Enteros y decimales con notación científica
        ("ID",           r'[a-zA-Z_][a-zA-Z0-9_]*'),   # Identificadores y palabras clave
        ("ASSIGN",       r'='),                         # Asignación
        ("PLUS",         r'\+'),                        # Suma
        ("MINUS",        r'-'),                         # Resta / Menos unario
        ("MUL",          r'\*'),                        # Multiplicación
        ("DIV",          r'/'),                         # División
        ("MOD",          r'%'),                         # Módulo
        ("LPAREN",       r'\('),                        # Paréntesis izquierdo
        ("RPAREN",       r'\)'),                        # Paréntesis derecho
        ("SEMICOLON",    r';'),                         # Fin de sentencia
        ("NEWLINE",      r'\n'),                        # Salto de línea para rastreo
        ("WS",           r'[ \t\r]+'),                  # Espacios y tabulaciones
        ("MISMATCH",     r'.'),                         # Cualquier otro carácter erróneo
    ]

    def __init__(self, texto: str):
        self.texto = texto
        self.regex = re.compile('|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.REGLAS))

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        linea = 1
        inicio_linea = 0

        for match in self.regex.finditer(self.texto):
            tipo_coincidencia = match.lastgroup
            valor = match.group()
            pos = match.start()
            columna = pos - inicio_linea + 1

            if tipo_coincidencia == "WS" or tipo_coincidencia == "COMMENT_LINE":
                continue
            elif tipo_coincidencia == "NEWLINE":
                linea += 1
                inicio_linea = match.end()
            elif tipo_coincidencia == "NUM":
                tokens.append(Token(TokenType.NUM, valor, linea, columna, pos))
            elif tipo_coincidencia == "ID":
                # Verificar si es función matemática reservada o identificador de variable
                tipo_token = self.RESERVADAS.get(valor.lower(), TokenType.ID)
                # Si es 'sen' o 'raiz', normalizamos internamente para coincidir con los terminales de la gramática
                val_lower = valor.lower()
                if val_lower == "sen":
                    val_normalizado = "sin"
                elif val_lower == "raiz":
                    val_normalizado = "sqrt"
                else:
                    val_normalizado = valor
                tokens.append(Token(tipo_token, val_normalizado, linea, columna, pos))
            elif tipo_coincidencia == "ASSIGN":
                tokens.append(Token(TokenType.ASSIGN, valor, linea, columna, pos))
            elif tipo_coincidencia == "PLUS":
                tokens.append(Token(TokenType.PLUS, valor, linea, columna, pos))
            elif tipo_coincidencia == "MINUS":
                tokens.append(Token(TokenType.MINUS, valor, linea, columna, pos))
            elif tipo_coincidencia == "MUL":
                tokens.append(Token(TokenType.MUL, valor, linea, columna, pos))
            elif tipo_coincidencia == "DIV":
                tokens.append(Token(TokenType.DIV, valor, linea, columna, pos))
            elif tipo_coincidencia == "MOD":
                tokens.append(Token(TokenType.MOD, valor, linea, columna, pos))
            elif tipo_coincidencia == "LPAREN":
                tokens.append(Token(TokenType.LPAREN, valor, linea, columna, pos))
            elif tipo_coincidencia == "RPAREN":
                tokens.append(Token(TokenType.RPAREN, valor, linea, columna, pos))
            elif tipo_coincidencia == "SEMICOLON":
                tokens.append(Token(TokenType.SEMICOLON, valor, linea, columna, pos))
            elif tipo_coincidencia == "MISMATCH":
                raise LexerError(f"Carácter no reconocido '{valor}'", linea, columna)

        columna_final = len(self.texto) - inicio_linea + 1
        tokens.append(Token(TokenType.EOF, "$", linea, columna_final, len(self.texto)))
        return tokens

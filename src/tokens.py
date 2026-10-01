"""
Módulo de Definición de Tokens y Tipos Léxicos
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

from enum import Enum
from typing import Any, NamedTuple


class TokenType(str, Enum):
    # Identificadores y literales
    ID = "id"
    NUM = "num"

    # Operadores aritméticos
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"

    # Asignación
    ASSIGN = "="

    # Funciones matemáticas y trigonométricas
    ABS = "abs"
    SQRT = "sqrt"
    SIN = "sin"
    COS = "cos"
    TAN = "tan"

    # Delimitadores
    LPAREN = "("
    RPAREN = ")"
    SEMICOLON = ";"

    # Fin de entrada
    EOF = "$"


class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int
    pos: int

    def __repr__(self) -> str:
        return f"Token({self.type.value}, '{self.value}', línea {self.line}:{self.column})"

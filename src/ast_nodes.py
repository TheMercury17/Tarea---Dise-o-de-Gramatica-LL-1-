"""
Módulo de Nodos del Árbol de Sintaxis Abstracta (AST)
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

from abc import ABC, abstractmethod
from typing import List, Any


class ASTNode(ABC):
    """Clase base abstracta para todos los nodos del AST."""
    @abstractmethod
    def __repr__(self) -> str:
        pass


class ProgramNode(ASTNode):
    """Representa el programa completo compuesto por una lista de sentencias."""
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def __repr__(self) -> str:
        return f"ProgramNode(statements={self.statements})"


class AssignNode(ASTNode):
    """Representa una sentencia de asignación: id = Expr ;"""
    def __init__(self, var_name: str, expr: ASTNode):
        self.var_name = var_name
        self.expr = expr

    def __repr__(self) -> str:
        return f"AssignNode({self.var_name} = {self.expr})"


class ExprStmtNode(ASTNode):
    """Representa una expresión evaluada como sentencia independiente: Expr ;"""
    def __init__(self, expr: ASTNode):
        self.expr = expr

    def __repr__(self) -> str:
        return f"ExprStmtNode({self.expr})"


class BinaryOpNode(ASTNode):
    """Representa una operación binaria: left (op) right (+, -, *, /, %)."""
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryOpNode({self.left} {self.op} {self.right})"


class UnaryOpNode(ASTNode):
    """Representa una operación unaria (menos unario): - operand."""
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryOpNode({self.op}{self.operand})"


class FunctionCallNode(ASTNode):
    """Representa una invocación a función matemática: abs, sin, cos, tan."""
    def __init__(self, func_name: str, arg: ASTNode):
        self.func_name = func_name.lower()
        self.arg = arg

    def __repr__(self) -> str:
        return f"FunctionCallNode({self.func_name}({self.arg}))"


class NumberNode(ASTNode):
    """Representa un valor numérico literal (entero o punto flotante)."""
    def __init__(self, value: float):
        self.value = value

    def __repr__(self) -> str:
        return f"NumberNode({self.value})"


class VariableNode(ASTNode):
    """Representa la lectura de una variable por su identificador."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"VariableNode({self.name})"

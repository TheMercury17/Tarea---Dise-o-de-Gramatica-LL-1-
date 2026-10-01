"""
Módulo del Intérprete y Evaluador Semántico
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

import math
from typing import Any, List, Optional
from .ast_nodes import (
    ASTNode, ProgramNode, AssignNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, FunctionCallNode, NumberNode, VariableNode
)
from .semantic import SymbolTable, SemanticError


class Interpreter:
    """
    Recorre y evalúa el Árbol de Sintaxis Abstracta (AST) aplicando
    las reglas semánticas del lenguaje.
    """
    def __init__(self, symbol_table: Optional[SymbolTable] = None):
        self.symbol_table = symbol_table if symbol_table is not None else SymbolTable()
        self.output_history: List[str] = []

    def evaluate(self, node: ASTNode) -> Any:
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No existe método de evaluación para el nodo {type(node).__name__}")

    def visit_ProgramNode(self, node: ProgramNode) -> List[Any]:
        results = []
        for stmt in node.statements:
            res = self.evaluate(stmt)
            if res is not None:
                results.append(res)
        return results

    def visit_AssignNode(self, node: AssignNode) -> Any:
        val = self.evaluate(node.expr)
        self.symbol_table.set(node.var_name, val)
        msg = f"[Asignación] {node.var_name} = {val}"
        self.output_history.append(msg)
        return val

    def visit_ExprStmtNode(self, node: ExprStmtNode) -> Any:
        val = self.evaluate(node.expr)
        msg = f"[Expresión] Resultado: {val}"
        self.output_history.append(msg)
        return val

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        left_val = self.evaluate(node.left)
        right_val = self.evaluate(node.right)
        op = node.op

        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise SemanticError("División por cero no permitida.")
            res = left_val / right_val
            return int(res) if isinstance(res, float) and res.is_integer() else res
        elif op == '%':
            if right_val == 0:
                raise SemanticError("Operación módulo (%) por cero no permitida.")
            return left_val % right_val
        else:
            raise SemanticError(f"Operador binario desconocido: '{op}'")

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> Any:
        val = self.evaluate(node.operand)
        if node.op == '-':
            return -val
        raise SemanticError(f"Operador unario desconocido: '{node.op}'")

    def visit_FunctionCallNode(self, node: FunctionCallNode) -> Any:
        val = self.evaluate(node.arg)
        func = node.func_name

        if func == "abs":
            return abs(val)
        elif func == "sqrt":
            if val < 0:
                raise SemanticError(f"Raíz cuadrada de un número negativo ({val}) no está permitida en los números reales.")
            res = math.sqrt(val)
            return int(res) if isinstance(res, float) and res.is_integer() else res
        elif func == "sin":
            res = math.sin(val)
            # Redondeo para valores trigonométricos típicos (ej: sin(pi) ~ 0)
            return 0.0 if abs(res) < 1e-12 else res
        elif func == "cos":
            res = math.cos(val)
            return 0.0 if abs(res) < 1e-12 else res
        elif func == "tan":
            # Verificar asíntotas: cos(val) close to 0
            cos_val = math.cos(val)
            if abs(cos_val) < 1e-12:
                raise SemanticError(f"La tangente no está definida en {val} radianes (asíntota vertical).")
            res = math.tan(val)
            return 0.0 if abs(res) < 1e-12 else res
        else:
            raise SemanticError(f"Función matemática no reconocida: '{func}'")

    def visit_NumberNode(self, node: NumberNode) -> Any:
        return node.value

    def visit_VariableNode(self, node: VariableNode) -> Any:
        return self.symbol_table.get(node.name)

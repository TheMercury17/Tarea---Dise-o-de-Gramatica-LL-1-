"""
Módulo del Analizador Sintáctico LL(1) (Parser)
Implementa tanto el Parser Predictivo basado en Tabla y Pila (Algoritmo Clásico),
como la Construcción del Árbol de Sintaxis Abstracta (AST).

Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

from typing import List, Dict, Tuple, Any, Optional
from .tokens import Token, TokenType
from .ast_nodes import (
    ASTNode, ProgramNode, AssignNode, ExprStmtNode,
    BinaryOpNode, UnaryOpNode, FunctionCallNode, NumberNode, VariableNode
)
from gramatica import Gramatica, Regla, crear_gramatica_proyecto, EPSILON, FIN_CADENA


class ParserSyntaxError(Exception):
    """Excepción para errores sintácticos con información de línea y columna."""
    def __init__(self, mensaje: str, token: Optional[Token] = None):
        if token:
            super().__init__(f"Error Sintáctico [Línea {token.line}, Columna {token.column}]: {mensaje} (Token recibido: {token.type.value} '{token.value}')")
        else:
            super().__init__(f"Error Sintáctico: {mensaje}")
        self.token = token


class ParserTablaLL1:
    """
    Parser Predictivo no recursivo dirigido por Tabla de Análisis LL(1) y Pila.
    Aplica el algoritmo formal de reconocimiento de la teoría de compiladores:
    M[NoTerminal, Terminal] -> Regla.
    """
    def __init__(self, gramatica: Optional[Gramatica] = None):
        self.gramatica = gramatica or crear_gramatica_proyecto()
        self.primeros = self.gramatica.calcular_primeros()
        self.siguientes = self.gramatica.calcular_siguientes(self.primeros)
        self.predicciones = self.gramatica.calcular_prediccion(self.primeros, self.siguientes)
        self.tabla, self.conflictos = self.gramatica.construir_tabla_ll1(self.predicciones)

        if self.conflictos:
            raise ValueError(f"La gramática presenta conflictos en la tabla LL(1): {self.conflictos}")

    def analizar_con_traza(self, tokens: List[Token]) -> List[Dict[str, Any]]:
        """
        Ejecuta el reconocimiento paso a paso mostrando la traza de la pila,
        la entrada restante y la regla aplicada.
        """
        pila: List[str] = [FIN_CADENA, self.gramatica.inicial]
        cursor = 0
        traza: List[Dict[str, Any]] = []
        paso = 1

        while len(pila) > 0:
            tope = pila[-1]
            token_actual = tokens[cursor]
            terminal_actual = token_actual.type.value

            registro = {
                "paso": paso,
                "pila": list(pila),
                "entrada": [t.type.value for t in tokens[cursor:]],
                "token": token_actual,
                "accion": ""
            }

            if tope == FIN_CADENA and terminal_actual == FIN_CADENA:
                registro["accion"] = "Aceptar ($ coincide con fin de entrada)"
                traza.append(registro)
                pila.pop()
                break

            elif tope == terminal_actual:
                registro["accion"] = f"Emparejar terminal '{terminal_actual}'"
                traza.append(registro)
                pila.pop()
                cursor += 1

            elif self.gramatica.es_terminal(tope):
                msg = f"Se esperaba el terminal '{tope}', pero se encontró '{terminal_actual}'"
                registro["accion"] = f"ERROR: {msg}"
                traza.append(registro)
                raise ParserSyntaxError(msg, token_actual)

            else:
                # Es un No Terminal
                clave = (tope, terminal_actual)
                if clave in self.tabla:
                    regla = self.tabla[clave]
                    registro["accion"] = f"Aplicar Regla ({regla.id}): {regla.cabeza} -> {' '.join(regla.cuerpo)}"
                    traza.append(registro)
                    pila.pop()

                    if not regla.es_epsilon():
                        # Apilar en orden inverso
                        for simbolo in reversed(regla.cuerpo):
                            pila.append(simbolo)
                else:
                    validos = [t for (nt, t) in self.tabla.keys() if nt == tope]
                    msg = f"No existe transición en M[{tope}, {terminal_actual}]. Tokens esperados: {sorted(validos)}"
                    registro["accion"] = f"ERROR: {msg}"
                    traza.append(registro)
                    raise ParserSyntaxError(msg, token_actual)

            paso += 1

        return traza


class ParserLL1:
    """
    Parser Predictivo LL(1) que realiza el reconocimiento y genera
    el Árbol de Sintaxis Abstracta (AST) para el análisis semántico.
    Garantiza estricta correspondencia con las reglas y conjuntos de predicción LL(1).
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @classmethod
    def from_text(cls, text: str) -> "ParserLL1":
        from .lexer import Lexer
        tokens = Lexer(text).tokenize()
        return cls(tokens)

    @property
    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def match(self, expected_type: TokenType) -> Token:
        """Verifica y consume el token esperado; en caso contrario lanza error sintáctico."""
        token = self.current_token
        if token.type == expected_type:
            self.pos += 1
            return token
        else:
            raise ParserSyntaxError(
                f"Se esperaba token '{expected_type.value}', pero se obtuvo '{token.type.value}'",
                token
            )

    def parse(self) -> ProgramNode:
        """Punto de entrada: Program -> StmtList $"""
        statements = self.parse_stmt_list()
        self.match(TokenType.EOF)
        return ProgramNode(statements)

    def parse_stmt_list(self) -> List[ASTNode]:
        """
        StmtList -> Stmt StmtList | ε
        PRED(Stmt StmtList) = { id, num, (, abs, sin, cos, tan, - }
        PRED(ε) = { $ }
        """
        statements: List[ASTNode] = []
        terminales_stmt = {
            TokenType.ID, TokenType.NUM, TokenType.LPAREN,
            TokenType.ABS, TokenType.SQRT, TokenType.SIN, TokenType.COS, TokenType.TAN, TokenType.MINUS
        }

        while self.current_token.type in terminales_stmt:
            stmt = self.parse_stmt()
            statements.append(stmt)

        return statements

    def parse_stmt(self) -> ASTNode:
        """
        Stmt -> id StmtTail
              | NonIdFactor TermPrime ExprPrime ;
        """
        token = self.current_token

        if token.type == TokenType.ID:
            id_token = self.match(TokenType.ID)
            return self.parse_stmt_tail(id_token.value)
        else:
            # NonIdFactor Term' Expr' ;
            factor = self.parse_non_id_factor()
            term = self.parse_term_prime(factor)
            expr = self.parse_expr_prime(term)
            self.match(TokenType.SEMICOLON)
            return ExprStmtNode(expr)

    def parse_stmt_tail(self, var_name: str) -> ASTNode:
        """
        StmtTail -> = Expr ;
                  | TermPrime ExprPrime ;
        """
        token = self.current_token

        if token.type == TokenType.ASSIGN:
            self.match(TokenType.ASSIGN)
            expr = self.parse_expr()
            self.match(TokenType.SEMICOLON)
            return AssignNode(var_name, expr)
        else:
            # Inicia con ID dentro de una expresión aritmética: id Term' Expr' ;
            factor = VariableNode(var_name)
            term = self.parse_term_prime(factor)
            expr = self.parse_expr_prime(term)
            self.match(TokenType.SEMICOLON)
            return ExprStmtNode(expr)

    def parse_expr(self) -> ASTNode:
        """Expr -> Term ExprPrime"""
        term = self.parse_term()
        return self.parse_expr_prime(term)

    def parse_expr_prime(self, left: ASTNode) -> ASTNode:
        """
        ExprPrime -> + Term ExprPrime
                   | - Term ExprPrime
                   | ε
        """
        token = self.current_token

        if token.type == TokenType.PLUS:
            self.match(TokenType.PLUS)
            right = self.parse_term()
            new_left = BinaryOpNode(left, "+", right)
            return self.parse_expr_prime(new_left)

        elif token.type == TokenType.MINUS:
            self.match(TokenType.MINUS)
            right = self.parse_term()
            new_left = BinaryOpNode(left, "-", right)
            return self.parse_expr_prime(new_left)

        # Regla ε: seguimiento en { ')', ';', '$' }
        return left

    def parse_term(self) -> ASTNode:
        """Term -> Factor TermPrime"""
        factor = self.parse_factor()
        return self.parse_term_prime(factor)

    def parse_term_prime(self, left: ASTNode) -> ASTNode:
        """
        TermPrime -> * Factor TermPrime
                   | / Factor TermPrime
                   | % Factor TermPrime
                   | ε
        """
        token = self.current_token

        if token.type == TokenType.MUL:
            self.match(TokenType.MUL)
            right = self.parse_factor()
            new_left = BinaryOpNode(left, "*", right)
            return self.parse_term_prime(new_left)

        elif token.type == TokenType.DIV:
            self.match(TokenType.DIV)
            right = self.parse_factor()
            new_left = BinaryOpNode(left, "/", right)
            return self.parse_term_prime(new_left)

        elif token.type == TokenType.MOD:
            self.match(TokenType.MOD)
            right = self.parse_factor()
            new_left = BinaryOpNode(left, "%", right)
            return self.parse_term_prime(new_left)

        # Regla ε: seguimiento en { '+', '-', ')', ';', '$' }
        return left

    def parse_factor(self) -> ASTNode:
        """
        Factor -> id
                | NonIdFactor
        """
        token = self.current_token

        if token.type == TokenType.ID:
            id_token = self.match(TokenType.ID)
            return VariableNode(id_token.value)
        else:
            return self.parse_non_id_factor()

    def parse_non_id_factor(self) -> ASTNode:
        """
        NonIdFactor -> num
                     | ( Expr )
                     | abs ( Expr )
                     | sin ( Expr )
                     | cos ( Expr )
                     | tan ( Expr )
                     | - Factor
        """
        token = self.current_token

        if token.type == TokenType.NUM:
            num_tok = self.match(TokenType.NUM)
            val = float(num_tok.value) if '.' in num_tok.value or 'e' in num_tok.value.lower() else int(num_tok.value)
            return NumberNode(val)

        elif token.type == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return expr

        elif token.type == TokenType.ABS:
            self.match(TokenType.ABS)
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return FunctionCallNode("abs", expr)

        elif token.type == TokenType.SQRT:
            self.match(TokenType.SQRT)
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return FunctionCallNode("sqrt", expr)

        elif token.type == TokenType.SIN:
            self.match(TokenType.SIN)
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return FunctionCallNode("sin", expr)

        elif token.type == TokenType.COS:
            self.match(TokenType.COS)
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return FunctionCallNode("cos", expr)

        elif token.type == TokenType.TAN:
            self.match(TokenType.TAN)
            self.match(TokenType.LPAREN)
            expr = self.parse_expr()
            self.match(TokenType.RPAREN)
            return FunctionCallNode("tan", expr)

        elif token.type == TokenType.MINUS:
            self.match(TokenType.MINUS)
            operand = self.parse_factor()
            return UnaryOpNode("-", operand)

        else:
            raise ParserSyntaxError(
                f"Factor inválido. Se esperaba número, '(', función matemática o menos unario",
                token
            )

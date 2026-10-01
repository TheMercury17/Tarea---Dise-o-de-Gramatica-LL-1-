"""
Módulo para el Modelado Formal de Gramáticas Libres de Contexto (GLC)
y el Cálculo de Conjuntos de PRIMEROS, SIGUIENTES, PREDICCIÓN y TABLA LL(1).

Universidad Sergio Arboleda
Escuela de Ciencias Exactas e Ingeniería
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5:
- Andrés Sebastián Coral Vallejo
- Carol Arenas Cardona
"""

import sys
from typing import List, Dict, Set, Tuple, Optional

# Asegurar codificación UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

EPSILON = 'ε'
FIN_CADENA = '$'


class Regla:
    """Representa una regla de producción de la gramática: A -> α."""
    def __init__(self, id_regla: int, cabeza: str, cuerpo: List[str]):
        self.id = id_regla
        self.cabeza = cabeza
        self.cuerpo = list(cuerpo)

    def es_epsilon(self) -> bool:
        return self.cuerpo == [EPSILON] or len(self.cuerpo) == 0

    def __repr__(self):
        cuerpo_str = " ".join(self.cuerpo) if self.cuerpo else EPSILON
        return f"({self.id}) {self.cabeza} -> {cuerpo_str}"


class Gramatica:
    """Representa una Gramática Libre de Contexto G = (Vn, Vt, P, S)."""
    def __init__(self, no_terminales: List[str], terminales: List[str], inicial: str):
        self.no_terminales: List[str] = list(no_terminales)
        self.terminales: List[str] = list(terminales)
        self.inicial: str = inicial
        self.reglas: List[Regla] = []
        self._contador_reglas = 1

    def agregar_regla(self, cabeza: str, cuerpo: List[str]) -> Regla:
        if not cuerpo:
            cuerpo = [EPSILON]
        regla = Regla(self._contador_reglas, cabeza, cuerpo)
        self.reglas.append(regla)
        self._contador_reglas += 1
        return regla

    def es_terminal(self, simbolo: str) -> bool:
        return simbolo in self.terminales or simbolo == FIN_CADENA

    def es_no_terminal(self, simbolo: str) -> bool:
        return simbolo in self.no_terminales

    def calcular_primeros(self) -> Dict[str, Set[str]]:
        """
        Calcula el conjunto PRIMEROS (FIRST) para cada símbolo de la gramática
        empleando el algoritmo de punto fijo.
        """
        primeros: Dict[str, Set[str]] = {nt: set() for nt in self.no_terminales}
        for t in self.terminales:
            primeros[t] = {t}
        primeros[EPSILON] = {EPSILON}
        primeros[FIN_CADENA] = {FIN_CADENA}

        cambio = True
        while cambio:
            cambio = False
            for regla in self.reglas:
                A = regla.cabeza
                cuerpo = regla.cuerpo

                if regla.es_epsilon():
                    if EPSILON not in primeros[A]:
                        primeros[A].add(EPSILON)
                        cambio = True
                    continue

                todos_derivan_epsilon = True
                for Y in cuerpo:
                    primeros_Y = primeros.get(Y, {Y})
                    elementos_a_anadir = primeros_Y - {EPSILON}
                    if not elementos_a_anadir.issubset(primeros[A]):
                        primeros[A].update(elementos_a_anadir)
                        cambio = True

                    if EPSILON not in primeros_Y:
                        todos_derivan_epsilon = False
                        break

                if todos_derivan_epsilon:
                    if EPSILON not in primeros[A]:
                        primeros[A].add(EPSILON)
                        cambio = True

        return {nt: primeros[nt] for nt in self.no_terminales}

    def calcular_primeros_cadena(self, cadena: List[str], primeros_simbolos: Dict[str, Set[str]]) -> Set[str]:
        """Calcula PRIMEROS de una secuencia de símbolos α = X1 X2 ... Xk."""
        if not cadena or cadena == [EPSILON]:
            return {EPSILON}

        resultado: Set[str] = set()
        todos_derivan_epsilon = True

        for simbolo in cadena:
            if self.es_terminal(simbolo):
                resultado.add(simbolo)
                todos_derivan_epsilon = False
                break
            elif simbolo == EPSILON:
                continue
            else:
                primeros_X = primeros_simbolos.get(simbolo, set())
                resultado.update(primeros_X - {EPSILON})
                if EPSILON not in primeros_X:
                    todos_derivan_epsilon = False
                    break

        if todos_derivan_epsilon:
            resultado.add(EPSILON)

        return resultado

    def calcular_siguientes(self, primeros_simbolos: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """
        Calcula el conjunto SIGUIENTES (FOLLOW) para todos los no terminales
        utilizando iteración de punto fijo.
        """
        siguientes: Dict[str, Set[str]] = {nt: set() for nt in self.no_terminales}
        siguientes[self.inicial].add(FIN_CADENA)

        cambio = True
        while cambio:
            cambio = False
            for regla in self.reglas:
                A = regla.cabeza
                cuerpo = regla.cuerpo

                if regla.es_epsilon():
                    continue

                for i, B in enumerate(cuerpo):
                    if not self.es_no_terminal(B):
                        continue

                    beta = cuerpo[i + 1:]
                    if beta:
                        primeros_beta = self.calcular_primeros_cadena(beta, primeros_simbolos)
                        elementos = primeros_beta - {EPSILON}
                        if not elementos.issubset(siguientes[B]):
                            siguientes[B].update(elementos)
                            cambio = True

                        if EPSILON in primeros_beta:
                            if not siguientes[A].issubset(siguientes[B]):
                                siguientes[B].update(siguientes[A])
                                cambio = True
                    else:
                        if not siguientes[A].issubset(siguientes[B]):
                            siguientes[B].update(siguientes[A])
                            cambio = True

        return siguientes

    def calcular_prediccion(self, primeros_simbolos: Dict[str, Set[str]],
                            siguientes: Dict[str, Set[str]]) -> Dict[int, Tuple[Regla, Set[str]]]:
        """
        Calcula el conjunto de PREDICCIÓN (SELECT) para cada regla A -> α:
        - Si ε ∉ FIRST(α): PRED(A -> α) = FIRST(α)
        - Si ε ∈ FIRST(α): PRED(A -> α) = (FIRST(α) - {ε}) ∪ FOLLOW(A)
        """
        predicciones: Dict[int, Tuple[Regla, Set[str]]] = {}

        for regla in self.reglas:
            A = regla.cabeza
            alpha = regla.cuerpo

            if regla.es_epsilon():
                primeros_alpha = {EPSILON}
            else:
                primeros_alpha = self.calcular_primeros_cadena(alpha, primeros_simbolos)

            if EPSILON not in primeros_alpha:
                conjunto_pred = set(primeros_alpha)
            else:
                conjunto_pred = (primeros_alpha - {EPSILON}) | siguientes[A]

            predicciones[regla.id] = (regla, conjunto_pred)

        return predicciones

    def verificar_ll1(self, predicciones: Dict[int, Tuple[Regla, Set[str]]]) -> Tuple[bool, List[str]]:
        """Verifica la condición de gramática LL(1): predicciones disjuntas para cada no terminal."""
        es_ll1 = True
        conflictos: List[str] = []
        reglas_por_cabeza: Dict[str, List[Tuple[Regla, Set[str]]]] = {nt: [] for nt in self.no_terminales}

        for id_regla, (regla, pred) in predicciones.items():
            reglas_por_cabeza[regla.cabeza].append((regla, pred))

        for nt, lista in reglas_por_cabeza.items():
            for i in range(len(lista)):
                for j in range(i + 1, len(lista)):
                    r1, p1 = lista[i]
                    r2, p2 = lista[j]
                    interseccion = p1 & p2
                    if interseccion:
                        es_ll1 = False
                        inter_str = ", ".join(sorted(interseccion))
                        conflictos.append(
                            f"Conflicto en '{nt}' entre Regla {r1.id} [{r1}] y Regla {r2.id} [{r2}]: Intersección = {{{inter_str}}}"
                        )

        return es_ll1, conflictos

    def construir_tabla_ll1(self, predicciones: Dict[int, Tuple[Regla, Set[str]]]) -> Tuple[Dict[Tuple[str, str], Regla], List[str]]:
        """
        Construye la Tabla de Análisis Sintáctico LL(1) M[NoTerminal, Terminal] -> Regla.
        Retorna la tabla y una lista de conflictos (si existiera múltiple asignación).
        """
        tabla: Dict[Tuple[str, str], Regla] = {}
        conflictos: List[str] = []

        for id_regla, (regla, pred) in predicciones.items():
            nt = regla.cabeza
            for terminal in pred:
                clave = (nt, terminal)
                if clave in tabla:
                    regla_existente = tabla[clave]
                    conflictos.append(
                        f"Conflicto M[{nt}, {terminal}]: Ya contiene Regla {regla_existente.id} [{regla_existente}] y se intentó asignar Regla {regla.id} [{regla}]"
                    )
                else:
                    tabla[clave] = regla

        return tabla, conflictos


def crear_gramatica_proyecto() -> Gramatica:
    """
    Crea y retorna la Gramática Formal LL(1) diseñada para el lenguaje
    con operaciones aritméticas (+, -, *, /, %), valor absoluto (abs),
    raíz cuadrada (sqrt), funciones trigonométricas (sin, cos, tan)
    y asignación de variables.
    """
    no_terminales = [
        "Program",
        "StmtList",
        "Stmt",
        "StmtTail",
        "Expr",
        "ExprPrime",
        "Term",
        "TermPrime",
        "Factor",
        "NonIdFactor"
    ]

    terminales = [
        "id",
        "num",
        "=",
        "+",
        "-",
        "*",
        "/",
        "%",
        "(",
        ")",
        "abs",
        "sqrt",
        "sin",
        "cos",
        "tan",
        ";"
    ]

    g = Gramatica(no_terminales, terminales, "Program")

    # Reglas del programa y sentencias
    # (1) Program -> StmtList
    g.agregar_regla("Program", ["StmtList"])

    # (2) StmtList -> Stmt StmtList
    g.agregar_regla("StmtList", ["Stmt", "StmtList"])
    # (3) StmtList -> ε
    g.agregar_regla("StmtList", [EPSILON])

    # (4) Stmt -> id StmtTail
    g.agregar_regla("Stmt", ["id", "StmtTail"])
    # (5) Stmt -> NonIdFactor TermPrime ExprPrime ;
    g.agregar_regla("Stmt", ["NonIdFactor", "TermPrime", "ExprPrime", ";"])

    # (6) StmtTail -> = Expr ;
    g.agregar_regla("StmtTail", ["=", "Expr", ";"])
    # (7) StmtTail -> TermPrime ExprPrime ;
    g.agregar_regla("StmtTail", ["TermPrime", "ExprPrime", ";"])

    # Expresiones y términos (Aritmética y Asociatividad Izquierda mediante LL(1))
    # (8) Expr -> Term ExprPrime
    g.agregar_regla("Expr", ["Term", "ExprPrime"])

    # (9) ExprPrime -> + Term ExprPrime
    g.agregar_regla("ExprPrime", ["+", "Term", "ExprPrime"])
    # (10) ExprPrime -> - Term ExprPrime
    g.agregar_regla("ExprPrime", ["-", "Term", "ExprPrime"])
    # (11) ExprPrime -> ε
    g.agregar_regla("ExprPrime", [EPSILON])

    # (12) Term -> Factor TermPrime
    g.agregar_regla("Term", ["Factor", "TermPrime"])

    # (13) TermPrime -> * Factor TermPrime
    g.agregar_regla("TermPrime", ["*", "Factor", "TermPrime"])
    # (14) TermPrime -> / Factor TermPrime
    g.agregar_regla("TermPrime", ["/", "Factor", "TermPrime"])
    # (15) TermPrime -> % Factor TermPrime
    g.agregar_regla("TermPrime", ["%", "Factor", "TermPrime"])
    # (16) TermPrime -> ε
    g.agregar_regla("TermPrime", [EPSILON])

    # Factores
    # (17) Factor -> id
    g.agregar_regla("Factor", ["id"])
    # (18) Factor -> NonIdFactor
    g.agregar_regla("Factor", ["NonIdFactor"])

    # Factores no-identificadores (desambiguación y factorización a la izquierda)
    # (19) NonIdFactor -> num
    g.agregar_regla("NonIdFactor", ["num"])
    # (20) NonIdFactor -> ( Expr )
    g.agregar_regla("NonIdFactor", ["(", "Expr", ")"])
    # (21) NonIdFactor -> abs ( Expr )
    g.agregar_regla("NonIdFactor", ["abs", "(", "Expr", ")"])
    # (22) NonIdFactor -> sin ( Expr )
    g.agregar_regla("NonIdFactor", ["sin", "(", "Expr", ")"])
    # (23) NonIdFactor -> cos ( Expr )
    g.agregar_regla("NonIdFactor", ["cos", "(", "Expr", ")"])
    # (24) NonIdFactor -> tan ( Expr )
    g.agregar_regla("NonIdFactor", ["tan", "(", "Expr", ")"])
    # (25) NonIdFactor -> sqrt ( Expr )
    g.agregar_regla("NonIdFactor", ["sqrt", "(", "Expr", ")"])
    # (26) NonIdFactor -> - Factor
    g.agregar_regla("NonIdFactor", ["-", "Factor"])

    return g

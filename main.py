"""
Módulo Principal y Punto de Entrada (CLI / REPL / Demostraciones)
Universidad Sergio Arboleda
Escuela de Ciencias Exactas e Ingeniería
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5:
- Andrés Sebastián Coral Vallejo
- Carol Arenas Cardona
"""

import sys
import argparse
from typing import List

# Asegurar codificación UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from gramatica import crear_gramatica_proyecto, Gramatica, EPSILON, FIN_CADENA
from src.tokens import Token, TokenType
from src.lexer import Lexer, LexerError
from src.parser_ll1 import ParserLL1, ParserTablaLL1, ParserSyntaxError
from src.semantic import SymbolTable, SemanticError
from src.interpreter import Interpreter


def mostrar_encabezado():
    print("=" * 80)
    print(" UNIVERSIDAD SERGIO ARBOLEDA - ESCUELA DE CIENCIAS EXACTAS E INGENIERÍA")
    print(" Materia: Lenguajes de Programación y Transducción")
    print(" Docente: Joaquin F. Sanchez")
    print(" Grupo 5:")
    print("   - Andrés Sebastián Coral Vallejo")
    print("   - Carol Arenas Cardona")
    print(" Tarea: Diseño e Implementación de Gramática LL(1)")
    print("=" * 80)


def mostrar_gramatica_y_conjuntos():
    """Calcula y muestra la gramática formal, PRIMEROS, SIGUIENTES, PREDICCIÓN y diagnóstico LL(1)."""
    mostrar_encabezado()
    g = crear_gramatica_proyecto()

    print("\n--- 1. GRAMÁTICA FORMAL G = (Vn, Vt, P, S) ---")
    print(f"Símbolo Inicial: {g.inicial}\n")
    print(f"No Terminales ({len(g.no_terminales)}): {', '.join(g.no_terminales)}\n")
    print(f"Terminales ({len(g.terminales)}): {', '.join(g.terminales)}\n")

    print(f"Reglas de Producción ({len(g.reglas)}):")
    for r in g.reglas:
        print(f"  {r}")

    primeros = g.calcular_primeros()
    siguientes = g.calcular_siguientes(primeros)
    predicciones = g.calcular_prediccion(primeros, siguientes)
    es_ll1, conflictos = g.verificar_ll1(predicciones)

    print("\n--- 2. CONJUNTOS DE PRIMEROS (FIRST) ---")
    for nt in g.no_terminales:
        items = sorted(list(primeros[nt]))
        print(f"  PRIMEROS({nt:<12}) = {{ {', '.join(items)} }}")

    print("\n--- 3. CONJUNTOS DE SIGUIENTES (FOLLOW) ---")
    for nt in g.no_terminales:
        items = sorted(list(siguientes[nt]))
        print(f"  SIGUIENTES({nt:<12}) = {{ {', '.join(items)} }}")

    print("\n--- 4. CONJUNTOS DE PREDICCIÓN (SELECT) POR REGLA ---")
    header = f"  {'ID':<4} | {'Regla de Producción':<45} | {'Conjunto de Predicción'}"
    print(header)
    print("  " + "-" * 85)
    for r_id, (regla, pred) in predicciones.items():
        r_str = f"{regla.cabeza} -> {' '.join(regla.cuerpo)}"
        pred_str = ", ".join(sorted(list(pred)))
        print(f"  {r_id:<4} | {r_str:<45} | {{ {pred_str} }}")

    print("\n--- 5. DIAGNÓSTICO DE CONDICIÓN LL(1) ---")
    if es_ll1:
        print("  >> [RESULTADO: EXITOSO] La gramática es ESTRICTAMENTE LL(1).")
        print("     Todos los conjuntos de predicción para reglas con la misma cabeza son mutuamente disjuntos.")
    else:
        print("  >> [RESULTADO: CONFLICTO] La gramática NO es LL(1):")
        for c in conflictos:
            print(f"     * {c}")


def mostrar_tabla_ll1():
    """Construye y visualiza la tabla M[A, a]."""
    mostrar_encabezado()
    g = crear_gramatica_proyecto()
    primeros = g.calcular_primeros()
    siguientes = g.calcular_siguientes(primeros)
    predicciones = g.calcular_prediccion(primeros, siguientes)
    tabla, conflictos = g.construir_tabla_ll1(predicciones)

    print(f"\n--- TABLA DE ANÁLISIS SINTÁCTICO LL(1) M[NoTerminal, Terminal] ---")
    print(f"Total de celdas activas: {len(tabla)}")
    print(f"Conflictos detectados: {len(conflictos)}\n")

    for nt in g.no_terminales:
        print(f"\n[No Terminal: {nt}]")
        entradas_nt = [(t, r) for (nt_key, t), r in tabla.items() if nt_key == nt]
        for t, r in sorted(entradas_nt, key=lambda x: x[0]):
            print(f"   M[{nt:<12}, {t:<4}]  --->  Regla ({r.id}): {r.cabeza} -> {' '.join(r.cuerpo)}")


def ejecutar_codigo(codigo: str, mostrar_traza: bool = False, interprete: Interpreter = None) -> Interpreter:
    """Ejecuta el pipeline completo para un bloque de código."""
    if interprete is None:
        interprete = Interpreter()

    try:
        # 1. Fase Léxica
        lexer = Lexer(codigo)
        tokens = lexer.tokenize()

        # 2. Fase Sintáctica (Parser con Tabla)
        if mostrar_traza:
            print("\n[TRAZA DEL PARSER PREDICTIVO CON PILA]")
            parser_tabla = ParserTablaLL1()
            traza = parser_tabla.analizar_con_traza(tokens)
            print(f"{'Paso':<5} | {'Pila':<40} | {'Entrada Restante':<30} | {'Acción'}")
            print("-" * 115)
            for t in traza:
                pila_str = " ".join(t["pila"])
                entrada_str = " ".join(t["entrada"][:5]) + ("..." if len(t["entrada"]) > 5 else "")
                print(f"{t['paso']:<5} | {pila_str:<40} | {entrada_str:<30} | {t['accion']}")

        # 3. Fase Sintáctica (AST) y Semántica
        parser_ast = ParserLL1(tokens)
        ast = parser_ast.parse()

        # 4. Evaluación Semántica
        resultados = interprete.evaluate(ast)

        for out in interprete.output_history[-len(ast.statements):]:
            print(f"  {out}")

        return interprete

    except (LexerError, ParserSyntaxError, SemanticError) as err:
        print(f"\n  [ERROR DURANTE LA EJECUCIÓN] {err}")
        return interprete
    except Exception as ex:
        print(f"\n  [ERROR INESPERADO] {type(ex).__name__}: {ex}")
        return interprete


def ejecutar_archivo(ruta_archivo: str, mostrar_traza: bool = False):
    mostrar_encabezado()
    print(f"\nEjecutando archivo fuente: {ruta_archivo}\n" + "-" * 60)
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        print(f"No se pudo leer el archivo: {e}")
        return

    interprete = ejecutar_codigo(contenido, mostrar_traza=mostrar_traza)
    print("\n--- ESTADO FINAL DE LA TABLA DE SÍMBOLOS (VARIABLES) ---")
    vars = interprete.symbol_table.get_all()
    if vars:
        for k, v in vars.items():
            print(f"   {k} = {v}")
    else:
        print("   (No hay variables registradas)")


def iniciar_repl():
    """Inicia la consola interactiva REPL."""
    mostrar_encabezado()
    print("\n--- CONSOLA INTERACTIVA (REPL) - LENGUAJE LL(1) ---")
    print("Escriba sentencias terminadas en ';' (ejemplo: 'x = 10;', 'sin(x);').")
    print("Comandos especiales: 'tabla' (ver variables), 'limpiar' (borrar variables), 'salir' (terminar).\n")

    interprete = Interpreter()

    while True:
        try:
            linea = input("LL1> ").strip()
            if not linea:
                continue
            if linea.lower() in ["salir", "exit", "quit"]:
                print("Finalizando sesión REPL. ¡Hasta pronto!")
                break
            elif linea.lower() == "tabla":
                print("Variables actuales:", interprete.symbol_table.get_all())
                continue
            elif linea.lower() == "limpiar":
                interprete.symbol_table.clear()
                print("Tabla de símbolos restablecida.")
                continue

            ejecutar_codigo(linea, mostrar_traza=False, interprete=interprete)

        except (KeyboardInterrupt, EOFError):
            print("\nFinalizando sesión REPL.")
            break


def ejecutar_demostracion():
    mostrar_encabezado()
    print("\n========================================================")
    print("   EJECUCIÓN DE DEMOSTRACIÓN DE CASOS DE PRUEBA")
    print("========================================================")

    demos = [
        ("Caso 1: Operaciones Aritméticas Básicas (+, -, *, /, %)", """
        x = 100 + 50 * 2;
        y = (100 + 50) * 2;
        modulo = 47 % 5;
        division = 144 / 12;
        resultado = x - modulo + division;
        resultado;
        """),
        ("Caso 2: Valor Absoluto (abs)", """
        negativo = -25.75;
        positivo = abs(negativo);
        expresion_abs = abs(10 - 50) % 7;
        expresion_abs;
        """),
        ("Caso 3: Funciones Trigonométricas (sin, cos, tan)", """
        angulo = 0;
        s = sin(angulo);
        c = cos(angulo);
        t = tan(angulo);
        identidad = (s * s) + (c * c);
        identidad;
        """),
        ("Caso 4: Asignación y Reutilización de Variables", """
        base = 12.5;
        altura = 8.0;
        area_triangulo = (base * altura) / 2;
        perimetro_aprox = base * 3;
        area_triangulo;
        """),
        ("Caso 5: Manejo Robusto de Errores Semánticos y Léxicos", """
        // Intento de división por cero
        error_div = 10 / 0;
        // Intento de usar variable no declarada
        error_var = variable_fantasma + 5;
        """)
    ]

    for titulo, codigo in demos:
        print(f"\n>>> {titulo}")
        print("Código:")
        for line in codigo.strip().split("\n"):
            print(f"    {line}")
        print("\nEjecución:")
        ejecutar_codigo(codigo, mostrar_traza=False)
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Compilador e Intérprete basado en Gramática LL(1) - Grupo 5"
    )
    parser.add_argument("--gramatica", action="store_true", help="Muestra la gramática formal, PRIMEROS, SIGUIENTES, PREDICCIÓN y diagnóstico LL(1)")
    parser.add_argument("--tabla", action="store_true", help="Muestra la Tabla de Análisis Sintáctico LL(1) M[A, a]")
    parser.add_argument("--archivo", type=str, help="Ruta de un archivo fuente para analizar y ejecutar")
    parser.add_argument("--traza", action="store_true", help="Muestra la traza paso a paso del parser predictivo con pila")
    parser.add_argument("--repl", action="store_true", help="Inicia la consola interactiva (REPL)")
    parser.add_argument("--demo", action="store_true", help="Ejecuta una demostración de casos de prueba guiados")

    args = parser.parse_args()

    if args.gramatica:
        mostrar_gramatica_y_conjuntos()
    elif args.tabla:
        mostrar_tabla_ll1()
    elif args.archivo:
        ejecutar_archivo(args.archivo, mostrar_traza=args.traza)
    elif args.repl:
        iniciar_repl()
    elif args.demo:
        ejecutar_demostracion()
    else:
        # Por defecto muestra la gramática y luego ejecuta demo
        mostrar_gramatica_y_conjuntos()
        print("\n(Ejecute con --help para ver opciones como --tabla, --archivo, --repl, --demo)")


if __name__ == "__main__":
    main()

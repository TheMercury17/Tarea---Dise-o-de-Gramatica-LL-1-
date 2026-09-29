# Tarea: Diseño e Implementación de Gramática LL(1)

**Universidad Sergio Arboleda**  
**Escuela de Ciencias Exactas e Ingeniería**  
**Materia:** Lenguajes de Programación y Transducción  
**Docente:** Joaquin F. Sanchez  
**Grupo 5:**
- **Andrés Sebastián Coral Vallejo**
- **Carol Arenas Cardona**

---

## Enlace del Repositorio
- GitHub: [https://github.com/TheMercury17/Tarea---Dise-o-de-Gramatica-LL-1-](https://github.com/TheMercury17/Tarea---Dise-o-de-Gramatica-LL-1-)

---

## Descripción del Proyecto
Diseño e implementación formal de un compilador / intérprete basado en una **Gramática LL(1)** para un lenguaje aritmético y trigonométrico con soporte para asignación de variables.

### Requerimientos Funcionales del Lenguaje
- Operaciones Aritméticas: Suma (`+`), Resta (`-`), Multiplicación (`*`), División (`/`), Módulo (`%`).
- Funciones Matemáticas: Valor Absoluto (`abs`), Seno (`sin`), Coseno (`cos`), Tangente (`tan`).
- Asignación de variables e identificadores (`ID = Expr`).
- Análisis Léxico (Lexer con expresiones regulares y manejo de errores léxicos).
- Análisis Sintáctico (Parser predictivo basado en tabla de análisis LL(1) y cálculo formal de Primeros, Siguientes y Predicción).
- Análisis Semántico (Comprobación de tipos, tabla de símbolos, detección de variables no inicializadas, división por cero).
- Pruebas unitarias de implementación exhaustivas.

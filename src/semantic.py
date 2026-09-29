"""
Módulo del Analizador Semántico y Tabla de Símbolos
Universidad Sergio Arboleda
Materia: Lenguajes de Programación y Transducción
Docente: Joaquin F. Sanchez
Grupo 5: Andrés Sebastián Coral Vallejo & Carol Arenas Cardona
"""

from typing import Dict, Any, Optional


class SemanticError(Exception):
    """Excepción para violaciones a las reglas semánticas del lenguaje."""
    def __init__(self, mensaje: str):
        super().__init__(f"Error Semántico: {mensaje}")
        self.mensaje = mensaje


class SymbolTable:
    """
    Tabla de símbolos que gestiona los identificadores, tipos y valores en memoria.
    Proporciona aislamiento de contexto y detección de variables no inicializadas.
    """
    def __init__(self, parent: Optional["SymbolTable"] = None):
        self.symbols: Dict[str, Any] = {}
        self.parent: Optional["SymbolTable"] = parent

    def set(self, name: str, value: Any):
        """Asigna o define una variable en la tabla actual."""
        self.symbols[name] = value

    def get(self, name: str) -> Any:
        """Obtiene el valor de una variable; lanza SemanticError si no está declarada."""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            raise SemanticError(f"La variable '{name}' no ha sido definida antes de su uso.")

    def exists(self, name: str) -> bool:
        """Verifica si la variable existe en el entorno."""
        if name in self.symbols:
            return True
        if self.parent is not None:
            return self.parent.exists(name)
        return False

    def get_all(self) -> Dict[str, Any]:
        """Retorna una copia del diccionario con todas las variables."""
        copia = dict(self.parent.get_all()) if self.parent else {}
        copia.update(self.symbols)
        return copia

    def clear(self):
        """Limpia los símbolos registrados."""
        self.symbols.clear()

# ll1.py: tabla LL(1) y prueba de si una gramática es LL(1) (Aho 4.4.3)

from grammar import first_de_cadena  # traemos de grammar.py la función que da el FIRST de una alternativa


def construir_tabla_ll1(gramatica, first, follow):  # arma la tabla M[A, a] (Algoritmo 4.31 del libro)
    tabla = {}  # diccionario vacío: llave (fila, columna) -> lista de alternativas de esa casilla

    for A in gramatica:  # recorre cada no terminal: cada uno es una fila de la tabla
        for alt in gramatica[A]:  # recorre cada alternativa de A, ej: A -> aA y A -> d
            f = first_de_cadena(alt, first)  # con qué letras empieza esta alternativa (puede traer "e")

            for a in f - {"e"}:  # REGLA 1: por cada letra de FIRST (sin épsilon)...
                tabla.setdefault((A, a), [])  # ...si la casilla [A, a] no existe, la crea vacía
                tabla[(A, a)].append(alt)  # ...y mete la alternativa en esa casilla

            if "e" in f:  # REGLA 2: si la alternativa puede desaparecer...
                for b in follow[A]:  # ...por cada letra que puede venir después de A (incluye $)...
                    tabla.setdefault((A, b), [])  # ...crea la casilla [A, b] si no existe
                    tabla[(A, b)].append(alt)  # ...y mete la alternativa ahí

    return tabla  # devuelve la tabla completa


def es_ll1(tabla):  # una gramática es LL(1) si ninguna casilla tiene dos alternativas
    for alternativas in tabla.values():  # recorre lo que hay dentro de cada casilla llena
        if len(alternativas) > 1:  # si hay 2 o más, pelean por la misma casilla
            return False  # conflicto: NO es LL(1)
    return True  # revisó todas y ninguna tenía conflicto: SÍ es LL(1)


if __name__ == "__main__":  # esto solo corre con: python ll1.py (es una prueba rápida)
    from grammar import leer_gramatica, calcular_first, calcular_follow  # funciones del ítem 1

    gramatica = leer_gramatica(["3", "S -> AB", "A -> aA d", "B -> bBc e"])  # ejemplo 2 del enunciado
    first = calcular_first(gramatica)  # FIRST de cada no terminal
    follow = calcular_follow(gramatica, first)  # FOLLOW de cada no terminal
    tabla = construir_tabla_ll1(gramatica, first, follow)  # arma la tabla

    for casilla in sorted(tabla):  # recorre las casillas en orden (primero por fila, luego por columna)
        print(casilla, tabla[casilla])  # imprime: ('A', 'a') [['a', 'A']]
    print("Es LL(1):", es_ll1(tabla))  # debe decir True

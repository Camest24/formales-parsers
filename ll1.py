# ll1.py: tabla LL(1) y prueba de si una gramática es LL(1) (Aho 4.4.3)

from grammar import first_de_cadena  # traemos de grammar.py la función que da el FIRST de una alternativa


#Construye y llena el Diccionarioe
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


def parsear_ll1(tabla, palabra, traza=False):  # traza=True imprime Pila / Entrada / Acción en cada paso
    pila = ["$", "S"]                # lo que espero leer (el tope es el último)
    entrada = list(palabra) + ["$"]  # lo que me falta, con $ al final
    i = 0                            # en qué letra de la entrada voy
    if traza:                        # (solo imprime) encabezado de la traza
        print(f"{'Pila':<16}{'Entrada':<10}Acción")

    while True:
        X = pila[-1]                 # tope de la pila
        a = entrada[i]               # letra que toca
        fila = f"{' '.join(pila):<16}{''.join(entrada[i:]):<10}"  # (solo imprime) pila y entrada de este paso

        # ACEPTAR: no espero nada y no me falta nada
        if X == "$" and a == "$":
            if traza:
                print(fila + "ACEPTAR -> yes")
            return True

        # TACHAR: el tope es igual a la letra → las dos se van
        if X == a:
            if traza:
                print(fila + f"TACHAR {a}")
            pila.pop()               # saco el tope
            i += 1                   # avanzo en la entrada

        # REEMPLAZAR: tope no terminal y la tabla tiene casilla → uso su alternativa
        elif X.isupper() and (X, a) in tabla:
            alt = tabla[(X, a)][0]   # [0]: en LL(1) la casilla tiene una sola alternativa
            if traza:
                print(fila + f"REEMPLAZAR {X} -> {' '.join(alt) or 'e'}   (casilla M[{X}, {a}])")
            pila.pop()               # saco el no terminal
            for simbolo in reversed(alt):    # al revés: la 1ª letra queda en el tope
                pila.append(simbolo)         # si alt es ε (lista vacía), no entra nada

        # ERROR: minúscula distinta, o no terminal sin casilla
        else:
            if traza:
                motivo = f"la casilla M[{X}, {a}] está vacía" if X.isupper() else f"esperaba {X} y llegó {a}"
                print(fila + f"ERROR: {motivo} -> no")
            return False


def imprimir_tabla_ll1(gramatica, tabla):  # muestra la tabla M[A, a] (sirve para el informe)
    letras = sorted({a for (_, a) in tabla if a != "$"}) + ["$"]  # columnas: terminales y $ al final

    def celda(A, a):  # texto de una casilla; si hay conflicto, las alternativas van separadas por /
        return " / ".join(A + " -> " + ("".join(alt) or "e") for alt in tabla.get((A, a), []))

    filas = [[""] + letras] + [[A] + [celda(A, a) for a in letras] for A in gramatica]  # encabezado + una fila por no terminal
    ancho = max(len(t) for fila in filas for t in fila)  # todas las columnas del mismo ancho
    for fila in filas:
        print(" | ".join(t.ljust(ancho) for t in fila))


if __name__ == "__main__":  # esto solo corre con: python ll1.py (o el botón ▶). Es una demostración con el hechizo
    from grammar import leer_gramatica, calcular_first, calcular_follow  # funciones del ítem 1
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # para que • y las tildes se vean bien también en el panel Output del botón ▶

    gramatica = leer_gramatica(["3", "S -> H", "H -> EH e", "E -> f a t v"])  # el hechizo: S -> H, H -> E H | ε, E -> f | a | t | v
    first = calcular_first(gramatica)  # FIRST de cada no terminal
    follow = calcular_follow(gramatica, first)  # FOLLOW de cada no terminal
    tabla = construir_tabla_ll1(gramatica, first, follow)  # arma la tabla

    print("1) La tabla LL(1) del hechizo:")
    imprimir_tabla_ll1(gramatica, tabla)
    print("Es LL(1):", es_ll1(tabla))  # ninguna casilla tiene dos alternativas → True

    for palabra in ["fa", "fx"]:  # una que pertenece y una que no
        print()
        print(f"2) El parser con pila, paso a paso, con la cadena '{palabra}':")
        ok = parsear_ll1(tabla, palabra, traza=True)
        print("Resultado:", "yes" if ok else "no")

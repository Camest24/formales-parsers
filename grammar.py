def leer_gramatica(lineas):  # recibe la lista de líneas y devuelve la gramática como diccionario
    n = int(lineas[0])  # la primera línea dice cuántas producciones hay
    gramatica = {}  # aquí guardamos no terminal -> lista de alternativas

    for i in range(1, n + 1):  # recorre las n líneas de producciones
        cabeza, cuerpo = lineas[i].split("->", 1)  # "A -> aA d" se corta en "A " y " aA d"
        cabeza = cabeza.strip()  # quita espacios: "A " queda "A"

        alternativas = []  # alternativas de esta cabeza
        for alt in cuerpo.split():  # separa por espacios: "aA", "d"
            if alt == "e":  # "e" es épsilon
                alternativas.append([])  # épsilon se guarda como lista vacía
            else:
                alternativas.append(list(alt))  # "aA" se vuelve ['a', 'A']

        gramatica[cabeza] = alternativas  # gramatica["A"] = [['a','A'], ['d']]

    return gramatica


def first_de_cadena(simbolos, first):  # FIRST de una cadena X1 X2 ... Xn (regla 3 del libro)
    resultado = set()  # conjunto vacío donde juntamos las letras
    for X in simbolos:  # recorre los símbolos de izquierda a derecha
        if not X.isupper():  # si X es terminal (minúscula o símbolo)
            resultado.add(X)  # la cadena empieza con esa letra
            return resultado  # un terminal nunca desaparece: paramos aquí
        resultado |= first[X] - {"e"}  # agrega FIRST(X) sin épsilon
        if "e" not in first[X]:  # si X NO puede desaparecer
            return resultado  # paramos aquí
    resultado.add("e")  # todos desaparecieron (o la cadena era vacía): entra épsilon
    return resultado


def calcular_first(gramatica):  # FIRST de cada no terminal (Aho 4.4.2)
    first = {A: set() for A in gramatica}  # empieza vacío para cada no terminal
    cambio = True  # bandera: ¿algún conjunto creció en esta vuelta?
    while cambio:  # repite vueltas hasta que nada cambie
        cambio = False  # suponemos que esta vuelta no cambia nada
        for A in gramatica:  # recorre cada no terminal
            for alt in gramatica[A]:  # recorre cada alternativa de A
                antes = len(first[A])  # tamaño antes de agregar
                first[A] |= first_de_cadena(alt, first)  # agrega lo que aporta esta alternativa
                if len(first[A]) != antes:  # si creció
                    cambio = True  # hay que dar otra vuelta
    return first


def calcular_follow(gramatica, first):  # FOLLOW de cada no terminal (Aho 4.4.2)
    follow = {A: set() for A in gramatica}  # empieza vacío para cada no terminal
    follow["S"].add("$")  # regla 1: S es el inicial, $ siempre lo sigue
    cambio = True  # bandera: ¿algún conjunto creció en esta vuelta?
    while cambio:  # repite vueltas hasta que nada cambie
        cambio = False  # suponemos que esta vuelta no cambia nada
        for A in gramatica:  # A es la cabeza de la producción
            for alt in gramatica[A]:  # recorre cada alternativa de A
                for i, X in enumerate(alt):  # recorre cada símbolo con su posición
                    if not X.isupper():  # los terminales no tienen FOLLOW
                        continue  # salta al siguiente símbolo
                    antes = len(follow[X])  # tamaño antes de agregar
                    derecha = alt[i + 1:]  # todo lo que está a la derecha de X
                    f = first_de_cadena(derecha, first)  # con qué empieza lo de la derecha
                    follow[X] |= f - {"e"}  # regla 2: se suma el vecino (sin épsilon)
                    if "e" in f:  # regla 3: X al final, o lo de la derecha desaparece
                        follow[X] |= follow[A]  # X se roba el FOLLOW de la cabeza
                    if len(follow[X]) != antes:  # si creció
                        cambio = True  # hay que dar otra vuelta
    return follow


def formatear_conjunto(conjunto):  # convierte {'$', 'b', 'e'} en el texto "{b, e, $}"
    terminales = sorted(x for x in conjunto if x != "e" and x != "$")  # terminales en orden ASCII
    if "e" in conjunto:  # si está épsilon
        terminales.append("e")  # va después de los terminales
    if "$" in conjunto:  # si está el fin de cadena
        terminales.append("$")  # va de último
    return "{" + ", ".join(terminales) + "}"  # une con ", " y pone las llaves


def imprimir_sets(gramatica, first, follow):  # lo que imprime la opción --sets
    for A in sorted(gramatica):  # no terminales en orden alfabético
        print(f"First({A}) = {formatear_conjunto(first[A])}")  # una línea por FIRST
    for A in sorted(gramatica):  # otra vez en orden alfabético
        print(f"Follow({A}) = {formatear_conjunto(follow[A])}")  # una línea por FOLLOW


if __name__ == "__main__":  # solo corre al ejecutar este archivo directamente
    prueba = ["3", "S -> AB", "A -> aA d", "B -> bBc e"]
    gramatica = leer_gramatica(prueba)
    first = calcular_first(gramatica)
    follow = calcular_follow(gramatica, first)
    imprimir_sets(gramatica, first, follow)

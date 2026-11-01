# slr.py: autómata LR(0) para el parser SLR(1) (Aho 4.6.2)
# Analogía: cada producción es una "receta" y el punto es el dedo que señala lo que falta.


def numerar_producciones(gramatica):  # paso 1: lista numerada de recetas, con la meta S' -> S de primera
    producciones = [("S'", ["S"])]  # receta 0: gramática aumentada
    for A in gramatica:  # recorre cada no terminal
        for alt in gramatica[A]:  # recorre cada alternativa
            producciones.append((A, alt))  # le da el siguiente número
    return producciones


# Paso 2: un ítem es una tupla (número de receta, posición del dedo).
# Ej: (2, 1) con la receta 2 = A -> a A significa  A -> a • A


def closure(items, producciones):  # paso 3: abre todas las recetas que el dedo señale (como epsilon_closure)
    resultado = set(items)  # empieza con las listas que ya tengo
    cambio = True  # bandera: ¿se abrió algo nuevo en esta vuelta?
    while cambio:  # repite hasta que no se abra nada nuevo
        cambio = False  # suponemos que esta vuelta no abre nada
        for (p, dedo) in list(resultado):  # recorre cada lista abierta (list() para poder agregar mientras)
            derecha = producciones[p][1]  # lo que hay a la derecha de la flecha
            if dedo < len(derecha) and derecha[dedo].isupper():  # ¿el dedo señala una mayúscula?
                for q in range(len(producciones)):  # busca las recetas de esa mayúscula
                    if producciones[q][0] == derecha[dedo] and (q, 0) not in resultado:  # receta nueva
                        resultado.add((q, 0))  # la abre con el dedo al principio
                        cambio = True  # hubo cambio: otra vuelta
    return frozenset(resultado)  # frozenset: un conjunto que no cambia (sirve como llave)


def goto(caja, X, producciones):  # paso 4: llegó la pieza X (como move + epsilon_closure)
    movidos = set()  # aquí van las listas que esperaban X, con el dedo movido
    for (p, dedo) in caja:  # recorre cada lista de la caja
        derecha = producciones[p][1]  # lo que hay a la derecha de la flecha
        if dedo < len(derecha) and derecha[dedo] == X:  # ¿el dedo señalaba X?
            movidos.add((p, dedo + 1))  # mueve el dedo un lugar
    return closure(movidos, producciones)  # y abre las recetas que haga falta


def construir_cajas(producciones):  # paso 5: el mapa completo de cajas y flechas (como armar el DFA)
    cajas = [closure({(0, 0)}, producciones)]  # la primera caja: S' -> • S y lo que abra
    flechas = {}  # (número de caja, símbolo) -> número de caja a la que llega
    i = 0  # caja que estamos revisando
    while i < len(cajas):  # mientras queden cajas sin revisar (la lista crece mientras tanto)
        simbolos = set()  # símbolos que algún dedo de esta caja señala
        for (p, dedo) in cajas[i]:  # recorre cada lista de la caja
            derecha = producciones[p][1]  # lo que hay a la derecha de la flecha
            if dedo < len(derecha):  # si el dedo no está al final
                simbolos.add(derecha[dedo])  # anota lo que señala
        for X in sorted(simbolos):  # prueba cada símbolo (sorted: siempre en el mismo orden)
            nueva = goto(cajas[i], X, producciones)  # ¿a qué caja llego si consigo X?
            if nueva not in cajas:  # si es una caja que no existía
                cajas.append(nueva)  # la agrega al final de la lista
            flechas[(i, X)] = cajas.index(nueva)  # anota la flecha i --X--> nueva
        i += 1  # pasa a la siguiente caja
    return cajas, flechas


def mostrar_item(item, producciones):  # convierte (2, 1) en el texto "A -> a • A"
    p, dedo = item  # número de receta y posición del dedo
    cabeza, derecha = producciones[p]  # nombre y lado derecho de la receta
    simbolos = derecha[:dedo] + ["•"] + derecha[dedo:]  # mete el punto en su lugar
    return cabeza + " -> " + " ".join(simbolos)


def imprimir_cajas(cajas, flechas, producciones):  # muestra el mapa (sirve para el informe)
    for i, caja in enumerate(cajas):  # recorre cada caja con su número
        print(f"Caja {i}:")  # título de la caja
        for item in sorted(caja):  # cada ítem, en orden de receta
            print("   ", mostrar_item(item, producciones))  # el ítem con el punto
    for (i, X), j in sorted(flechas.items()):  # cada flecha
        print(f"Caja {i} --{X}--> Caja {j}")  # ej: Caja 0 --S--> Caja 1


def construir_tabla_slr(producciones, cajas, flechas, follow):  # paso 6: los letreros de cada caja (Aho 4.6.4, Algoritmo 4.46)
    action = {}  # (caja, letra) -> ("s", caja destino) | ("r", número de receta) | ("acc",)
    goto_tabla = {}  # (caja, mayúscula) -> caja destino
    conflictos = []  # casillas con dos letreros distintos (si hay alguna, no es SLR(1))

    def poner(caja, letra, accion):  # pega un letrero y revisa que no choque con otro
        if (caja, letra) in action and action[(caja, letra)] != accion:  # ya había otro distinto
            conflictos.append((caja, letra, action[(caja, letra)], accion))  # anota el choque
        else:
            action[(caja, letra)] = accion  # pega el letrero

    for (i, X), j in flechas.items():  # regla 1: cada flecha del mapa
        if X.isupper():  # flecha con mayúscula: va a la tabla GOTO
            goto_tabla[(i, X)] = j
        else:  # flecha con minúscula: el dedo señalaba una letra
            poner(i, X, ("s", j))  # letrero: shift a la caja j

    for i, caja in enumerate(cajas):  # recorre cada caja
        for (p, dedo) in caja:  # recorre cada ítem
            cabeza, derecha = producciones[p]  # receta del ítem
            if dedo == len(derecha):  # el dedo está al final
                if p == 0:  # S' -> S •: la meta completa
                    poner(i, "$", ("acc",))  # letrero: yes si llega $
                else:  # regla 2: reduce con las letras de FOLLOW(cabeza)
                    for a in follow[cabeza]:  # cada letra que puede venir después de la cabeza
                        poner(i, a, ("r", p))  # letrero: reduce con la receta p
    return action, goto_tabla, conflictos


def es_slr1(conflictos):  # SLR(1) = ninguna casilla con dos letreros distintos
    return len(conflictos) == 0


def parsear_slr(producciones, action, goto_tabla, palabra, traza=False):  # paso 7: el juego de la mesa con cajas (Aho 4.6.3, Algoritmo 4.44)
    pila = [0]  # pila de cajas: empieza en la caja 0
    entrada = list(palabra) + ["$"]  # la palabra con $ al final
    i = 0  # posición de la letra que toca
    if traza:  # si piden la traza, imprime el encabezado
        print(f"{'Pila':<18}{'Entrada':<12}Acción")

    while True:  # repite hasta que salga yes o no
        caja = pila[-1]  # caja donde estoy parado
        a = entrada[i]  # letra que toca
        accion = action.get((caja, a))  # lee el letrero de esa caja para esa letra
        fila = f"{' '.join(map(str, pila)):<18}{''.join(entrada[i:]):<12}"  # pila y entrada de este paso

        if accion is None:  # no hay letrero: atascado
            if traza:
                print(fila + "error")
            return False  # no
        if accion[0] == "s":  # shift
            if traza:
                print(fila + f"shift {accion[1]}")
            pila.append(accion[1])  # me muevo a la caja destino
            i += 1  # avanzo en la palabra
        elif accion[0] == "r":  # reduce
            cabeza, derecha = producciones[accion[1]]  # receta con la que se reduce
            if traza:
                print(fila + f"reduce {cabeza} -> {' '.join(derecha) or 'e'}")
            for _ in derecha:  # una caja por cada pieza de la receta
                pila.pop()  # retrocedo esas cajas
            pila.append(goto_tabla[(pila[-1], cabeza)])  # sigo la flecha de la mayúscula
        else:  # acc
            if traza:
                print(fila + "accept")
            return True  # yes


def imprimir_tabla_slr(producciones, action, goto_tabla, n_cajas):  # muestra la tabla (sirve para el informe)
    letras = sorted({a for (_, a) in action if a != "$"}) + ["$"]  # columnas de ACTION
    nts = sorted({X for (_, X) in goto_tabla})  # columnas de GOTO
    print("Caja | " + " | ".join(letras) + " || " + " | ".join(nts))  # encabezado
    for i in range(n_cajas):  # una fila por caja
        celdas = []
        for a in letras:  # columnas de ACTION
            ac = action.get((i, a))
            celdas.append("" if ac is None else "acc" if ac[0] == "acc" else ac[0] + str(ac[1]))
        gs = [str(goto_tabla.get((i, X), "")) for X in nts]  # columnas de GOTO
        print(f"{i:>4} | " + " | ".join(celdas) + " || " + " | ".join(gs))  # fila


if __name__ == "__main__":  # prueba rápida: la gramática del mapa del 28 oct
    from grammar import leer_gramatica  # función del ítem 1
    gramatica = leer_gramatica(["1", "S -> S+i i"])  # S -> S+i | i
    producciones = numerar_producciones(gramatica)  # 0: S'->S, 1: S->S+i, 2: S->i
    cajas, flechas = construir_cajas(producciones)  # arma el mapa
    imprimir_cajas(cajas, flechas, producciones)  # debe dar 5 cajas
    from grammar import calcular_first, calcular_follow  # para la tabla
    first = calcular_first(gramatica)
    follow = calcular_follow(gramatica, first)
    action, goto_tabla, conflictos = construir_tabla_slr(producciones, cajas, flechas, follow)
    imprimir_tabla_slr(producciones, action, goto_tabla, len(cajas))
    print("Es SLR(1):", es_slr1(conflictos))
    for w in ["i", "i+i", "i+i+i", "i+", "+i", "ii"]:  # palabras de práctica
        print(w, "yes" if parsear_slr(producciones, action, goto_tabla, w) else "no")

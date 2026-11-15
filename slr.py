# slr.py: parser SLR(1)  (Aho, sección 4.6)
#
# Cómo se guardan las cosas:
#   producción  ->  ("S", ["S", "+", "i"])        cabeza y lado derecho
#   ítem        ->  (p, dedo)                      producción p con el punto en la posición dedo
#                   ej: (1, 2) = S -> S + • i
#   caja        ->  frozenset de ítems             = un estado del autómata LR(0)
#   flechas     ->  {(caja, símbolo): caja}        = las transiciones


# ============================================================
#  PASO 1: NUMERAR LAS PRODUCCIONES (gramática aumentada)
# ============================================================

def numerar_producciones(gramatica):
    producciones = [("S'", ["S"])]          # la 0 siempre es S' -> S
    for A in gramatica:                     # cada no terminal
        for alt in gramatica[A]:            # cada alternativa A -> alt
            producciones.append((A, alt))   # le toca el siguiente número
    return producciones


# ============================================================
#  PASO 2: CLOSURE
#  Si el punto está antes de una mayúscula B, agrega todos los B -> • ...
#  Repite hasta que no salga nada nuevo.
# ============================================================

def closure(items, producciones):
    resultado = set(items)
    cambio = True
    while cambio:                           # repite mientras se agregue algo
        cambio = False
        for (p, dedo) in list(resultado):   # list(): copia para poder agregar mientras recorro
            derecha = producciones[p][1]
            if dedo < len(derecha) and derecha[dedo].isupper():   # punto antes de una mayúscula
                for q in range(len(producciones)):
                    if producciones[q][0] == derecha[dedo] and (q, 0) not in resultado:
                        resultado.add((q, 0))   # agrega B -> • ...
                        cambio = True
    return frozenset(resultado)             # frozenset: no cambia, así se puede comparar y guardar


# ============================================================
#  PASO 3: GOTO(caja, X)
#  Avanza el punto sobre X en los ítems que lo esperaban, y luego closure.
# ============================================================

def goto(caja, X, producciones):
    movidos = set()
    for (p, dedo) in caja:
        derecha = producciones[p][1]
        if dedo < len(derecha) and derecha[dedo] == X:   # el punto estaba antes de X
            movidos.add((p, dedo + 1))                   # lo paso al otro lado de X
    return closure(movidos, producciones)


# ============================================================
#  PASO 4: ARMAR EL AUTÓMATA LR(0)
#  Arranca con closure(S' -> • S). A cada caja le aplica goto con
#  cada símbolo posible. Si sale una caja nueva, la agrega a la cola.
# ============================================================

def construir_cajas(producciones):
    cajas = [closure({(0, 0)}, producciones)]   # caja 0 = closure(S' -> • S)
    flechas = {}                                # (caja, símbolo) -> caja destino
    i = 0                                       # caja que estoy revisando
    while i < len(cajas):                       # la lista crece mientras recorro
        simbolos = set()                        # símbolos que están justo después de un punto
        for (p, dedo) in cajas[i]:
            derecha = producciones[p][1]
            if dedo < len(derecha):             # el punto no está al final
                simbolos.add(derecha[dedo])
        for X in sorted(simbolos):              # sorted: siempre el mismo orden -> mismos números
            nueva = goto(cajas[i], X, producciones)
            if nueva not in cajas:              # caja nueva -> se agrega
                cajas.append(nueva)
            flechas[(i, X)] = cajas.index(nueva)   # anoto la transición i --X--> destino
        i += 1
    return cajas, flechas


# ============================================================
#  SOLO PARA VER EL AUTÓMATA (no hace lógica, solo dibuja)
# ============================================================

# (2, 1) -> "S -> i •"
def mostrar_item(item, producciones):
    p, dedo = item
    cabeza, derecha = producciones[p]
    simbolos = derecha[:dedo] + ["•"] + derecha[dedo:]   # mete el punto en su posición
    return cabeza + " -> " + " ".join(simbolos)


def imprimir_cajas(cajas, flechas, producciones):
    for i, caja in enumerate(cajas):        # cada caja con sus ítems
        print(f"Caja {i}:")
        for item in sorted(caja):
            print("   ", mostrar_item(item, producciones))
    for (i, X), j in sorted(flechas.items()):   # luego todas las transiciones
        print(f"Caja {i} --{X}--> Caja {j}")    # ej: Caja 0 --S--> Caja 1


# ============================================================
#  PASO 5: LLENAR LA TABLA SLR  (Aho, Algoritmo 4.46)
# ============================================================

def construir_tabla_slr(producciones, cajas, flechas, follow):
    action = {}       # casillas de terminales:  (caja, letra) -> ("s", j) / ("r", p) / ("acc",)
    goto_tabla = {}   # casillas de mayúsculas:  (caja, mayúscula) -> j
    conflictos = []   # si queda algo aquí, NO es SLR(1)

    # Ayudante: escribe en una casilla. Si ya había algo distinto, es un choque.
    def poner(caja, letra, accion):
        if (caja, letra) in action and action[(caja, letra)] != accion:
            conflictos.append((caja, letra, action[(caja, letra)], accion))
        else:
            action[(caja, letra)] = accion

    # Regla 1: cada flecha del autómata
    for (i, X), j in flechas.items():
        if X.isupper():                 # flecha con mayúscula -> GOTO
            goto_tabla[(i, X)] = j
        else:                           # flecha con terminal -> shift
            poner(i, X, ("s", j))

    # Regla 2: ítems con el punto al final
    for i, caja in enumerate(cajas):
        for (p, dedo) in caja:
            cabeza, derecha = producciones[p]
            if dedo == len(derecha):    # punto al final = receta completa
                if p == 0:              # S' -> S •  -> aceptar con $
                    poner(i, "$", ("acc",))
                else:                   # A -> α •   -> reduce en cada letra de FOLLOW(A)
                    for a in follow[cabeza]:
                        poner(i, a, ("r", p))

    return action, goto_tabla, conflictos


# ¿Es SLR(1)? Sí, si no hubo ningún choque.
def es_slr1(conflictos):
    return len(conflictos) == 0


# ============================================================
#  PASO 6: PARSEAR UNA PALABRA  (Aho, Algoritmo 4.44)
#  Todo lo que dice "if traza" solo imprime. Puedes ignorarlo.
# ============================================================

def parsear_slr(producciones, action, goto_tabla, palabra, traza=False):
    pila = [0]                          # la pila arranca en el estado 0
    entrada = list(palabra) + ["$"]     # "i+i" -> ["i", "+", "i", "$"]
    i = 0                               # índice de la letra actual
    if traza:                           # (solo imprime)
        print(f"{'Pila':<18}{'Entrada':<12}Acción")

    while True:
        caja = pila[-1]                 # tope de la pila
        a = entrada[i]                  # letra actual
        accion = action.get((caja, a))  # leo la casilla (None si está vacía)
        fila = f"{' '.join(map(str, pila)):<18}{''.join(entrada[i:]):<12}"  # (solo imprime)

        # Casilla vacía -> rechazo
        if accion is None:
            if traza:
                print(fila + "error")
            return False

        # Shift: push del estado y avanzo
        if accion[0] == "s":
            if traza:
                print(fila + f"shift {accion[1]}")
            pila.append(accion[1])
            i += 1

        # Reduce: pop |derecha| veces, luego push de GOTO[tope, cabeza]
        elif accion[0] == "r":
            cabeza, derecha = producciones[accion[1]]
            if traza:
                print(fila + f"reduce {cabeza} -> {' '.join(derecha) or 'e'}")
            for _ in derecha:
                pila.pop()
            pila.append(goto_tabla[(pila[-1], cabeza)])

        # Acc -> acepto
        else:
            if traza:
                print(fila + "accept")
            return True


# ============================================================
#  SOLO PARA VER LA TABLA (no hace lógica, solo dibuja)
# ============================================================

def imprimir_tabla_slr(producciones, action, goto_tabla, n_cajas):
    letras = sorted({a for (_, a) in action if a != "$"}) + ["$"]  # columnas ACTION: terminales y $ al final
    nts = sorted({X for (_, X) in goto_tabla})                     # columnas GOTO: mayúsculas
    filas = [["Caja"] + letras + ["||"] + nts]                     # encabezado

    for i in range(n_cajas):            # una fila por estado
        celdas = []
        for a in letras:                # ("s", 2) -> "s2",  ("acc",) -> "acc",  vacía -> ""
            ac = action.get((i, a))
            celdas.append("" if ac is None else "acc" if ac[0] == "acc" else ac[0] + str(ac[1]))
        gs = [str(goto_tabla.get((i, X), "")) for X in nts]
        filas.append([str(i)] + celdas + ["||"] + gs)

    ancho = max(len(t) for fila in filas for t in fila)  # mismo ancho para que quede alineado
    for fila in filas:
        print(" ".join(t.ljust(ancho) for t in fila).rstrip())


# ============================================================
#  PRUEBA con  S -> S+i | i
# ============================================================

if __name__ == "__main__":  # esto solo corre con: python slr.py (o el botón ▶). Es una demostración con el hechizo
    from grammar import leer_gramatica, calcular_first, calcular_follow
    import sys
    sys.stdout.reconfigure(encoding="utf-8")  # para que • y las tildes se vean bien también en el panel Output del botón ▶

    # 1. Gramática -> recetas -> autómata (closure y goto)
    gramatica = leer_gramatica(["3", "S -> H", "H -> EH e", "E -> f a t v"])  # el hechizo: S -> H, H -> E H | ε, E -> f | a | t | v
    producciones = numerar_producciones(gramatica)   # 0: S'->S  1: S->H  2: H->E H  3: H->ε  4-7: E->f|a|t|v
    cajas, flechas = construir_cajas(producciones)
    print("1) Las cajas (autómata LR(0)), armadas con closure y goto:")
    imprimir_cajas(cajas, flechas, producciones)     # deben salir 9 cajas

    # 2. FOLLOW -> tabla
    first = calcular_first(gramatica)
    follow = calcular_follow(gramatica, first)
    action, goto_tabla, conflictos = construir_tabla_slr(producciones, cajas, flechas, follow)
    print()
    print("2) La tabla SLR (ACTION || GOTO):")
    imprimir_tabla_slr(producciones, action, goto_tabla, len(cajas))
    print("Es SLR(1):", es_slr1(conflictos))

    # 3. El parser con la pila de cajas, paso a paso
    for w in ["fa", "fx"]:  # una que pertenece y una que no
        print()
        print(f"3) El parser con la pila de cajas, con la cadena '{w}':")
        ok = parsear_slr(producciones, action, goto_tabla, w, traza=True)
        print("Resultado:", "yes" if ok else "no")

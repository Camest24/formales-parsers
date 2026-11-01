import sys  # para leer las opciones de la consola (sys.argv)
from grammar import leer_gramatica, calcular_first, calcular_follow, imprimir_sets
from ll1 import construir_tabla_ll1, es_ll1, parsear_ll1
from slr import numerar_producciones, construir_cajas, construir_tabla_slr, es_slr1, parsear_slr


def leer_palabra():  # lee una cadena a analizar; devuelve None cuando ya no hay más
    try:  # intenta leer una línea
        linea = input().strip()  # strip quita espacios y saltos de línea sobrantes
    except EOFError:  # el archivo de entrada se acabó (no hay más líneas)
        return None  # no hay más cadenas
    if linea == "":  # la línea vacía marca el final de las cadenas
        return None  # no hay más cadenas
    if linea == "e":  # la "e" sola representa la cadena vacía
        return ""  # devolvemos la cadena vacía de verdad
    return linea  # una cadena normal, ej: "adbc"


def main():  # punto de entrada del programa
    n = int(input())  # primera línea: cuántas producciones vienen
    lineas = [str(n)]  # leer_gramatica espera la lista completa, con el número de primero
    for i in range(n):  # leemos exactamente n líneas más
        lineas.append(input())  # cada una es una producción

    gramatica = leer_gramatica(lineas)  # texto -> diccionario
    first = calcular_first(gramatica)  # FIRST de cada no terminal
    follow = calcular_follow(gramatica, first)  # FOLLOW de cada no terminal

    if "--sets" in sys.argv:  # si se corrió con: python main.py --sets
        imprimir_sets(gramatica, first, follow)  # imprime los conjuntos

    tabla_ll1 = construir_tabla_ll1(gramatica, first, follow)  # el directorio LL(1)
    es_ll1_ok = es_ll1(tabla_ll1)  # ¿la tabla LL(1) no tiene choques?

    producciones = numerar_producciones(gramatica)  # recetas numeradas, con S' -> S
    cajas, flechas = construir_cajas(producciones)  # el mapa de cajas
    action, goto_tabla, conflictos = construir_tabla_slr(producciones, cajas, flechas, follow)  # letreros
    es_slr_ok = es_slr1(conflictos)  # ¿la tabla SLR no tiene choques?

    def parsear_t(palabra):  # parser LL(1) para una palabra
        return parsear_ll1(tabla_ll1, palabra)

    traza = "--trace" in sys.argv  # si se corrió con: python main.py --trace

    def parsear_b(palabra):  # parser SLR(1) para una palabra
        if traza:  # con --trace se imprime un título antes de cada palabra
            print(f"--- trace: {palabra or 'e'} ---")  # ej: --- trace: ((i)) ---
        return parsear_slr(producciones, action, goto_tabla, palabra, traza)  # traza=True imprime Pila / Entrada / Acción

    def responder_palabras(parsear):  # lee cadenas hasta la línea vacía y responde yes/no
        palabra = leer_palabra()  # primera cadena
        while palabra is not None:  # mientras haya cadenas
            print("yes" if parsear(palabra) else "no")  # responde
            palabra = leer_palabra()  # siguiente cadena

    if es_ll1_ok and es_slr_ok:  # caso 1: las dos
        while True:  # menú hasta que den Q
            print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")  # mensaje exacto del enunciado
            try:
                letra = input().strip()  # lee la letra
            except EOFError:  # se acabó la entrada
                break
            if letra == "Q":  # salir
                break
            if letra == "T":  # parser LL(1)
                responder_palabras(parsear_t)
            elif letra == "B":  # parser SLR(1)
                responder_palabras(parsear_b)
    elif es_ll1_ok:  # caso 2: solo LL(1)
        print("Grammar is LL(1).")  # mensaje exacto del enunciado
        responder_palabras(parsear_t)
    elif es_slr_ok:  # caso 3: solo SLR(1)
        print("Grammar is SLR(1).")  # mensaje exacto del enunciado
        responder_palabras(parsear_b)
    else:  # caso 4: ninguna
        print("Grammar is neither LL(1) nor SLR(1).")  # mensaje exacto del enunciado


if __name__ == "__main__":  # solo corre al ejecutar este archivo directamente
    main()

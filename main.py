import sys  # para leer las opciones de la consola (sys.argv)
from grammar import leer_gramatica, calcular_first, calcular_follow, imprimir_sets
from ll1 import construir_tabla_ll1, es_ll1, parsear_ll1


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
    es_ll1_ok = es_ll1(tabla_ll1)  # ¿la tabla no tiene choques?
    es_slr_ok = False  # TODO: cuando exista slr.py, preguntar si es SLR(1)

    if es_ll1_ok and es_slr_ok:  # caso 1: las dos
        pass  # TODO: el menú T / B / Q
    elif es_ll1_ok:  # caso 2: solo LL(1)
        print("Grammar is LL(1).")  # mensaje exacto del enunciado
        palabra = leer_palabra()  # primera cadena
        while palabra is not None:  # mientras haya cadenas
            print("yes" if parsear_ll1(tabla_ll1, palabra) else "no")  # responde yes o no
            palabra = leer_palabra()  # siguiente cadena
    elif es_slr_ok:  # caso 3: solo SLR(1)
        pass  # TODO: igual que el caso 2, pero con el parser SLR(1)
    else:  # caso 4: ninguna
        print("Grammar is neither LL(1) nor SLR(1).")  # mensaje exacto del enunciado


if __name__ == "__main__":  # solo corre al ejecutar este archivo directamente
    main()

import sys  # para leer las opciones de la consola (sys.argv)
from grammar import leer_gramatica, calcular_first, calcular_follow, imprimir_sets


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

    # TODO ítem 2: decidir si es LL(1) y/o SLR(1) y leer las cadenas


if __name__ == "__main__":  # solo corre al ejecutar este archivo directamente
    main()

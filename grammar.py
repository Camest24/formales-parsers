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


if __name__ == "__main__":  # solo corre al ejecutar este archivo directamente
    prueba = ["3", "S -> AB", "A -> aA d", "B -> bBc e"]
    print(leer_gramatica(prueba))

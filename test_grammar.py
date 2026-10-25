import unittest  # librería de pruebas que viene con Python
from grammar import leer_gramatica, first_de_cadena, calcular_first, calcular_follow, formatear_conjunto

EJEMPLO_1 = ["3", "S -> S+T T", "T -> T*F F", "F -> (S) i"]  # ejemplo 1 del enunciado
EJEMPLO_2 = ["3", "S -> AB", "A -> aA d", "B -> bBc e"]  # ejemplo 2 del enunciado
EJEMPLO_3 = ["1", "S -> SS a"]  # ejemplo 3 del enunciado
CON_EPSILON = ["3", "S -> ABc", "A -> a e", "B -> b e"]  # A y B pueden desaparecer
S_NO_PRIMERA = ["3", "B -> b", "A -> a", "S -> AB"]  # S no está en la primera línea


def conjuntos(lineas):  # atajo: lee la gramática y devuelve (first, follow)
    gramatica = leer_gramatica(lineas)  # texto -> diccionario
    first = calcular_first(gramatica)  # FIRST de cada no terminal
    return first, calcular_follow(gramatica, first)  # y su FOLLOW


class TestLeerGramatica(unittest.TestCase):  # pruebas de la lectura
    def test_ejemplo_2(self):  # alternativas separadas y épsilon como lista vacía
        self.assertEqual(leer_gramatica(EJEMPLO_2),
                         {"S": [["A", "B"]], "A": [["a", "A"], ["d"]], "B": [["b", "B", "c"], []]})

    def test_simbolos_especiales(self):  # + * ( ) se guardan como terminales normales
        self.assertEqual(leer_gramatica(EJEMPLO_1)["F"], [["(", "S", ")"], ["i"]])


class TestFirst(unittest.TestCase):  # pruebas de FIRST
    def test_ejemplo_1(self):  # recursión por la izquierda no aporta nada nuevo
        first, _ = conjuntos(EJEMPLO_1)
        self.assertEqual(first, {"S": {"(", "i"}, "T": {"(", "i"}, "F": {"(", "i"}})

    def test_ejemplo_2(self):  # B -> e hace que épsilon esté en FIRST(B)
        first, _ = conjuntos(EJEMPLO_2)
        self.assertEqual(first, {"S": {"a", "d"}, "A": {"a", "d"}, "B": {"b", "e"}})

    def test_ejemplo_3(self):  # gramática ambigua
        first, _ = conjuntos(EJEMPLO_3)
        self.assertEqual(first, {"S": {"a"}})

    def test_simbolos_que_desaparecen(self):  # avanza por A y B porque pueden ser épsilon
        first, _ = conjuntos(CON_EPSILON)
        self.assertEqual(first["S"], {"a", "b", "c"})

    def test_first_de_cadena_vacia(self):  # la cadena vacía da épsilon
        self.assertEqual(first_de_cadena([], {}), {"e"})


class TestFollow(unittest.TestCase):  # pruebas de FOLLOW
    def test_ejemplo_1(self):
        _, follow = conjuntos(EJEMPLO_1)
        self.assertEqual(follow, {"S": {"$", "+", ")"}, "T": {"$", "+", ")", "*"}, "F": {"$", "+", ")", "*"}})

    def test_ejemplo_2(self):  # B desaparece, entonces A se roba el FOLLOW de S
        _, follow = conjuntos(EJEMPLO_2)
        self.assertEqual(follow, {"S": {"$"}, "A": {"b", "$"}, "B": {"c", "$"}})

    def test_ejemplo_3(self):
        _, follow = conjuntos(EJEMPLO_3)
        self.assertEqual(follow, {"S": {"a", "$"}})

    def test_s_no_esta_primero(self):  # el $ va en S aunque S no sea la primera línea
        _, follow = conjuntos(S_NO_PRIMERA)
        self.assertEqual(follow, {"S": {"$"}, "A": {"b"}, "B": {"$"}})


class TestFormato(unittest.TestCase):  # pruebas del formato de --sets
    def test_orden_ascii(self):  # ) * + en orden ASCII y $ al final
        self.assertEqual(formatear_conjunto({"$", "+", ")", "*"}), "{), *, +, $}")

    def test_epsilon_antes_de_dolar(self):  # terminales, luego e, luego $
        self.assertEqual(formatear_conjunto({"$", "e", "b"}), "{b, e, $}")


if __name__ == "__main__":  # permite correrlo con: python test_grammar.py
    unittest.main()

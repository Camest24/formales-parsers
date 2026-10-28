import unittest  # librería de pruebas que viene con Python
from grammar import leer_gramatica, calcular_first, calcular_follow
from ll1 import construir_tabla_ll1, es_ll1, parsear_ll1


def tabla_de(lineas):  # atajo: de las líneas de la gramática a la tabla LL(1)
    gramatica = leer_gramatica(lineas)  # texto -> diccionario
    first = calcular_first(gramatica)  # FIRST
    return construir_tabla_ll1(gramatica, first, calcular_follow(gramatica, first))  # tabla


EJEMPLO_1 = ["3", "S -> S+T T", "T -> T*F F", "F -> (S) i"]  # SLR(1), no LL(1)
EJEMPLO_2 = ["3", "S -> AB", "A -> aA d", "B -> bBc e"]  # LL(1)
EJEMPLO_3 = ["1", "S -> SS a"]  # ni LL(1) ni SLR(1)
LUNES = ["2", "S -> aBc d", "B -> bB e"]  # la que hicimos a mano el 26 oct


class TestTabla(unittest.TestCase):  # pruebas de la tabla LL(1)
    def test_tabla_ejemplo_2(self):  # las 7 casillas que armamos a mano
        self.assertEqual(tabla_de(EJEMPLO_2), {
            ("S", "a"): [["A", "B"]], ("S", "d"): [["A", "B"]],
            ("A", "a"): [["a", "A"]], ("A", "d"): [["d"]],
            ("B", "b"): [["b", "B", "c"]], ("B", "c"): [[]], ("B", "$"): [[]]})

    def test_epsilon_va_en_follow(self):  # B -> e va en [B, c] porque FOLLOW(B) = {c}
        self.assertEqual(tabla_de(LUNES)[("B", "c")], [[]])

    def test_conflicto_recursion_izquierda(self):  # S -> S+T y S -> T chocan en [S, i]
        self.assertEqual(len(tabla_de(EJEMPLO_1)[("S", "i")]), 2)


class TestEsLL1(unittest.TestCase):  # pruebas de la decisión LL(1)
    def test_ejemplo_1_no(self):
        self.assertFalse(es_ll1(tabla_de(EJEMPLO_1)))

    def test_ejemplo_2_si(self):
        self.assertTrue(es_ll1(tabla_de(EJEMPLO_2)))

    def test_ejemplo_3_no(self):
        self.assertFalse(es_ll1(tabla_de(EJEMPLO_3)))


class TestParser(unittest.TestCase):  # pruebas del parser con pila
    def test_cadenas_del_enunciado(self):  # ejemplo 2: d yes, adbc yes, a no
        tabla = tabla_de(EJEMPLO_2)
        self.assertEqual([parsear_ll1(tabla, w) for w in ["d", "adbc", "a"]], [True, True, False])

    def test_cadena_vacia(self):  # S nunca desaparece en el ejemplo 2
        self.assertFalse(parsear_ll1(tabla_de(EJEMPLO_2), ""))

    def test_se_acaba_la_palabra(self):  # ab: todavía se espera la c
        self.assertFalse(parsear_ll1(tabla_de(LUNES), "ab"))

    def test_sobran_letras(self):  # dc: ya no se espera nada pero sobra la c
        self.assertFalse(parsear_ll1(tabla_de(LUNES), "dc"))

    def test_recursion_profunda(self):  # muchas b seguidas
        self.assertTrue(parsear_ll1(tabla_de(LUNES), "a" + "b" * 50 + "c"))


if __name__ == "__main__":  # permite correrlo con: python test_ll1.py
    unittest.main()

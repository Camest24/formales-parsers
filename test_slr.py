import io  # para atrapar lo que el parser imprime
import unittest  # librería de pruebas que viene con Python
from contextlib import redirect_stdout  # desvía los print hacia un cuaderno en memoria
from grammar import leer_gramatica, calcular_first, calcular_follow
from slr import numerar_producciones, construir_cajas, construir_tabla_slr, es_slr1, parsear_slr


def armar(lineas):  # atajo: de las líneas de la gramática a todo lo que usa el parser SLR
    g = leer_gramatica(lineas)  # texto -> diccionario
    follow = calcular_follow(g, calcular_first(g))  # FOLLOW
    prods = numerar_producciones(g)  # recetas numeradas
    cajas, flechas = construir_cajas(prods)  # mapa de cajas
    action, goto_t, conflictos = construir_tabla_slr(prods, cajas, flechas, follow)  # letreros
    return prods, cajas, flechas, action, goto_t, conflictos


EJEMPLO_1 = ["3", "S -> S+T T", "T -> T*F F", "F -> (S) i"]  # SLR(1), no LL(1)
EJEMPLO_2 = ["3", "S -> AB", "A -> aA d", "B -> bBc e"]  # las dos
EJEMPLO_3 = ["1", "S -> SS a"]  # ninguna
SUMA = ["1", "S -> S+i i"]  # el mapa de 5 cajas del 28 oct
MERCADO = ["2", "S -> Ab", "A -> aA c"]  # la gramática de la lista de mercado
SOLO_LL1 = ["3", "S -> AaAb BbBa", "A -> e", "B -> e"]  # LL(1) pero no SLR(1)


class TestCajas(unittest.TestCase):  # pruebas del autómata LR(0)
    def test_suma_5_cajas(self):  # el mapa del 28 oct
        _, cajas, flechas, *_ = armar(SUMA)
        self.assertEqual(len(cajas), 5)
        self.assertEqual(flechas, {(0, "S"): 1, (0, "i"): 2, (1, "+"): 3, (3, "i"): 4})

    def test_ejemplo_1_12_cajas(self):  # coincide con los estados I0..I11 del libro
        self.assertEqual(len(armar(EJEMPLO_1)[1]), 12)

    def test_flecha_que_da_la_vuelta(self):  # A -> a • A abre otra vez A: la caja de "llegó a" vuelve a sí misma
        _, _, flechas, *_ = armar(MERCADO)
        self.assertEqual(flechas[(3, "a")], 3)


class TestEsSLR(unittest.TestCase):  # pruebas de la decisión SLR(1)
    def test_ejemplo_1_si(self):
        self.assertTrue(es_slr1(armar(EJEMPLO_1)[5]))

    def test_ejemplo_2_si(self):
        self.assertTrue(es_slr1(armar(EJEMPLO_2)[5]))

    def test_ejemplo_3_no(self):
        self.assertFalse(es_slr1(armar(EJEMPLO_3)[5]))

    def test_solo_ll1_no(self):  # conflicto reduce/reduce: A -> e y B -> e
        self.assertFalse(es_slr1(armar(SOLO_LL1)[5]))


class TestParser(unittest.TestCase):  # pruebas del parser LR
    def palabras(self, lineas, ws):
        prods, _, _, action, goto_t, _ = armar(lineas)
        return [parsear_slr(prods, action, goto_t, w) for w in ws]

    def test_cadenas_ejemplo_1(self):  # las del enunciado
        self.assertEqual(self.palabras(EJEMPLO_1, ["i+i", "(i)", "(i+i)*i)"]), [True, True, False])

    def test_cadenas_ejemplo_2(self):
        self.assertEqual(self.palabras(EJEMPLO_2, ["d", "adbc", "a", ""]), [True, True, False, False])

    def test_suma(self):  # las de los juegos
        self.assertEqual(self.palabras(SUMA, ["i", "i+i+i", "i+", "+i", "ii"]), [True, True, False, False, False])

    def test_anidamiento_profundo(self):  # 50 paréntesis anidados
        self.assertEqual(self.palabras(EJEMPLO_1, ["(" * 50 + "i" + ")" * 50, "(" * 50 + "i" + ")" * 49]), [True, False])

    def traza(self, w, lineas=SUMA):  # corre el parser con traza=True y devuelve (resultado, líneas impresas)
        prods, _, _, action, goto_t, _ = armar(lineas)
        cuaderno = io.StringIO()  # un cuaderno en memoria donde cae lo que se imprimiría
        with redirect_stdout(cuaderno):  # los print van al cuaderno, no a la consola
            ok = parsear_slr(prods, action, goto_t, w, traza=True)
        return ok, cuaderno.getvalue().splitlines()

    def test_traza_acciones(self):  # i+i: el mismo recorrido del juego de las migas
        ok, lineas = self.traza("i+i")
        self.assertTrue(ok)
        self.assertTrue(lineas[0].startswith("Pila"))  # la primera línea es el encabezado
        self.assertEqual([l[30:] for l in lineas[1:]],  # la columna Acción empieza en el carácter 30
                         ["shift 2", "reduce S -> i", "shift 3", "shift 4", "reduce S -> S + i", "accept"])

    def test_traza_error(self):  # ii: se atasca en la caja 2 con una i
        ok, lineas = self.traza("ii")
        self.assertFalse(ok)
        self.assertEqual([l[30:] for l in lineas[1:]], ["shift 2", "error"])

    def test_sin_traza_no_imprime(self):  # por defecto el parser no escribe nada en pantalla
        cuaderno = io.StringIO()
        with redirect_stdout(cuaderno):
            self.palabras(SUMA, ["i+i"])
        self.assertEqual(cuaderno.getvalue(), "")


if __name__ == "__main__":  # permite correrlo con: python test_slr.py
    unittest.main()

import copy  # para modificar copias del SDD en las pruebas
import json
import unittest
from sdd import cargar_archivo, cargar_sdd, evaluar_cadena, SDDError, preorden

HECHIZO = "ejemplos/sdd_hechizo.json"  # el SDD de Mariana (puntaje de hechizos)
CIRCULAR = "ejemplos/sdd_hechizo_circular.json"  # el mismo con H1.ant = H.pts (a propósito)


def datos_hechizo():  # el JSON del hechizo como diccionario, para modificarlo en las pruebas
    with open(HECHIZO, encoding="utf-8") as f:
        return json.load(f)


class TestEvaluador(unittest.TestCase):  # pruebas del evaluador con el SDD del hechizo
    @classmethod
    def setUpClass(cls):
        cls.sdd = cargar_archivo(HECHIZO)

    def valor(self, palabra):  # atajo: el puntaje de una cadena
        r = evaluar_cadena(self.sdd, palabra)
        self.assertTrue(r["pertenece"])
        return r["valor"]

    def test_ejemplo_a_mano(self):  # el hechizo f a a t v del informe: 0+1+0+1+1
        self.assertEqual(self.valor("faatv"), 3)

    def test_cadena_mas_corta(self):  # un solo elemento y la cadena vacía no suman nada
        self.assertEqual(self.valor("f"), 0)
        self.assertEqual(self.valor(""), 0)

    def test_cadena_que_no_pertenece(self):  # x no es un elemento
        self.assertFalse(evaluar_cadena(self.sdd, "fxa")["pertenece"])

    def test_anidamiento_profundo(self):  # 3000 elementos alternados: todos cambian menos el primero
        self.assertEqual(self.valor("fa" * 1500), 2999)

    def test_todo_repetido_y_todo_distinto(self):  # los dos extremos
        self.assertEqual(self.valor("ffff"), 0)
        self.assertEqual(self.valor("fatvf"), 4)

    def test_valores_del_arbol_anotado(self):  # los post-its coinciden con los del ejemplo a mano
        r = evaluar_cadena(self.sdd, "faatv")
        hs = [n for n in preorden(r["raiz"]) if n.simbolo == "H"]
        self.assertEqual([h.attrs["ant"] for h in hs], ["n", "f", "a", "a", "t", "v"])
        self.assertEqual([h.attrs["pts"] for h in hs], [3, 3, 2, 2, 1, 0])

    def test_grafo_del_ejemplo(self):  # 33 vértices y 36 flechas, como en el dibujo a mano
        r = evaluar_cadena(self.sdd, "faatv")
        self.assertEqual(len(r["instancias"]), 33)
        self.assertEqual(len(r["aristas"]), 36)

    def test_orden_respeta_las_flechas(self):  # en un orden topológico toda flecha va hacia adelante
        r = evaluar_cadena(self.sdd, "faatv")
        pos = {clave: i for i, (clave, _) in enumerate(r["orden"])}
        self.assertEqual(len(pos), 33)
        for de, a in r["aristas"]:
            self.assertLess(pos[de], pos[a])


class TestCircular(unittest.TestCase):  # el SDD circular debe detectarse
    @classmethod
    def setUpClass(cls):
        cls.sdd = cargar_archivo(CIRCULAR)

    def test_detecta_el_ciclo(self):  # con dos elementos ya hay ciclo
        r = evaluar_cadena(self.sdd, "fa")
        self.assertTrue(r["pertenece"])
        self.assertTrue(r["circular"])
        self.assertEqual(r["ciclo"][0], r["ciclo"][-1])  # un ciclo vuelve a donde empezó
        self.assertEqual(r["valor"], None)  # y no se evalúa nada

    def test_con_un_elemento_no_hay_ciclo(self):  # el ciclo depende de la cadena
        self.assertFalse(evaluar_cadena(self.sdd, "f")["circular"])

    def test_la_cadena_que_no_pertenece_sigue_siendo_no(self):
        self.assertFalse(evaluar_cadena(self.sdd, "z")["pertenece"])


class TestValidacion(unittest.TestCase):  # un SDD mal hecho debe rechazarse
    def rechaza(self, datos, fragmento):  # el SDD falla y el mensaje menciona el fragmento
        with self.assertRaises(SDDError) as c:
            cargar_sdd(datos)
        self.assertIn(fragmento, str(c.exception))

    def test_falta_una_regla(self):
        d = datos_hechizo()
        d["rules"]["H -> e"] = []
        self.rechaza(d, "falta definir H.pts")

    def test_atributo_definido_dos_veces(self):
        d = datos_hechizo()
        d["rules"]["H -> e"] = ["H.pts = 0", "H.pts = 1"]
        self.rechaza(d, "se define más de una vez")

    def test_s_con_heredado(self):
        d = datos_hechizo()
        d["attributes"]["S"]["x"] = {"kind": "inherited", "type": "integer", "meaning": "no permitido"}
        self.rechaza(d, "S no puede tener atributos heredados")

    def test_atributo_que_no_existe(self):
        d = datos_hechizo()
        d["rules"]["S -> H"] = ["H.ant = 'n'", "S.pts = H.nada"]
        self.rechaza(d, "H.nada no existe")

    def test_regla_con_codigo_peligroso(self):  # las reglas no pueden llamar cualquier cosa
        d = datos_hechizo()
        d["rules"]["H -> e"] = ["H.pts = __import__('os').getcwd()"]
        self.rechaza(d, "permit")  # el mensaje dice "no permitida" o "no se permite"

    def test_produccion_que_no_esta_en_la_gramatica(self):
        d = datos_hechizo()
        d["rules"]["H -> E E"] = ["H.pts = 0"]
        self.rechaza(d, "no está en la gramática")


if __name__ == "__main__":
    unittest.main()

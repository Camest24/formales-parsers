# app.py: servidor web (bono). Es el "mesero": recibe el pedido de la página, se lo pasa a la "cocina"
# (grammar.py, ll1.py, slr.py, sdd.py) y devuelve el plato en JSON. Solo usa la librería estándar.
import io  # cuaderno en memoria para atrapar lo que imprimen las funciones
import json  # pedidos y respuestas viajan en JSON
import os  # para encontrar los archivos junto a este
from contextlib import redirect_stdout  # desvía los print hacia el cuaderno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # el servidor de la librería estándar

import sdd  # ítem 3
from grammar import leer_gramatica, calcular_first, calcular_follow, imprimir_sets  # ítem 1
from ll1 import construir_tabla_ll1, es_ll1, parsear_ll1, imprimir_tabla_ll1  # ítem 2: LL(1)
from slr import numerar_producciones, construir_cajas, construir_tabla_slr, es_slr1, parsear_slr  # ítem 2: SLR(1)
from slr import imprimir_cajas, imprimir_tabla_slr

CARPETA = os.path.dirname(os.path.abspath(__file__))  # la carpeta parsers
PUERTO = 8000  # la página queda en http://localhost:8000
MAX_SDD = 300  # largo máximo de una cadena para el SDD en la web (el árbol viaja como JSON anidado)


def capturar(funcion, *args, **kwargs):  # corre una función que imprime; devuelve (lo que retorna, lo que imprimió)
    cuaderno = io.StringIO()
    with redirect_stdout(cuaderno):
        resultado = funcion(*args, **kwargs)
    return resultado, cuaderno.getvalue()


def preparar(texto):  # la gramática en texto -> todo lo que usan los parsers (lo mismo que hace main.py)
    lineas = [l for l in texto.strip().splitlines() if l.strip()]  # quita líneas vacías
    g = leer_gramatica(lineas)
    first = calcular_first(g)
    follow = calcular_follow(g, first)
    producciones = numerar_producciones(g)
    cajas, flechas = construir_cajas(producciones)
    action, goto_tabla, conflictos = construir_tabla_slr(producciones, cajas, flechas, follow)
    tabla_ll1 = construir_tabla_ll1(g, first, follow)
    return {"g": g, "first": first, "follow": follow, "producciones": producciones, "cajas": cajas,
            "flechas": flechas, "action": action, "goto": goto_tabla, "ll1": tabla_ll1,
            "es_ll1": es_ll1(tabla_ll1), "es_slr1": es_slr1(conflictos)}


def leer_cadena(datos):  # la cadena del pedido; "e" es la cadena vacía, igual que en la consola
    w = datos.get("word", "").strip()
    return "" if w == "e" else w


# ---------- Los pedidos (endpoints) ----------

def pedido_sets(datos):  # /api/sets: FIRST y FOLLOW
    G = preparar(datos["grammar"])
    _, texto = capturar(imprimir_sets, G["g"], G["first"], G["follow"])
    return {"text": texto}


def pedido_tables(datos):  # /api/tables: tablas, cajas y qué tipo de gramática es
    G = preparar(datos["grammar"])
    _, ll1 = capturar(imprimir_tabla_ll1, G["g"], G["ll1"])
    _, cajas = capturar(imprimir_cajas, G["cajas"], G["flechas"], G["producciones"])
    _, slr = capturar(imprimir_tabla_slr, G["producciones"], G["action"], G["goto"], len(G["cajas"]))
    if G["es_ll1"] and G["es_slr1"]:  # los 4 casos del enunciado
        tipo = "Grammar is LL(1) and SLR(1)."
    elif G["es_ll1"]:
        tipo = "Grammar is LL(1)."
    elif G["es_slr1"]:
        tipo = "Grammar is SLR(1)."
    else:
        tipo = "Grammar is neither LL(1) nor SLR(1)."
    return {"kind": tipo, "ll1": G["es_ll1"], "slr1": G["es_slr1"], "ll1_table": ll1, "automaton": cajas, "slr_table": slr}


def pedido_parse(datos):  # /api/parse: yes/no con el parser elegido (T = LL(1), B = SLR(1))
    G = preparar(datos["grammar"])
    w = leer_cadena(datos)
    if datos.get("parser") == "T":
        if not G["es_ll1"]:
            return {"error": "The grammar is not LL(1)."}
        return {"answer": "yes" if parsear_ll1(G["ll1"], w) else "no", "trace": ""}
    if not G["es_slr1"]:
        return {"error": "The grammar is not SLR(1)."}
    ok, traza = capturar(parsear_slr, G["producciones"], G["action"], G["goto"], w, traza=True)
    return {"answer": "yes" if ok else "no", "trace": traza}


def pedido_sdd(datos):  # /api/sdd: evalúa el SDD (en JSON) con una cadena
    w = leer_cadena(datos)
    if len(w) > MAX_SDD:
        return {"error": f"Use at most {MAX_SDD} symbols here (the console has no limit)."}
    s = sdd.cargar_sdd(json.loads(datos["sdd"]))  # el SDD como datos; si está mal hecho lanza SDDError
    r = sdd.evaluar_cadena(s, w)
    _, texto = capturar(sdd.imprimir_resultado, s, r, True)  # la misma salida de la consola, con el grafo
    respuesta = {"belongs": r["pertenece"], "circular": r["circular"], "cycle": r["ciclo"], "text": texto}
    if r["pertenece"] and not r["circular"]:
        respuesta["tree"] = sdd.arbol_a_dict(r["raiz"], s)
        respuesta["value"] = r["valor"]
        respuesta["main"] = "S." + s["principal"]
    return respuesta


def pedido_examples():  # GET /api/examples: la gramática y los SDD de la carpeta ejemplos
    carpeta = os.path.join(CARPETA, "ejemplos")
    sdds = {}
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.startswith("sdd_") and nombre.endswith(".json"):
            with open(os.path.join(carpeta, nombre), encoding="utf-8") as f:
                sdds[nombre] = f.read()
    hechizo = json.loads(sdds["sdd_hechizo.json"])["grammar"]  # la gramática del hechizo
    return {"grammar": "\n".join(hechizo), "sdds": sdds}


PEDIDOS = {"/api/sets": pedido_sets, "/api/tables": pedido_tables, "/api/parse": pedido_parse, "/api/sdd": pedido_sdd}


class Mesero(BaseHTTPRequestHandler):  # atiende cada pedido que llega del navegador
    def responder(self, codigo, cuerpo, tipo="application/json; charset=utf-8"):  # manda la respuesta
        datos = cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):  # pedir la página o los ejemplos
        if self.path in ("/", "/index.html"):
            with open(os.path.join(CARPETA, "web", "index.html"), encoding="utf-8") as f:
                self.responder(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/examples":
            self.responder(200, json.dumps(pedido_examples()))
        else:
            self.responder(404, json.dumps({"error": "not found"}))

    def do_POST(self):  # un pedido a la cocina
        if self.path not in PEDIDOS:
            self.responder(404, json.dumps({"error": "not found"}))
            return
        largo = int(self.headers.get("Content-Length", 0))
        try:
            datos = json.loads(self.rfile.read(largo) or b"{}")
            respuesta = PEDIDOS[self.path](datos)  # la cocina hace su trabajo
        except Exception as e:  # gramática o SDD mal escritos: se le cuenta a la página, el servidor sigue vivo
            respuesta = {"error": f"{type(e).__name__}: {e}"}
        self.responder(200, json.dumps(respuesta))

    def log_message(self, *args):  # no llenar la consola con cada pedido
        pass


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("127.0.0.1", PUERTO), Mesero)
    print(f"Open http://localhost:{PUERTO}  (Ctrl+C to stop)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

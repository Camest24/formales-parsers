# sdd.py: evaluador de SDD (Aho 5.1 y 5.2). El SDD vive en un archivo JSON y este código no sabe nada de él.
# Analogía: el árbol es un organigrama; cada atributo es una ficha por llenar; cada regla dice cómo llenarla.
import ast  # lee cada regla como una expresión de Python que revisamos nosotros (nunca se usa eval)
import json  # el SDD se guarda como datos en un archivo JSON
import operator  # + - == != < ... como funciones
import sys  # para leer las opciones de la consola
from collections import deque  # cola para el orden topológico

from grammar import leer_gramatica, calcular_first, calcular_follow
from slr import numerar_producciones, construir_cajas, construir_tabla_slr, es_slr1


class SDDError(Exception):  # el archivo del SDD está mal hecho
    pass


class Nodo:  # una ficha del organigrama: un nodo del árbol de derivación
    def __init__(self, simbolo, produccion=None, hijos=None):
        self.simbolo = simbolo  # 'H', 'E', 'f', ...
        self.produccion = produccion  # número de receta con la que se creó (None si es terminal)
        self.hijos = hijos or []  # hijos de izquierda a derecha
        self.attrs = {}  # atributo -> valor (se llena al evaluar)
        self.nombre = simbolo  # nombre único, ej: H3 (se asigna en numerar_nodos)
        if not simbolo.isupper():  # un terminal trae su lexval desde el principio
            self.attrs["lexval"] = simbolo  # lexval = el carácter mismo


def parsear_slr_arbol(producciones, action, goto_tabla, palabra):  # igual que parsear_slr pero devuelve el árbol (o None)
    pila = [0]  # pila de cajas
    nodos = []  # pila paralela: un nodo por cada símbolo leído o reducido
    entrada = list(palabra) + ["$"]  # la palabra con $ al final
    i = 0  # letra que toca
    while True:
        accion = action.get((pila[-1], entrada[i]))  # letrero de esta caja para esta letra
        if accion is None:  # casilla vacía
            return None  # la palabra no pertenece
        if accion[0] == "s":  # shift
            pila.append(accion[1])  # sube la caja destino
            nodos.append(Nodo(entrada[i]))  # nace un nodo terminal
            i += 1  # avanza en la palabra
        elif accion[0] == "r":  # reduce
            cabeza, derecha = producciones[accion[1]]  # receta con la que se reduce
            corte = len(nodos) - len(derecha)  # desde aquí están los hijos
            hijos = nodos[corte:]  # los últimos len(derecha) nodos son los hijos
            del nodos[corte:]  # salen de la pila de nodos
            for _ in derecha:  # una caja por cada símbolo de la receta
                pila.pop()  # retrocede esas cajas
            pila.append(goto_tabla[(pila[-1], cabeza)])  # sigue la flecha de la mayúscula
            nodos.append(Nodo(cabeza, accion[1], hijos))  # nace el nodo padre con sus hijos
        else:  # acc
            return nodos[0]  # lo único que queda es la raíz S


# ---------- Leer y revisar el SDD (los datos) ----------

PERMITIDOS = (ast.Constant, ast.Attribute, ast.Name, ast.Load, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
              ast.IfExp, ast.Call, ast.Add, ast.Sub, ast.Mult, ast.Mod, ast.FloorDiv, ast.USub, ast.Not, ast.And,
              ast.Or, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)  # lo único que puede aparecer en una regla
OPERADORES = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Mod: operator.mod,
              ast.FloorDiv: operator.floordiv, ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
              ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}  # operador de ast -> función
FUNCIONES = {"max": max, "min": min, "abs": abs, "len": len, "str": str, "int": int}  # funciones que una regla puede llamar


def base_de(ficha):  # 'H1' -> 'H' (los números solo distinguen apariciones repetidas de un no terminal)
    return ficha.rstrip("0123456789") if ficha[0].isupper() else ficha


def leer_regla(texto, nombres):  # convierte "H1.ant = E.el" en un diccionario con destino, expresión y usos
    try:
        arbol = ast.parse(texto.strip())  # Python ya sabe leer "A.b = expresión"
    except SyntaxError:
        raise SDDError(f"regla mal escrita: {texto}")
    if len(arbol.body) != 1 or not isinstance(arbol.body[0], ast.Assign):  # debe ser una sola asignación
        raise SDDError(f"la regla debe ser 'Simbolo.atributo = expresión': {texto}")
    asignacion = arbol.body[0]
    destino = asignacion.targets[0]  # lo que está a la izquierda del =
    if len(asignacion.targets) != 1 or not isinstance(destino, ast.Attribute) or not isinstance(destino.value, ast.Name):
        raise SDDError(f"el lado izquierdo debe ser 'Simbolo.atributo': {texto}")
    expr = asignacion.value  # lo que está a la derecha del =
    nodos = list(ast.walk(expr))  # todas las piezas de la expresión
    bases = {id(n.value) for n in nodos if isinstance(n, ast.Attribute)}  # nombres usados como Simbolo.atributo
    bases |= {id(n.func) for n in nodos if isinstance(n, ast.Call)}  # nombres usados como función
    for n in nodos:
        if not isinstance(n, PERMITIDOS):  # una pieza que no está en la lista blanca
            raise SDDError(f"no se permite '{type(n).__name__}' en la regla: {texto}")
        if isinstance(n, ast.Name) and id(n) not in bases:  # un nombre suelto, sin atributo
            raise SDDError(f"'{n.id}' debe escribirse como Simbolo.atributo: {texto}")
        if isinstance(n, ast.Attribute) and not isinstance(n.value, ast.Name):
            raise SDDError(f"solo se permite Simbolo.atributo: {texto}")
        if isinstance(n, ast.Call) and (not isinstance(n.func, ast.Name) or n.func.id not in FUNCIONES or n.keywords):
            raise SDDError(f"función no permitida en la regla: {texto}")
    usos = list(dict.fromkeys((n.value.id, n.attr) for n in nodos if isinstance(n, ast.Attribute)))  # atributos que la regla necesita, sin repetir
    for nombre in [destino.value.id] + [u[0] for u in usos]:
        if nombre not in nombres:  # símbolo que no aparece en la producción
            raise SDDError(f"'{nombre}' no aparece en la producción de la regla: {texto}")
    return {"destino": (destino.value.id, destino.attr), "expr": expr, "usos": usos, "texto": texto.strip()}


def mostrar_produccion(cabeza, derecha):  # ('H', ['E','H']) -> "H -> E H"
    return cabeza + " -> " + (" ".join(derecha) or "e")


def cargar_sdd(datos):  # datos: el diccionario leído del JSON; devuelve todo lo que necesita el evaluador
    gramatica = leer_gramatica(datos["grammar"])  # texto -> diccionario (ítem 1)
    first = calcular_first(gramatica)  # FIRST
    follow = calcular_follow(gramatica, first)  # FOLLOW
    producciones = numerar_producciones(gramatica)  # recetas numeradas
    cajas, flechas = construir_cajas(producciones)  # autómata LR(0)
    action, goto_tabla, conflictos = construir_tabla_slr(producciones, cajas, flechas, follow)  # tabla SLR
    if not es_slr1(conflictos):  # el árbol se construye con nuestro parser SLR
        raise SDDError("la gramática del SDD no es SLR(1)")
    atributos = datos["attributes"]  # símbolo -> {atributo: {kind, type, meaning}}
    nombres = {p: [c] + list(d) for p, (c, d) in enumerate(producciones)}  # nombres por defecto de cada receta
    reglas = {p: [] for p in range(len(producciones))}  # número de receta -> reglas semánticas
    for clave, textos in datos["rules"].items():  # una entrada por producción: "H -> E H1": [reglas]
        cabeza, cuerpo = clave.split("->", 1)  # "H " y " E H1"
        fichas = [] if cuerpo.split() == ["e"] else cuerpo.split()  # "e" es ε
        buscada = (cabeza.strip(), [base_de(f) for f in fichas])  # la receta sin los números
        p = next((i for i, pr in enumerate(producciones) if i > 0 and pr == buscada), None)  # ¿cuál receta es?
        if p is None:
            raise SDDError(f"la producción '{clave}' no está en la gramática")
        nombres[p] = [buscada[0]] + fichas  # nombres con los que las reglas llaman a cada símbolo
        if len(set(nombres[p])) != len(nombres[p]):
            raise SDDError(f"hay símbolos repetidos en '{clave}': distínguelos con números (H1, H2)")
        reglas[p] = [leer_regla(t, nombres[p]) for t in textos]  # lee cada regla
    sdd = {"producciones": producciones, "action": action, "goto": goto_tabla, "atributos": atributos,
           "nombres": nombres, "reglas": reglas, "principal": datos.get("main"), "nombre": datos.get("name", "")}
    errores = validar_sdd(sdd)  # revisa las condiciones del enunciado
    if errores:
        raise SDDError("\n".join(errores))
    return sdd


def validar_sdd(sdd):  # devuelve la lista de errores del SDD (vacía si todo está bien)
    errores = []
    atributos, producciones = sdd["atributos"], sdd["producciones"]
    for simbolo, attrs in atributos.items():  # revisa la tabla de atributos
        for a, d in attrs.items():
            if d.get("kind") not in ("synthesized", "inherited"):
                errores.append(f"{simbolo}.{a}: 'kind' debe ser synthesized o inherited")
            if simbolo == "S" and d.get("kind") == "inherited":
                errores.append(f"S no puede tener atributos heredados ({a})")
    if sdd["principal"] is None or sdd["principal"] not in atributos.get("S", {}):
        errores.append("'main' debe ser un atributo sintetizado de S")
    for p in range(1, len(producciones)):  # revisa cada producción
        cabeza, derecha = producciones[p]
        nombres = sdd["nombres"][p]
        simbolos = [cabeza] + derecha  # el símbolo que hay en cada posición
        esperados = [(nombres[0], a) for a, d in atributos.get(cabeza, {}).items() if d.get("kind") == "synthesized"]
        for k, s in enumerate(derecha, start=1):  # los hijos no terminales reciben sus heredados
            if s.isupper():
                esperados += [(nombres[k], a) for a, d in atributos.get(s, {}).items() if d.get("kind") == "inherited"]
        destinos = [r["destino"] for r in sdd["reglas"][p]]  # lo que las reglas definen
        texto = mostrar_produccion(cabeza, derecha)
        for e in esperados:
            if e not in destinos:
                errores.append(f"[{texto}] falta definir {e[0]}.{e[1]}")
        for d in set(destinos):
            if destinos.count(d) > 1:
                errores.append(f"[{texto}] {d[0]}.{d[1]} se define más de una vez")
            elif d not in esperados:
                errores.append(f"[{texto}] {d[0]}.{d[1]} no se puede definir aquí (debe ser sintetizado de la cabeza o heredado de un hijo)")
        for r in sdd["reglas"][p]:  # los atributos usados deben existir
            for nombre, a in r["usos"]:
                simbolo = simbolos[nombres.index(nombre)]
                existe = (a == "lexval") if not simbolo.isupper() else (a in atributos.get(simbolo, {}))
                if not existe:
                    errores.append(f"[{texto}] {nombre}.{a} no existe")
    return errores


def cargar_archivo(ruta):  # lee un archivo JSON y lo convierte en SDD
    with open(ruta, encoding="utf-8") as f:
        return cargar_sdd(json.load(f))


# ---------- Árbol, grafo de dependencias y evaluación ----------

def preorden(raiz):  # los nodos con la raíz primero, luego los hijos de izquierda a derecha (sin recursión)
    lista, pila = [], [raiz]
    while pila:
        n = pila.pop()
        lista.append(n)
        pila.extend(reversed(n.hijos))
    return lista


def numerar_nodos(raiz):  # le da a cada nodo un nombre único: S1, H1, H2, E1, f1, ...
    cuenta = {}
    for n in preorden(raiz):
        cuenta[n.simbolo] = cuenta.get(n.simbolo, 0) + 1
        n.nombre = f"{n.simbolo}{cuenta[n.simbolo]}"


def construir_grafo(raiz, sdd):  # el grafo de dependencias de este árbol (Aho 5.2.1)
    nodos = preorden(raiz)
    instancias = []  # un vértice por cada atributo de cada nodo, ej: 'H2.ant'
    donde = {}  # 'H2.ant' -> el nodo dueño del atributo
    definicion = {}  # 'H2.ant' -> (expresión que lo calcula, {nombre en la regla: nodo})
    aristas = []  # (de, a): 'de' se necesita para calcular 'a'
    for n in nodos:
        lista = ["lexval"] if n.produccion is None else list(sdd["atributos"].get(n.simbolo, {}))
        for a in lista:
            instancias.append(f"{n.nombre}.{a}")
            donde[f"{n.nombre}.{a}"] = n
    for n in nodos:
        if n.produccion is None:  # los terminales no tienen reglas
            continue
        mapa = dict(zip(sdd["nombres"][n.produccion], [n] + n.hijos))  # 'H' -> este nodo, 'E' -> su primer hijo...
        for r in sdd["reglas"][n.produccion]:
            destino = f"{mapa[r['destino'][0]].nombre}.{r['destino'][1]}"
            definicion[destino] = (r["expr"], mapa)
            for nombre, a in r["usos"]:
                aristas.append((f"{mapa[nombre].nombre}.{a}", destino))  # flecha: del atributo usado al definido
    return instancias, donde, definicion, aristas


def orden_topologico(instancias, aristas):  # Kahn: devuelve (orden, []) o (None, ciclo)
    entran = {x: 0 for x in instancias}  # cuántas flechas le llegan a cada vértice
    salen = {x: [] for x in instancias}  # a quién apunta cada vértice
    antes = {x: [] for x in instancias}  # quién le apunta a cada vértice
    for de, a in aristas:
        salen[de].append(a)
        antes[a].append(de)
        entran[a] += 1
    cola = deque(x for x in instancias if entran[x] == 0)  # los que no dependen de nadie
    orden = []
    while cola:
        x = cola.popleft()  # saca uno que ya se puede calcular
        orden.append(x)
        for y in salen[x]:  # a los que dependían de él les falta una flecha menos
            entran[y] -= 1
            if entran[y] == 0:
                cola.append(y)
    if len(orden) == len(instancias):  # todos salieron: no hay ciclos
        return orden, []
    pendientes = {x for x in instancias if entran[x] > 0}  # los que quedaron atrapados
    x, visto = next(iter(sorted(pendientes))), []
    while x not in visto:  # camina hacia atrás por los pendientes hasta repetir uno
        visto.append(x)
        x = next(y for y in antes[x] if y in pendientes)
    ciclo = visto[visto.index(x):][::-1]  # el ciclo, en el sentido de las flechas
    return None, ciclo + [ciclo[0]]


def evaluar_expr(e, valor):  # calcula una expresión de una regla; valor(nombre, atributo) busca un atributo
    if isinstance(e, ast.Constant):
        return e.value
    if isinstance(e, ast.Attribute):
        return valor(e.value.id, e.attr)
    if isinstance(e, ast.BinOp):
        return OPERADORES[type(e.op)](evaluar_expr(e.left, valor), evaluar_expr(e.right, valor))
    if isinstance(e, ast.UnaryOp):
        x = evaluar_expr(e.operand, valor)
        return (not x) if isinstance(e.op, ast.Not) else -x
    if isinstance(e, ast.BoolOp):  # and / or: se detiene en cuanto se sabe la respuesta
        for sub in e.values:
            r = evaluar_expr(sub, valor)
            if (isinstance(e.op, ast.And) and not r) or (isinstance(e.op, ast.Or) and r):
                return r
        return r
    if isinstance(e, ast.Compare):  # a < b < c
        izq = evaluar_expr(e.left, valor)
        for op, der in zip(e.ops, e.comparators):
            d = evaluar_expr(der, valor)
            if not OPERADORES[type(op)](izq, d):
                return False
            izq = d
        return True
    if isinstance(e, ast.IfExp):
        return evaluar_expr(e.body, valor) if evaluar_expr(e.test, valor) else evaluar_expr(e.orelse, valor)
    if isinstance(e, ast.Call):
        return FUNCIONES[e.func.id](*[evaluar_expr(a, valor) for a in e.args])
    raise SDDError("expresión no soportada")


def evaluar_cadena(sdd, palabra):  # todo el ítem 3 para una cadena; devuelve un diccionario con el resultado
    resultado = {"pertenece": False, "circular": False, "ciclo": [], "raiz": None,
                 "instancias": [], "aristas": [], "orden": [], "valor": None}
    raiz = parsear_slr_arbol(sdd["producciones"], sdd["action"], sdd["goto"], palabra)  # nuestro parser, con árbol
    if raiz is None:
        return resultado  # no pertenece
    resultado["pertenece"] = True
    numerar_nodos(raiz)
    instancias, donde, definicion, aristas = construir_grafo(raiz, sdd)
    orden, ciclo = orden_topologico(instancias, aristas)
    resultado.update(raiz=raiz, instancias=instancias, aristas=aristas)
    if ciclo:  # hay ciclo: el SDD es circular para esta cadena
        resultado.update(circular=True, ciclo=ciclo)
        return resultado
    for clave in orden:  # calcula en el orden topológico
        if clave in definicion:  # los lexval ya vienen llenos
            expr, mapa = definicion[clave]
            attr = clave.rsplit(".", 1)[1]
            donde[clave].attrs[attr] = evaluar_expr(expr, lambda nombre, a: mapa[nombre].attrs[a])
    resultado["orden"] = [(c, donde[c].attrs[c.rsplit(".", 1)[1]]) for c in orden]  # (atributo, valor) en orden
    resultado["valor"] = raiz.attrs[sdd["principal"]]  # el atributo principal de S
    return resultado


# ---------- Salida ----------

def texto_nodo(n, sdd):  # una línea del árbol anotado: H2 [ant=f, pts=3]
    nombres = ["lexval"] if n.produccion is None else list(sdd["atributos"].get(n.simbolo, {}))
    partes = [f"{a}={n.attrs[a]}" for a in nombres if a in n.attrs]
    return f"{n.nombre} [{', '.join(partes)}]" if partes else n.nombre


def imprimir_arbol(raiz, sdd):  # el árbol anotado, indentado
    pila = [(raiz, 0)]
    while pila:
        n, nivel = pila.pop()
        print("  " * nivel + texto_nodo(n, sdd))
        if n.produccion is not None and not n.hijos:  # producción vacía
            print("  " * (nivel + 1) + "e")
        pila.extend((h, nivel + 1) for h in reversed(n.hijos))


def arbol_a_dict(n, sdd):  # el árbol como diccionario (sirve para el servidor web)
    nombres = ["lexval"] if n.produccion is None else list(sdd["atributos"].get(n.simbolo, {}))  # en el orden declarado
    return {"name": n.nombre, "symbol": n.simbolo, "attrs": {a: n.attrs[a] for a in nombres if a in n.attrs},
            "children": [arbol_a_dict(h, sdd) for h in n.hijos]}


def imprimir_resultado(sdd, r, grafo=False):  # la salida del ítem 3 para una cadena
    if not r["pertenece"]:
        print("no")
        return
    if grafo:  # opción --graph: el grafo de dependencias
        print(f"Dependency graph ({len(r['instancias'])} nodes, {len(r['aristas'])} edges):")
        for de, a in r["aristas"]:
            print(f"  {de} -> {a}")
    if r["circular"]:
        print("circular")
        print("Cycle: " + " -> ".join(r["ciclo"]))
        return
    print("Annotated tree:")
    imprimir_arbol(r["raiz"], sdd)
    print("Evaluation order:")
    for i, (clave, valor) in enumerate(r["orden"], start=1):
        print(f"  {i}. {clave} = {valor}")
    print(f"S.{sdd['principal']} = {r['valor']}")


def main():  # python sdd.py archivo.json [--graph] < cadenas (una por línea; línea vacía al final)
    from main import leer_palabra  # misma lectura de cadenas que en el ítem 2
    rutas = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not rutas:
        print("usage: python sdd.py <sdd.json> [--graph] < strings")
        return
    try:
        sdd = cargar_archivo(rutas[0])
    except SDDError as e:
        print("Invalid SDD:\n" + str(e))
        return
    palabra = leer_palabra()
    while palabra is not None:
        imprimir_resultado(sdd, evaluar_cadena(sdd, palabra), "--graph" in sys.argv)
        print()
        palabra = leer_palabra()


if __name__ == "__main__":
    main()

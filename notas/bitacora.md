# Bitácora del proyecto

Notas internas (en español) para el informe: lo que desarrollamos y los problemas que encontramos.
**Esta carpeta `notas/` NO se entrega**: hay que sacarla antes de subir el proyecto.

---

## Lo desarrollado

### 24 oct 2026 — Ítem 1 completo
- **Estructura del proyecto**: carpeta `parsers`, repo privado en GitHub (`Camest24/formales-parsers`), `.gitignore`, README.
- **Lectura de la gramática** (`leer_gramatica` en `grammar.py`): pasa el texto del enunciado (sección 2.2.1) a un diccionario `no terminal -> lista de alternativas`, donde cada alternativa es una lista de símbolos.
- **FIRST** (`first_de_cadena` y `calcular_first`): Aho 4.4.2, reglas de FIRST. `first_de_cadena` calcula el FIRST de una cadena X1...Xn (lo va a necesitar la tabla LL(1)).
- **FOLLOW** (`calcular_follow`): Aho 4.4.2, reglas de FOLLOW.
- **Formato de `--sets`** (`formatear_conjunto` e `imprimir_sets`): no terminales en orden alfabético; dentro de las llaves, terminales en orden ASCII, luego `e` y luego `$`.
- **Pruebas** (`test_grammar.py`): 13 pruebas con los 3 ejemplos del enunciado y casos especiales.
- **Ejemplos** (`ejemplos/`): las entradas de los 3 ejemplos del enunciado, para probar con `<`.
- **Programa de consola** (`main.py`): lee la gramática desde la entrada estándar y, con la opción `--sets`, imprime los conjuntos. Probado con los 3 ejemplos: `python main.py --sets < ejemplos/ejemplo1.txt`. Queda un `TODO` donde se conectan los parsers del ítem 2.
- **README**: estructura del proyecto, cómo correr el ítem 1 y las pruebas, y explicación de FIRST/FOLLOW citando Aho 4.4.2.

**Cómo lo trabajamos:** primero calculamos FIRST y FOLLOW del Ejemplo 1 **a mano** (escribiendo palabras y mirando con qué empiezan, y buscando el vecino a la derecha de cada no terminal) y después lo pasamos a código. Los resultados a mano coinciden con los del programa.

**Commits del día:** `Initial project structure` → `Read grammar` → `Compute FIRST sets` → `Compute FOLLOW sets` (incluye `--sets`) → pruebas, ejemplos, notas y README → `main.py`.

**Estado:** ítem 1 terminado (el plan lo tenía para el 30 oct).

### 27 oct 2026 — Ítem 2: mitad LL(1)
- **Tabla LL(1)** (`construir_tabla_ll1` en `ll1.py`): Aho 4.4.3, Algoritmo 4.31. Regla 1: cada alternativa va en las casillas de su FIRST. Regla 2: si la alternativa puede ser ε, va en las casillas de FOLLOW de la cabeza.
- **Prueba de LL(1)** (`es_ll1`): la gramática es LL(1) si ninguna casilla tiene dos alternativas. Resultados: Ejemplo 2 sí; Ejemplo 1 y Ejemplo 3 no (coincide con el enunciado).
- **Parser con pila** (`parsear_ll1`): Aho 4.4.4, Algoritmo 4.34. Probado con las cadenas del Ejemplo 2 (`d` yes, `adbc` yes, `a` no) y con `S -> aBc d`, `B -> bB e` (`abc`, `abbc` yes; `ab`, `dc` no).

**Cómo lo trabajamos:** el 26 oct armamos a mano las tablas LL(1) del Ejemplo 2 y de `S -> aBc | d`, `B -> bB | e`. El 27 oct practicamos el parser como un juego de dos listas ("lo que espero leer" contra "lo que me falta"), con dos movimientos: tachar si las fichas son iguales, o buscar en la tabla si la ficha es un no terminal. Después lo pasamos a código.

**Estado:** falta conectar el parser LL(1) a `main.py` (leer las cadenas hasta la línea vacía, la cadena vacía `e`) y hacer el SLR(1).

### 27 oct 2026 (tarde) — LL(1) conectado a `main.py`
- `main.py` decide si la gramática es LL(1) y, en el caso "solo LL(1)", imprime `Grammar is LL(1).` y responde `yes`/`no` a cada cadena hasta la línea vacía (`e` = cadena vacía). Los casos con SLR(1) quedan como `TODO` (por ahora `es_slr_ok = False`).
- `test_ll1.py`: 11 pruebas de la tabla, de la decisión LL(1) y del parser (24 pruebas en total con `test_grammar.py`).
- README: cómo correr el ítem 2 y explicación del LL(1) citando Aho 4.4.3–4.4.4.

### 28 oct 2026 — Ítem 2: SLR(1), la teoría (sin código todavía)
- **Shift-reduce (Aho 4.5):** el parser arma de abajo hacia arriba. Dos movimientos: *shift* (meter la siguiente letra) y *reduce* (juntar las últimas piezas que forman el lado derecho de una producción en su cabeza). Acepta cuando solo queda S y no falta nada.
- **Cuándo es no:** el parser queda atascado (ni shift ni reduce sirven). Tres casos: se acaba la palabra sin completar S (`i+`), llega una letra que no encaja (`i+i)`), o dos letras seguidas que ninguna regla permite (`ii`).
- **Cuándo NO reducir aunque las piezas coincidan:** si la letra que viene no está en FOLLOW de la cabeza. Ej.: con `S + T` en la mesa y `*` como siguiente letra, no se reduce `S → S+T`, porque `*` no está en FOLLOW(S). Es justo lo que usa la tabla SLR (Aho 4.6.4).
- **Gramática aumentada (4.6.2):** se agrega `S' → S` como meta.
- **Ítems LR(0) (4.6.2):** una producción con un punto. Una producción con n símbolos tiene n + 1 ítems; `A → e` tiene uno solo, `A → •`, que ya es reduce.
- **CLOSURE y GOTO (4.6.2):** las calculamos a mano para `S → S+i | i` (5 estados) y para `S → A b`, `A → a A | c`.

**Cómo lo aprendimos:** juegos interactivos de shift-reduce (gramáticas `S → S+i | i` y la del Ejemplo 1) y la analogía de la **lista de mercado**: el punto es el dedo que señala lo siguiente que falta; las mayúsculas tienen su propia receta (CLOSURE = abrirla con el dedo al principio) y GOTO = conseguir lo que el dedo señalaba y moverlo. La conexión que hizo que encajara: **es la construcción NFA → DFA de la entrega 1**. Cada ítem es un estado de un NFA; el punto antes de una mayúscula da transiciones ε al inicio de sus producciones; CLOSURE = `epsilon_closure`, GOTO = `move` + `epsilon_closure`, y cada estado del autómata LR(0) es un conjunto de ítems (como `q1q2q3`).

**Estado:** falta escribir `slr.py` (closure, goto, colección de estados, tabla ACTION/GOTO, parser LR) y conectarlo a `main.py`.

### 1 nov 2026 — Ítem 2 completo: SLR(1) y `main.py` con los 4 casos
- **Autómata LR(0)** (`slr.py`: `numerar_producciones`, `closure`, `goto`, `construir_cajas`): Aho 4.6.2. Con `S -> S+i | i` da las 5 cajas que calculamos a mano; con el Ejemplo 1 da 12 cajas (los estados I0 a I11 del libro).
- **Tabla SLR(1)** (`construir_tabla_slr`, `es_slr1`): Aho 4.6.4, Algoritmo 4.46. Una flecha con terminal da shift; una flecha con no terminal da GOTO; un ítem con el punto al final da reduce en cada letra de FOLLOW(cabeza); `S' -> S •` da accept en `$`. Si una casilla recibe dos acciones distintas se registra un conflicto y la gramática no es SLR(1).
- **Parser LR** (`parsear_slr`): Aho 4.6.3, Algoritmo 4.44. Pila de estados; el reduce saca un estado por cada símbolo de la producción y apila el GOTO.
- **`main.py` completo:** decide LL(1) / SLR(1) / ambas / ninguna e imprime el mensaje exacto de cada caso, con el menú T / B / Q cuando son las dos. Los 3 ejemplos del enunciado dan la salida esperada.
- **Pruebas:** `test_slr.py` (11 pruebas) y las de LL(1) y FIRST/FOLLOW; 35 pruebas en total, todas pasan.

**Cómo lo aprendimos:** juegos interactivos para (1) pegar los letreros de las flechas, (2) pegar los reduce usando FOLLOW y (3) leer la tabla paso a paso con la pila de estados. Quedó una duda para repasar: el llenado de la tabla, sobre todo el reduce.

### Estructuras de datos usadas (lo pide el informe)
- Gramática: diccionario `{"A": [["a", "A"], ["d"]], ...}`.
- ε: lista vacía `[]` en la gramática, y el texto `"e"` dentro de los conjuntos.
- FIRST y FOLLOW: diccionario `no terminal -> set` de símbolos.
- Tabla LL(1): diccionario con llave `(no terminal, terminal)` y valor la **lista** de alternativas de esa casilla. Es una lista (y no una sola alternativa) para poder detectar conflictos. Las casillas vacías no se guardan.
- Ítem LR(0) (planeado): tupla `(número de producción, posición del punto)`, ej. `(1, 1)` = `S → S • + i`. Las producciones se numeran en una lista, con `S' → S` como la número 0.
- Estado LR(0) (planeado): `frozenset` de ítems, para poder compararlo y usarlo como llave de diccionario.
- Pila del parser LL(1): lista de Python, donde el **final** de la lista es el tope (porque `append` y `pop` trabajan al final). Empieza como `["$", "S"]`.

---

## Problemas encontrados y cómo los resolvimos

1. **Cómo representar ε.** Si la guardábamos como el símbolo `e`, se podía confundir con un terminal.
   → En la gramática, ε es una **lista vacía** `[]`: recorrerla no hace nada, que es justo lo que significa ε. Así la regla "X → ε" de FIRST sale sola, sin un caso aparte (`first_de_cadena([])` devuelve `{"e"}`).

2. **S no siempre está en la primera línea** (lo dice el enunciado, sección 2.2).
   → No asumimos el orden: el `$` se agrega directamente a `follow["S"]` y la gramática se guarda en un diccionario. Lo prueba `test_s_no_esta_primero`.

3. **Un FIRST depende de otro que todavía no se ha calculado.** Por ejemplo, en `S -> ABc`, la primera vez que se mira S, FIRST(A) todavía está vacío.
   → Se calcula por **vueltas** con un `while cambio`: se repite hasta que ningún conjunto crezca (punto fijo).

4. **Recursión por la izquierda** (`S -> S+T`, `T -> T*F`): parecía que FIRST(S) dependía de sí mismo y podía dar un ciclo infinito.
   → Esas alternativas copian FIRST(S) en FIRST(S): el conjunto no crece, así que no activan `cambio` y el `while` termina. Ojo: el enunciado prohíbe quitar la recursión de la gramática; no hizo falta.

5. **Separar la cabeza del cuerpo con `->`.** Si un terminal fuera `-` o `>`, cortar por todos los `->` podría dañar la línea.
   → `split("->", 1)` corta solo en el primero.

6. **Orden de salida de `--sets`.** Los `set` de Python no tienen orden.
   → `sorted()` (orden ASCII) para los terminales, y `e` y `$` se agregan al final a mano.

7. **Cuánto leer de la entrada.** Después de la gramática vienen la letra del parser y las cadenas; si el programa leyera toda la entrada de una vez, las mezclaría con las producciones, y si alguien escribe a mano, se quedaría esperando cadenas antes de decir qué tipo de gramática es.
   → `main.py` lee exactamente `1 + n` líneas (el número `n` y las `n` producciones) con `input()`. Las cadenas se leerán después, una por una.

8. **Una misma función para la consola y para el web server.** `input()` solo sirve en la consola.
   → `leer_gramatica` recibe una **lista de líneas** ya leídas: `main.py` las lee con `input()`, y el servidor las podrá sacar del texto que llegue por HTTP.

9. **Correr el programa con un archivo de entrada (Windows).**
   - "El sistema no puede encontrar la ruta especificada": la terminal estaba en `C:\Users\juanc` y no en la carpeta del proyecto → hacer `cd` a la carpeta `parsers` (o abrir `parsers` en VS Code con *Open Folder*).
   - El `<` funciona en CMD y Git Bash, pero no en PowerShell → en PowerShell: `Get-Content ejemplos/ejemplo1.txt | python main.py --sets`.

10. **Cómo detectar si una gramática no es LL(1).** Si cada casilla guardara una sola alternativa, la segunda sobrescribiría a la primera y el conflicto no se vería.
   → Cada casilla guarda una **lista** de alternativas; `es_ll1` revisa si alguna tiene más de una. En el Ejemplo 1, la recursión por la izquierda hace que `S -> S+T` y `S -> T` caigan en [S, i] y [S, (].

11. **Orden en que se mete una alternativa en la pila.** Con `S -> aBc`, la `a` tiene que quedar en el tope porque es lo primero que se lee.
   → Se mete con `reversed(alt)`: primero `c`, luego `B`, luego `a`. Una alternativa ε (`[]`) no mete nada, así que el no terminal simplemente desaparece.

12. **Cuándo responder no.** Hay tres casos: las fichas de adelante son terminales distintos, la casilla de la tabla está vacía, o una lista se acaba antes que la otra (ej. `ab`: se acaba la palabra pero aún se espera `c`; `dc`: ya no se espera nada pero sobra `c`).
   → Todos caen en el `else` final del parser; solo es yes cuando la pila y la entrada llegan a `$` al mismo tiempo.

13. **Recursión en CLOSURE.** En `A → a • A`, el punto señala la misma A, así que su receta se vuelve a abrir.
   → No es un problema: CLOSURE agrega cada ítem una sola vez y para cuando no hay nada nuevo (el mismo `while cambio` de FIRST/FOLLOW). En el autómata, esto se ve como una flecha `a` que vuelve al mismo estado.

14. **La parte más abstracta del proyecto: ítems, CLOSURE y GOTO.** Las explicaciones con estados y "cajas" no se entendían.
   → Lo que funcionó: (1) practicar primero shift-reduce como juego; (2) la analogía del dedo en una lista de mercado; (3) relacionarlo con el NFA → DFA de la entrega 1, que ya habíamos programado.

15. **Probar el caso "solo LL(1)".** El Ejemplo 2 del enunciado es LL(1) y también SLR(1), así que muestra el menú; hacía falta una gramática que fuera LL(1) pero no SLR(1).
   → `S -> AaAb BbBa`, `A -> e`, `B -> e`: LL(1) porque las dos alternativas de S empiezan con letras distintas, pero en SLR(1) la caja 0 tiene `A -> •` y `B -> •` y las dos reducen con `a` y `b` (conflicto reduce/reduce). Quedó en `ejemplos/solo_ll1.txt`.

16. **Cuándo reducir.** Reducir siempre que el punto llegue al final aceptaría palabras malas (como `ii`).
   → El reduce solo se pega en las letras de FOLLOW(cabeza); el resto de las casillas queda vacío y el parser responde no. Dos letreros distintos en la misma casilla se anotan en `conflictos`.

---

## Siguiente paso
- Ítem 3 (SDD): Mariana escoge la gramática y los atributos; después se escribe el evaluador (árbol, grafo de dependencias, orden topológico, detección de ciclos).
- Informe en PDF: la gramática propia con FIRST/FOLLOW, tabla LL(1) o autómata y tabla SLR (usar `imprimir_cajas` e `imprimir_tabla_slr`), y una cadena parseada paso a paso.
- Web server (bonus) y ensayo de la sustentación.

## Reparto del trabajo (propuesto el 27 oct)
- **Camilo:** ítem 2 (parsers LL(1) y SLR(1)).
- **Mariana:** ítem 3 en papel (escoger gramática y atributos, tabla de reglas semánticas, ejemplo a mano con árbol anotado y grafo de dependencias). Leer Aho 5.1 y 5.2.
- **Los dos:** evaluador del SDD, web server, informe y ensayo de la sustentación. Cada uno le explica al otro lo que hizo.

---

## Preguntas pendientes para el profe
- [ ] En `--sets`, ¿van primero todas las líneas `First` y luego todas las `Follow`, o intercaladas por no terminal? (Por ahora: primero todas las `First`.)
- [ ] El web server, ¿va además del programa de consola o lo puede reemplazar? ¿Basta con un API o espera una interfaz web?
- [ ] ¿La gramática que escojamos para el SDD cumple la regla G3?

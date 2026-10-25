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

### Estructuras de datos usadas (lo pide el informe)
- Gramática: diccionario `{"A": [["a", "A"], ["d"]], ...}`.
- ε: lista vacía `[]` en la gramática, y el texto `"e"` dentro de los conjuntos.
- FIRST y FOLLOW: diccionario `no terminal -> set` de símbolos.

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

---

## Preguntas pendientes para el profe
- [ ] En `--sets`, ¿van primero todas las líneas `First` y luego todas las `Follow`, o intercaladas por no terminal? (Por ahora: primero todas las `First`.)
- [ ] El web server, ¿va además del programa de consola o lo puede reemplazar? ¿Basta con un API o espera una interfaz web?
- [ ] ¿La gramática que escojamos para el SDD cumple la regla G3?

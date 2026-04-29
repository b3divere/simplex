import numpy as np
import json
import os

ruta = os.path.join(os.path.dirname(__file__), "problema.json")

with open(ruta, "r") as f:
    datos = json.load(f)

maximizar     = np.array(datos["maximizar"], dtype=float)
restricciones = np.array(datos["restricciones"], dtype=float)
derecho       = np.array(datos["derecho"], dtype=float)
tipos         = datos["tipos"]

for i in range(len(derecho)):
    if derecho[i] < 0:
        derecho[i]       = -derecho[i]
        restricciones[i] = -restricciones[i]
        if tipos[i] == "<=":
            tipos[i] = ">="
        else:
            tipos[i] = "<="

n_vars         = len(maximizar)
n_holguras     = restricciones.shape[0]
n_artificiales = tipos.count(">=")
n_reales       = n_vars + n_holguras

nombre = [f"x{i+1}" for i in range(n_vars)] + \
         [f"h{i+1}" for i in range(n_holguras)] + \
         [f"a{i+1}" for i in range(n_artificiales)]

base = []
contador_art = 1
for i, t in enumerate(tipos):
    if t == "<=":
        base.append(f"h{i+1}")
    elif t in (">=", "="):
        base.append(f"a{contador_art}")
        contador_art += 1

# ─────────────────────────────────────────────
# FASE 1: construir tabla con objetivo W = suma de artificiales
# ─────────────────────────────────────────────
def construir_tabla_fase1(restricciones, derecho, tipos):
    n_vb           = restricciones.shape[0]
    c_holguras     = np.eye(n_vb)
    res            = derecho.reshape(-1, 1)
    n_art          = tipos.count(">=") + tipos.count("=")
    c_artificiales = np.zeros((n_vb, n_art))

    contador_art = 0
    for i in range(n_vb):
        if tipos[i] == ">=":
            c_holguras[i, i]            = -1
            c_artificiales[i, contador_art] = 1
            contador_art += 1
        elif tipos[i] == "=":
            c_holguras[i, i]            = 0
            c_artificiales[i, contador_art] = 1
            contador_art += 1

    cuerpo = np.hstack([restricciones, c_holguras, c_artificiales, res])

    fila_w = np.concatenate([np.zeros(n_vb + len(maximizar)), [1]*n_art, [0]])

    tabla = np.vstack([cuerpo, fila_w])

    for i in range(n_vb):
        if tipos[i] == ">=":
            tabla[-1] = tabla[-1] - tabla[i]

    return tabla

# ─────────────────────────────────────────────
# FASE 2: reemplazar fila W por la función objetivo real
# y eliminar columnas artificiales
# ─────────────────────────────────────────────
def construir_tabla_fase2(tabla, maximizar, base, nombre, n_vars, n_holguras):
    n_art = tabla.shape[1] - 1 - n_vars - n_holguras

    cols_reales = list(range(n_vars + n_holguras)) + [tabla.shape[1] - 1]
    tabla2      = tabla[:, cols_reales]

    fila_z = np.concatenate([-maximizar, np.zeros(n_holguras), [0]])
    tabla2[-1] = fila_z

    nombre2 = nombre[:n_vars + n_holguras]
    for i, var in enumerate(base):
        if var in nombre2:
            col = nombre2.index(var)
            if abs(tabla2[-1, col]) > 1e-10:
                tabla2[-1] = tabla2[-1] - tabla2[-1, col] * tabla2[i]

    return tabla2

def c_pivote(tabla, n_cols):
    fila_z = tabla[-1, :n_cols]
    if np.all(fila_z >= -1e-6):
        return None
    return np.argmin(fila_z)

def f_fila(tabla, columna):
    cocientes = []
    for i in range(len(tabla)-1):
        if tabla[i, columna] > 1e-10:
            cocientes.append(tabla[i, -1] / tabla[i, columna])
        else:
            cocientes.append(np.inf)
    return np.argmin(cocientes)

def pivotear(tabla, fila, columna, nombres, base):
    base[fila] = nombres[columna]
    tabla[fila] = tabla[fila] / tabla[fila, columna]
    for i in range(len(tabla)):
        if i != fila:
            factor       = tabla[i, columna]
            tabla[i]     = tabla[i] - factor * tabla[fila]

def precio_sombra(tabla, n_vars, n_holguras):
    return tabla[-1, n_vars: n_vars + n_holguras]

def imprimir(tabla, base, nombre):
    col_w      = max(10, max(len(n) for n in nombre) + 4)
    encabezado = f"{'Base':<8}" + "".join(f"{n:>{col_w}}" for n in nombre) + f"{'RES':>{col_w}}"
    separador  = "-" * len(encabezado)
    print("\nTABLA SIMPLEX")
    print(encabezado)
    print(separador)
    for i, fila in enumerate(tabla[:-1]):
        vals = "".join(f"{v:>{col_w}.4f}" for v in fila)
        print(f"{base[i]:<8}{vals}")
    vals = "".join(f"{v:>{col_w}.4f}" for v in tabla[-1])
    print(f"{'W' if 'a' in str(nombre) else 'Z':<8}{vals}")
    print(separador)

def imprimir_solucion(tabla, base, n_vars):
    print("\n--- SOLUCIÓN ÓPTIMA ---")
    print(f"Z = {tabla[-1, -1]:.6f}")
    print("\nValores de las variables:")
    for i in range(n_vars):
        var = f"x{i+1}"
        if var in base:
            fila = base.index(var)
            print(f"  {var} = {tabla[fila, -1]:.6f}")
        else:
            print(f"  {var} = 0.000000")

def loop_simplex(tabla, base, nombre, n_cols, etiqueta_z):
    iteracion = 1
    while True:
        columna = c_pivote(tabla, n_cols)
        if columna is None:
            break

        cocientes = []
        for i in range(len(tabla)-1):
            if tabla[i, columna] > 1e-10:
                cocientes.append(tabla[i, -1] / tabla[i, columna])
            else:
                cocientes.append(np.inf)
        if all(c == np.inf for c in cocientes):
            print("Problema no acotado")
            exit()

        fila = f_fila(tabla, columna)
        pivotear(tabla, fila, columna, nombre, base)

        print(f"{etiqueta_z} - Iteración {iteracion}:")
        imprimir(tabla, base, nombre)
        iteracion += 1


if n_artificiales == 0:
    print("No hay restricciones >=, se resuelve directamente.\n")

    fila_z = np.concatenate([-maximizar, np.zeros(n_holguras), [0]])
    n_vb   = restricciones.shape[0]
    res    = derecho.reshape(-1, 1)
    cuerpo = np.hstack([restricciones, np.eye(n_vb), res])
    tabla  = np.vstack([cuerpo, fila_z])
    nombre_fase = nombre[:n_vars + n_holguras]

    print("Estado inicial")
    imprimir(tabla, base, nombre_fase)
    loop_simplex(tabla, base, nombre_fase, n_reales, "Fase única")

    imprimir_solucion(tabla, base, n_vars)
    sombras = precio_sombra(tabla, n_vars, n_holguras)
    print("\nPrecios Sombra:")
    for i, s in enumerate(sombras):
        print(f"  Restricción {i+1}: {s:.4f}")

else:
    print("=" * 50)
    print("FASE 1: encontrar solución básica factible")
    print("=" * 50)

    tabla = construir_tabla_fase1(restricciones, derecho, tipos)
    print("Estado inicial Fase 1")
    imprimir(tabla, base, nombre)
    loop_simplex(tabla, base, nombre, n_reales, "Fase 1")

    w_final = tabla[-1, -1]
    if abs(w_final) > 1e-6:
        print("Problema infactible: W no llegó a 0")
        exit()

    for i, b in enumerate(base):
        if "a" in b and tabla[i, -1] > 1e-6:
            print("Problema infactible: artificial quedó en la base")
            exit()

    print("\nFase 1 completada: solución básica factible encontrada (W = 0)")

    print("\n" + "=" * 50)
    print("FASE 2: optimizar función objetivo real")
    print("=" * 50)

    nombre2 = nombre[:n_vars + n_holguras]
    tabla2  = construir_tabla_fase2(tabla, maximizar, base, nombre, n_vars, n_holguras)

    print("Estado inicial Fase 2")
    imprimir(tabla2, base, nombre2)
    loop_simplex(tabla2, base, nombre2, n_reales, "Fase 2")

    imprimir_solucion(tabla2, base, n_vars)
    sombras = precio_sombra(tabla2, n_vars, n_holguras)
    print("\nPrecios Sombra:")
    for i, s in enumerate(sombras):
        print(f"  Restricción {i+1}: {s:.4f}")
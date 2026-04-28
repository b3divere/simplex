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
M             = datos["M"]

def construir_tabla(maximizar, restricciones, derecho, tipos, M):
    n_vb = restricciones.shape[0]
    c_holguras = np.eye(n_vb)
    res = derecho.reshape(-1, 1)
    n_artificiales = tipos.count(">=")
    c_artificiales = np.zeros((n_vb, n_artificiales))

    contador_art = 0
    for i in range(n_vb):
        if tipos[i] == ">=":
            c_holguras[i, i] = -1
            c_artificiales[i, contador_art] = 1
            contador_art += 1

    cuerpo = np.hstack([restricciones, c_holguras, c_artificiales, res])
    fila_z = np.concatenate([-maximizar, np.zeros(n_vb), [M]*n_artificiales, [0]])
    tabla = np.vstack([cuerpo, fila_z])

    for i in range(n_vb):
        if tipos[i] == ">=":
            tabla[-1] = tabla[-1] - M * tabla[i]

    return tabla

n_vars         = len(maximizar)
n_holguras     = restricciones.shape[0]
n_artificiales = tipos.count(">=")

nombre = [f"x{i+1}" for i in range(n_vars)] + \
         [f"h{i+1}" for i in range(n_holguras)] + \
         [f"a{i+1}" for i in range(n_artificiales)]

base = []
contador_art = 1
for i, t in enumerate(tipos):
    if t == "<=":
        base.append(f"h{i+1}")
    else:
        base.append(f"a{contador_art}")
        contador_art += 1

def c_pivote(tabla):
    fila_z = tabla[-1, :-1]
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
            factor = tabla[i, columna]
            tabla[i] = tabla[i] - factor * tabla[fila]

def precio_sombra(tabla, n_vars, n_holguras):
    return tabla[-1, n_vars: n_vars + n_holguras]

def imprimir(tabla, base, nombre):
    col_w = max(10, max(len(n) for n in nombre) + 4)
    encabezado = f"{'Base':<8}" + "".join(f"{n:>{col_w}}" for n in nombre) + f"{'RES':>{col_w}}"
    separador  = "-" * len(encabezado)
    print("\nTABLA SIMPLEX")
    print(encabezado)
    print(separador)
    for i, fila in enumerate(tabla[:-1]):
        vals = "".join(f"{v:>{col_w}.4f}" for v in fila)
        print(f"{base[i]:<8}{vals}")
    vals = "".join(f"{v:>{col_w}.4f}" for v in tabla[-1])
    print(f"{'Z':<8}{vals}")
    print(separador)

def imprimir_solucion(tabla, base, nombre, n_vars):
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

tabla = construir_tabla(maximizar, restricciones, derecho, tipos, M)
print("Estado inicial")
imprimir(tabla, base, nombre)

iteracion = 1
while True:
    if np.all(tabla[-1, :-1] >= -1e-6):
        break

    columna = c_pivote(tabla)

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

    print(f"Iteración {iteracion}:")
    imprimir(tabla, base, nombre)
    iteracion += 1

infactible = any("a" in b and tabla[i, -1] > 1e-6 for i, b in enumerate(base))

if infactible:
    print("Problema infactible: no existe solución factible")
else:
    imprimir_solucion(tabla, base, nombre, n_vars)
    sombras = precio_sombra(tabla, n_vars, n_holguras)
    print("\nPrecios Sombra:")
    for i, s in enumerate(sombras):
        print(f"  Restricción {i+1}: {s:.4f}")
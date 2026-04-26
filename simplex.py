import numpy as np
import json

with open("problema.json", "r") as f:
    datos = json.load(f)

maximizar     = np.array(datos["maximizar"], dtype=float)
restricciones = np.array(datos["restricciones"], dtype=float)
derecho       = np.array(datos["derecho"], dtype=float)
tipos         = datos["tipos"]

def construir_tabla(maximizar, restricciones, derecho, tipos):
    n_vb = restricciones.shape[0]
    c_holguras = np.eye(n_vb)
    res = derecho.reshape(-1, 1)
    n_artificiales = tipos.count(">=")
    c_artificiales = np.zeros((n_vb, n_artificiales))

    j = 0
    for i in range(n_vb):
        if tipos[i] == ">=":
            c_holguras[i, i] = -1
            c_artificiales[i, j] = 1
            j += 1

    cuerpo = np.hstack([restricciones, c_holguras, c_artificiales, res])
    M = 1000
    fila_z = np.concatenate([-maximizar, np.zeros(n_vb), [M]*n_artificiales, [0]])
    tabla = np.vstack([cuerpo, fila_z])

    for i in range(n_vb):
        if tipos[i] == ">=":
            tabla[-1] = tabla[-1] - M * tabla[i]

    return tabla, n_artificiales

n_vars = len(maximizar)
n_holguras = restricciones.shape[0]
n_artificiales = tipos.count(">=")

nombre = [f"x{i+1}" for i in range(n_vars)] + \
         [f"h{i+1}" for i in range(n_holguras)] + \
         [f"a{i+1}" for i in range(n_artificiales)]

base = []
j = 1
for i, t in enumerate(tipos):
    if t == "<=":
        base.append(f"h{i+1}")
    else:
        base.append(f"a{j}")
        j += 1

def c_pivote(tabla):
    fila_z = tabla[-1, :-1]
    columna = np.argmin(fila_z)
    return columna

def f_fila(tabla, columna):
    cocientes = []
    for i in range(len(tabla)-1):
        if tabla[i, columna] > 1e-10:
            cociente = tabla[i, -1] / tabla[i, columna]
        else:
            cociente = np.inf
        cocientes.append(cociente)
    return np.argmin(cocientes)

def pivotear(tabla, fila, columna, nombres, base):
    base[fila] = nombres[columna]
    tabla[fila] = tabla[fila] / tabla[fila, columna]
    for i in range(len(tabla)):
        if i != fila:
            factor = tabla[i, columna]
            tabla[i] = tabla[i] - factor * tabla[fila]

def precio_sombra(tabla, n_vars):
    fila_z = tabla[-1]
    sombras = fila_z[n_vars:-1]
    return sombras

def imprimir(tabla, base, nombre):
    print("\nTABLA SIMPLEX")
    header = "Base\t" + "\t".join(nombre) + "\tRES"
    print(header)
    print("-" * 70)
    for i, fila in enumerate(tabla[:-1]):
        vals = "\t".join([f"{v:.4f}" for v in fila])
        print(f"{base[i]}\t{vals}")
    vals = "\t".join([f"{v:.4f}" for v in tabla[-1]])
    print(f"Z\t{vals}")
    print("-" * 70)

tabla, n_art = construir_tabla(maximizar, restricciones, derecho, tipos)
print("Estado inicial")
imprimir(tabla, base, nombre)

iteracion = 1

while True:
    if np.all(tabla[-1, :-1] >= -1e-6):
        break

    columna = c_pivote(tabla)
    fila = f_fila(tabla, columna)

    cocientes = []
    for i in range(len(tabla)-1):
        if tabla[i, columna] > 1e-10:
            cocientes.append(tabla[i, -1] / tabla[i, columna])
        else:
            cocientes.append(np.inf)
    if all(c == np.inf for c in cocientes):
        print("Problema no acotado")
        exit()

    pivotear(tabla, fila, columna, nombre, base)

    print(f"Iteración {iteracion}:")
    imprimir(tabla, base, nombre)
    iteracion += 1

infactible = False
for i, b in enumerate(base):
    if "a" in b and tabla[i, -1] > 1e-6:
        infactible = True
        break

if infactible:
    print("Problema infactible: no existe solución factible")
else:
    print("Solución óptima encontrada")
    print(f"Z = {tabla[-1, -1]:.6f}")
    sombras = precio_sombra(tabla, n_vars)
    print("\nPrecios Sombra:")
    for i, s in enumerate(sombras):
        print(f"  Restricción {i+1}: {s:.4f}")
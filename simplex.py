import numpy as np
import matplotlib.pyplot as plt

maximizar = np.array([2,1])

restricciones = np.array([[2,1],
                          [1,3],
                          [1,0],
                          [0,1]])

derecho = np.array([100,
                    80,
                    45,
                    100])


restricciones_grafico = [
    "Destilación: 2x₁ + x₂ ≤ 100",
    "Preparación: x₁ + 3x₂ ≤ 80",
    "Demanda P1:  x₁ ≤ 45",
    "Demanda P2:  x₂ ≤ 100",
]

def contruir_tabla(maximizar, restricciones, derecho):
    
    n_vb = restricciones.shape[0]
    c_holguras = np.eye(n_vb)
    res = derecho.reshape(-1,1)
    
    cuerpo = np.hstack([restricciones, c_holguras, res])
    
    fila_z = np.concatenate([-maximizar, np.zeros(n_vb), [0]])
    
    tabla = np.vstack([cuerpo, fila_z])
    
    return tabla

n_vars = len(maximizar)
n_holguras = restricciones.shape[0]

nombre = [f"x{i+1}" for i in range(n_vars)] + [f"h{i+1}" for i in range(n_holguras)]

base = [f"h{i+1}" for i in range(n_holguras)]

def c_pivote(tabla):
    fila_z = tabla[-1]
    columna = np.argmin(fila_z)
    
    return columna

def f_fila(tabla, columna):
    
    cocientes = []
    
    for i in range(len(tabla)-1):
        if tabla[i, columna] > 0:
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
            factor = tabla[i,columna]
            tabla[i] = tabla[i]-factor*tabla[fila]
         
def precio_sombra(tabla, n_vars):
    fila_z = tabla[-1]
    sombras = fila_z[n_vars:-1]
    return sombras

def imprimir(tabla, base):
    print("\nTABLA SIMPLEX")
    header = "Base\tx1\tx2\th1\th2\th3\th4\tRES"
    print(header)
    print("-" * 70)
    for i, fila in enumerate(tabla[:-1]):
        vals = "\t".join([f"{v:.2f}" for v in fila])
        print(f"{base[i]}\t{vals}")
        
    vals = "\t".join([f"{v:.2f}" for v in tabla[-1]])
    print(f"Z\t{vals}")
    print("-" * 70)

tabla = contruir_tabla(maximizar, restricciones, derecho)
print("Estado incial")
imprimir(tabla, base)

iteracion = 1

while True:
    if np.all(tabla[-1] >= 0):
        break
    
    columna = c_pivote(tabla)
    fila = f_fila(tabla, columna)
    pivotear(tabla, fila, columna, base, nombre)
    
    print(f"Iteracccion {iteracion}: ")
    imprimir(tabla, base)
    iteracion += 1

print("Solucion optima encontrada")
print(f"Z = {tabla[-1, -1]}")

sombras = precio_sombra(tabla, len(maximizar))
print("\nPrecios Sombra:")
for i, s in enumerate(sombras):
    print(f"Restricción {i+1}: {s:.2f}")

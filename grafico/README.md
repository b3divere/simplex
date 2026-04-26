## 🚀 Uso

```bash
# Usando params.json por defecto (misma carpeta)
python main.py

# Especificando un archivo diferente
python main.py params.json
```

---

## 📝 Cómo ingresar los datos (`params.json`)

El archivo tiene **3 secciones principales**: `c`, `restricciones` y `logica`.

---

### 1️⃣ Función objetivo — `"c"`

Lista con los coeficientes de `x1` y `x2`.

```json
"c": [3, 4]
```

Representa: **Z = 3x₁ + 4x₂**

---

### 2️⃣ Restricciones — `"restricciones"`

Cada restricción es una lista con **3 o 4 valores**:

```
[a1, a2, b]          ← signo deducido automáticamente
[a1, a2, b, "signo"] ← signo forzado manualmente
```

| Elemento  | Descripción                       |
| --------- | --------------------------------- |
| `a1`      | Coeficiente de x₁                 |
| `a2`      | Coeficiente de x₂                 |
| `b`       | Lado derecho                      |
| `"signo"` | `"<="`, `">="` o `"="` (opcional) |

#### ✅ Signo automático según modo

Si **no** se especifica el signo, el script lo deduce solo:

| `modo`  | Signo por defecto |
| ------- | ----------------- |
| `"max"` | `<=`              |
| `"min"` | `>=`              |

#### Ejemplos

```json
"restricciones": [
  [2, 1, 100],           // 2x₁ + x₂ <= 100  (deducido por modo max)
  [1, 3,  80],           // x₁ + 3x₂ <= 80   (deducido por modo max)
  [3, -1, 16, ">="],     // 3x₁ - x₂ >= 16   (forzado manualmente)
  [1,  1, 50, "="]       // x₁ + x₂ = 50     (igualdad, se expande en <= y >=)
]
```

> **Nota:** `x1 >= 0` y `x2 >= 0` están **siempre implícitos**, no hace falta escribirlos.

---

### 3️⃣ Lógica — `"logica"`

Controla el comportamiento del motor de resolución.

```json
"logica": {
  "modo":                "max",
  "tolerancia":          1e-6,
  "tolerancia_activa":   1e-3,
  "decimales_dedup":     6,
  "decimales_etiqueta":  2,
  "decimales_comparacion": 6,
  "margen":              5
}
```

| Parámetro               | Descripción                                        | Valor típico |
| ----------------------- | -------------------------------------------------- | ------------ |
| `modo`                  | `"max"` o `"min"`                                  | `"max"`      |
| `tolerancia`            | Margen numérico para considerar factible           | `1e-6`       |
| `tolerancia_activa`     | Margen para detectar restricción activa            | `1e-3`       |
| `decimales_dedup`       | Decimales para eliminar vértices duplicados        | `6`          |
| `decimales_etiqueta`    | Decimales mostrados en el gráfico                  | `2`          |
| `decimales_comparacion` | Decimales para comparar el óptimo                  | `6`          |
| `margen`                | Espacio extra en los ejes más allá de los vértices | `5`          |

---

### 4️⃣ Gráfico — `"grafico"`

Controla la apariencia visual. Todos los valores son opcionales si se usan los defaults.

```json
"grafico": {
  "figsize":               [13, 7],
  "width_ratios":          [3, 1],
  "x_vals_n":              400,
  "region_alpha":          0.4,
  "region_color":          "gray",
  "region_label":          "Region factible",
  "vertices_color":        "blue",
  "vertices_size":         60,
  "vertices_fontsize":     8,
  "vertices_text_offset":  [0.5, 0.5],
  "vertices_mostrar_z":    true,
  "optimo_color":          "red",
  "optimo_size":           140,
  "optimo_fontsize":       9,
  "optimo_text_offset":    [1, 1],
  "nivel_color":           "r--",
  "nivel_linewidth":       1.5,
  "ejes_color":            "black",
  "xlim_margen":           2,
  "ylim_margen":           2,
  "grid":                  true,
  "titulo":                "Region factible y solucion optima",
  "xlabel":                "x1",
  "ylabel":                "x2",
  "resumen_mostrar":       true,
  "resumen_posicion":      [0.5, 0.42],
  "resumen_fontsize":      8.5,
  "resumen_alpha":         0.9,
  "resumen_color_fondo":   "lightyellow",
  "resumen_color_borde":   "gray",
  "leyenda_markersize":    10,
  "leyenda_fontsize":      9,
  "leyenda_titulo":        "Referencias",
  "leyenda_titulo_fontsize": 10,
  "leyenda_borderpad":     1,
  "leyenda_labelspacing":  0.8,
  "autoajuste_margen_pct":    0.2,
  "autoajuste_offset_pct":    0.015,
  "autoajuste_offset_escala": 50,
  "autoajuste_clip_factor":   1.1
}
```

| Parámetro                         | Descripción                                                            |
| --------------------------------- | ---------------------------------------------------------------------- |
| `figsize`                         | Tamaño de la ventana `[ancho, alto]` en pulgadas                       |
| `region_color` / `region_alpha`   | Color y transparencia de la región factible                            |
| `vertices_color` / `optimo_color` | Color de puntos vértice y óptimo                                       |
| `nivel_color`                     | Color/estilo de la línea de nivel óptimo (ej. `"r--"` = rojo punteado) |
| `vertices_mostrar_z`              | Muestra el valor Z en cada vértice                                     |
| `resumen_mostrar`                 | Muestra el cuadro resumen con la solución                              |
| `autoajuste_*`                    | Parámetros de escala automática de los ejes                            |

---

## 🧪 Ejemplos completos

### Maximización con restricciones mixtas

**Problema:**

```
Max Z = 3x₁ + 4x₂
-x₁ + 2x₂ ≤  8
3x₁ -  x₂ ≥ 16
 x₁ +  x₂ ≤ 20
```

```json
{
  "c": [3, 4],
  "restricciones": [
    [-1, 2, 8],
    [3, -1, 16, ">="],
    [1, 1, 20]
  ],
  "logica": {
    "modo": "max",
    "tolerancia": 1e-6,
    "tolerancia_activa": 1e-3,
    "decimales_dedup": 6,
    "decimales_etiqueta": 2,
    "decimales_comparacion": 6,
    "margen": 5
  }
}
```

**Salida esperada:**

```
Óptimo: (10.67, 9.33)
Valor óptimo: Z = 69.33
```

---

### Minimización (signo deducido automáticamente)

**Problema:**

```
Min Z = 0.12x₁ + 0.15x₂
60x₁ + 60x₂ ≥ 300
12x₁ +  6x₂ ≥  36
10x₁ + 30x₂ ≥  90
```

```json
{
  "c": [0.12, 0.15],
  "restricciones": [
    [60, 60, 300],
    [12, 6, 36],
    [10, 30, 90]
  ],
  "logica": {
    "modo": "min",
    "tolerancia": 1e-6,
    "tolerancia_activa": 1e-3,
    "decimales_dedup": 6,
    "decimales_etiqueta": 2,
    "decimales_comparacion": 6,
    "margen": 5
  }
}
```

> Como el modo es `"min"`, todas las restricciones sin signo asumen `>=` automáticamente.

**Salida esperada:**

```
Óptimo: (3.00, 2.00)
Valor óptimo: Z = 0.66
```

---

## 🔍 Cómo funciona internamente

```
params.json
    │
    ▼
logica.py
    ├── normalizar_restricciones()   → asigna signo según modo
    ├── interseccion()               → calcula cruces entre pares de restricciones
    ├── es_factible()                → filtra puntos que cumplen TODAS las restricciones
    ├── convex_hull()                → ordena vértices para dibujar la región
    └── resolver_PL()                → evalúa Z en cada vértice y elige el óptimo
    │
    ▼
main.py
    ├── Traza las líneas de cada restricción
    ├── Rellena la región factible
    ├── Marca y etiqueta cada vértice con su Z
    ├── Resalta el punto óptimo
    └── Dibuja la línea de nivel Z*
```

---

## ⚠️ Errores comunes

| Error                                  | Causa                                          | Solución                                       |
| -------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| `No se encontraron vértices factibles` | Restricciones incompatibles o modo incorrecto  | Verifica los signos y el modo                  |
| `LinAlgError`                          | Dos restricciones paralelas (sin intersección) | Es normal, el script lo maneja automáticamente |
| Gráfico con región vacía               | Problema infactible                            | Revisa que las restricciones tengan solución   |
| Etiquetas superpuestas                 | Vértices muy cercanos                          | Ajusta `vertices_text_offset` en `grafico`     |

---

## 📌 Referencia rápida de signos

| Situación                    | JSON                |
| ---------------------------- | ------------------- |
| `modo max`, restricción `<=` | `[a1, a2, b]`       |
| `modo min`, restricción `>=` | `[a1, a2, b]`       |
| Cualquier modo, forzar `>=`  | `[a1, a2, b, ">="]` |
| Cualquier modo, forzar `<=`  | `[a1, a2, b, "<="]` |
| Igualdad exacta              | `[a1, a2, b, "="]`  |

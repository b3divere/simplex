import numpy as np

def interseccion(r1, r2):
    A = np.array([[r1[0], r1[1]], [r2[0], r2[1]]])
    B = np.array([r1[2], r2[2]])
    try:
        return np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return None

def signo_por_defecto(modo):
    return ">=" if modo == "min" else "<="

def normalizar_restricciones(restricciones, modo):
    default = signo_por_defecto(modo)
    normalizadas = []
    for r in restricciones:
        a1, a2, b = r[0], r[1], r[2]
        signo = r[3] if len(r) > 3 else default
        # "=" se expande en dos restricciones: <= y >=
        if signo == "=":
            normalizadas.append((a1, a2, b, "<="))
            normalizadas.append((a1, a2, b, ">="))
        else:
            normalizadas.append((a1, a2, b, signo))
    return normalizadas

def es_factible(p, restricciones, tolerancia):
    x1, x2 = p
    if x1 < -tolerancia or x2 < -tolerancia:
        return False
    for (a1, a2, b, signo) in restricciones:
        val = a1 * x1 + a2 * x2
        if signo == ">=" and val < b - tolerancia:
            return False
        if signo == "<=" and val > b + tolerancia:
            return False
    return True

def restricciones_activas(p, restricciones, tolerancia_activa):
    x1, x2 = p
    activas = []
    vistos = set()
    for i, (a1, a2, b, _) in enumerate(restricciones):
        if abs(a1 * x1 + a2 * x2 - b) <= tolerancia_activa:
            # Evitar duplicados por restricciones "=" expandidas
            clave = (a1, a2, b)
            if clave not in vistos:
                activas.append(i + 1)
                vistos.add(clave)
    return activas

def convex_hull(puntos):
    puntos = list(set(puntos))
    if len(puntos) <= 1:
        return puntos
    cx, cy = np.mean(puntos, axis=0)
    return sorted(puntos, key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))

def resolver_PL(c, restricciones_raw, l):
    tolerancia        = l["tolerancia"]
    tolerancia_activa = l["tolerancia_activa"]
    margen            = l["margen"]
    decimales_dedup   = l["decimales_dedup"]
    modo              = l.get("modo", "max")

    # ── Normalizar restricciones automáticamente según modo ──
    restricciones = normalizar_restricciones(restricciones_raw, modo)

    # ── Generar vértices candidatos ──
    vertices = []
    n = len(restricciones)

    for i in range(n):
        for j in range(i + 1, n):
            p = interseccion(restricciones[i], restricciones[j])
            if p is not None:
                vertices.append(tuple(p))

    for (a1, a2, b, _) in restricciones:
        if a2 != 0:
            vertices.append((0, b / a2))
        if a1 != 0:
            vertices.append((b / a1, 0))

    vertices.append((0, 0))

    # ── Filtrar factibles ──
    vertices = [v for v in vertices if es_factible(v, restricciones, tolerancia)]

    vertices_unicos = list({
        (round(v[0], decimales_dedup), round(v[1], decimales_dedup))
        for v in vertices
    })

    if not vertices_unicos:
        raise ValueError("No se encontraron vértices factibles. "
                         "Verifica las restricciones o el modo.")

    vertices_ordenados = convex_hull(vertices_unicos)

    # ── Óptimo según modo ──
    if modo == "min":
        optimo = min(vertices_unicos, key=lambda p: np.dot(c, p))
    else:
        optimo = max(vertices_unicos, key=lambda p: np.dot(c, p))

    z_vertices       = {v: round(float(np.dot(c, v)), decimales_dedup) for v in vertices_unicos}
    activas_vertices = {v: restricciones_activas(v, restricciones, tolerancia_activa)
                        for v in vertices_unicos}

    xs, ys = zip(*vertices_unicos)

    return {
        "vertices":           vertices_unicos,
        "vertices_ordenados": vertices_ordenados,
        "z_vertices":         z_vertices,
        "activas_vertices":   activas_vertices,
        "optimo":             optimo,
        "valor_optimo":       float(np.dot(c, optimo)),
        "x_max":              max(xs) + margen,
        "y_max":              max(ys) + margen
    }
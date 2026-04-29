import numpy as np


def interseccion(restriccion1, restriccion2):
    matriz_coeficientes = np.array([
        [restriccion1[0], restriccion1[1]],
        [restriccion2[0], restriccion2[1]]
    ])

    vector_resultados = np.array([
        restriccion1[2],
        restriccion2[2]
    ])

    try:
        return np.linalg.solve(matriz_coeficientes, vector_resultados)
    except np.linalg.LinAlgError:
        return None


def signo_por_defecto(tipo_optimizacion):
    return ">=" if tipo_optimizacion == "min" else "<="


def normalizar_restricciones(restricciones_originales, tipo_optimizacion):
    signo_default = signo_por_defecto(tipo_optimizacion)
    restricciones_normalizadas = []

    for restriccion in restricciones_originales:
        coef_x1 = restriccion[0]
        coef_x2 = restriccion[1]
        termino_independiente = restriccion[2]

        signo = restriccion[3] if len(restriccion) > 3 else signo_default

        if signo == "=":
            restricciones_normalizadas.append(
                (coef_x1, coef_x2, termino_independiente, "<=")
            )
            restricciones_normalizadas.append(
                (coef_x1, coef_x2, termino_independiente, ">=")
            )
        else:
            restricciones_normalizadas.append(
                (coef_x1, coef_x2, termino_independiente, signo)
            )

    return restricciones_normalizadas


def es_factible(punto, restricciones, tolerancia):
    x1, x2 = punto

    if x1 < -tolerancia or x2 < -tolerancia:
        return False

    for coef_x1, coef_x2, termino_independiente, signo in restricciones:
        valor_restriccion = coef_x1 * x1 + coef_x2 * x2

        if signo == ">=" and valor_restriccion < termino_independiente - tolerancia:
            return False

        if signo == "<=" and valor_restriccion > termino_independiente + tolerancia:
            return False

    return True


def restricciones_activas(punto, restricciones, tolerancia_activa):
    x1, x2 = punto
    restricciones_cumplidas = []
    restricciones_vistas = set()

    for indice, (coef_x1, coef_x2, termino_independiente, _) in enumerate(restricciones):
        diferencia = abs(coef_x1 * x1 + coef_x2 * x2 - termino_independiente)

        if diferencia <= tolerancia_activa:
            clave_restriccion = (coef_x1, coef_x2, termino_independiente)

            if clave_restriccion not in restricciones_vistas:
                restricciones_cumplidas.append(indice + 1)
                restricciones_vistas.add(clave_restriccion)

    return restricciones_cumplidas


def convex_hull(lista_puntos):
    lista_puntos = list(set(lista_puntos))

    if len(lista_puntos) <= 1:
        return lista_puntos

    centro_x, centro_y = np.mean(lista_puntos, axis=0)

    return sorted(
        lista_puntos,
        key=lambda punto: np.arctan2(
            punto[1] - centro_y,
            punto[0] - centro_x
        )
    )


def resolver_PL(coeficientes_objetivo, restricciones_originales, configuracion):
    tolerancia = configuracion["tolerancia"]
    tolerancia_activa = configuracion["tolerancia_activa"]
    margen = configuracion["margen"]
    decimales = configuracion["decimales_dedup"]

    tipo_optimizacion = configuracion.get("modo", "max")

    restricciones = normalizar_restricciones(
        restricciones_originales,
        tipo_optimizacion
    )

    vertices = []
    total_restricciones = len(restricciones)

    for i in range(total_restricciones):
        for j in range(i + 1, total_restricciones):
            punto_interseccion = interseccion(
                restricciones[i],
                restricciones[j]
            )

            if punto_interseccion is not None:
                vertices.append(tuple(punto_interseccion))

    for coef_x1, coef_x2, termino_independiente, _ in restricciones:
        if coef_x2 != 0:
            vertices.append((0, termino_independiente / coef_x2))

        if coef_x1 != 0:
            vertices.append((termino_independiente / coef_x1, 0))

    vertices.append((0, 0))

    vertices = [
        punto for punto in vertices
        if es_factible(punto, restricciones, tolerancia)
    ]

    vertices_unicos = list({
        (
            round(punto[0], decimales),
            round(punto[1], decimales)
        )
        for punto in vertices
    })

    if not vertices_unicos:
        raise ValueError("No se encontraron vértices factibles.")

    vertices_ordenados = convex_hull(vertices_unicos)

    if tipo_optimizacion == "min":
        punto_optimo = min(
            vertices_unicos,
            key=lambda punto: np.dot(coeficientes_objetivo, punto)
        )
    else:
        punto_optimo = max(
            vertices_unicos,
            key=lambda punto: np.dot(coeficientes_objetivo, punto)
        )

    z_vertices = {
        punto: round(
            float(np.dot(coeficientes_objetivo, punto)),
            decimales
        )
        for punto in vertices_unicos
    }

    activas_vertices = {
        punto: restricciones_activas(
            punto,
            restricciones,
            tolerancia_activa
        )
        for punto in vertices_unicos
    }

    coordenadas_x, coordenadas_y = zip(*vertices_unicos)

    x_max = max(coordenadas_x) + margen
    y_max = max(coordenadas_y) + margen

    return {
        "vertices": vertices_unicos,
        "vertices_ordenados": vertices_ordenados,
        "z_vertices": z_vertices,
        "activas_vertices": activas_vertices,
        "optimo": punto_optimo,
        "valor_optimo": float(
            np.dot(coeficientes_objetivo, punto_optimo)
        ),
        "x_max": x_max,
        "y_max": y_max
    }
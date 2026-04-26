import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import json
import sys
import os
from logica import resolver_PL

# INPUT
carpeta = os.path.dirname(os.path.abspath(__file__))
archivo = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, "params.json")

with open(archivo, "r") as f:
    params = json.load(f)

c = np.array(params["c"])
restricciones = [tuple(r) for r in params["restricciones"]]
g = params["grafico"]
l = params["logica"]

# DATOS (desde lógica)
res = resolver_PL(c, restricciones, l)

p = res["optimo"]
z = res["valor_optimo"]

print(f"Óptimo: ({p[0]:.2f}, {p[1]:.2f})")
print(f"Valor óptimo: Z = {z:.2f}")

# ── AUTO-AJUSTE de límites basado en vértices reales ──
xs, ys = zip(*res["vertices"])
x_max_data = max(xs)
y_max_data = max(ys)

margen_pct     = g["autoajuste_margen_pct"]
offset_pct     = g["autoajuste_offset_pct"]
offset_escala  = g["autoajuste_offset_escala"]
clip_factor    = g["autoajuste_clip_factor"]

x_plot_max = x_max_data * (1 + margen_pct) + g["xlim_margen"]
y_plot_max = y_max_data * (1 + margen_pct) + g["ylim_margen"]

# Offsets de texto escalados al rango de datos
ox = x_max_data * offset_pct + g["vertices_text_offset"][0] * (x_max_data / offset_escala)
oy = y_max_data * offset_pct + g["vertices_text_offset"][1] * (y_max_data / offset_escala)
tx = x_max_data * offset_pct + g["optimo_text_offset"][0] * (x_max_data / offset_escala)
ty = y_max_data * offset_pct + g["optimo_text_offset"][1] * (y_max_data / offset_escala)

# x_vals cubre todo el rango visible
x_vals = np.linspace(0, x_plot_max, g["x_vals_n"])

# GRÁFICO
fig, (ax_plot, ax_legend) = plt.subplots(
    1, 2,
    figsize=tuple(g["figsize"]),
    gridspec_kw={"width_ratios": g["width_ratios"]}
)

# Restricciones
colores_lineas = []
for i, (a1, a2, b) in enumerate(restricciones):
    if a2 != 0:
        y_line = (b - a1 * x_vals) / a2
        mask = (y_line >= -g["ylim_margen"]) & (y_line <= y_plot_max * clip_factor)
        line, = ax_plot.plot(x_vals[mask], y_line[mask])
        colores_lineas.append(line.get_color())
    else:
        line = ax_plot.axvline(x=b / a1)
        colores_lineas.append(line.get_color())

# Región factible
px, py = zip(*res["vertices_ordenados"])
ax_plot.fill(px, py, alpha=g["region_alpha"], color=g["region_color"])

# Vértices
dec     = l["decimales_etiqueta"]
dec_cmp = l["decimales_comparacion"]
for v in res["vertices"]:
    es_optimo = (round(v[0], dec_cmp) == round(res["optimo"][0], dec_cmp) and
                 round(v[1], dec_cmp) == round(res["optimo"][1], dec_cmp))
    if not es_optimo:
        ax_plot.scatter(*v, color=g["vertices_color"], s=g["vertices_size"], zorder=5)
        z_v    = res["z_vertices"][v]
        activas = res["activas_vertices"][v]
        etiqueta = f'({round(v[0], dec)}, {round(v[1], dec)})'
        if g["vertices_mostrar_z"]:
            etiqueta += f'\nZ={z_v}'
        if activas:
            etiqueta += f'\n[R{",R".join(map(str, activas))}]'
        ax_plot.text(v[0] + ox, v[1] + oy, etiqueta,
                     fontsize=g["vertices_fontsize"], color=g["vertices_color"])

# Óptimo
ax_plot.scatter(*res["optimo"], s=g["optimo_size"], color=g["optimo_color"], zorder=6)
activas_opt  = res["activas_vertices"][res["optimo"]]
etiqueta_opt = (f'ÓPTIMO\n({round(res["optimo"][0], dec)}, {round(res["optimo"][1], dec)})'
                f'\nZ={res["valor_optimo"]:.{dec}f}')
if activas_opt:
    etiqueta_opt += f'\n[R{",R".join(map(str, activas_opt))}]'
ax_plot.text(res["optimo"][0] + tx, res["optimo"][1] + ty, etiqueta_opt,
             fontsize=g["optimo_fontsize"], color=g["optimo_color"], fontweight='bold')

# Línea de nivel óptimo
if c[1] != 0:
    y_nivel     = (z - c[0] * x_vals) / c[1]
    mask_nivel  = (y_nivel >= -g["ylim_margen"]) & (y_nivel <= y_plot_max * clip_factor)
    ax_plot.plot(x_vals[mask_nivel], y_nivel[mask_nivel], g["nivel_color"],
                 linewidth=g["nivel_linewidth"])

# Ejes y estética
ax_plot.axhline(0, color=g["ejes_color"])
ax_plot.axvline(0, color=g["ejes_color"])
ax_plot.set_xlabel(g["xlabel"])
ax_plot.set_ylabel(g["ylabel"])
ax_plot.set_xlim(-g["xlim_margen"], x_plot_max)
ax_plot.set_ylim(-g["ylim_margen"], y_plot_max)
ax_plot.grid(g["grid"])
ax_plot.set_title(g["titulo"])

# ── PANEL DERECHO: leyenda + resumen ──
ax_legend.axis("off")

handles = []
for i, (a1, a2, b) in enumerate(restricciones):
    lbl = f'R{i+1}: {a1}x1 + {a2}x2 ≤ {b}' if a2 != 0 else f'R{i+1}: x1 ≤ {b/a1}'
    handles.append(mlines.Line2D([], [], color=colores_lineas[i], label=lbl))

handles.append(mpatches.Patch(color=g["region_color"], alpha=g["region_alpha"], label=g["region_label"]))
handles.append(mlines.Line2D([], [], marker='o', color='w', markerfacecolor=g["optimo_color"],
                              markersize=g["leyenda_markersize"], label='Óptimo'))
handles.append(mlines.Line2D([], [], color=g["nivel_color"].replace('-', ''),
                              linestyle='--', linewidth=g["nivel_linewidth"],
                              label=f'Nivel Z={z:.2f}'))

leg = ax_legend.legend(handles=handles, loc='upper center',
                       frameon=True, fontsize=g["leyenda_fontsize"],
                       title=g["leyenda_titulo"], title_fontsize=g["leyenda_titulo_fontsize"],
                       borderpad=g["leyenda_borderpad"], labelspacing=g["leyenda_labelspacing"])
leg.get_frame().set_facecolor(g["resumen_color_fondo"])
leg.get_frame().set_edgecolor(g["resumen_color_borde"])

if g["resumen_mostrar"]:
    modo_str = "Min" if l.get("modo", "max") == "min" else "Max"
    expr_c = " + ".join(f'{ci}·x{i+1}' for i, ci in enumerate(c))
    texto  = (f'Función objetivo:\n  {modo_str} Z = {expr_c}\n\n'
              f'Solución óptima:\n'
              + "\n".join(f'  x{i+1} = {round(res["optimo"][i], l["decimales_dedup"])}' for i in range(len(c)))
              + f'\n  Z* = {res["valor_optimo"]:.{dec}f}\n\n'
              + (f'Restricciones activas:\n  R{", R".join(map(str, activas_opt))}\n\n' if activas_opt else '')
              + f'Vértices evaluados: {len(res["vertices"])}')
    ax_legend.text(g["resumen_posicion"][0], g["resumen_posicion"][1], texto,
                   transform=ax_legend.transAxes,
                   fontsize=g["resumen_fontsize"], verticalalignment='top', horizontalalignment='center',
                   bbox=dict(boxstyle='round', facecolor=g["resumen_color_fondo"],
                             edgecolor=g["resumen_color_borde"], alpha=g["resumen_alpha"]))

plt.tight_layout()
plt.show()
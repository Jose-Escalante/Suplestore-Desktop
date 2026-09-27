try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.ticker import FuncFormatter, MaxNLocator
    from matplotlib.figure import Figure
    GRAFICOS_OK = True
except Exception:
    GRAFICOS_OK = False

from datetime import date

BG = "#3B3B3B"
FG = "#EEEEEE"
VERDE = "#5CB85C"
NARANJA = "#E0A800"
GRIS = "#CCCCCC"
ANCHO = 6.2
ALTO = 2.2


def _base(titulo, ancho_px=None):
    ancho = (ancho_px or ANCHO * 100) / 100.0
    alto = ancho * (ALTO / ANCHO)
    fig = Figure(figsize=(ancho, alto), dpi=100, facecolor=BG, tight_layout=True)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG)
    ax.set_title(titulo, color=FG, fontsize=10, fontweight="bold")
    ax.tick_params(colors=FG, labelsize=9)
    for lado in ("top", "right"):
        ax.spines[lado].set_color("none")
    ax.spines["left"].set_color("#666666")
    ax.spines["bottom"].set_color("#666666")
    ax.grid(axis="x", color="#555555", linestyle="--", linewidth=0.6, alpha=0.6)
    return fig, ax


def _dolar(val, _pos):
    return f"${float(val):,.0f}"


def _etiqueta_dia(valor):
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m")
    return str(valor)


def _vertical(filas, key_x, key_y, titulo, periodo_label="", es_dinero=False, rotacion=0, alerta_dias=False, ancho_px=None):
    fig, ax = _base(f"{titulo} - {periodo_label}".strip(" -") if periodo_label else titulo, ancho_px)
    ax.grid(axis="x", color="none")
    etiquetas = [_etiqueta_dia(f[key_x]) for f in filas]
    if rotacion:
        etiquetas = [e[:24] for e in etiquetas]
    valores = [float(f[key_y]) for f in filas]
    colores = [NARANJA if v <= 30 else VERDE for v in valores] if alerta_dias else VERDE
    ax.bar(etiquetas, valores, color=colores, width=0.35)
    if len(valores) == 1:
        ax.set_xlim(-1.75, 1.75)
    if es_dinero:
        ax.yaxis.set_major_formatter(FuncFormatter(_dolar))
    else:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if rotacion:
        ax.tick_params(axis="x", rotation=rotacion)
    ax.margins(y=0.15)
    return fig


def _descuentos(filas, ancho_px=None):
    f = filas[0]
    con = int(f["notas_con_descuento"])
    sin = int(f["notas"]) - con
    fig, ax = _base("Notas con Descuento", ancho_px)
    ax.grid(axis="x", color="none")
    ax.bar(["Con descuento", "Sin descuento"], [con, sin], color=[VERDE, GRIS], width=0.35)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.margins(y=0.15)
    return fig


def _inactivos(filas, ancho_px=None):
    hoy = date.today()
    etiquetas = []
    valores = []
    colores = []
    for f in filas:
        etiquetas.append(f["nombre"])
        ultima = f.get("ultima_venta")
        if ultima:
            if hasattr(ultima, "date"):
                ultima = ultima.date()
            valores.append(max(0, (hoy - ultima).days))
            colores.append(VERDE)
        else:
            valores.append(int(f.get("dias_filtro") or 30))
            colores.append(GRIS)
    if not valores:
        return None
    etiquetas = [e[:24] for e in etiquetas]
    fig, ax = _base("Dias Sin Comprar", ancho_px)
    ax.grid(axis="x", color="none")
    ax.bar(etiquetas, valores, color=colores, width=0.35)
    if len(valores) == 1:
        ax.set_xlim(-1.75, 1.75)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="x", rotation=30)
    ax.margins(y=0.15)
    return fig


TIPOS_CON_GRAFICO = {
    "Ventas por Periodo",
    "Productos mas Vendidos",
    "Productos menos Vendidos",
    "Ventas por Cliente",
    "Ventas por Vendedor",
    "Ventas por Metodo de Pago",
    "Descuentos Aplicados",
    "Productos con Stock Bajo",
    "Clientes Inactivos",
    "Vencimientos de Lotes",
}


def crear_grafico(tipo, filas, periodo_label="", ancho_px=None):
    if not GRAFICOS_OK or not filas or tipo not in TIPOS_CON_GRAFICO:
        return None
    if tipo == "Ventas por Periodo":
        return _vertical(filas, "dia", "total", "Ventas por Dia", periodo_label, es_dinero=True, ancho_px=ancho_px)
    if tipo == "Productos mas Vendidos":
        return _vertical(filas, "nombre_producto", "unidades", "Unidades Vendidas por Producto", rotacion=30, ancho_px=ancho_px)
    if tipo == "Productos menos Vendidos":
        return _vertical(filas, "nombre_producto", "unidades", "Unidades por Producto", rotacion=30, ancho_px=ancho_px)
    if tipo == "Ventas por Cliente":
        return _vertical(filas, "nombre", "total", "Ventas por Cliente", es_dinero=True, rotacion=30, ancho_px=ancho_px)
    if tipo == "Ventas por Vendedor":
        return _vertical(filas, "usuario", "notas", "Cantidad de Ventas por Vendedor", rotacion=30, ancho_px=ancho_px)
    if tipo == "Ventas por Metodo de Pago":
        return _vertical(filas, "metodo_pago", "total", "Ventas por Metodo de Pago", es_dinero=True, rotacion=30, ancho_px=ancho_px)
    if tipo == "Descuentos Aplicados":
        return _descuentos(filas, ancho_px)
    if tipo == "Productos con Stock Bajo":
        return _vertical(filas, "nombre_producto", "stock_total", "Stock Disponible", rotacion=30, ancho_px=ancho_px)
    if tipo == "Clientes Inactivos":
        return _inactivos(filas, ancho_px)
    if tipo == "Vencimientos de Lotes":
        filas_aux = [
            {**f, "etiqueta": f"{f['nombre_producto']} (L{f['lote']})"}
            for f in filas
        ]
        return _vertical(filas_aux, "etiqueta", "dias", "Dias Restantes para Vencer", rotacion=30, alerta_dias=True, ancho_px=ancho_px)
    return None


def crear_canvas(fig, master):
    if not GRAFICOS_OK or fig is None:
        return None
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().configure(bg=BG)
    return canvas
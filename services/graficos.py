try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.ticker import FuncFormatter
    from matplotlib.figure import Figure
    GRAFICOS_OK = True
except Exception:
    GRAFICOS_OK = False

BG = "#3B3B3B"
FG = "#EEEEEE"
VERDE = "#5CB85C"
NARANJA = "#E0A800"
ANCHO = 6.2
ALTO = 2.2


def _base(titulo):
    fig = Figure(figsize=(ANCHO, ALTO), dpi=100, facecolor=BG, tight_layout=True)
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


def _vertical(filas, key_x, key_y, titulo):
    fig, ax = _base(titulo)
    ax.grid(axis="x", color="none")
    ax.bar([_etiqueta_dia(f[key_x]) for f in filas],
           [float(f[key_y]) for f in filas],
           color=VERDE, width=0.55)
    ax.yaxis.set_major_formatter(FuncFormatter(_dolar))
    ax.margins(y=0.15)
    return fig


def _horizontal(filas, key_etiqueta, key_valor, titulo, dinero=False, verdes_por_dias=False):
    fig, ax = _base(titulo)
    etiquetas = [str(f[key_etiqueta]) for f in filas][::-1]
    valores = [float(f[key_valor]) for f in filas][::-1]
    colores = [NARANJA if v <= 30 else VERDE for v in valores] if verdes_por_dias else VERDE
    ax.barh(etiquetas, valores, color=colores, height=0.6)
    if dinero:
        ax.xaxis.set_major_formatter(FuncFormatter(_dolar))
    ax.margins(x=0.12)
    return fig


def crear_grafico(tipo, filas):
    if not GRAFICOS_OK or not filas:
        return None
    if tipo == "Descuentos Aplicados" or tipo == "Clientes Inactivos":
        return None
    if tipo == "Ventas por Periodo":
        return _vertical(filas, "dia", "total", "Ventas por Dia")
    if tipo in ("Productos mas Vendidos", "Productos menos Vendidos"):
        return _horizontal(filas, "nombre_producto", "unidades", "Unidades Vendidas por Producto")
    if tipo == "Ventas por Cliente":
        return _horizontal(filas, "nombre", "total", "Ventas por Cliente", dinero=True)
    if tipo == "Ventas por Vendedor":
        return _horizontal(filas, "usuario", "total", "Ventas por Vendedor", dinero=True)
    if tipo == "Ventas por Metodo de Pago":
        return _horizontal(filas, "metodo_pago", "total", "Ventas por Metodo de Pago", dinero=True)
    if tipo == "Productos con Stock Bajo":
        return _horizontal(filas, "nombre_producto", "stock_total", "Stock Disponible")
    if tipo == "Vencimientos de Lotes":
        filas_aux = [
            {**f, "etiqueta": f"{f['nombre_producto']} (L{f['lote']})"}
            for f in filas
        ]
        return _horizontal(filas_aux, "etiqueta", "dias", "Dias Restantes para Vencer", verdes_por_dias=True)
    return None


def crear_canvas(fig, master):
    if not GRAFICOS_OK or fig is None:
        return None
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().configure(bg=BG)
    return canvas
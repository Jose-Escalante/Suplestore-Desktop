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


def _vertical(filas, key_x, key_y, titulo, periodo_label="", es_dinero=False, rotacion=0):
    fig, ax = _base(f"{titulo} - {periodo_label}".strip(" -") if periodo_label else titulo)
    ax.grid(axis="x", color="none")
    etiquetas = [_etiqueta_dia(f[key_x]) for f in filas]
    if rotacion:
        etiquetas = [e[:18] for e in etiquetas]
    ax.bar(etiquetas, [float(f[key_y]) for f in filas], color=VERDE, width=0.55)
    if es_dinero:
        ax.yaxis.set_major_formatter(FuncFormatter(_dolar))
    if rotacion:
        ax.tick_params(axis="x", rotation=rotacion)
    ax.margins(y=0.15)
    return fig


TIPOS_CON_GRAFICO = {
    "Ventas por Periodo",
    "Productos mas Vendidos",
    "Ventas por Metodo de Pago",
    "Productos con Stock Bajo",
}


def crear_grafico(tipo, filas, periodo_label=""):
    if not GRAFICOS_OK or not filas or tipo not in TIPOS_CON_GRAFICO:
        return None
    if tipo == "Ventas por Periodo":
        return _vertical(filas, "dia", "total", "Ventas por Dia", periodo_label, es_dinero=True)
    if tipo == "Productos mas Vendidos":
        return _vertical(filas, "nombre_producto", "unidades", "Unidades Vendidas por Producto", rotacion=30)
    if tipo == "Ventas por Metodo de Pago":
        return _vertical(filas, "metodo_pago", "total", "Ventas por Metodo de Pago", es_dinero=True, rotacion=30)
    if tipo == "Productos con Stock Bajo":
        return _vertical(filas, "nombre_producto", "stock_total", "Stock Disponible", rotacion=30)
    return None


def crear_canvas(fig, master):
    if not GRAFICOS_OK or fig is None:
        return None
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.get_tk_widget().configure(bg=BG)
    return canvas
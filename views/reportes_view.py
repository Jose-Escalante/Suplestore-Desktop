from datetime import datetime
from tkinter import filedialog, font as tkfont, messagebox, ttk

import customtkinter as ctk

from services.excel_export import exportar_ventas_xlsx
from services.graficos import crear_grafico, crear_canvas, GRAFICOS_OK

PERIODOS = ["Última semana", "Último mes", "Último año"]
OPCIONES_DIAS = ["30 días", "60 días", "90 días", "Todos"]

PERIODO_KEY = {"Última semana": "semana", "Último mes": "mes", "Último año": "anio"}
DIAS_KEY = {"30 días": 30, "60 días": 60, "90 días": 90, "Todos": None}


class ReportesView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self.tipos = [
            "Ventas por Período",
            "Productos más Vendidos",
            "Productos menos Vendidos",
            "Ventas por Cliente",
            "Ventas por Vendedor",
            "Ventas por Método de Pago",
            "Descuentos Aplicados",
            "Productos con Stock Bajo",
            "Clientes Inactivos",
            "Vencimientos de Lotes",
        ]
        self.tipos_con_periodo = set(self.tipos[:7])
        self.tipos_con_dias = {self.tipos[8], self.tipos[9]}
        self._headers = []
        self._mostrar = []
        self._exportar = []
        self._crudas = []
        self._kpis = []
        self._chart_ancho = 620
        self._chart_render_ancho = 0
        self._resize_after = None
        self._kpi_resize_after = None

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Reportes Gerenciales", text_color="#111111", font=("Arial", 13, "bold")).pack(anchor="w", padx=12, pady=4)

        container = ctk.CTkFrame(self.root, fg_color="#3B3B3B")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        kpi_frame = ctk.CTkFrame(container, fg_color="#3B3B3B")
        kpi_frame.pack(fill="x", pady=(0, 12))
        kpis = self.controller.model.obtener_metricas_kpi()
        for titulo, valor in [
            ("Ventas Hoy", f"${float(kpis['ventas_hoy']):.2f}"),
            ("Ventas del Mes", f"${float(kpis['ventas_mes']):.2f}"),
            ("Notas Registradas", str(kpis["notas"])),
            ("Producto Top", str(kpis["top_producto"])),
        ]:
            tarjeta = ctk.CTkFrame(kpi_frame, fg_color="#5CB85C", corner_radius=8, height=64)
            tarjeta.pack(side="left", padx=4, fill="x", expand=True)
            tarjeta.pack_propagate(False)
            ctk.CTkLabel(tarjeta, text=titulo, text_color="#111111", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
            label_valor = ctk.CTkLabel(tarjeta, text=valor, text_color="#111111", font=("Arial", 16, "bold"))
            label_valor.pack(anchor="w", padx=10)
            self._kpis.append((tarjeta, label_valor))

        body = ctk.CTkFrame(container, fg_color="#3B3B3B")
        body.pack(fill="both", expand=True)

        columna = ctk.CTkFrame(body, fg_color="#3B3B3B")
        columna.pack(side="left", fill="both", expand=True)

        self.chart_frame = ctk.CTkFrame(columna, fg_color="#3B3B3B", height=230)
        self.chart_frame.pack(fill="x", pady=(0, 10))
        self.chart_frame.pack_propagate(False)
        self.chart_frame.bind("<Configure>", self._en_chart_resize)

        table_frame = ctk.CTkFrame(columna, fg_color="#777777", corner_radius=8)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        scrollbar_h = ttk.Scrollbar(table_frame, orient="horizontal")
        scrollbar_h.pack(side="bottom", fill="x")
        self.table_frame = table_frame
        self.scrollbar = scrollbar
        self.scrollbar_h = scrollbar_h
        self._reconstruir_arbol()

        sidebar = ctk.CTkFrame(body, fg_color="#3B3B3B", width=210)
        sidebar.pack(side="right", fill="y", padx=(12, 0))
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Tipo de reporte:", text_color="#FFFFFF", font=("Arial", 12)).pack(anchor="w", pady=(4, 2))
        self.combo_tipo = ctk.CTkComboBox(sidebar, values=self.tipos, state="readonly",
                                          font=("Arial", 12), dropdown_font=("Arial", 12),
                                          command=self._cambiar_tipo)
        self.combo_tipo.set(self.tipos[0])
        self.combo_tipo.pack(fill="x", pady=(0, 10))

        self.lbl_periodo = ctk.CTkLabel(sidebar, text="Período:", text_color="#FFFFFF", font=("Arial", 12))
        self.combo_periodo = ctk.CTkComboBox(sidebar, values=PERIODOS, state="readonly",
                                             font=("Arial", 12), dropdown_font=("Arial", 12))
        self.combo_periodo.set("Último mes")

        self.lbl_dias = ctk.CTkLabel(sidebar, text="Filtro:", text_color="#FFFFFF", font=("Arial", 12))
        self.combo_dias = ctk.CTkComboBox(sidebar, values=OPCIONES_DIAS, state="readonly",
                                          font=("Arial", 12), dropdown_font=("Arial", 12))
        self.combo_dias.set("30 días")

        ctk.CTkButton(sidebar, text="Exportar Excel", fg_color="#5CB85C", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=40, command=self.exportar_excel).pack(pady=(14, 6))
        ctk.CTkButton(sidebar, text="Refrescar", fg_color="#E0A800", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=34, command=self.cargar).pack(pady=6)
        ctk.CTkButton(sidebar, text="Volver", fg_color="#E0E0E0", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=34, command=controller.show_panel).pack(pady=(16, 0))

        kpi_frame.bind("<Configure>", self._en_kpi_resize)
        self._ajustar_kpis()
        self._actualizar_controles()
        self.cargar()

    def _cambiar_tipo(self, _valor):
        self.combo_dias.set("30 días")
        self._actualizar_controles()
        self.cargar()

    def _actualizar_controles(self):
        tipo = self.combo_tipo.get()
        if tipo in self.tipos_con_periodo:
            self.lbl_periodo.pack(anchor="w", pady=(0, 2))
            self.combo_periodo.pack(fill="x", pady=(0, 10))
        else:
            self.lbl_periodo.pack_forget()
            self.combo_periodo.pack_forget()
        if tipo in self.tipos_con_dias:
            if tipo == "Vencimientos de Lotes":
                self.combo_dias.configure(values=OPCIONES_DIAS)
                self.combo_dias.set("Todos")
            else:
                self.combo_dias.configure(values=OPCIONES_DIAS[:-1])
                if self.combo_dias.get() == "Todos":
                    self.combo_dias.set("90 días")
            self.lbl_dias.pack(anchor="w", pady=(0, 2))
            self.combo_dias.pack(fill="x", pady=(0, 10))
        else:
            self.lbl_dias.pack_forget()
            self.combo_dias.pack_forget()

    def _en_chart_resize(self, _evento):
        if self._resize_after:
            try:
                self.root.after_cancel(self._resize_after)
            except Exception:
                pass
        self._resize_after = self.root.after(120, self._re_render_grafico)

    def _re_render_grafico(self):
        self._resize_after = None
        try:
            if not self.chart_frame.winfo_exists():
                return
        except Exception:
            return
        objetivo = max(self._chart_ancho, 300)
        if not self._crudas or objetivo == self._chart_render_ancho:
            return
        self._render_grafico(self.combo_tipo.get())

    def _en_kpi_resize(self, _evento):
        if self._kpi_resize_after:
            try:
                self.root.after_cancel(self._kpi_resize_after)
            except Exception:
                pass
        self._kpi_resize_after = self.root.after(120, self._ajustar_kpis)

    def _ajustar_kpis(self):
        self._kpi_resize_after = None
        try:
            self.root.update_idletasks()
        except Exception:
            return
        for tarjeta, label in self._kpis:
            try:
                ancho = max(tarjeta.winfo_width() - 26, 60)
                texto = label.cget("text")
                tamano = 16
                for propuesto in range(16, 7, -1):
                    fuente = tkfont.Font(family="Arial", size=propuesto, weight="bold")
                    if fuente.measure(texto) <= ancho:
                        tamano = propuesto
                        break
                label.configure(font=("Arial", tamano, "bold"))
            except Exception:
                continue

    def _ancho_columnas(self):
        fuente = tkfont.Font(family="Arial", size=13)
        anchos = []
        for i, head in enumerate(self._headers):
            max_px = fuente.measure(head)
            for fila in self._mostrar:
                if i < len(fila):
                    max_px = max(max_px, fuente.measure(str(fila[i])))
            anchos.append(min(280, max(90, max_px + 26)))
        return anchos

    def _reconstruir_arbol(self):
        arbol = getattr(self, "tree", None)
        if arbol is not None:
            try:
                if arbol.winfo_exists():
                    arbol.destroy()
            except Exception:
                pass
        try:
            estilo = ttk.Style(self.root)
            estilo.configure("Reportes.Treeview", font=("Arial", 13), rowheight=30)
            estilo.configure("Reportes.Treeview.Heading", font=("Arial", 13, "bold"))
            estilo_tree = "Reportes.Treeview"
        except Exception:
            estilo_tree = "default"
        self.tree = ttk.Treeview(self.table_frame, style=estilo_tree, show="headings",
                                 yscrollcommand=self.scrollbar.set, xscrollcommand=self.scrollbar_h.set)
        self.scrollbar.config(command=self.tree.yview)
        self.scrollbar_h.config(command=self.tree.xview)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def cargar(self):
        tipo = self.combo_tipo.get()
        periodo = PERIODO_KEY.get(self.combo_periodo.get(), "mes")
        dias = DIAS_KEY.get(self.combo_dias.get())
        self._headers, self._mostrar, self._exportar, self._crudas = self._obtener(tipo, periodo, dias)
        self._reconstruir_arbol()
        self.tree["columns"] = tuple(str(i) for i in range(len(self._headers)))
        anchos = self._ancho_columnas()
        for i, head in enumerate(self._headers):
            self.tree.heading(str(i), text=head)
            self.tree.column(str(i), width=anchos[i], minwidth=70, anchor="w", stretch=False)
        for fila in self._mostrar:
            self.tree.insert("", "end", values=fila)
        self._render_grafico(tipo)

    def _render_grafico(self, tipo):
        for hijo in self.chart_frame.winfo_children():
            hijo.destroy()
        if not GRAFICOS_OK:
            ctk.CTkLabel(self.chart_frame, text="Gráficos no disponibles en este equipo.",
                         text_color="#AAAAAA", font=("Arial", 13)).pack(expand=True)
            return
        ancho = max(self._chart_ancho, 300)
        self._chart_render_ancho = ancho
        fig = crear_grafico(tipo, self._crudas, self.combo_periodo.get(), ancho)
        if fig is None:
            ctk.CTkLabel(self.chart_frame, text="Sin gráfico para este reporte.",
                         text_color="#AAAAAA", font=("Arial", 13)).pack(expand=True)
            return
        canvas = crear_canvas(fig, self.chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def _obtener(self, tipo, periodo, dias):
        model = self.controller.model
        if tipo == "Ventas por Período":
            filas = model.reporte_ventas_por_periodo(periodo)
            if periodo == "anio":
                headers = ["Mes", "Notas", "Total ($)"]
                mostrar = [(f["dia"].strftime("%m/%Y"), f["notas"], f"${float(f['total']):.2f}") for f in filas]
                exportar = [(f["dia"].strftime("%Y-%m"), f["notas"], float(f["total"])) for f in filas]
            else:
                headers = ["Día", "Notas", "Total ($)"]
                mostrar = [(self._fecha(f["dia"]), f["notas"], f"${float(f['total']):.2f}") for f in filas]
                exportar = [(str(f["dia"]), f["notas"], float(f["total"])) for f in filas]
        elif tipo == "Productos más Vendidos":
            filas = model.reporte_productos_mas_vendidos(periodo)
            headers = ["Producto", "Unidades", "Ingresos ($)"]
            mostrar = [(f["nombre_producto"], f["unidades"], f"${float(f['ingresos']):.2f}") for f in filas]
            exportar = [(f["nombre_producto"], f["unidades"], float(f["ingresos"])) for f in filas]
        elif tipo == "Productos menos Vendidos":
            filas = model.reporte_productos_menos_vendidos(periodo)
            headers = ["Producto", "Unidades", "Ingresos ($)"]
            mostrar = [(f["nombre_producto"], f["unidades"], f"${float(f['ingresos']):.2f}") for f in filas]
            exportar = [(f["nombre_producto"], f["unidades"], float(f["ingresos"])) for f in filas]
        elif tipo == "Ventas por Cliente":
            filas = model.reporte_ventas_por_cliente(periodo)
            headers = ["Cliente", "Notas", "Total ($)"]
            mostrar = [(f["nombre"], f["notas"], f"${float(f['total']):.2f}") for f in filas]
            exportar = [(f["nombre"], f["notas"], float(f["total"])) for f in filas]
        elif tipo == "Ventas por Vendedor":
            filas = model.reporte_ventas_por_vendedor(periodo)
            headers = ["Vendedor", "Notas", "Total ($)"]
            mostrar = [(f["usuario"], f["notas"], f"${float(f['total']):.2f}") for f in filas]
            exportar = [(f["usuario"], f["notas"], float(f["total"])) for f in filas]
        elif tipo == "Ventas por Método de Pago":
            filas = model.reporte_ventas_por_metodo_pago(periodo)
            headers = ["Método de Pago", "Notas", "Total ($)"]
            mostrar = [(f["metodo_pago"], f["notas"], f"${float(f['total']):.2f}") for f in filas]
            exportar = [(f["metodo_pago"], f["notas"], float(f["total"])) for f in filas]
        elif tipo == "Descuentos Aplicados":
            filas = model.reporte_descuentos_aplicados(periodo)
            headers = ["Notas", "Notas con Descuento", "Total Descontado ($)"]
            mostrar = [(f["notas"], f["notas_con_descuento"], f"${float(f['total_descontado']):.2f}") for f in filas]
            exportar = [(f["notas"], f["notas_con_descuento"], float(f["total_descontado"])) for f in filas]
        elif tipo == "Productos con Stock Bajo":
            filas = model.reporte_productos_stock_bajo(5)
            headers = ["Producto", "Stock Total"]
            mostrar = [(f["nombre_producto"], f["stock_total"]) for f in filas]
            exportar = [(f["nombre_producto"], f["stock_total"]) for f in filas]
        elif tipo == "Clientes Inactivos":
            filas = model.reporte_clientes_inactivos(dias or 90)
            for f in filas:
                f["dias_filtro"] = dias or 90
            headers = ["Cliente", "Cédula", "Teléfono", "Última Venta"]
            mostrar = [(f["nombre"], f["cedula"], f["telefono"], self._fecha(f["ultima_venta"])) for f in filas]
            exportar = [(f["nombre"], f["cedula"], f["telefono"], str(f["ultima_venta"])) for f in filas]
        else:
            filas = model.reporte_vencimientos_lotes(dias)
            headers = ["Producto", "Lote", "Stock", "Vencimiento", "Días Restantes"]
            mostrar = [(f["nombre_producto"], f["lote"], f["stock"], self._fecha(f["vencimiento"]), f["dias"]) for f in filas]
            exportar = [(f["nombre_producto"], f["lote"], f["stock"], str(f["vencimiento"]), f["dias"]) for f in filas]
        return headers, mostrar, exportar, filas

    def exportar_excel(self):
        if not self._mostrar:
            messagebox.showinfo("Excel", "No hay datos que exportar.")
            return
        tipo = self.combo_tipo.get().replace(" ", "_")
        ruta = filedialog.asksaveasfilename(parent=self.root, defaultextension=".xlsx",
                                            filetypes=[("Excel", "*.xlsx")],
                                            initialfile=f"reporte_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        if not ruta:
            return
        exportar_ventas_xlsx(ruta, self._headers, self._exportar, titulo=self.combo_tipo.get())
        messagebox.showinfo("Éxito", f"Reporte exportado en:\n{ruta}")

    @staticmethod
    def _fecha(valor):
        if valor is None:
            return "Sin compras"
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
        return str(valor)
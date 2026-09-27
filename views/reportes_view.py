from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from services.excel_export import exportar_ventas_xlsx
from services.graficos import crear_grafico, crear_canvas, GRAFICOS_OK

PERIODOS = ["Hoy", "Ultimos 7 dias", "Ultimos 30 dias"]
OPCIONES_DIAS = ["30 dias", "60 dias", "90 dias", "Todos"]

PERIODO_KEY = {"Hoy": "hoy", "Ultimos 7 dias": "semana", "Ultimos 30 dias": "mes"}
DIAS_KEY = {"30 dias": 30, "60 dias": 60, "90 dias": 90, "Todos": None}


class ReportesView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self.tipos = [
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
        ]
        self.tipos_con_periodo = set(self.tipos[:7])
        self.tipos_con_dias = {self.tipos[8], self.tipos[9]}
        self._headers = []
        self._mostrar = []
        self._exportar = []
        self._crudas = []

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
            ctk.CTkLabel(tarjeta, text=valor, text_color="#111111", font=("Arial", 16, "bold")).pack(anchor="w", padx=10)

        body = ctk.CTkFrame(container, fg_color="#3B3B3B")
        body.pack(fill="both", expand=True)

        columna = ctk.CTkFrame(body, fg_color="#3B3B3B")
        columna.pack(side="left", fill="both", expand=True)

        self.chart_frame = ctk.CTkFrame(columna, fg_color="#3B3B3B", height=230)
        self.chart_frame.pack(fill="x", pady=(0, 10))
        self.chart_frame.pack_propagate(False)

        table_frame = ctk.CTkFrame(columna, fg_color="#777777", corner_radius=8)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        try:
            estilo = ttk.Style(controller.root)
            estilo.configure("Reportes.Treeview", font=("Arial", 13), rowheight=30)
            estilo.configure("Reportes.Treeview.Heading", font=("Arial", 13, "bold"))
            estilo_tree = "Reportes.Treeview"
        except Exception:
            estilo_tree = "default"
        self.tree = ttk.Treeview(table_frame, style=estilo_tree, show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        sidebar = ctk.CTkFrame(body, fg_color="#3B3B3B", width=210)
        sidebar.pack(side="right", fill="y", padx=(12, 0))
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Tipo de reporte:", text_color="#FFFFFF", font=("Arial", 12)).pack(anchor="w", pady=(4, 2))
        self.combo_tipo = ctk.CTkComboBox(sidebar, values=self.tipos, state="readonly",
                                          font=("Arial", 12), dropdown_font=("Arial", 12),
                                          command=self._cambiar_tipo)
        self.combo_tipo.set(self.tipos[0])
        self.combo_tipo.pack(fill="x", pady=(0, 10))

        self.lbl_periodo = ctk.CTkLabel(sidebar, text="Periodo:", text_color="#FFFFFF", font=("Arial", 12))
        self.combo_periodo = ctk.CTkComboBox(sidebar, values=PERIODOS, state="readonly",
                                             font=("Arial", 12), dropdown_font=("Arial", 12))
        self.combo_periodo.set("Ultimos 30 dias")

        self.lbl_dias = ctk.CTkLabel(sidebar, text="Filtro:", text_color="#FFFFFF", font=("Arial", 12))
        self.combo_dias = ctk.CTkComboBox(sidebar, values=OPCIONES_DIAS, state="readonly",
                                          font=("Arial", 12), dropdown_font=("Arial", 12))
        self.combo_dias.set("30 dias")

        ctk.CTkButton(sidebar, text="Exportar Excel", fg_color="#5CB85C", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=40, command=self.exportar_excel).pack(pady=(14, 6))
        ctk.CTkButton(sidebar, text="Refrescar", fg_color="#E0A800", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=34, command=self.cargar).pack(pady=6)
        ctk.CTkButton(sidebar, text="Volver", fg_color="#E0E0E0", text_color="#000000", font=("Arial", 12, "bold"),
                      width=170, height=34, command=controller.show_panel).pack(pady=(16, 0))

        self._actualizar_controles()
        self.cargar()

    def _cambiar_tipo(self, _valor):
        self.combo_dias.set("30 dias")
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
                if self.combo_dias.get() not in OPCIONES_DIAS:
                    self.combo_dias.set("90 dias")
            else:
                self.combo_dias.configure(values=OPCIONES_DIAS[:-1])
                if self.combo_dias.get() == "Todos":
                    self.combo_dias.set("90 dias")
            self.lbl_dias.pack(anchor="w", pady=(0, 2))
            self.combo_dias.pack(fill="x", pady=(0, 10))
        else:
            self.lbl_dias.pack_forget()
            self.combo_dias.pack_forget()

    def cargar(self):
        tipo = self.combo_tipo.get()
        periodo = PERIODO_KEY.get(self.combo_periodo.get(), "mes")
        dias = DIAS_KEY.get(self.combo_dias.get())
        self._headers, self._mostrar, self._exportar, self._crudas = self._obtener(tipo, periodo, dias)
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = tuple(str(i) for i in range(len(self._headers)))
        for i, head in enumerate(self._headers):
            self.tree.heading(str(i), text=head)
            self.tree.column(str(i), width=150, anchor="w")
        for fila in self._mostrar:
            self.tree.insert("", "end", values=fila)
        self._render_grafico(tipo)

    def _render_grafico(self, tipo):
        for hijo in self.chart_frame.winfo_children():
            hijo.destroy()
        if not GRAFICOS_OK:
            ctk.CTkLabel(self.chart_frame, text="Graficos no disponibles en este equipo.",
                         text_color="#AAAAAA", font=("Arial", 13)).pack(expand=True)
            return
        fig = crear_grafico(tipo, self._crudas)
        if fig is None:
            ctk.CTkLabel(self.chart_frame, text="Sin grafico para este reporte.",
                         text_color="#AAAAAA", font=("Arial", 13)).pack(expand=True)
            return
        canvas = crear_canvas(fig, self.chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def _obtener(self, tipo, periodo, dias):
        model = self.controller.model
        if tipo == "Ventas por Periodo":
            filas = model.reporte_ventas_por_periodo(periodo)
            headers = ["Dia", "Notas", "Total ($)"]
            mostrar = [(self._fecha(f["dia"]), f["notas"], f"${float(f['total']):.2f}") for f in filas]
            exportar = [(str(f["dia"]), f["notas"], float(f["total"])) for f in filas]
        elif tipo == "Productos mas Vendidos":
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
        elif tipo == "Ventas por Metodo de Pago":
            filas = model.reporte_ventas_por_metodo_pago(periodo)
            headers = ["Metodo de Pago", "Notas", "Total ($)"]
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
            headers = ["Cliente", "Cedula", "Telefono", "Ultima Venta"]
            mostrar = [(f["nombre"], f["cedula"], f["telefono"], self._fecha(f["ultima_venta"])) for f in filas]
            exportar = [(f["nombre"], f["cedula"], f["telefono"], str(f["ultima_venta"])) for f in filas]
        else:
            filas = model.reporte_vencimientos_lotes(dias)
            headers = ["Producto", "Lote", "Stock", "Vencimiento", "Dias Restantes"]
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
        messagebox.showinfo("Exito", f"Reporte exportado en:\n{ruta}")

    @staticmethod
    def _fecha(valor):
        if valor is None:
            return "Sin compras"
        if hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y")
        return str(valor)
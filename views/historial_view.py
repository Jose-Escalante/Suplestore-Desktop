import customtkinter as ctk
from tkinter import messagebox, ttk


class HistorialView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        ctk.CTkLabel(top_bar, text="Historial de Eventos", text_color="#111111", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)

        container = ctk.CTkFrame(self.root, fg_color="#333333")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        table_frame = ctk.CTkFrame(container, fg_color="#2D2D2D")
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("id", "usuario", "tipo", "detalle", "fecha")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                 selectmode="browse")

        headers = ["ID", "Usuario", "Tipo", "Detalle", "Fecha y Hora"]
        configs = [
            ("id", 40, 40, False),
            ("usuario", 90, 70, False),
            ("tipo", 130, 110, False),
            ("detalle", 260, 120, True),
            ("fecha", 140, 110, True)
        ]
        for head, (col, width, minwidth, stretch) in zip(headers, configs):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=width, minwidth=minwidth, anchor="w", stretch=stretch)

        scroll_h = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=scroll_h.set)
        self.tree.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 0))
        scroll_h.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

        self.tipos = {
            "login": "Inicio de Sesion",
            "logout": "Cierre de Sesion",
            "venta": "Venta realizadas",
            "cambio_contrasena": "Cambio de Contrasena",
            "reset_contrasena": "Reset de Contrasena",
            "respaldo": "Copias de Seguridad"
        }

        sidebar = ctk.CTkFrame(container, fg_color="#333333", width=220)
        sidebar.pack(side="right", fill="y", padx=(20, 0))

        ctk.CTkLabel(sidebar, text="Filtrar por usuario o detalle:", text_color="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(5, 2))
        self.entry_busqueda = ctk.CTkEntry(sidebar, font=("Arial", 11), width=180)
        self.entry_busqueda.pack(pady=(0, 8))

        ctk.CTkLabel(sidebar, text="Tipo de evento:", text_color="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(0, 2))
        self.combo_tipo = ctk.CTkComboBox(sidebar, values=["Todos"] + list(self.tipos.values()), width=180, state="readonly")
        self.combo_tipo.set("Todos")
        self.combo_tipo.pack(pady=(0, 12))

        ctk.CTkButton(sidebar, text="Filtrar", fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=160, height=40, command=self.filtrar).pack(pady=6)
        ctk.CTkButton(sidebar, text="Limpiar Filtro", fg_color="#E0A800", text_color="#000000", font=("Arial", 10, "bold"),
                      width=160, height=30, command=self.cargar_datos).pack(pady=6)

        ctk.CTkButton(sidebar, text="Volver", fg_color="#E0E0E0", text_color="#000000", font=("Arial", 10, "bold"),
                      width=160, height=30, command=controller.show_panel).pack(pady=(30, 0))

        self.cargar_datos()

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.entry_busqueda.delete(0, "end")
        self.combo_tipo.set("Todos")
        self.consultar_eventos(None, None)

    def filtrar(self):
        busqueda = self.entry_busqueda.get().strip()
        tipo = self.combo_tipo.get()
        tipo_key = None
        if tipo != "Todos":
            tipo_key = [k for k, v in self.tipos.items() if v == tipo][0]
        self.consultar_eventos(busqueda or None, tipo_key)

    def consultar_eventos(self, busqueda, tipo):
        eventos = self.controller.model.obtener_eventos(busqueda, tipo)
        self.tree.delete(*self.tree.get_children())
        for ev in eventos:
            fecha = ""
            if ev["fecha_hora"]:
                fecha = ev["fecha_hora"].strftime("%d/%m/%Y %I:%M %p") if hasattr(ev["fecha_hora"], "strftime") else str(ev["fecha_hora"])
            tipo_show = self.tipos.get(ev["tipo"], ev["tipo"])
            usuario = ev["usuario"] if ev["usuario"] else "Sistema"
            self.tree.insert("", "end", values=(ev["id_evento"], usuario, tipo_show, ev["detalle"] or "", fecha))
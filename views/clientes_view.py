import os
import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image


class ClientesView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self._id_seleccionado = None
        icons_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

        def ico(name):
            path = os.path.join(icons_dir, name)
            if os.path.exists(path):
                return ctk.CTkImage(Image.open(path), size=(22, 22))
            return None

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Clientes", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        container = ctk.CTkFrame(self.root, fg_color="#3B3B3B")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        container.grid_columnconfigure(0, weight=0, minsize=380)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(container, fg_color="#3B3B3B")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(left_panel, text="Clientes", text_color="#FFFFFF", font=("Arial", 20, "bold")).pack(anchor="w", pady=(15, 25))

        vcmd_nombre = self.root.register(lambda P: P == "" or all(c.isalpha() or c.isspace() for c in P))
        vcmd_dig = self.root.register(lambda P: P == "" or P.isdigit())

        row_nombre = ctk.CTkFrame(left_panel, fg_color="#3B3B3B")
        row_nombre.pack(fill="x", pady=5)
        ctk.CTkLabel(row_nombre, text="Nombre:", text_color="#FFFFFF", font=("Arial", 11), width=80, anchor="w").pack(side="left")
        self.e_nombre = ctk.CTkEntry(row_nombre, font=("Arial", 11), width=260, validate="key", validatecommand=(vcmd_nombre, "%P"))
        self.e_nombre.pack(side="left")

        row_cedula = ctk.CTkFrame(left_panel, fg_color="#3B3B3B")
        row_cedula.pack(fill="x", pady=5)
        ctk.CTkLabel(row_cedula, text="Cedula:", text_color="#FFFFFF", font=("Arial", 11), width=80, anchor="w").pack(side="left")
        self.e_cedula = ctk.CTkEntry(row_cedula, font=("Arial", 11), width=260, validate="key", validatecommand=(vcmd_dig, "%P"))
        self.e_cedula.pack(side="left")

        row_telefono = ctk.CTkFrame(left_panel, fg_color="#3B3B3B")
        row_telefono.pack(fill="x", pady=5)
        ctk.CTkLabel(row_telefono, text="Telefono:", text_color="#FFFFFF", font=("Arial", 11), width=80, anchor="w").pack(side="left")
        self.e_telefono = ctk.CTkEntry(row_telefono, font=("Arial", 11), width=260, validate="key", validatecommand=(vcmd_dig, "%P"))
        self.e_telefono.pack(side="left")

        btn_row = ctk.CTkFrame(left_panel, fg_color="#3B3B3B")
        btn_row.pack(fill="x", pady=(30, 0))

        btn_h = 42
        ctk.CTkButton(btn_row, text="Ingresar", image=ico("inventario_registrar.png"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=120, height=btn_h, corner_radius=8,
                      command=self.ingresar_cliente).pack(side="left", padx=4)

        ctk.CTkButton(btn_row, text="Modificar", image=ico("inventario_editar.png"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=120, height=btn_h, corner_radius=8,
                      command=self.modificar_cliente).pack(side="left", padx=4)

        ctk.CTkButton(btn_row, text="Eliminar", image=ico("inventario_eliminar.png"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=120, height=btn_h, corner_radius=8,
                      command=self.eliminar_seleccionado).pack(side="left", padx=4)

        ctk.CTkButton(left_panel, text="Volver", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=360, height=32, corner_radius=6,
                      command=controller.show_panel).pack(pady=(25, 0))

        ctk.CTkFrame(left_panel, fg_color="#3B3B3B").pack(fill="both", expand=True)

        right_panel = ctk.CTkFrame(container, fg_color="#3B3B3B")
        right_panel.grid(row=0, column=1, sticky="nsew")

        search_frame = ctk.CTkFrame(right_panel, fg_color="#3B3B3B")
        search_frame.pack(fill="x", pady=(0, 10))

        self.entry_search = ctk.CTkEntry(search_frame, font=("Arial", 11), width=200, placeholder_text="Buscar cliente...")
        self.entry_search.pack(side="left", padx=(0, 5))
        self.entry_search.bind("<Return>", lambda e: self.buscar())

        ctk.CTkButton(search_frame, text="Buscar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=70, height=32, corner_radius=6,
                      command=self.buscar).pack(side="left")

        table_frame = ctk.CTkFrame(right_panel, fg_color="#777777", corner_radius=8)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("id", "Nombre", "Cedula", "Telefono")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                 yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        headers = ["ID", "Nombre", "Cedula", "Telefono"]
        widths = [60, 180, 130, 130]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.cargar_datos()

    def _on_select(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        valores = self.tree.item(seleccion[0], "values")
        self._id_seleccionado = valores[0]
        self.e_nombre.delete(0, ctk.END)
        self.e_nombre.insert(0, valores[1])
        self.e_cedula.delete(0, ctk.END)
        self.e_cedula.insert(0, valores[2])
        self.e_telefono.delete(0, ctk.END)
        self.e_telefono.insert(0, valores[3] if valores[3] else "")

    def cargar_datos(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if data is None:
            data = self.controller.model.obtener_clientes()
            self.all_data = data
        for c in data:
            self.tree.insert("", "end", values=(c["id_cliente"], c["nombre"], c["cedula"], c["telefono"]))

    def buscar(self):
        texto = self.entry_search.get().strip().lower()
        if not texto:
            self.cargar_datos(self.all_data)
            return
        filtrados = [item for item in self.all_data if texto in str(item["nombre"]).lower() or texto in str(item["cedula"])]
        self.cargar_datos(filtrados)

    def _limpiar_formulario(self):
        self.e_nombre.delete(0, ctk.END)
        self.e_cedula.delete(0, ctk.END)
        self.e_telefono.delete(0, ctk.END)
        self._id_seleccionado = None

    def ingresar_cliente(self):
        nombre = self.e_nombre.get().strip()
        cedula = self.e_cedula.get().strip()
        telefono = self.e_telefono.get().strip()
        if not nombre or not cedula:
            messagebox.showwarning("Aviso", "Nombre y Cedula son obligatorios")
            return
        if not (7 <= len(cedula) <= 8):
            messagebox.showwarning("Cedula invalida", "La cedula debe tener entre 7 y 8 digitos")
            return
        if self.controller.model.agregar_cliente(nombre, cedula, telefono):
            messagebox.showinfo("Exito", "Cliente registrado correctamente")
            self._limpiar_formulario()
            self.cargar_datos()

    def modificar_cliente(self):
        if not self._id_seleccionado:
            messagebox.showwarning("Seleccion requerida", "Seleccione un cliente de la tabla para modificar.")
            return
        nombre = self.e_nombre.get().strip()
        cedula = self.e_cedula.get().strip()
        telefono = self.e_telefono.get().strip()
        if not nombre or not cedula:
            messagebox.showwarning("Aviso", "Nombre y Cedula son obligatorios")
            return
        if not (7 <= len(cedula) <= 8):
            messagebox.showwarning("Cedula invalida", "La cedula debe tener entre 7 y 8 digitos")
            return
        if self.controller.model.actualizar_cliente(self._id_seleccionado, nombre, cedula, telefono):
            messagebox.showinfo("Exito", "Cliente actualizado correctamente")
            self._limpiar_formulario()
            self.cargar_datos()

    def eliminar_seleccionado(self):
        if not self._id_seleccionado:
            messagebox.showwarning("Seleccion requerida", "Seleccione un cliente de la tabla para eliminar.")
            return
        nombre = self.e_nombre.get().strip()
        confirmacion = messagebox.askyesno("Confirmar Eliminacion", f"Esta seguro que desea eliminar al cliente '{nombre}'?")
        if confirmacion:
            if self.controller.model.eliminar_cliente(self._id_seleccionado):
                messagebox.showinfo("Exito", "Cliente eliminado correctamente")
                self._limpiar_formulario()
                self.cargar_datos()

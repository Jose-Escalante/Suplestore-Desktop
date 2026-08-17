import os
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image


class InventarioView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self.all_data = []
        icons_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=35)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Inventario", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=15, pady=6)

        container = ctk.CTkFrame(self.root, fg_color="#3B3B3B")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        left_panel = ctk.CTkFrame(container, fg_color="#3B3B3B")
        left_panel.pack(side="left", fill="both", padx=(0, 15))

        def ico(name):
            for ext in (".png", ".PNG"):
                path = os.path.join(icons_dir, f"{name}{ext}")
                if os.path.exists(path):
                    return ctk.CTkImage(Image.open(path), size=(52, 52))
            return None

        btn_frame = ctk.CTkFrame(left_panel, fg_color="#3B3B3B")
        btn_frame.place(relx=0.5, rely=0.47, anchor="center")

        btn_size = 95

        ctk.CTkButton(btn_frame, text="Registrar", image=ico("inventario_registrar"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_registrar_producto).grid(row=0, column=0, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Editar", image=ico("inventario_editar"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_editar_producto).grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Eliminar", image=ico("inventario_eliminar"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.eliminar_producto).grid(row=1, column=0, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Ver lote", image=ico("inventario_ver_lote"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_ver_lotes).grid(row=1, column=1, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Historial\nlotes", image=ico("inventario_historial_lotes"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_historial_lotes).grid(row=2, column=0, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Actualizar\nlotes", image=ico("inventario_actualizar_lotes"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_actualizar_lote).grid(row=2, column=1, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Volver", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=202, height=28, corner_radius=6,
                      command=controller.show_panel).grid(row=3, column=0, columnspan=2, pady=(20, 0))

        right_panel = ctk.CTkFrame(container, fg_color="#3B3B3B")
        right_panel.pack(side="right", fill="both", expand=True)

        search_frame = ctk.CTkFrame(right_panel, fg_color="#3B3B3B")
        search_frame.pack(fill="x", pady=(0, 10))

        self.entry_search = ctk.CTkEntry(search_frame, font=("Arial", 11), width=200, placeholder_text="Buscar producto...")
        self.entry_search.pack(side="left", padx=(0, 5))
        self.entry_search.bind("<Return>", lambda e: self.buscar())

        self.lbl_sin_stock = ctk.CTkLabel(search_frame, text="", text_color="#FF5555", font=("Arial", 10, "bold"))
        self.lbl_sin_stock.pack(side="left", padx=(10, 0))

        ctk.CTkButton(search_frame, text="Buscar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=70, height=32, corner_radius=6,
                      command=self.buscar).pack(side="left")

        table_frame = ctk.CTkFrame(right_panel, fg_color="#777777", corner_radius=8)
        table_frame.pack(fill="both", expand=True)

        inner_frame = ctk.CTkFrame(table_frame, fg_color="#777777")
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)

        columns = ("id", "Producto", "Categoria", "Stock")
        self.tree = ttk.Treeview(inner_frame, columns=columns, show="headings", height=15)

        headers = ["ID", "Producto", "Categoria", "Stock"]
        widths = [60, 180, 140, 100]
        anchorings = ["w", "w", "w", "e"]
        for col, head, w, a in zip(columns, headers, widths, anchorings):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor=a)
        self.tree.tag_configure("sin_stock", foreground="#FF5555", font=("Arial", 9, "bold"))
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.cargar_datos()

    def cargar_datos(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if data is None:
            data = self.controller.model.obtener_inventario()
            self.all_data = data
        sin_stock = 0
        for item in data:
            stock = int(item["Stock"]) if str(item["Stock"]).isdigit() else 0
            if stock <= 0:
                sin_stock += 1
                self.tree.insert("", "end", values=(item["id"], item["Producto"], item["Categoria"], item["Stock"]),
                                 tags=("sin_stock",))
            else:
                self.tree.insert("", "end", values=(item["id"], item["Producto"], item["Categoria"], item["Stock"]))
        if sin_stock > 0:
            self.lbl_sin_stock.configure(text=f"{sin_stock} producto(s) sin stock")
        else:
            self.lbl_sin_stock.configure(text="")

    def buscar(self):
        texto = self.entry_search.get().strip().lower()
        if not texto:
            self.cargar_datos(self.all_data)
            return
        filtrados = [item for item in self.all_data if texto in str(item["Producto"]).lower() or texto in str(item["Categoria"]).lower()]
        self.cargar_datos(filtrados)

    def obtener_producto_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Por favor, seleccione un producto de la tabla primero.")
            return None
        valores = self.tree.item(seleccion[0], "values")
        return {"id": valores[0], "Producto": valores[1], "Categoria": valores[2], "Stock": valores[3]}

    def abrir_modal_registrar_producto(self):
        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Registrar Producto y Lote Inicial")
        modal.geometry("460x520")
        modal.configure(fg_color="#333333")

        categorias = self.controller.model.obtener_categorias()
        if not categorias:
            messagebox.showwarning("Aviso", "Primero debe registrar al menos una categoria en el modulo de Categorias.", parent=modal)
            modal.destroy()
            return

        cat_dict = {c["nombre_categoria"]: c["id_categoria"] for c in categorias}

        top_bar = ctk.CTkFrame(modal, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Registrar producto", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        body = ctk.CTkFrame(modal, fg_color="#333333")
        body.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(body, text="DATOS DEL PRODUCTO", text_color="#FFFFFF", font=("Arial", 12, "bold")).pack(pady=(0, 12))

        row_nombre = ctk.CTkFrame(body, fg_color="#333333")
        row_nombre.pack(fill="x", pady=4)
        ctk.CTkLabel(row_nombre, text="Nombre:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_nombre = ctk.CTkEntry(row_nombre, font=("Arial", 11), width=240)
        e_nombre.pack(side="left")

        row_cat = ctk.CTkFrame(body, fg_color="#333333")
        row_cat.pack(fill="x", pady=4)
        ctk.CTkLabel(row_cat, text="Categoria:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        combo_cat = ctk.CTkComboBox(row_cat, values=list(cat_dict.keys()), width=240, state="readonly")
        combo_cat.pack(side="left")
        combo_cat.set(list(cat_dict.keys())[0])

        ctk.CTkLabel(body, text="DATOS DEL LOTE INICIAL", text_color="#FFFFFF", font=("Arial", 12, "bold")).pack(pady=(18, 12))

        vcmd_int = modal.register(lambda P: P == "" or P.isdigit())
        vcmd_float = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))

        row_stock = ctk.CTkFrame(body, fg_color="#333333")
        row_stock.pack(fill="x", pady=4)
        ctk.CTkLabel(row_stock, text="Stock:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_stock = ctk.CTkEntry(row_stock, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_int, "%P"))
        e_stock.pack(side="left")

        row_costo = ctk.CTkFrame(body, fg_color="#333333")
        row_costo.pack(fill="x", pady=4)
        ctk.CTkLabel(row_costo, text="Costo del lote:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_costo = ctk.CTkEntry(row_costo, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_costo.pack(side="left")

        row_precio = ctk.CTkFrame(body, fg_color="#333333")
        row_precio.pack(fill="x", pady=4)
        ctk.CTkLabel(row_precio, text="Precio por unidad:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_venta = ctk.CTkEntry(row_precio, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_venta.pack(side="left")

        from tkcalendar import Calendar
        row_venc = ctk.CTkFrame(body, fg_color="#333333")
        row_venc.pack(fill="x", pady=4)
        ctk.CTkLabel(row_venc, text="Fecha de Vencimiento:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")

        venc_str = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        def abrir_calendario():
            cal_modal = ctk.CTkToplevel(modal)
            cal_modal.title("Seleccionar fecha")
            cal_modal.resizable(False, False)
            cal_modal.transient(modal)
            cal_modal.grab_set()
            cal = Calendar(cal_modal, selectmode="day", date_pattern="y-mm-dd",
                           year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                           background="#333333", foreground="white", headersbackground="#5CB85C", headersforeground="black",
                           normalbackground="#444444", normalforeground="white",
                           weekendforeground="white", weekendbackground="#555555",
                           selectbackground="#5CB85C", bordercolor="#333333")
            cal.pack(padx=10, pady=10)
            def seleccionar():
                venc_str.set(cal.get_date())
                btn_venc.configure(text=cal.get_date())
                cal_modal.destroy()
            ctk.CTkButton(cal_modal, text="Seleccionar", fg_color="#5CB85C", text_color="#000000",
                          font=("Arial", 10, "bold"), command=seleccionar).pack(pady=(0, 10))

        btn_venc = ctk.CTkButton(row_venc, text=venc_str.get(), fg_color="#444444", text_color="#FFFFFF",
                                 font=("Arial", 11), width=240, anchor="w", command=abrir_calendario)
        btn_venc.pack(side="left")

        btn_row = ctk.CTkFrame(body, fg_color="#333333")
        btn_row.pack(fill="x", pady=(20, 0))

        def guardar_prod():
            nombre = e_nombre.get().strip()
            cat_nombre = combo_cat.get()
            stock_str = e_stock.get().strip()
            costo_str = e_costo.get().strip()
            venta_str = e_venta.get().strip()
            venc = venc_str.get().strip()

            if not all([nombre, cat_nombre, stock_str, costo_str, venta_str, venc]):
                messagebox.showwarning("Aviso", "Todos los campos son obligatorios", parent=modal)
                return
            try:
                datetime.strptime(venc, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error de Fecha", "El formato debe ser AAAA-MM-DD", parent=modal)
                return
            try:
                stock = int(stock_str)
                costo = float(costo_str)
                venta = float(venta_str)
                if stock <= 0:
                    raise ValueError
                if venta < costo / stock:
                    messagebox.showerror("Precio invalido",
                                         f"El precio por unidad (${venta:.2f}) es menor al costo por unidad (${costo/stock:.2f}).\n"
                                         f"Esto generaria perdidas.",
                                         parent=modal)
                    return
            except ValueError:
                messagebox.showerror("Error", "Stock debe ser entero positivo, y costo/venta numericos", parent=modal)
                return

            if self.controller.model.registrar_producto_y_lote(nombre, cat_dict[cat_nombre], stock, costo, venta, venc):
                messagebox.showinfo("Exito", "Producto y lote registrados con exito", parent=modal)
                modal.destroy()
                self.cargar_datos()

        btn_inner = ctk.CTkFrame(btn_row, fg_color="transparent")
        btn_inner.pack(expand=True)

        ctk.CTkButton(btn_inner, text="Cancelar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=modal.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_inner, text="Guardar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=guardar_prod).pack(side="left", padx=6)

    def abrir_modal_editar_producto(self):
        prod = self.obtener_producto_seleccionado()
        if not prod:
            return

        categorias = self.controller.model.obtener_categorias()
        cat_dict = {c["nombre_categoria"]: c["id_categoria"] for c in categorias}

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title(f"Editar Producto")
        modal.geometry("380x280")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text=f"Editando: {prod['Producto']}", text_color="#FFFFFF",
                     font=("Arial", 12, "bold")).pack(pady=(15, 10))

        ctk.CTkLabel(modal, text="Nombre:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(5, 2))
        e_nombre = ctk.CTkEntry(modal, width=260, font=("Arial", 11))
        e_nombre.pack(padx=30)
        e_nombre.insert(0, prod["Producto"])

        ctk.CTkLabel(modal, text="Categoria:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(10, 2))
        combo_cat = ctk.CTkComboBox(modal, values=list(cat_dict.keys()), width=260, state="readonly")
        combo_cat.pack(padx=30)
        if prod["Categoria"] in cat_dict:
            combo_cat.set(prod["Categoria"])
        else:
            combo_cat.set(list(cat_dict.keys())[0])

        def guardar():
            nombre = e_nombre.get().strip()
            cat_nombre = combo_cat.get()
            if not nombre:
                messagebox.showwarning("Aviso", "El nombre es obligatorio", parent=modal)
                return
            if self.controller.model.actualizar_producto(prod["id"], nombre, cat_dict[cat_nombre]):
                messagebox.showinfo("Exito", "Producto actualizado correctamente", parent=modal)
                modal.destroy()
                self.cargar_datos()

        ctk.CTkButton(modal, text="Guardar Cambios", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), command=guardar).pack(pady=20)

    def eliminar_producto(self):
        prod = self.obtener_producto_seleccionado()
        if not prod:
            return
        confirmacion = messagebox.askyesno("Confirmar Eliminacion",
                                           f"Esta seguro que desea eliminar el producto '{prod['Producto']}'?\nSe eliminaran todos sus lotes asociados.")
        if confirmacion:
            if self.controller.model.eliminar_producto(prod["id"]):
                messagebox.showinfo("Exito", "Producto eliminado correctamente")
                self.cargar_datos()

    def abrir_modal_actualizar_lote(self):
        prod = self.obtener_producto_seleccionado()
        if not prod:
            return

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title(f"Agregar Lote a: {prod['Producto']}")
        modal.geometry("460x420")
        modal.configure(fg_color="#333333")

        top_bar = ctk.CTkFrame(modal, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Actualizar lote", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        body = ctk.CTkFrame(modal, fg_color="#333333")
        body.pack(fill="both", expand=True, padx=20, pady=10)

        row_prod = ctk.CTkFrame(body, fg_color="#333333")
        row_prod.pack(fill="x", pady=3)
        ctk.CTkLabel(row_prod, text="Producto:", text_color="#FFFFFF", font=("Arial", 11, "bold"), width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(row_prod, text=prod["Producto"], text_color="#FFFFFF", font=("Arial", 11)).pack(side="left")

        lotes = self.controller.model.obtener_lotes_por_producto(prod["id"])
        id_lote_anterior = lotes[-1]["id_lote"] if lotes else "N/A"
        row_lote = ctk.CTkFrame(body, fg_color="#333333")
        row_lote.pack(fill="x", pady=3)
        ctk.CTkLabel(row_lote, text="Lote anterior:", text_color="#FFFFFF", font=("Arial", 11, "bold"), width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(row_lote, text=str(id_lote_anterior), text_color="#FFFFFF", font=("Arial", 11)).pack(side="left")

        ctk.CTkLabel(body, text="DATOS DEL NUEVO LOTE", text_color="#FFFFFF", font=("Arial", 12, "bold")).pack(pady=(12, 8))

        vcmd_int = modal.register(lambda P: P == "" or P.isdigit())
        vcmd_float = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))

        row_stock = ctk.CTkFrame(body, fg_color="#333333")
        row_stock.pack(fill="x", pady=2)
        ctk.CTkLabel(row_stock, text="Stock:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_stock = ctk.CTkEntry(row_stock, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_int, "%P"))
        e_stock.pack(side="left")

        row_costo = ctk.CTkFrame(body, fg_color="#333333")
        row_costo.pack(fill="x", pady=2)
        ctk.CTkLabel(row_costo, text="Costo:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_costo = ctk.CTkEntry(row_costo, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_costo.pack(side="left")

        row_precio = ctk.CTkFrame(body, fg_color="#333333")
        row_precio.pack(fill="x", pady=2)
        ctk.CTkLabel(row_precio, text="Precio:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_venta = ctk.CTkEntry(row_precio, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_venta.pack(side="left")

        from tkcalendar import Calendar
        row_venc = ctk.CTkFrame(body, fg_color="#333333")
        row_venc.pack(fill="x", pady=2)
        ctk.CTkLabel(row_venc, text="Fecha de Vencimiento:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        venc_str = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        def abrir_calendario():
            cal_modal = ctk.CTkToplevel(modal)
            cal_modal.title("Seleccionar fecha")
            cal_modal.resizable(False, False)
            cal_modal.transient(modal)
            cal_modal.grab_set()
            cal = Calendar(cal_modal, selectmode="day", date_pattern="y-mm-dd",
                           year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                           background="#333333", foreground="white", headersbackground="#5CB85C", headersforeground="black",
                           normalbackground="#444444", normalforeground="white",
                           weekendforeground="white", weekendbackground="#555555",
                           selectbackground="#5CB85C", bordercolor="#333333")
            cal.pack(padx=10, pady=10)
            def seleccionar():
                venc_str.set(cal.get_date())
                btn_venc.configure(text=cal.get_date())
                cal_modal.destroy()
            ctk.CTkButton(cal_modal, text="Seleccionar", fg_color="#5CB85C", text_color="#000000",
                          font=("Arial", 10, "bold"), command=seleccionar).pack(pady=(0, 10))

        btn_venc = ctk.CTkButton(row_venc, text=venc_str.get(), fg_color="#444444", text_color="#FFFFFF",
                                 font=("Arial", 11), width=240, anchor="w", command=abrir_calendario)
        btn_venc.pack(side="left")

        btn_row = ctk.CTkFrame(body, fg_color="#333333")
        btn_row.pack(fill="x", pady=(12, 0))

        def guardar_nuevo_lote():
            stock_str = e_stock.get().strip()
            costo_str = e_costo.get().strip()
            venta_str = e_venta.get().strip()
            venc = venc_str.get().strip()

            if not all([stock_str, costo_str, venta_str, venc]):
                messagebox.showwarning("Aviso", "Complete todos los campos", parent=modal)
                return
            try:
                datetime.strptime(venc, "%Y-%m-%d")
                stock = int(stock_str)
                costo = float(costo_str)
                venta = float(venta_str)
                if stock <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Revise los formatos (Stock entero positivo, Costo/Venta numericos)", parent=modal)
                return

            if self.controller.model.agregar_lote_a_producto(prod["id"], stock, costo, venta, venc):
                messagebox.showinfo("Exito", "Lote agregado y stock actualizado correctamente", parent=modal)
                modal.destroy()
                self.cargar_datos()

        btn_inner = ctk.CTkFrame(btn_row, fg_color="transparent")
        btn_inner.pack(expand=True)
        ctk.CTkButton(btn_inner, text="Cancelar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=modal.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_inner, text="Guardar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=guardar_nuevo_lote).pack(side="left", padx=6)

    def abrir_modal_ver_lotes(self):
        prod = self.obtener_producto_seleccionado()
        if not prod:
            return

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title(f"Lotes - {prod['Producto']}")
        modal.geometry("600x400")
        modal.configure(fg_color="#333333")

        top_bar = ctk.CTkFrame(modal, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text=f"Lotes de: {prod['Producto']}", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        frame_t = ctk.CTkFrame(modal, fg_color="transparent")
        frame_t.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id_lote", "stock", "costo", "precio", "vencimiento", "estado")
        tree = ttk.Treeview(frame_t, columns=columns, show="headings", height=8)

        headers = ["ID Lote", "Stock", "Costo ($)", "Precio ($)", "Vencimiento", "Estado"]
        for col, head in zip(columns, headers):
            tree.heading(col, text=head)
            tree.column(col, width=90, anchor="w")
        tree.pack(fill="both", expand=True)

        lotes = self.controller.model.obtener_lotes_por_producto(prod["id"])
        for l in lotes:
            tree.insert("", "end", values=(l["id_lote"], l["stock"], l["costo"], l["precio"], l["fecha_vencimiento"], l["estado"]))

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Editar lote", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100,
                      command=lambda: self.abrir_modal_editar_lote(tree, prod, modal)).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cerrar", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=modal.destroy).pack(side="left", padx=6)

    def abrir_modal_editar_lote(self, tree_orig, prod_orig, modal_orig):
        seleccion = tree_orig.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Seleccione un lote de la tabla primero.", parent=modal_orig)
            return
        vals = tree_orig.item(seleccion[0], "values")
        lote = {"id_lote": vals[0], "stock": vals[1], "costo": vals[2], "precio": vals[3], "vencimiento": vals[4]}

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title(f"Editar Lote #{lote['id_lote']}")
        modal.geometry("460x420")
        modal.configure(fg_color="#333333")

        top_bar = ctk.CTkFrame(modal, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text=f"Editar Lote #{lote['id_lote']}", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        body = ctk.CTkFrame(modal, fg_color="#333333")
        body.pack(fill="both", expand=True, padx=20, pady=10)

        row_prod = ctk.CTkFrame(body, fg_color="#333333")
        row_prod.pack(fill="x", pady=3)
        ctk.CTkLabel(row_prod, text="Producto:", text_color="#FFFFFF", font=("Arial", 11, "bold"), width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(row_prod, text=prod_orig["Producto"], text_color="#FFFFFF", font=("Arial", 11)).pack(side="left")

        ctk.CTkLabel(body, text="DATOS DEL LOTE", text_color="#FFFFFF", font=("Arial", 12, "bold")).pack(pady=(12, 8))

        vcmd_int = modal.register(lambda P: P == "" or P.isdigit())
        vcmd_float = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))

        row_stock = ctk.CTkFrame(body, fg_color="#333333")
        row_stock.pack(fill="x", pady=2)
        ctk.CTkLabel(row_stock, text="Stock:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_stock = ctk.CTkEntry(row_stock, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_int, "%P"))
        e_stock.pack(side="left")
        e_stock.insert(0, lote["stock"])

        row_costo = ctk.CTkFrame(body, fg_color="#333333")
        row_costo.pack(fill="x", pady=2)
        ctk.CTkLabel(row_costo, text="Costo:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_costo = ctk.CTkEntry(row_costo, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_costo.pack(side="left")
        e_costo.insert(0, lote["costo"])

        row_precio = ctk.CTkFrame(body, fg_color="#333333")
        row_precio.pack(fill="x", pady=2)
        ctk.CTkLabel(row_precio, text="Precio:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        e_precio = ctk.CTkEntry(row_precio, font=("Arial", 11), width=240, validate="key", validatecommand=(vcmd_float, "%P"))
        e_precio.pack(side="left")
        e_precio.insert(0, lote["precio"])

        from tkcalendar import Calendar
        row_venc = ctk.CTkFrame(body, fg_color="#333333")
        row_venc.pack(fill="x", pady=2)
        ctk.CTkLabel(row_venc, text="Fecha de Vencimiento:", text_color="#FFFFFF", font=("Arial", 11), width=110, anchor="w").pack(side="left")
        venc_str = ctk.StringVar(value=lote["vencimiento"])

        def abrir_calendario():
            cal_modal = ctk.CTkToplevel(modal)
            cal_modal.title("Seleccionar fecha")
            cal_modal.resizable(False, False)
            cal_modal.transient(modal)
            cal_modal.grab_set()
            cal = Calendar(cal_modal, selectmode="day", date_pattern="y-mm-dd",
                           year=int(lote["vencimiento"][:4]), month=int(lote["vencimiento"][5:7]), day=int(lote["vencimiento"][8:10]),
                           background="#333333", foreground="white", headersbackground="#5CB85C", headersforeground="black",
                           normalbackground="#444444", normalforeground="white",
                           weekendforeground="white", weekendbackground="#555555",
                           selectbackground="#5CB85C", bordercolor="#333333")
            cal.pack(padx=10, pady=10)
            def seleccionar():
                venc_str.set(cal.get_date())
                btn_venc.configure(text=cal.get_date())
                cal_modal.destroy()
            ctk.CTkButton(cal_modal, text="Seleccionar", fg_color="#5CB85C", text_color="#000000",
                          font=("Arial", 10, "bold"), command=seleccionar).pack(pady=(0, 10))

        btn_venc = ctk.CTkButton(row_venc, text=venc_str.get(), fg_color="#444444", text_color="#FFFFFF",
                                 font=("Arial", 11), width=240, anchor="w", command=abrir_calendario)
        btn_venc.pack(side="left")

        btn_row = ctk.CTkFrame(body, fg_color="#333333")
        btn_row.pack(fill="x", pady=(12, 0))

        def guardar_cambios():
            stock_str = e_stock.get().strip()
            costo_str = e_costo.get().strip()
            precio_str = e_precio.get().strip()
            venc = venc_str.get().strip()

            if not all([stock_str, costo_str, precio_str, venc]):
                messagebox.showwarning("Aviso", "Complete todos los campos", parent=modal)
                return
            try:
                datetime.strptime(venc, "%Y-%m-%d")
                stock = int(stock_str)
                costo = float(costo_str)
                precio = float(precio_str)
                if stock <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Revise los formatos (Stock entero positivo, Costo/Precio numericos)", parent=modal)
                return

            if self.controller.model.actualizar_lote(int(lote["id_lote"]), stock, costo, precio, venc):
                messagebox.showinfo("Exito", "Lote actualizado correctamente", parent=modal)
                modal.destroy()
                modal_orig.destroy()
                self.abrir_modal_ver_lotes()

        btn_inner = ctk.CTkFrame(btn_row, fg_color="transparent")
        btn_inner.pack(expand=True)
        ctk.CTkButton(btn_inner, text="Cancelar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=modal.destroy).pack(side="left", padx=6)
        ctk.CTkButton(btn_inner, text="Guardar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=guardar_cambios).pack(side="left", padx=6)

    def abrir_modal_historial_lotes(self):
        prod = self.obtener_producto_seleccionado()
        if not prod:
            return

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title(f"Historial de Lotes - {prod['Producto']}")
        modal.geometry("600x350")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text=f"Historial de Lotes: {prod['Producto']}", text_color="#FFFFFF",
                     font=("Arial", 12, "bold")).pack(pady=10)

        frame_t = ctk.CTkFrame(modal, fg_color="transparent")
        frame_t.pack(fill="both", expand=True, padx=15, pady=10)

        columns = ("id_lote", "stock", "costo", "precio", "vencimiento", "estado")
        tree = ttk.Treeview(frame_t, columns=columns, show="headings", height=8)

        headers = ["ID Lote", "Stock", "Costo ($)", "Precio ($)", "Vencimiento", "Estado"]
        for col, head in zip(columns, headers):
            tree.heading(col, text=head)
            tree.column(col, width=90, anchor="w")
        tree.pack(fill="both", expand=True)

        lotes = self.controller.model.obtener_lotes_por_producto(prod["id"])
        for l in lotes:
            tree.insert("", "end", values=(l["id_lote"], l["stock"], l["costo"], l["precio"], l["fecha_vencimiento"], l["estado"]))

        ctk.CTkButton(modal, text="Cerrar", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), command=modal.destroy).pack(pady=10)

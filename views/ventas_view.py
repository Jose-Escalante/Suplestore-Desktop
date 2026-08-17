import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from datetime import datetime
from services.nota_entrega import generar_nota_entrega
from services.excel_export import exportar_ventas_xlsx


class VentasView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        self.carrito_items = []

        icons_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        def ico(name, size=24):
            path = os.path.join(icons_dir, name)
            if os.path.exists(path):
                return ctk.CTkImage(Image.open(path), size=(size, size))
            return None

        def ico_big(name):
            return ico(name, 36)

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Ventas", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        container = ctk.CTkFrame(self.root, fg_color="#333333")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        controls_frame = ctk.CTkFrame(container, fg_color="#333333")
        controls_frame.pack(fill="x", pady=(0, 10))

        col_a = ctk.CTkFrame(controls_frame, fg_color="#333333")
        col_a.pack(side="left", fill="y", padx=(0, 15))

        row_cliente = ctk.CTkFrame(col_a, fg_color="#333333")
        row_cliente.pack(fill="x", pady=4)
        ctk.CTkLabel(row_cliente, text="Cliente:", text_color="#FFFFFF", font=("Arial", 11), width=62, anchor="w").pack(side="left", padx=(0, 5), fill="y")

        clientes_raw = controller.model.obtener_clientes()
        self.clientes_list = [(f"{c['nombre']} ({c['cedula']})", c['id_cliente'], c) for c in clientes_raw]
        self.clientes_data = {c['id_cliente']: c for c in clientes_raw}
        self.cliente_id_seleccionado = None

        self.cliente_frame = ctk.CTkFrame(row_cliente, fg_color="#333333")
        self.cliente_frame.pack(side="left", fill="y")

        self.entry_cliente = ctk.CTkEntry(self.cliente_frame, font=("Arial", 11), width=240)
        self.entry_cliente.pack(fill="x", expand=True)

        self.sugerencias_frame = None
        self.entry_cliente.bind("<KeyRelease>", self._filtrar_clientes)
        self.entry_cliente.bind("<FocusOut>", lambda e: self.root.after(200, self._ocultar_sugerencias))

        row_producto = ctk.CTkFrame(col_a, fg_color="#333333")
        row_producto.pack(fill="x", pady=4)
        ctk.CTkLabel(row_producto, text="Producto:", text_color="#FFFFFF", font=("Arial", 11), width=62, anchor="w").pack(side="left", padx=(0, 5), fill="y")
        self.inventario_lista = controller.model.obtener_inventario()
        self.productos_dict = {f"{item['Producto']} (Stock: {item['Stock']})": item for item in self.inventario_lista}
        self.id_to_stock = {item['id']: int(item['Stock']) for item in self.inventario_lista}
        self.combo_productos = ctk.CTkComboBox(row_producto, values=list(self.productos_dict.keys()), width=240, state="readonly",
                                                font=("Arial", 11), command=self._on_producto_selected)
        self.combo_productos.pack(side="left", fill="y")
        if self.productos_dict:
            self.combo_productos.set(list(self.productos_dict.keys())[0])

        col_b = ctk.CTkFrame(controls_frame, fg_color="#333333")
        col_b.pack(side="left", fill="y", padx=(0, 15))

        row_cant = ctk.CTkFrame(col_b, fg_color="#333333")
        row_cant.pack(fill="x", pady=4)
        ctk.CTkLabel(row_cant, text="Cantidad:", text_color="#FFFFFF", font=("Arial", 11), width=62, anchor="w").pack(side="left", padx=(0, 8), fill="y")
        vcmd_cant = self.root.register(lambda P: P == "" or P.isdigit())
        self.entry_cant = ctk.CTkEntry(row_cant, width=90, font=("Arial", 12), validate="key", validatecommand=(vcmd_cant, "%P"))
        self.entry_cant.pack(side="left")
        self.entry_cant.insert(0, "1")

        row_stock = ctk.CTkFrame(col_b, fg_color="#333333")
        row_stock.pack(fill="x", pady=4)
        self.lbl_stock = ctk.CTkLabel(row_stock, text="Stock: ---", text_color="#FFFFFF", font=("Arial", 12, "bold"))
        self.lbl_stock.pack(side="left")
        self._actualizar_stock_label()

        col_c = ctk.CTkFrame(controls_frame, fg_color="#333333")
        col_c.pack(side="left", fill="y", padx=(0, 15))

        btn_sq = 64
        ctk.CTkButton(col_c, text="Agregar", image=ico_big("ventas_agregar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_sq, height=btn_sq, corner_radius=8,
                      command=self.agregar_item).pack(side="left", padx=5)

        ctk.CTkButton(col_c, text="Editar", image=ico_big("inventario_editar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_sq, height=btn_sq, corner_radius=8,
                      command=self.editar_item).pack(side="left", padx=5)

        ctk.CTkButton(col_c, text="Eliminar", image=ico_big("usuarios_eliminar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_sq, height=btn_sq, corner_radius=8,
                      command=self.quitar_item).pack(side="left", padx=5)

        col_d = ctk.CTkFrame(controls_frame, fg_color="#333333")
        col_d.pack(side="right", fill="y")

        cajero_nombre = controller.usuario_actual['usuario'] if controller.usuario_actual else "usuario"
        ctk.CTkLabel(col_d, text=f"Cajero: {cajero_nombre}", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="e", pady=3)
        siguiente_nota = controller.model.obtener_siguiente_numero_control()
        ctk.CTkLabel(col_d, text=f"Nota: {siguiente_nota}", text_color="#5CB85C",
                     font=("Arial", 11, "bold")).pack(anchor="e", pady=3)

        table_container = ctk.CTkFrame(container, fg_color="#777777", corner_radius=8)
        table_container.pack(fill="both", expand=True, pady=8)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns_cart = ("Producto", "Precio Unit.", "Cantidad", "Descuento", "Subtotal")
        self.tree_carrito = ttk.Treeview(table_container, columns=columns_cart, show="headings", height=8,
                                         yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree_carrito.yview)

        widths = [240, 130, 80, 100, 130]
        for col, w in zip(columns_cart, widths):
            self.tree_carrito.heading(col, text=col)
            self.tree_carrito.column(col, width=w, anchor="center")
        self.tree_carrito.pack(fill="both", expand=True, padx=8, pady=8)

        footer_frame = ctk.CTkFrame(container, fg_color="#333333")
        footer_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(footer_frame, text="Pagar", image=ico("ventas_pagar.png"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 12, "bold"),
                      width=150, height=42, corner_radius=8,
                      command=self.abrir_modal_pagar).pack(side="left", padx=5)

        ctk.CTkButton(footer_frame, text="Ver Ventas", image=ico("ventas_ver_ventas.png"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 12, "bold"),
                      width=150, height=42, corner_radius=8,
                      command=self.abrir_modal_historial).pack(side="left", padx=5)

        ctk.CTkButton(footer_frame, text="Descuento Item", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=120, height=36, corner_radius=8,
                      command=self.descuento_item).pack(side="left", padx=5)

        total_frame = ctk.CTkFrame(footer_frame, fg_color="#333333")
        total_frame.pack(side="right", padx=10)

        ico_precio = ico("ventas_precio.png")
        if ico_precio:
            ctk.CTkLabel(total_frame, image=ico_precio, text="").pack(side="left", padx=(0, 5))
        self.lbl_total = ctk.CTkLabel(total_frame, text="Precio a Pagar: $0.00", text_color="#FFFFFF",
                                      font=("Arial", 16, "bold"))
        self.lbl_total.pack(side="left", padx=5)

        ctk.CTkButton(footer_frame, text="Volver", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 11, "bold"), width=120, height=36,
                      command=controller.show_panel).pack(side="right", padx=10)

    def _filtrar_clientes(self, event=None):
        texto = self.entry_cliente.get().strip().lower()
        self._ocultar_sugerencias()

        if not texto:
            self.cliente_id_seleccionado = None
            return

        coincidencias = [item for item in self.clientes_list
                         if texto in item[0].lower() or texto in item[2]["cedula"]]
        if not coincidencias:
            self.cliente_id_seleccionado = None
            return

        self.sugerencias_frame = ctk.CTkFrame(self.cliente_frame, fg_color="#555555", corner_radius=4)
        self.sugerencias_frame.pack(fill="x", pady=(2, 0))

        for label, cid, cdata in coincidencias[:8]:
            btn = ctk.CTkButton(self.sugerencias_frame, text=label, fg_color="#555555",
                                text_color="#FFFFFF", font=("Arial", 10), anchor="w",
                                hover_color="#5CB85C", command=lambda lid=cid, lbl=label, cd=cdata: self._seleccionar_cliente(lid, lbl, cd))
            btn.pack(fill="x", padx=2, pady=1)

    def _seleccionar_cliente(self, cid, label, cdata):
        self.cliente_id_seleccionado = cid
        self.entry_cliente.delete(0, ctk.END)
        self.entry_cliente.insert(0, label)
        self._ocultar_sugerencias()

    def _ocultar_sugerencias(self):
        if self.sugerencias_frame is not None:
            self.sugerencias_frame.destroy()
            self.sugerencias_frame = None

    def _on_producto_selected(self, valor):
        self._actualizar_stock_label()

    def _actualizar_stock_label(self):
        seleccion = self.combo_productos.get()
        if seleccion and seleccion in self.productos_dict:
            item = self.productos_dict[seleccion]
            if int(item['Stock']) <= 0:
                self.lbl_stock.configure(text="Stock: 0 (AGOTADO)", text_color="#FF5555")
            else:
                self.lbl_stock.configure(text=f"Stock: {item['Stock']}", text_color="#FFFFFF")

    def agregar_item(self):
        seleccion_prod = self.combo_productos.get()
        if not seleccion_prod or seleccion_prod not in self.productos_dict:
            messagebox.showwarning("Seleccion", "Seleccione un producto valido.")
            return

        item_db = self.productos_dict[seleccion_prod]
        stock_disp = int(item_db['Stock'])

        if stock_disp <= 0:
            messagebox.showerror("Producto sin stock", f"El producto '{item_db['Producto']}' no tiene stock disponible.")
            return

        try:
            cantidad = int(self.entry_cant.get().strip())
            if cantidad <= 0 or cantidad > stock_disp:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", f"Cantidad invalida o supera el stock disponible ({stock_disp}).")
            return

        lotes = self.controller.model.obtener_lotes_por_producto(item_db['id'])
        precio = float(lotes[0]['precio']) if lotes else 0.0
        subtotal = cantidad * precio

        encontrado = False
        for item in self.carrito_items:
            if item["id_producto"] == item_db['id']:
                if item["cantidad"] + cantidad > stock_disp:
                    messagebox.showwarning("Stock Insuficiente", "La cantidad total excede el stock disponible.")
                    return
                item["cantidad"] += cantidad
                item["subtotal"] = item["cantidad"] * item["precio"] - item.get("descuento", 0.0)
                encontrado = True
                break

        if not encontrado:
            self.carrito_items.append({
                "id_producto": item_db['id'],
                "nombre": item_db['Producto'],
                "cantidad": cantidad,
                "precio": precio,
                "descuento": 0.0,
                "subtotal": subtotal
            })

        self.actualizar_vista_carrito()
        self.entry_cant.delete(0, ctk.END)
        self.entry_cant.insert(0, "1")

    def editar_item(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion", "Seleccione un producto del carrito para editar su cantidad.")
            return

        index = self.tree_carrito.index(seleccion[0])
        item_actual = self.carrito_items[index]

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Editar Cantidad")
        modal.geometry("300x160")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text=f"Producto: {item_actual['nombre']}", text_color="#FFFFFF",
                     font=("Arial", 10, "bold")).pack(pady=10)
        ctk.CTkLabel(modal, text="Nueva Cantidad:", text_color="#FFFFFF").pack()

        vcmd_int = modal.register(lambda P: P == "" or P.isdigit())
        e_nueva_cant = ctk.CTkEntry(modal, font=("Arial", 11), width=100, validate="key", validatecommand=(vcmd_int, "%P"))
        e_nueva_cant.pack(pady=5)
        e_nueva_cant.insert(0, str(item_actual['cantidad']))

        def guardar_cambio():
            try:
                nueva_cant = int(e_nueva_cant.get().strip())
                if nueva_cant <= 0:
                    raise ValueError()
                stock_disp = self.id_to_stock.get(item_actual['id_producto'], 0)
                if nueva_cant > stock_disp:
                    messagebox.showwarning("Stock Insuficiente",
                                           f"La cantidad supera el stock disponible ({stock_disp}).", parent=modal)
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad valida mayor a cero.", parent=modal)
                return
            item_actual['cantidad'] = nueva_cant
            item_actual['subtotal'] = nueva_cant * item_actual['precio'] - item_actual.get('descuento', 0.0)
            self.actualizar_vista_carrito()
            modal.destroy()

        ctk.CTkButton(modal, text="Guardar Cambios", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 9, "bold"), command=guardar_cambio).pack(pady=10)

    def quitar_item(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion", "Seleccione un producto del carrito para eliminar.")
            return
        index = self.tree_carrito.index(seleccion[0])
        del self.carrito_items[index]
        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        for row in self.tree_carrito.get_children():
            self.tree_carrito.delete(row)

        total_general = 0
        for item in self.carrito_items:
            desc = item.get("descuento", 0.0)
            self.tree_carrito.insert("", "end", values=(
                item["nombre"],
                f"${item['precio']:.2f}",
                item["cantidad"],
                f"${desc:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total_general += item["subtotal"]

        self.lbl_total.configure(text=f"Precio a Pagar: ${total_general:.2f}")

    def descuento_item(self):
        seleccion = self.tree_carrito.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion", "Seleccione un producto del carrito para aplicarle un descuento.")
            return
        index = self.tree_carrito.index(seleccion[0])
        item_actual = self.carrito_items[index]
        base = item_actual["cantidad"] * item_actual["precio"]

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Descuento por Producto")
        modal.geometry("320x240")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text=f"Producto: {item_actual['nombre']}", text_color="#FFFFFF",
                     font=("Arial", 10, "bold"), wraplength=280).pack(pady=(15, 8))
        ctk.CTkLabel(modal, text=f"Subtotal base: ${base:.2f}", text_color="#5CB85C",
                     font=("Arial", 11, "bold")).pack(pady=(0, 8))

        combo_tipo = ctk.CTkComboBox(modal, values=["Porcentaje (%)", "Monto ($)"], width=200, state="readonly")
        combo_tipo.pack(pady=5)
        combo_tipo.set("Porcentaje (%)")

        vcmd = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))
        e_valor = ctk.CTkEntry(modal, font=("Arial", 11), width=150, validate="key", validatecommand=(vcmd, "%P"))
        e_valor.pack(pady=5)
        e_valor.insert(0, "0")

        def aplicar():
            try:
                valor = float(e_valor.get().strip())
                if valor < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor de descuento valido.", parent=modal)
                return
            if combo_tipo.get() == "Porcentaje (%)":
                if valor > 100:
                    messagebox.showerror("Error", "El porcentaje no puede superar 100%.", parent=modal)
                    return
                desc = round(base * valor / 100, 2)
            else:
                desc = round(valor, 2)
            if desc > base:
                desc = base
            item_actual["descuento"] = desc
            item_actual["subtotal"] = round(base - desc, 2)
            self.actualizar_vista_carrito()
            modal.destroy()

        ctk.CTkButton(modal, text="Aplicar Descuento", fg_color="#E0A800", text_color="#000000",
                      font=("Arial", 10, "bold"), command=aplicar).pack(pady=12)

    def abrir_modal_pagar(self):
        if not self.carrito_items:
            messagebox.showwarning("Carrito Vacio", "No hay productos en el carrito para procesar el pago.")
            return

        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Procesar Pago y Nota de Entrega")
        modal.geometry("380x360")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Seleccione Metodo de Pago", text_color="#FFFFFF",
                     font=("Arial", 12, "bold")).pack(pady=10)

        combo_metodo = ctk.CTkComboBox(modal, values=["Efectivo ($)", "Punto de Venta", "Pago Movil"],
                                       width=260, state="readonly", font=("Arial", 11))
        combo_metodo.pack(pady=5)
        combo_metodo.set("Efectivo ($)")

        total_base = sum(item["subtotal"] for item in self.carrito_items)
        ctk.CTkLabel(modal, text=f"Total a cancelar: ${total_base:.2f}", text_color="#5CB85C",
                     font=("Arial", 12, "bold")).pack(pady=5)

        desc_frame = ctk.CTkFrame(modal, fg_color="#333333")
        desc_frame.pack(fill="x", padx=40, pady=(2, 5))
        ctk.CTkLabel(desc_frame, text="Descuento global:", text_color="#FFFFFF", font=("Arial", 10)).pack(anchor="w", padx=(40, 0))
        dl_inner = ctk.CTkFrame(desc_frame, fg_color="#333333")
        dl_inner.pack(fill="x", padx=(40, 0), pady=(3, 0))
        combo_desc_tipo = ctk.CTkComboBox(dl_inner, values=["Porcentaje (%)", "Monto ($)"], width=110, state="readonly")
        combo_desc_tipo.pack(side="left", padx=(0, 8))
        combo_desc_tipo.set("Porcentaje (%)")
        vcmd_desc = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))
        entry_desc = ctk.CTkEntry(dl_inner, font=("Arial", 12), width=130, validate="key", validatecommand=(vcmd_desc, "%P"))
        entry_desc.pack(side="left")
        entry_desc.insert(0, "0")

        ctk.CTkLabel(modal, text="Monto Cancelado ($):", text_color="#FFFFFF",
                     font=("Arial", 10)).pack(anchor="w", padx=40, pady=(10, 2))
        vcmd_monto = modal.register(lambda P: P == "" or (P.replace(".", "", 1).isdigit() and P.count(".") <= 1))
        entry_monto = ctk.CTkEntry(modal, font=("Arial", 12), width=200, validate="key", validatecommand=(vcmd_monto, "%P"))
        entry_monto.pack(padx=40)
        entry_monto.insert(0, f"{total_base:.2f}")

        def confirmar_pago():
            if self.cliente_id_seleccionado is None:
                messagebox.showwarning("Cliente", "Seleccione un cliente valido.", parent=modal)
                return
            try:
                desc_val = float(entry_desc.get().strip())
                if desc_val < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese un descuento valido.", parent=modal)
                return
            if combo_desc_tipo.get() == "Porcentaje (%)":
                if desc_val > 100:
                    messagebox.showerror("Error", "El porcentaje de descuento no puede superar 100%.", parent=modal)
                    return
                descuento = round(total_base * desc_val / 100, 2)
            else:
                descuento = round(min(desc_val, total_base), 2)
            total_final = round(total_base - descuento, 2)

            try:
                monto_cancelado = float(entry_monto.get().strip())
                if monto_cancelado < total_final:
                    messagebox.showwarning("Monto Insuficiente", "El monto cancelado es menor al total a pagar.", parent=modal)
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto cancelado valido.", parent=modal)
                return

            id_cliente = self.cliente_id_seleccionado
            metodo_pago = combo_metodo.get()
            id_usuario = self.controller.usuario_actual["id_usuario"]

            resultado = self.controller.model.registrar_venta_y_nota(
                id_usuario, id_cliente, metodo_pago, total_final, monto_cancelado, self.carrito_items, descuento
            )
            if resultado:
                detalle_evento = f"Venta registrada: Nota {resultado['numero_control']} por ${total_final:.2f}"
                if descuento > 0:
                    detalle_evento += f" (descuento ${descuento:.2f})"
                self.controller.registrar_evento("venta", detalle_evento)
                cl_data = self.clientes_data.get(id_cliente, {})
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                datos_nota = {
                    "empresa": "Suplestore Tachira",
                    "direccion": "Centro Comercial Boulevard\nLos Mangos, Local 34, Barrio\nObrero. San Cristobal, Estado\nTachira.",
                    "num_nota": resultado["numero_control"],
                    "fecha": fecha_actual,
                    "cliente": cl_data.get("nombre", ""),
                    "ci": cl_data.get("cedula", ""),
                    "telefono": cl_data.get("telefono", ""),
                    "metodo_pago": metodo_pago,
                    "total": total_final,
                    "descuento": descuento,
                    "total_cancelado": monto_cancelado,
                    "items": [{"descripcion": it["nombre"], "cantidad": it["cantidad"],
                               "precio": it["precio"], "subtotal": it["subtotal"]}
                              for it in self.carrito_items]
                }
                ruta_pdf = generar_nota_entrega(datos_nota)
                os.startfile(ruta_pdf)
                vuelto = monto_cancelado - total_final
                messagebox.showinfo("Exito", f"Nota de Entrega registrada con exito.\nN de Nota: {resultado['numero_control']}\nVuelto: ${vuelto:.2f}", parent=modal)
                modal.destroy()
                self.controller.show_ventas()

        ctk.CTkButton(modal, text="Confirmar y Pagar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 11, "bold"), width=200, command=confirmar_pago).pack(pady=20)

    def abrir_modal_historial(self):
        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Historial de Notas de Entrega")
        modal.geometry("860x520")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Historial de Notas de Entrega", text_color="#FFFFFF",
                     font=("Arial", 12, "bold")).pack(pady=(10, 5))

        search_row = ctk.CTkFrame(modal, fg_color="#333333")
        search_row.pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkLabel(search_row, text="Cedula:", text_color="#FFFFFF", font=("Arial", 11)).pack(side="left", padx=(0, 5))
        entry_cedula = ctk.CTkEntry(search_row, font=("Arial", 11), width=180)
        entry_cedula.pack(side="left", padx=(0, 5))
        lbl_consulta = ctk.CTkLabel(search_row, text="", text_color="#5CB85C", font=("Arial", 11, "bold"))
        lbl_consulta.pack(side="left", padx=15)

        def _poblar(treeview, ventas):
            for row in treeview.get_children():
                treeview.delete(row)
            for v in ventas:
                desc = v.get("descuento", 0) or 0
                treeview.insert("", "end", iid=str(v["id_venta"]), values=(
                    v["numero_control"], v["cliente"], v["vendedor"], v["metodo_pago"],
                    f"${v['total']:.2f}", f"${desc:.2f}" if desc else "-",
                    f"${v['monto_cancelado']:.2f}", v["fecha"]
                ))

        def exportar_excel():
            ruta = filedialog.asksaveasfilename(parent=modal, defaultextension=".xlsx",
                                                filetypes=[("Excel", "*.xlsx")],
                                                initialfile=f"ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            if not ruta:
                return
            filas = [tree.item(row, "values") for row in tree.get_children()]
            filas = [list(f) for f in filas]
            for f in filas:
                f[4] = f[4].replace("$", "")
                f[5] = 0 if f[5] == "-" else f[5].replace("$", "")
                f[6] = f[6].replace("$", "")
            exportar_ventas_xlsx(ruta, headers, filas)
            messagebox.showinfo("Exito", f"Ventas exportadas en:\n{ruta}", parent=modal)

        def buscar_por_cedula():
            cedula = entry_cedula.get().strip()
            if not cedula:
                messagebox.showwarning("Aviso", "Ingrese una cedula para buscar.", parent=modal)
                return
            cliente = self.controller.model.buscar_cliente_por_cedula(cedula)
            if not cliente:
                messagebox.showinfo("Sin resultados", "No existe un cliente con esa cedula.", parent=modal)
                return
            ventas = self.controller.model.obtener_historial_por_cliente(cliente["id_cliente"])
            _poblar(tree, ventas)
            lbl_consulta.configure(text=f"Cliente: {cliente['nombre']}")

        def ver_todos():
            ventas = self.controller.model.obtener_historial_ventas()
            _poblar(tree, ventas)
            lbl_consulta.configure(text="")

        ctk.CTkButton(search_row, text="Buscar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=70, height=28, corner_radius=6,
                      command=buscar_por_cedula).pack(side="left", padx=5)
        ctk.CTkButton(search_row, text="Ver Todos", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), width=90, height=28, corner_radius=6,
                      command=ver_todos).pack(side="left", padx=5)

        frame_t = ctk.CTkFrame(modal, fg_color="transparent")
        frame_t.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("id", "cliente", "vendedor", "pago", "total", "descuento", "cancelado", "fecha")
        tree = ttk.Treeview(frame_t, columns=columns, show="headings", height=12)

        headers = ["N Nota", "Cliente", "Vendedor", "Metodo Pago", "Total ($)", "Descuento ($)", "Cancelado ($)", "Fecha y Hora"]
        widths = [90, 120, 90, 95, 85, 95, 95, 140]
        for col, head, w in zip(columns, headers, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="center")
        tree.pack(fill="both", expand=True)

        _poblar(tree, self.controller.model.obtener_historial_ventas())

        def ver_detalles():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Seleccion", "Por favor seleccione una nota de entrega para ver sus detalles.", parent=modal)
                return
            id_nota = int(seleccion[0])

            modal_det = ctk.CTkToplevel(modal)
            modal_det.resizable(False, False)
            modal_det.title(f"Detalles de Nota {id_nota}")
            modal_det.geometry("550x300")
            modal_det.configure(fg_color="#333333")

            ctk.CTkLabel(modal_det, text=f"Productos de la Nota de Entrega {id_nota}",
                         text_color="#FFFFFF", font=("Arial", 11, "bold")).pack(pady=10)

            f_dt = ctk.CTkFrame(modal_det, fg_color="transparent")
            f_dt.pack(fill="both", expand=True, padx=15, pady=5)

            cols_det = ("producto", "precio", "cantidad", "subtotal")
            tree_det = ttk.Treeview(f_dt, columns=cols_det, show="headings", height=6)
            headers_det = ["Producto", "Precio Unit. ($)", "Cantidad", "Subtotal ($)"]
            widths_det = [200, 100, 90, 100]
            for c, h, w in zip(cols_det, headers_det, widths_det):
                tree_det.heading(c, text=h)
                tree_det.column(c, width=w, anchor="center")
            tree_det.pack(fill="both", expand=True)

            detalles = self.controller.model.obtener_detalles_nota(id_nota)
            for d in detalles:
                tree_det.insert("", "end", values=(
                    d["nombre_producto"], f"${d['precio_unitario']:.2f}", d["cantidad"], f"${d['subtotal']:.2f}"
                ))

            ctk.CTkButton(modal_det, text="Cerrar", fg_color="#E0E0E0", text_color="#000000",
                          font=("Arial", 9, "bold"), command=modal_det.destroy).pack(pady=10)

        def reimprimir():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Seleccion", "Seleccione una nota de entrega para reimprimir.", parent=modal)
                return
            id_nota = int(seleccion[0])
            cabecera = self.controller.model.obtener_nota_cabecera(id_nota)
            if not cabecera:
                messagebox.showerror("Error", "No se encontro la nota de entrega.", parent=modal)
                return
            detalles = self.controller.model.obtener_detalles_nota(id_nota)
            fecha = cabecera["fecha_hora"]
            fecha_texto = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
            datos_nota = {
                "empresa": "Suplestore Tachira",
                "direccion": "Centro Comercial Boulevard\nLos Mangos, Local 34, Barrio\nObrero. San Cristobal, Estado\nTachira.",
                "num_nota": cabecera["numero_control"],
                "fecha": fecha_texto,
                "cliente": cabecera["cliente"],
                "ci": cabecera["cedula"],
                "telefono": cabecera["telefono"],
                "metodo_pago": cabecera["metodo_pago"],
                "total": cabecera["monto_total"],
                "descuento": cabecera.get("descuento", 0),
                "total_cancelado": cabecera["monto_cancelado"],
                "items": [{"descripcion": d["nombre_producto"], "cantidad": d["cantidad"],
                           "precio": d["precio_unitario"], "subtotal": d["subtotal"]}
                          for d in detalles]
            }
            ruta_pdf = generar_nota_entrega(datos_nota)
            os.startfile(ruta_pdf)

        def descargar():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Seleccion", "Seleccione una nota de entrega para descargar el PDF.", parent=modal)
                return
            id_nota = int(seleccion[0])
            cabecera = self.controller.model.obtener_nota_cabecera(id_nota)
            if not cabecera:
                messagebox.showerror("Error", "No se encontro la nota de entrega.", parent=modal)
                return
            ruta = filedialog.asksaveasfilename(parent=modal, defaultextension=".pdf",
                                                filetypes=[("PDF", "*.pdf")],
                                                initialfile=f"nota_{cabecera['numero_control']}.pdf")
            if not ruta:
                return
            detalles = self.controller.model.obtener_detalles_nota(id_nota)
            fecha = cabecera["fecha_hora"]
            fecha_texto = fecha.strftime("%d/%m/%Y") if hasattr(fecha, "strftime") else str(fecha)
            datos_nota = {
                "empresa": "Suplestore Tachira",
                "direccion": "Centro Comercial Boulevard\nLos Mangos, Local 34, Barrio\nObrero. San Cristobal, Estado\nTachira.",
                "num_nota": cabecera["numero_control"],
                "fecha": fecha_texto,
                "cliente": cabecera["cliente"],
                "ci": cabecera["cedula"],
                "telefono": cabecera["telefono"],
                "metodo_pago": cabecera["metodo_pago"],
                "total": cabecera["monto_total"],
                "descuento": cabecera.get("descuento", 0),
                "total_cancelado": cabecera["monto_cancelado"],
                "items": [{"descripcion": d["nombre_producto"], "cantidad": d["cantidad"],
                           "precio": d["precio_unitario"], "subtotal": d["subtotal"]}
                          for d in detalles]
            }
            ruta_pdf = generar_nota_entrega(datos_nota, ruta_salida=ruta)
            messagebox.showinfo("Exito", f"Nota de entrega descargada en:\n{ruta_pdf}", parent=modal)

        btn_row = ctk.CTkFrame(modal, fg_color="#333333")
        btn_row.pack(fill="x", padx=15, pady=(0, 5))
        ctk.CTkButton(btn_row, text="Ver Detalles de Nota", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), command=ver_detalles).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Reimprimir", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), command=reimprimir).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Descargar en PDF", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), command=descargar).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Exportar a Excel", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 10, "bold"), command=exportar_excel).pack(side="left", padx=5)

        ctk.CTkButton(modal, text="Cerrar", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=120, command=modal.destroy).pack(pady=5)

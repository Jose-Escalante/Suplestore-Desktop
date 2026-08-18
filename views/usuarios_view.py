import os
import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image

from models.user_model import validar_complejidad
from services.ui_utils import traer_al_frente


class UsuariosView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        icons_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

        def ico(name, size=52):
            path = os.path.join(icons_dir, name)
            if os.path.exists(path):
                return ctk.CTkImage(Image.open(path), size=(size, size))
            return None

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Administrar usuarios", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        container = ctk.CTkFrame(self.root, fg_color="#3B3B3B")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        table_frame = ctk.CTkFrame(container, fg_color="#777777", corner_radius=8)
        table_frame.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("id", "Usuario", "Rol")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15,
                                 yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        headers = ["ID", "Usuario", "Rol"]
        widths = [60, 200, 140]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_datos()

        right_panel = ctk.CTkFrame(container, fg_color="#3B3B3B", width=200)
        right_panel.pack(side="right", fill="y", padx=(15, 0))

        btn_frame = ctk.CTkFrame(right_panel, fg_color="#3B3B3B")
        btn_frame.place(relx=0.5, rely=0.42, anchor="center")

        btn_size = 95

        ctk.CTkButton(btn_frame, text="Agregar", image=ico("usuarios_agregar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_agregar).grid(row=0, column=0, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Actualizar", image=ico("usuarios_actualizar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.abrir_modal_actualizar).grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Eliminar", image=ico("usuarios_eliminar.png"), compound="top",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      width=btn_size, height=btn_size, corner_radius=10,
                      command=self.eliminar_seleccionado).grid(row=1, column=0, columnspan=2, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Resetear Contrasena", image=ico("boton_reset.png", 30), compound="top",
                      fg_color="#E0A800", text_color="#000000", font=("Arial", 9, "bold"),
                      width=95, height=62, corner_radius=10,
                      command=self.abrir_modal_resetear).grid(row=2, column=0, columnspan=2, padx=6, pady=6)

        ctk.CTkButton(btn_frame, text="Volver", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=202, height=28, corner_radius=6,
                      command=controller.show_panel).grid(row=3, column=0, columnspan=2, pady=(20, 0))

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in self.controller.model.obtener_usuarios():
            self.tree.insert("", "end", values=(u["id_usuario"], u["usuario"], u["rol"]))

    def abrir_modal_agregar(self):
        modal = ctk.CTkToplevel(self.root)
        traer_al_frente(modal)
        modal.resizable(False, False)
        modal.title("Registrar Nuevo Usuario")
        modal.geometry("400x520")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Usuario:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(15, 2))
        e_usuario = ctk.CTkEntry(modal, width=260, font=("Arial", 11))
        e_usuario.pack(padx=30)

        ctk.CTkLabel(modal, text="Contrasena:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(10, 2))
        e_pass = ctk.CTkEntry(modal, width=260, font=("Arial", 11), show="*")
        e_pass.pack(padx=30)

        ctk.CTkLabel(modal, text="Rol:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(10, 2))
        combo_rol = ctk.CTkComboBox(modal, values=["Administrador", "Vendedor"], width=260, state="readonly",
                                     command=self._cambiar_rol_evento_agregar)
        combo_rol.pack(padx=30)
        combo_rol.set("Administrador")

        ctk.CTkLabel(modal, text="Permisos del Usuario:", text_color="#FFFFFF", font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(15, 5))

        chk_frame = ctk.CTkFrame(modal, fg_color="#333333")
        chk_frame.pack(padx=30, anchor="w")

        var_inv = ctk.BooleanVar(value=True)
        var_cli = ctk.BooleanVar(value=True)
        var_ven = ctk.BooleanVar(value=True)
        var_cat = ctk.BooleanVar(value=True)
        var_usu = ctk.BooleanVar(value=True)
        var_his = ctk.BooleanVar(value=True)

        self._vars_agregar = (var_inv, var_cli, var_ven, var_cat, var_usu, var_his)
        self._combo_rol_agregar = combo_rol

        ctk.CTkCheckBox(chk_frame, text="Modulo Inventario", variable=var_inv, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Clientes", variable=var_cli, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Ventas", variable=var_ven, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Categorias", variable=var_cat, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Usuarios", variable=var_usu, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Historial", variable=var_his, onvalue=True, offvalue=False).pack(anchor="w")

        def guardar():
            usuario = e_usuario.get().strip()
            password = e_pass.get().strip()
            rol = combo_rol.get()
            if not usuario or not password:
                messagebox.showwarning("Aviso", "Usuario y contrasena son obligatorios", parent=modal)
                return
            ok, msg = validar_complejidad(password)
            if not ok:
                messagebox.showwarning("Contrasena invalida", msg, parent=modal)
                return
            permisos = {
                "inventario": var_inv.get(),
                "clientes": var_cli.get(),
                "ventas": var_ven.get(),
                "categorias": var_cat.get(),
                "usuarios": var_usu.get(),
                "historial": var_his.get()
            }
            if self.controller.model.agregar_usuario(usuario, password, rol, permisos):
                messagebox.showinfo("Exito", "Usuario registrado correctamente", parent=modal)
                modal.destroy()
                self.cargar_datos()

        ctk.CTkButton(modal, text="Guardar Usuario", fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      command=guardar).pack(pady=20)

    def _cambiar_rol_evento_agregar(self, valor):
        if not hasattr(self, '_vars_agregar'):
            return
        es_admin = (valor == "Administrador")
        for var in self._vars_agregar:
            var.set(es_admin)

    def abrir_modal_actualizar(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Por favor, seleccione un usuario de la tabla para actualizar.")
            return

        valores = self.tree.item(seleccion[0], "values")
        id_usuario, user_act, rol_act = valores[0], valores[1], valores[2]
        permisos_actuales = self.controller.model.obtener_permisos_usuario(id_usuario)

        modal = ctk.CTkToplevel(self.root)
        traer_al_frente(modal)
        modal.resizable(False, False)
        modal.title("Actualizar Usuario")
        modal.geometry("400x520")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Usuario:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(15, 2))
        e_usuario = ctk.CTkEntry(modal, width=260, font=("Arial", 11))
        e_usuario.pack(padx=30)
        e_usuario.insert(0, user_act)

        ctk.CTkLabel(modal, text="Nueva Contrasena (Opcional):", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(10, 2))
        e_pass = ctk.CTkEntry(modal, width=260, font=("Arial", 11), show="*")
        e_pass.pack(padx=30)

        ctk.CTkLabel(modal, text="Contrasena actual del usuario (para cambiar contrasena):", text_color="#FFFFFF",
                     font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(10, 2))
        e_user_pass = ctk.CTkEntry(modal, width=260, font=("Arial", 11), show="*")
        e_user_pass.pack(padx=30)

        ctk.CTkLabel(modal, text="Rol:", text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(10, 2))
        combo_rol = ctk.CTkComboBox(modal, values=["Administrador", "Vendedor"], width=260, state="readonly",
                                     command=self._cambiar_rol_evento_actualizar)
        combo_rol.pack(padx=30)
        combo_rol.set(rol_act if rol_act in ["Administrador", "Vendedor"] else "Administrador")

        var_inv = ctk.BooleanVar(value=bool(permisos_actuales["modulo_inventario"]) if permisos_actuales else True)
        var_cli = ctk.BooleanVar(value=bool(permisos_actuales["modulo_clientes"]) if permisos_actuales else True)
        var_ven = ctk.BooleanVar(value=bool(permisos_actuales["modulo_ventas"]) if permisos_actuales else True)
        var_cat = ctk.BooleanVar(value=bool(permisos_actuales["modulo_categorias"]) if permisos_actuales else True)
        var_usu = ctk.BooleanVar(value=bool(permisos_actuales["modulo_usuarios"]) if permisos_actuales else True)
        var_his = ctk.BooleanVar(value=bool(permisos_actuales["modulo_historial"]) if permisos_actuales else True)

        self._vars_actualizar = (var_inv, var_cli, var_ven, var_cat, var_usu, var_his)
        self._combo_rol_actualizar = combo_rol

        ctk.CTkLabel(modal, text="Permisos del Usuario:", text_color="#FFFFFF", font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(15, 5))

        chk_frame = ctk.CTkFrame(modal, fg_color="#333333")
        chk_frame.pack(padx=30, anchor="w")

        ctk.CTkCheckBox(chk_frame, text="Modulo Inventario", variable=var_inv, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Clientes", variable=var_cli, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Ventas", variable=var_ven, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Categorias", variable=var_cat, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Usuarios", variable=var_usu, onvalue=True, offvalue=False).pack(anchor="w")
        ctk.CTkCheckBox(chk_frame, text="Modulo Historial", variable=var_his, onvalue=True, offvalue=False).pack(anchor="w")

        def actualizar():
            usuario = e_usuario.get().strip()
            password = e_pass.get().strip()
            rol = combo_rol.get()
            if not usuario:
                messagebox.showwarning("Aviso", "El nombre de usuario es obligatorio", parent=modal)
                return
            if password:
                ok, msg = validar_complejidad(password)
                if not ok:
                    messagebox.showwarning("Contrasena invalida", msg, parent=modal)
                    return
                user_pass = e_user_pass.get()
                if not self.controller.model.verificar_contrasena(id_usuario, user_pass):
                    messagebox.showerror("Acceso denegado", "La contrasena actual del usuario es incorrecta.", parent=modal)
                    return
            permisos = {
                "inventario": var_inv.get(),
                "clientes": var_cli.get(),
                "ventas": var_ven.get(),
                "categorias": var_cat.get(),
                "usuarios": var_usu.get(),
                "historial": var_his.get()
            }
            if self.controller.model.actualizar_usuario(id_usuario, usuario, password, rol, permisos):
                if password:
                    self.controller.registrar_evento("cambio_contrasena", f"Se cambio la contrasena del usuario {usuario}")
                messagebox.showinfo("Exito", "Usuario actualizado correctamente", parent=modal)
                modal.destroy()
                self.cargar_datos()

        ctk.CTkButton(modal, text="Guardar Cambios", fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      command=actualizar).pack(pady=20)

    def _cambiar_rol_evento_actualizar(self, valor):
        if not hasattr(self, '_vars_actualizar'):
            return
        es_admin = (valor == "Administrador")
        for var in self._vars_actualizar:
            var.set(es_admin)

    def abrir_modal_resetear(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Por favor, seleccione un usuario de la tabla para resetear su contrasena.")
            return

        valores = self.tree.item(seleccion[0], "values")
        id_usuario, usuario = valores[0], valores[1]
        if usuario == self.controller.usuario_actual["usuario"]:
            messagebox.showerror("Accion no permitida", "No puedes resetear tu propia contrasena desde aqui.")
            return

        modal = ctk.CTkToplevel(self.root)
        traer_al_frente(modal)
        modal.resizable(False, False)
        modal.title("Resetear Contrasena")
        modal.geometry("380x300")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text=f"Resetear contrasena del usuario: {usuario}", text_color="#FFFFFF",
                     font=("Arial", 11, "bold")).pack(anchor="w", padx=30, pady=(20, 10))

        ctk.CTkLabel(modal, text="Tu contrasena de administrador:", text_color="#FFFFFF", font=("Arial", 10)).pack(anchor="w", padx=30, pady=(0, 2))
        e_admin_pass = ctk.CTkEntry(modal, width=260, font=("Arial", 11), show="*")
        e_admin_pass.pack(padx=30)

        ctk.CTkLabel(modal, text="Nueva contrasena temporal:", text_color="#FFFFFF", font=("Arial", 10)).pack(anchor="w", padx=30, pady=(10, 2))
        e_nueva = ctk.CTkEntry(modal, width=260, font=("Arial", 11), show="*")
        e_nueva.pack(padx=30)

        def resetear():
            clave_admin = e_admin_pass.get()
            nueva = e_nueva.get().strip()
            if not clave_admin or not nueva:
                messagebox.showwarning("Aviso", "Debe ingresar su contrasena y la nueva contrasena temporal", parent=modal)
                return
            ok, msg = validar_complejidad(nueva)
            if not ok:
                messagebox.showwarning("Contrasena invalida", msg, parent=modal)
                return
            if self.controller.resetear_contrasena_usuario(id_usuario, clave_admin, nueva):
                modal.destroy()
                self.cargar_datos()

        ctk.CTkButton(modal, text="Resetear Contrasena", fg_color="#E0A800", text_color="#000000",
                      font=("Arial", 10, "bold"), command=resetear).pack(pady=20)

    def eliminar_seleccionado(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Por favor, seleccione un usuario de la tabla para eliminar.")
            return
        valores = self.tree.item(seleccion[0], "values")
        id_usuario, usuario = valores[0], valores[1]
        if usuario == self.controller.usuario_actual["usuario"]:
            messagebox.showerror("Accion no permitida", "No puedes eliminar el usuario con el que estas conectado actualmente.")
            return
        confirmacion = messagebox.askyesno("Confirmar Eliminacion", f"Esta seguro que desea eliminar al usuario '{usuario}'?")
        if confirmacion:
            if self.controller.model.eliminar_usuario(id_usuario):
                messagebox.showinfo("Exito", "Usuario eliminado correctamente")
                self.cargar_datos()

import customtkinter as ctk
from tkinter import messagebox, ttk
from services.ui_utils import traer_al_frente


class CategoriasView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        ctk.CTkLabel(top_bar, text="Gestion de Categorias", text_color="#111111", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)

        container = ctk.CTkFrame(self.root, fg_color="#333333")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        table_frame = ctk.CTkFrame(container, fg_color="#2D2D2D")
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("id", "nombre")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        headers = ["ID", "Nombre de Categoria"]
        for col, head in zip(columns, headers):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=250, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_datos()

        sidebar = ctk.CTkFrame(container, fg_color="#333333", width=200)
        sidebar.pack(side="right", fill="y", padx=(20, 0))

        ctk.CTkButton(sidebar, text="Agregar", fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=160, height=40, command=self.abrir_modal_agregar).pack(pady=10)
        ctk.CTkButton(sidebar, text="Eliminar", fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=160, height=40, command=self.eliminar_seleccionada).pack(pady=10)

        ctk.CTkButton(sidebar, text="Volver", fg_color="#E0E0E0", text_color="#000000", font=("Arial", 10, "bold"),
                      width=160, height=30, command=controller.show_panel).pack(pady=(30, 0))

    def cargar_datos(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cat in self.controller.model.obtener_categorias():
            self.tree.insert("", "end", values=(cat["id_categoria"], cat["nombre_categoria"]))

    def abrir_modal_agregar(self):
        modal = ctk.CTkToplevel(self.root)
        traer_al_frente(modal)
        modal.resizable(False, False)
        modal.title("Registrar Nueva Categoria")
        modal.geometry("350x230")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Nombre de la Categoria:", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="w", padx=30, pady=(20, 5))
        entry_cat = ctk.CTkEntry(modal, font=("Arial", 11), width=220)
        entry_cat.pack(padx=30)

        def guardar():
            nombre = entry_cat.get().strip()
            if nombre:
                if self.controller.model.agregar_categoria(nombre):
                    messagebox.showinfo("Exito", "Categoria agregada correctamente", parent=modal)
                    modal.destroy()
                    self.cargar_datos()
            else:
                messagebox.showwarning("Aviso", "Ingrese un nombre valido", parent=modal)

        ctk.CTkButton(modal, text="Guardar Categoria", fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      command=guardar).pack(pady=20)

    def eliminar_seleccionada(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion requerida", "Por favor, seleccione una categoria de la tabla para eliminar.")
            return
        valores = self.tree.item(seleccion[0], "values")
        id_categoria, nombre = valores[0], valores[1]
        confirmacion = messagebox.askyesno("Confirmar Eliminacion", f"Esta seguro que desea eliminar la categoria '{nombre}'?")
        if confirmacion:
            if self.controller.model.eliminar_categoria(id_categoria):
                messagebox.showinfo("Exito", "Categoria eliminada correctamente")
                self.cargar_datos()

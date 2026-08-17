import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image


class PanelView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        icons_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=35)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Panel de Control", text_color="#111111", font=("Arial", 11, "bold")).pack(anchor="w", padx=15, pady=6)

        container = ctk.CTkFrame(self.root, fg_color="#3B3B3B")
        container.pack(fill="both", expand=True)

        ctk.CTkLabel(container, text="PANEL DE CONTROL", text_color="#FFFFFF", font=("Arial", 26, "bold")).pack(pady=(40, 20))

        def icon(name):
            path = os.path.join(icons_dir, f"{name}.png")
            if os.path.exists(path):
                return ctk.CTkImage(Image.open(path), size=(24, 24))
            return None

        btn_width = 190
        btn_height = 50

        grid_frame = ctk.CTkFrame(container, fg_color="#3B3B3B")
        grid_frame.pack(expand=True)

        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(grid_frame, text="Inventario", image=icon("inventario"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_inventario).grid(row=0, column=0, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Clientes", image=icon("clientes"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_clientes).grid(row=0, column=1, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Ventas", image=icon("ventas"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_ventas).grid(row=0, column=2, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Usuarios", image=icon("usuarios"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_usuarios).grid(row=1, column=0, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Historial", image=icon("inventario_historial_lotes"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_historial).grid(row=1, column=1, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Categorias", image=icon("categorias"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=controller.show_categorias).grid(row=1, column=2, padx=5, pady=8)

        ctk.CTkButton(grid_frame, text="Respaldo BD", image=icon("inventario_registrar"), compound="left",
                      fg_color="#5CB85C", text_color="#000000", font=("Arial", 13, "bold"),
                      width=btn_width, height=btn_height, corner_radius=8,
                      command=self.abrir_modal_respaldo).grid(row=2, column=1, padx=5, pady=8)

        cerrar_frame = ctk.CTkFrame(container, fg_color="#3B3B3B")
        cerrar_frame.pack(fill="x", pady=(10, 20))

        ctk.CTkButton(cerrar_frame, text="Cerrar Sesion", fg_color="#E0E0E0", text_color="#000000", font=("Arial", 11, "bold"),
                      width=140, height=32, corner_radius=6,
                      command=controller.cerrar_sesion).pack(side="right", padx=30)

        rol_text = f"Usuario: {controller.usuario_actual['usuario']} | Rol: {controller.usuario_actual['rol']}"
        footer_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        footer_bar.pack(fill="x", side="bottom")
        footer_bar.pack_propagate(False)
        ctk.CTkLabel(footer_bar, text=rol_text, text_color="#111111", font=("Arial", 10, "bold")).pack(anchor="center", pady=5)

    def abrir_modal_respaldo(self):
        modal = ctk.CTkToplevel(self.root)
        modal.resizable(False, False)
        modal.title("Copias de Seguridad")
        modal.geometry("400x220")
        modal.configure(fg_color="#333333")

        ctk.CTkLabel(modal, text="Copias de Seguridad de la Base de Datos", text_color="#FFFFFF",
                     font=("Arial", 12, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(modal, text="Exporta o restaura un respaldo (.sql)", text_color="#AAAAAA",
                     font=("Arial", 10)).pack(pady=(0, 15))

        def exportar():
            ruta = filedialog.asksaveasfilename(parent=modal, defaultextension=".sql",
                                                filetypes=[("SQL", "*.sql"), ("Todos", "*.*")],
                                                initialfile=f"respaldo_suplestore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
            if not ruta:
                return
            if self.controller.model.exportar_respaldo(ruta):
                self.controller.registrar_evento("respaldo", f"Se exporto un respaldo de la base de datos")
                messagebox.showinfo("Exito", f"Respaldo exportado en:\n{ruta}", parent=modal)

        def importar():
            ruta = filedialog.askopenfilename(parent=modal, filetypes=[("SQL", "*.sql"), ("Todos", "*.*")])
            if not ruta:
                return
            confirmacion = messagebox.askyesno("Confirmacion",
                                               "Al importar un respaldo se REEMPLAZARA toda la informacion actual.\n\n"
                                               "Esta seguro que desea continuar?", parent=modal)
            if not confirmacion:
                return
            if self.controller.model.importar_respaldo(ruta):
                self.controller.registrar_evento("respaldo", "Se importo un respaldo de la base de datos")
                messagebox.showinfo("Exito", "Respaldo importado correctamente.", parent=modal)

        btn_row = ctk.CTkFrame(modal, fg_color="#333333")
        btn_row.pack(pady=10)
        ctk.CTkButton(btn_row, text="Exportar Respaldo", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 11, "bold"), width=160, command=exportar).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Importar Respaldo", fg_color="#E0A800", text_color="#000000",
                      font=("Arial", 11, "bold"), width=160, command=importar).pack(side="left", padx=6)

        ctk.CTkButton(modal, text="Cerrar", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 10, "bold"), width=100, command=modal.destroy).pack(pady=10)

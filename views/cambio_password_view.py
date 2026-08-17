import bcrypt
import customtkinter as ctk
from tkinter import messagebox

from models.user_model import validar_complejidad


class CambioPasswordView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="Cambio de contrasena obligatorio", text_color="#111111",
                     font=("Arial", 11, "bold")).pack(anchor="w", padx=12, pady=4)

        container = ctk.CTkFrame(self.root, fg_color="#333333")
        container.pack(fill="both", expand=True)

        form = ctk.CTkFrame(container, fg_color="#333333")
        form.place(relx=0.5, rely=0.5, anchor="center")

        nombre = controller.usuario_actual["usuario"] if controller.usuario_actual else ""
        ctk.CTkLabel(form, text="Bienvenido, " + nombre, text_color="#FFFFFF",
                     font=("Arial", 16, "bold")).pack(pady=(0, 5))
        ctk.CTkLabel(form, text="Debe cambiar su contrasena para continuar", text_color="#AAAAAA",
                     font=("Arial", 11)).pack(pady=(0, 20))

        ctk.CTkLabel(form, text="Contrasena actual:", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="w")
        e_actual = ctk.CTkEntry(form, font=("Arial", 12), width=260, show="*")
        e_actual.pack(pady=(5, 12))

        ctk.CTkLabel(form, text="Nueva contrasena (min 8, con mayuscula, numero y simbolo):", text_color="#FFFFFF",
                     font=("Arial", 11)).pack(anchor="w")
        e_nueva = ctk.CTkEntry(form, font=("Arial", 12), width=260, show="*")
        e_nueva.pack(pady=(5, 12))

        ctk.CTkLabel(form, text="Confirmar contrasena:", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="w")
        e_confirmar = ctk.CTkEntry(form, font=("Arial", 12), width=260, show="*")
        e_confirmar.pack(pady=(5, 20))

        def guardar():
            actual = e_actual.get()
            nueva = e_nueva.get()
            confirmar = e_confirmar.get()
            id_usuario = controller.usuario_actual["id_usuario"] if controller.usuario_actual else None
            if id_usuario is None:
                return
            if not controller.model.verificar_contrasena(id_usuario, actual):
                messagebox.showerror("Error", "La contrasena actual es incorrecta.")
                return
            ok, msg = validar_complejidad(nueva)
            if not ok:
                messagebox.showwarning("Contrasena invalida", msg)
                return
            if nueva != confirmar:
                messagebox.showerror("Error", "Las contrasenas no coinciden.")
                return
            hash_actual = controller.usuario_actual.get("contrasena", "") if controller.usuario_actual else ""
            if hash_actual.startswith("$2") and bcrypt.checkpw(nueva.encode("utf-8"), hash_actual.encode("utf-8")):
                messagebox.showerror("Error", "La nueva contrasena no puede ser igual a la actual.")
                return
            controller.registrar_evento("cambio_contrasena", f"El usuario {controller.usuario_actual.get('usuario')} cambio su contrasena")
            controller.completar_cambio_password(nueva)

        btn_row = ctk.CTkFrame(form, fg_color="#333333")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="Guardar y Continuar", fg_color="#5CB85C", text_color="#000000",
                      font=("Arial", 11, "bold"), width=160, command=guardar).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="Cerrar Sesion", fg_color="#E0E0E0", text_color="#000000",
                      font=("Arial", 11, "bold"), width=120, command=controller.cerrar_sesion).pack(side="left", padx=5)
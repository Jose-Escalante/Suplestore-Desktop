import os
import customtkinter as ctk
from PIL import Image


class LoginView:
    def __init__(self, controller):
        self.controller = controller
        self.root = controller.root
        assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

        top_bar = ctk.CTkFrame(self.root, fg_color="#5CB85C", height=30)
        top_bar.pack(fill="x", side="top")
        ctk.CTkLabel(top_bar, text="Inicio de sesion", text_color="#111111", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)

        container = ctk.CTkFrame(self.root, fg_color="#333333")
        container.pack(fill="both", expand=True)

        left_panel = ctk.CTkFrame(container, fg_color="#585858", width=450)
        left_panel.pack(side="left", fill="both", expand=True)
        left_panel.pack_propagate(False)

        logo_path = os.path.join(assets_dir, "logo.png")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(400, 178))
            ctk.CTkLabel(left_panel, image=logo_img, text="").pack(pady=(60, 10))
            ctk.CTkLabel(left_panel, text="Sistema de Gestion de Ventas", text_color="#FFFFFF", font=("Arial", 16, "bold")).pack(pady=5)
            ctk.CTkLabel(left_panel, text="Barrio Obrero. San Cristobal", text_color="#CCCCCC", font=("Arial", 12)).pack(pady=2)
        else:
            ctk.CTkLabel(left_panel, text="Sistema de Gestion de Ventas", text_color="#FFFFFF", font=("Arial", 18, "bold")).pack(pady=(120, 10))
            ctk.CTkLabel(left_panel, text="Barrio Obrero. San Cristobal", text_color="#CCCCCC", font=("Arial", 12)).pack(pady=5)

        ctk.CTkLabel(left_panel, text="Aplicacion de escritorio creada por:\nJose Escalante, Giornaldo Gomez, Brandon Correa",
                     text_color="#AAAAAA", font=("Arial", 10), justify="center").pack(pady=40)

        separator = ctk.CTkFrame(container, fg_color="#5CB85C", width=2)
        separator.pack(side="left", fill="y")

        right_panel = ctk.CTkFrame(container, fg_color="#383838", width=450)
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.pack_propagate(False)

        form_frame = ctk.CTkFrame(right_panel, fg_color="#383838")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form_frame, text="Inicio de sesion", text_color="#FFFFFF", font=("Arial", 20)).pack(pady=(0, 25))

        ctk.CTkLabel(form_frame, text="Nombre de usuario", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(form_frame, font=("Arial", 12), width=230)
        self.entry_user.pack(pady=(5, 15))

        ctk.CTkLabel(form_frame, text="Contrasena", text_color="#FFFFFF", font=("Arial", 11)).pack(anchor="w")

        ojo_path = os.path.join(assets_dir, "ojo.png")
        invisible_path = os.path.join(assets_dir, "invisible.png")
        self.img_ojo = ctk.CTkImage(Image.open(ojo_path), size=(22, 22)) if os.path.exists(ojo_path) else None
        self.img_invisible = ctk.CTkImage(Image.open(invisible_path), size=(22, 22)) if os.path.exists(invisible_path) else None

        pass_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        pass_frame.pack(pady=(5, 20))
        self.entry_pass = ctk.CTkEntry(pass_frame, font=("Arial", 12), width=200, show="*")
        self.entry_pass.pack(side="left")
        self.entry_pass.bind("<Return>", lambda e: self.procesar_login())

        self.pass_visible = False
        btn_eye = ctk.CTkButton(pass_frame, text="", width=30, height=30,
                                image=self.img_ojo,
                                fg_color="transparent", hover_color="#555555",
                                command=self._toggle_password)
        btn_eye.pack(side="left", padx=(5, 0))
        self.btn_eye = btn_eye

        ctk.CTkButton(form_frame, text="Iniciar", fg_color="#5CB85C", text_color="#000000", font=("Arial", 11, "bold"),
                      width=150, command=self.procesar_login).pack()

    def _toggle_password(self):
        self.pass_visible = not self.pass_visible
        self.entry_pass.configure(show="" if self.pass_visible else "*")
        self.btn_eye.configure(image=self.img_invisible if self.pass_visible else self.img_ojo)

    def procesar_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        self.controller.procesar_login(user, pwd)

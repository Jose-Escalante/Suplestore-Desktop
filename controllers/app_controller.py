import customtkinter as ctk
from tkinter import messagebox, ttk

from models.database_model import DatabaseModel

from services.ui_utils import traer_al_frente

from views.login_view import LoginView
from views.cambio_password_view import CambioPasswordView
from views.panel_view import PanelView
from views.categorias_view import CategoriasView
from views.usuarios_view import UsuariosView
from views.clientes_view import ClientesView
from views.ventas_view import VentasView
from views.inventario_view import InventarioView
from views.historial_view import HistorialView
from views.reportes_view import ReportesView

NOMBRES_MODULOS = {
    "inventario": "Inventario",
    "clientes": "Clientes",
    "ventas": "Ventas",
    "categorias": "Categorías",
    "usuarios": "Usuarios",
    "respaldos": "Respaldos",
    "historial": "Historial",
    "reportes": "Reportes",
}


class AppController:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.root = ctk.CTk()
        self.root.title("Suplestore Táchira")
        self.root.geometry("900x550")
        self.root.configure(fg_color="#333333")
        self.root.minsize(900, 550)
        self.root.resizable(True, True)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 900) // 2
        y = (self.root.winfo_screenheight() - 550) // 2
        self.root.geometry(f"900x550+{x}+{y}")

        self.model = DatabaseModel()
        self.usuario_actual = None
        self.current_view = None

        self.show_login()

    def run(self):
        self.root.mainloop()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def verificar_permiso(self, modulo):
        if not self.usuario_actual:
            return False
        permisos = self.model.obtener_permisos_usuario(self.usuario_actual["id_usuario"])
        if not permisos:
            return False
        mapa_permisos = {
            "inventario": permisos["modulo_inventario"],
            "clientes": permisos["modulo_clientes"],
            "ventas": permisos["modulo_ventas"],
            "categorias": permisos["modulo_categorias"],
            "usuarios": permisos["modulo_usuarios"],
            "respaldos": permisos["modulo_respaldos"],
            "historial": permisos["modulo_historial"],
            "reportes": permisos["modulo_reportes"]
        }
        return bool(mapa_permisos.get(modulo, False))

    def verificar_permiso_o_rechazar(self, modulo):
        if self.verificar_permiso(modulo):
            return True
        messagebox.showerror("Acceso Denegado", f"No tienes permisos para acceder al módulo de {NOMBRES_MODULOS.get(modulo, modulo)}.")
        return False

    def show_login(self):
        self.limpiar_ventana()
        self.current_view = LoginView(self)

    def show_panel(self):
        self.limpiar_ventana()
        self.current_view = PanelView(self)

    def show_cambio_password(self):
        self.limpiar_ventana()
        self.current_view = CambioPasswordView(self)

    def completar_cambio_password(self, nueva_contrasena):
        if not self.usuario_actual:
            return
        if self.model.cambiar_contrasena(self.usuario_actual["id_usuario"], nueva_contrasena):
            self.usuario_actual["cambio_obligatorio"] = 0
            self.show_panel()
            self.verificar_alertas_automaticas()

    def show_categorias(self):
        if not self.verificar_permiso_o_rechazar("categorias"):
            return
        self.limpiar_ventana()
        self.current_view = CategoriasView(self)

    def show_usuarios(self):
        if not self.verificar_permiso_o_rechazar("usuarios"):
            return
        self.limpiar_ventana()
        self.current_view = UsuariosView(self)

    def show_clientes(self):
        if not self.verificar_permiso_o_rechazar("clientes"):
            return
        self.limpiar_ventana()
        self.current_view = ClientesView(self)

    def show_ventas(self):
        if not self.verificar_permiso_o_rechazar("ventas"):
            return
        self.limpiar_ventana()
        self.current_view = VentasView(self)

    def show_inventario(self):
        if not self.verificar_permiso_o_rechazar("inventario"):
            return
        self.limpiar_ventana()
        self.current_view = InventarioView(self)

    def show_historial(self):
        if not self.verificar_permiso_o_rechazar("historial"):
            return
        self.limpiar_ventana()
        self.current_view = HistorialView(self)

    def show_reportes(self):
        if not self.verificar_permiso_o_rechazar("reportes"):
            return
        self.limpiar_ventana()
        self.current_view = ReportesView(self)

    def registrar_evento(self, tipo, detalle=None):
        if not self.usuario_actual:
            return
        self.model.registrar_evento(self.usuario_actual["id_usuario"], tipo, detalle)

    def resetear_contrasena_usuario(self, id_usuario, clave_admin, nueva_contrasena):
        if not self.usuario_actual:
            return False
        if id_usuario == self.usuario_actual["id_usuario"]:
            messagebox.showerror("Acción no permitida", "No puedes resetear tu propia contraseña desde aquí.")
            return False
        if not self.model.verificar_contrasena(self.usuario_actual["id_usuario"], clave_admin):
            messagebox.showerror("Clave incorrecta", "La contraseña del administrador es incorrecta.")
            return False
        if self.model.resetear_contrasena(id_usuario, nueva_contrasena):
            self.registrar_evento("reset_contrasena", f"El administrador reseteó la contraseña al usuario (ID {id_usuario})")
            messagebox.showinfo("Contraseña reseteada", "La contraseña fue reseteada. El usuario deberá cambiarla en su próximo ingreso.")
            return True
        return False

    def procesar_login(self, usuario, contrasena):
        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Por favor ingrese usuario y contraseña.")
            return

        resultado = self.model.intentar_login(usuario, contrasena)
        if resultado["estado"] == "ok":
            self.usuario_actual = resultado["usuario"]
            self.registrar_evento("login", f"El usuario {usuario} inició sesión")
            if self.usuario_actual.get("cambio_obligatorio"):
                self.show_cambio_password()
                return
            self.show_panel()
            self.verificar_alertas_automaticas()
        elif resultado["estado"] == "bloqueado":
            messagebox.showerror("Cuenta Bloqueada", f"Demasiados intentos fallidos. La cuenta será bloqueada por {resultado['minutos']} minuto(s). Intente más tarde.")
        else:
            mensaje = "Usuario o contraseña incorrectos."
            if resultado.get("restantes") is not None:
                mensaje += f" Le restan {resultado['restantes']} intento(s)."
            messagebox.showerror("Error de Acceso", mensaje)

    def cerrar_sesion(self):
        self.registrar_evento("logout", f"El usuario {self.usuario_actual.get('usuario')} cerró sesión" if self.usuario_actual else None)
        self.usuario_actual = None
        self.root.geometry("900x550")
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 900) // 2
        y = (self.root.winfo_screenheight() - 550) // 2
        self.root.geometry(f"900x550+{x}+{y}")
        self.show_login()

    def verificar_alertas_automaticas(self):
        alertas = self.model.obtener_alertas_vencimiento()
        if not alertas:
            return

        top = ctk.CTkToplevel(self.root)
        traer_al_frente(top)
        top.resizable(False, False)
        top.title("Alerta de Vencimiento Próximo")
        top.geometry("500x300")
        top.configure(fg_color="#333333")

        ctk.CTkLabel(top, text="Lotes próximos a vencer (< 90 días)!", text_color="#FF5555", font=("Arial", 12, "bold")).pack(pady=10)

        frame_t = ctk.CTkFrame(top, fg_color="transparent")
        frame_t.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(frame_t, columns=("Producto", "Stock", "Vencimiento", "Días"), show="headings", height=5)
        for col in ("Producto", "Stock", "Vencimiento", "Días"):
            tree.heading(col, text=col)
            tree.column(col, width=105, anchor="w")
        tree.pack(fill="both", expand=True)

        for a in alertas:
            tree.insert("", "end", values=(a["Producto"], a["Stock"], a["Vencimiento"], f"{a['Dias_Restantes']} días"))

        ctk.CTkButton(top, text="Ver en inventario", fg_color="#5CB85C", text_color="#000000", font=("Arial", 10, "bold"),
                      command=lambda: [top.destroy(), self.show_inventario()]).pack(pady=10)

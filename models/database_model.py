from .connection import DatabaseConnection
from .user_model import UserModel
from .client_model import ClientModel
from .category_model import CategoryModel
from .product_model import ProductModel
from .sale_model import SaleModel
from .event_model import EventModel
from .backup_model import BackupModel


class DatabaseModel:
    def __init__(self):
        self.db = DatabaseConnection()
        self.users = UserModel(self.db)
        self.clients = ClientModel(self.db)
        self.categories = CategoryModel(self.db)
        self.products = ProductModel(self.db)
        self.sales = SaleModel(self.db)
        self.events = EventModel(self.db)
        self.backup = BackupModel(self.db)

    def validar_login(self, usuario, contrasena):
        return self.users.validar_login(usuario, contrasena)

    def intentar_login(self, usuario, contrasena):
        return self.users.intentar_login(usuario, contrasena)

    def obtener_usuarios(self):
        return self.users.obtener_usuarios()

    def agregar_usuario(self, usuario, contrasena, rol, permisos):
        return self.users.agregar_usuario(usuario, contrasena, rol, permisos)

    def actualizar_usuario(self, id_usuario, usuario, contrasena, rol, permisos):
        return self.users.actualizar_usuario(id_usuario, usuario, contrasena, rol, permisos)

    def obtener_permisos_usuario(self, id_usuario):
        return self.users.obtener_permisos_usuario(id_usuario)

    def eliminar_usuario(self, id_usuario):
        return self.users.eliminar_usuario(id_usuario)

    def cambiar_contrasena(self, id_usuario, contrasena):
        return self.users.cambiar_contrasena(id_usuario, contrasena)

    def verificar_contrasena(self, id_usuario, contrasena):
        return self.users.verificar_contrasena(id_usuario, contrasena)

    def resetear_contrasena(self, id_usuario, contrasena):
        return self.users.resetear_contrasena(id_usuario, contrasena)

    def registrar_evento(self, id_usuario, tipo, detalle=None):
        return self.events.registrar_evento(id_usuario, tipo, detalle)

    def obtener_eventos(self, busqueda=None, tipo=None):
        return self.events.obtener_eventos(busqueda, tipo)

    def exportar_respaldo(self, ruta):
        return self.backup.exportar_respaldo(ruta)

    def importar_respaldo(self, ruta):
        return self.backup.importar_respaldo(ruta)

    def obtener_clientes(self):
        return self.clients.obtener_clientes()

    def buscar_cliente_por_cedula(self, cedula):
        return self.clients.buscar_cliente_por_cedula(cedula)

    def agregar_cliente(self, nombre, cedula, telefono):
        return self.clients.agregar_cliente(nombre, cedula, telefono)

    def actualizar_cliente(self, id_cliente, nombre, cedula, telefono):
        return self.clients.actualizar_cliente(id_cliente, nombre, cedula, telefono)

    def eliminar_cliente(self, id_cliente):
        return self.clients.eliminar_cliente(id_cliente)

    def obtener_categorias(self):
        return self.categories.obtener_categorias()

    def agregar_categoria(self, nombre):
        return self.categories.agregar_categoria(nombre)

    def eliminar_categoria(self, id_categoria):
        return self.categories.eliminar_categoria(id_categoria)

    def obtener_inventario(self):
        return self.products.obtener_inventario()

    def registrar_producto_y_lote(self, nombre, id_cat, stock, costo, precio, vencimiento):
        return self.products.registrar_producto_y_lote(nombre, id_cat, stock, costo, precio, vencimiento)

    def agregar_lote_a_producto(self, id_producto, stock, costo, precio, vencimiento):
        return self.products.agregar_lote_a_producto(id_producto, stock, costo, precio, vencimiento)

    def obtener_lotes_por_producto(self, id_producto):
        return self.products.obtener_lotes_por_producto(id_producto)

    def actualizar_producto(self, id_producto, nombre, id_categoria):
        return self.products.actualizar_producto(id_producto, nombre, id_categoria)

    def eliminar_producto(self, id_producto):
        return self.products.eliminar_producto(id_producto)

    def actualizar_lote(self, id_lote, stock, costo, precio, vencimiento):
        return self.products.actualizar_lote(id_lote, stock, costo, precio, vencimiento)

    def obtener_alertas_vencimiento(self):
        return self.products.obtener_alertas_vencimiento()

    def obtener_conteo_notas_entrega(self):
        return self.sales.obtener_conteo_notas_entrega()

    def obtener_siguiente_numero_control(self):
        return self.sales.obtener_siguiente_numero_control()

    def registrar_venta_y_nota(self, id_usuario, id_cliente, metodo_pago, total_venta, monto_cancelado, carrito, descuento=0.0):
        return self.sales.registrar_venta_y_nota(id_usuario, id_cliente, metodo_pago, total_venta, monto_cancelado, carrito, descuento)

    def obtener_historial_ventas(self):
        return self.sales.obtener_historial_ventas()

    def obtener_historial_por_cliente(self, id_cliente):
        return self.sales.obtener_historial_por_cliente(id_cliente)

    def obtener_nota_cabecera(self, numero_nota):
        return self.sales.obtener_nota_cabecera(numero_nota)

    def obtener_detalles_nota(self, numero_nota):
        return self.sales.obtener_detalles_nota(numero_nota)

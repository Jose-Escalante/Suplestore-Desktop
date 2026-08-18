import mysql.connector
from tkinter import messagebox
from datetime import datetime


class SaleModel:
    def __init__(self, db):
        self.db = db

    def obtener_conteo_notas_entrega(self):
        try:
            query = "SELECT COUNT(*) AS total FROM notas_entrega"
            self.db.cursor.execute(query)
            resultado = self.db.cursor.fetchone()
            return resultado["total"] if resultado else 0
        except Exception:
            return 0

    def obtener_siguiente_numero_control(self):
        anio = datetime.now().year
        try:
            query = "SELECT consecutivo FROM secuencia_notas WHERE anio = %s"
            self.db.cursor.execute(query, (anio,))
            row = self.db.cursor.fetchone()
            siguiente = (row["consecutivo"] + 1) if row else 1
        except Exception:
            siguiente = 1
        return f"{siguiente:04d}-{str(anio)[-2:]}"

    def registrar_venta_y_nota(self, id_usuario, id_cliente, metodo_pago, total_venta, monto_cancelado, carrito, descuento=0.0):
        try:
            anio = datetime.now().year
            q_sec = """
                INSERT INTO secuencia_notas (anio, consecutivo) VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE consecutivo = LAST_INSERT_ID(consecutivo + 1)
            """
            self.db.cursor.execute(q_sec, (anio,))
            self.db.cursor.execute("SELECT LAST_INSERT_ID() AS consecutivo")
            consecutivo = self.db.cursor.fetchone()["consecutivo"]
            numero_control = f"{consecutivo:04d}-{str(anio)[-2:]}"

            q_nota = "INSERT INTO notas_entrega (id_cliente, id_usuario, anio, secuencia, monto_total, descuento, metodo_pago, monto_cancelado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            self.db.cursor.execute(q_nota, (id_cliente, id_usuario, anio, consecutivo, total_venta, descuento, metodo_pago, monto_cancelado))
            numero_nota = self.db.cursor.lastrowid
            for item in carrito:
                id_prod = item["id_producto"]
                cantidad_comprada = item["cantidad"]
                precio_unitario = item["precio"]
                q_lotes = "SELECT id_lote, stock FROM lotes WHERE id_producto = %s AND stock > 0 ORDER BY fecha_vencimiento ASC"
                self.db.cursor.execute(q_lotes, (id_prod,))
                lotes = self.db.cursor.fetchall()
                pendiente_por_descontar = cantidad_comprada
                for lote in lotes:
                    if pendiente_por_descontar <= 0:
                        break
                    id_lote = lote["id_lote"]
                    stock_lote = lote["stock"]
                    if stock_lote >= pendiente_por_descontar:
                        nuevo_stock = stock_lote - pendiente_por_descontar
                        q_upd = "UPDATE lotes SET stock = %s WHERE id_lote = %s"
                        self.db.cursor.execute(q_upd, (nuevo_stock, id_lote))
                        q_detalle = "INSERT INTO detalle_nota (numero_nota, id_producto, id_lote, precio_unitario, cantidad, subtotal) VALUES (%s, %s, %s, %s, %s, %s)"
                        self.db.cursor.execute(q_detalle, (numero_nota, id_prod, id_lote, precio_unitario, pendiente_por_descontar, pendiente_por_descontar * precio_unitario))
                        pendiente_por_descontar = 0
                    else:
                        cantidad_usada_del_lote = stock_lote
                        pendiente_por_descontar -= stock_lote
                        q_upd = "UPDATE lotes SET stock = 0, estado = 'Agotado' WHERE id_lote = %s"
                        self.db.cursor.execute(q_upd, (id_lote,))
                        q_detalle = "INSERT INTO detalle_nota (numero_nota, id_producto, id_lote, precio_unitario, cantidad, subtotal) VALUES (%s, %s, %s, %s, %s, %s)"
                        self.db.cursor.execute(q_detalle, (numero_nota, id_prod, id_lote, precio_unitario, cantidad_usada_del_lote, cantidad_usada_del_lote * precio_unitario))
            self.db.commit()
            return {"numero_nota": numero_nota, "numero_control": numero_control}
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error de Base de Datos", f"No se pudo procesar la nota de entrega:\n{err}")
            return None

    def obtener_historial_ventas(self):
        query = """
            SELECT n.numero_nota AS id_venta,
                   CONCAT(LPAD(n.secuencia, 4, '0'), '-', RIGHT(n.anio, 2)) AS numero_control,
                   c.nombre AS cliente, c.cedula, u.usuario AS vendedor,
                   n.metodo_pago, n.monto_total AS total, n.descuento, n.monto_cancelado, n.fecha_hora AS fecha
            FROM notas_entrega n
            JOIN clientes c ON n.id_cliente = c.id_cliente
            JOIN usuarios u ON n.id_usuario = u.id_usuario
            ORDER BY n.fecha_hora DESC
        """
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def obtener_historial_por_cliente(self, id_cliente):
        query = """
            SELECT n.numero_nota AS id_venta,
                   CONCAT(LPAD(n.secuencia, 4, '0'), '-', RIGHT(n.anio, 2)) AS numero_control,
                   c.nombre AS cliente, c.cedula, u.usuario AS vendedor,
                   n.metodo_pago, n.monto_total AS total, n.descuento, n.monto_cancelado, n.fecha_hora AS fecha
            FROM notas_entrega n
            JOIN clientes c ON n.id_cliente = c.id_cliente
            JOIN usuarios u ON n.id_usuario = u.id_usuario
            WHERE n.id_cliente = %s
            ORDER BY n.fecha_hora DESC
        """
        self.db.cursor.execute(query, (id_cliente,))
        return self.db.cursor.fetchall()

    def obtener_nota_cabecera(self, numero_nota):
        try:
            query = """
                SELECT n.numero_nota, n.metodo_pago, n.monto_total, n.descuento, n.monto_cancelado, n.fecha_hora,
                       CONCAT(LPAD(n.secuencia, 4, '0'), '-', RIGHT(n.anio, 2)) AS numero_control,
                       c.nombre AS cliente, c.cedula, c.telefono
                FROM notas_entrega n
                JOIN clientes c ON n.id_cliente = c.id_cliente
                WHERE n.numero_nota = %s
            """
            self.db.cursor.execute(query, (numero_nota,))
            return self.db.cursor.fetchone()
        except Exception:
            return None

    def obtener_detalles_nota(self, numero_nota):
        try:
            query_safe = """
                SELECT p.nombre_producto, d.precio_unitario, d.cantidad, d.subtotal
                FROM detalle_nota d
                JOIN productos p ON d.id_producto = p.id_producto
                WHERE d.numero_nota = %s
            """
            self.db.cursor.execute(query_safe, (numero_nota,))
            return self.db.cursor.fetchall()
        except Exception:
            return []
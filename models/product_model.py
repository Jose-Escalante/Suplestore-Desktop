import mysql.connector
from tkinter import messagebox


class ProductModel:
    def __init__(self, db):
        self.db = db

    def obtener_inventario(self):
        query = "SELECT * FROM vista_inventario_general"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def registrar_producto_y_lote(self, nombre, id_cat, stock, costo, precio, vencimiento):
        try:
            q_prod = "INSERT INTO productos (nombre_producto, id_categoria) VALUES (%s, %s)"
            self.db.cursor.execute(q_prod, (nombre, id_cat))
            id_prod = self.db.cursor.lastrowid
            q_lote = "INSERT INTO lotes (id_producto, stock, costo, precio, fecha_vencimiento, estado) VALUES (%s, %s, %s, %s, %s, 'Activo')"
            self.db.cursor.execute(q_lote, (id_prod, stock, costo, precio, vencimiento))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error Detallado", f"Ocurrio un error al registrar:\n{err}")
            return False

    def agregar_lote_a_producto(self, id_producto, stock, costo, precio, vencimiento):
        try:
            q_lote = "INSERT INTO lotes (id_producto, stock, costo, precio, fecha_vencimiento, estado) VALUES (%s, %s, %s, %s, %s, 'Activo')"
            self.db.cursor.execute(q_lote, (id_producto, stock, costo, precio, vencimiento))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo agregar el lote:\n{err}")
            return False

    def obtener_lotes_por_producto(self, id_producto):
        query = "SELECT * FROM lotes WHERE id_producto = %s"
        self.db.cursor.execute(query, (id_producto,))
        return self.db.cursor.fetchall()

    def actualizar_producto(self, id_producto, nombre, id_categoria):
        try:
            query = "UPDATE productos SET nombre_producto = %s, id_categoria = %s WHERE id_producto = %s"
            self.db.cursor.execute(query, (nombre, id_categoria, id_producto))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar el producto:\n{err}")
            return False

    def eliminar_producto(self, id_producto):
        try:
            query = "DELETE FROM lotes WHERE id_producto = %s"
            self.db.cursor.execute(query, (id_producto,))
            query = "DELETE FROM productos WHERE id_producto = %s"
            self.db.cursor.execute(query, (id_producto,))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo eliminar el producto:\n{err}")
            return False

    def actualizar_lote(self, id_lote, stock, costo, precio, vencimiento):
        try:
            query = "UPDATE lotes SET stock = %s, costo = %s, precio = %s, fecha_vencimiento = %s WHERE id_lote = %s"
            self.db.cursor.execute(query, (stock, costo, precio, vencimiento, id_lote))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo actualizar el lote:\n{err}")
            return False

    def obtener_alertas_vencimiento(self):
        try:
            query = "SELECT * FROM vista_alertas_vencimiento"
            self.db.cursor.execute(query)
            return self.db.cursor.fetchall()
        except Exception:
            return []

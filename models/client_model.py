import mysql.connector
from tkinter import messagebox


class ClientModel:
    def __init__(self, db):
        self.db = db

    def obtener_clientes(self):
        query = "SELECT id_cliente, nombre, cedula, telefono FROM clientes ORDER BY id_cliente"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def buscar_cliente_por_cedula(self, cedula):
        try:
            query = "SELECT id_cliente, nombre, cedula, telefono FROM clientes WHERE cedula = %s"
            self.db.cursor.execute(query, (cedula,))
            return self.db.cursor.fetchone()
        except Exception:
            return None

    def agregar_cliente(self, nombre, cedula, telefono):
        try:
            query = "INSERT INTO clientes (nombre, cedula, telefono) VALUES (%s, %s, %s)"
            self.db.cursor.execute(query, (nombre, cedula, telefono))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo registrar el cliente (Verifique si la cedula ya existe):\n{err}")
            return False

    def actualizar_cliente(self, id_cliente, nombre, cedula, telefono):
        try:
            query = "UPDATE clientes SET nombre = %s, cedula = %s, telefono = %s WHERE id_cliente = %s"
            self.db.cursor.execute(query, (nombre, cedula, telefono, id_cliente))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error de Base de Datos", f"No se pudo actualizar el cliente:\n{err}")
            return False

    def eliminar_cliente(self, id_cliente):
        try:
            query = "DELETE FROM clientes WHERE id_cliente = %s"
            self.db.cursor.execute(query, (id_cliente,))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el cliente:\n{err}")
            return False

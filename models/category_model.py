import mysql.connector
from tkinter import messagebox


class CategoryModel:
    def __init__(self, db):
        self.db = db

    def obtener_categorias(self):
        query = "SELECT * FROM categorias ORDER BY id_categoria"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def agregar_categoria(self, nombre):
        try:
            query = "INSERT INTO categorias (nombre_categoria) VALUES (%s)"
            self.db.cursor.execute(query, (nombre,))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error de Base de Datos", f"No se pudo agregar la categoria:\n{err}")
            return False

    def eliminar_categoria(self, id_categoria):
        try:
            query = "DELETE FROM categorias WHERE id_categoria = %s"
            self.db.cursor.execute(query, (id_categoria,))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar la categoria (Puede estar asociada a productos):\n{err}")
            return False

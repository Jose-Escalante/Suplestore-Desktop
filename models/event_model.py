import mysql.connector
from tkinter import messagebox


class EventModel:
    def __init__(self, db):
        self.db = db

    def registrar_evento(self, id_usuario, tipo, detalle=None):
        try:
            query = "INSERT INTO eventos (id_usuario, tipo, detalle) VALUES (%s, %s, %s)"
            self.db.cursor.execute(query, (id_usuario, tipo, detalle))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo registrar el evento:\n{err}")
            return False

    def obtener_eventos(self, busqueda=None, tipo=None):
        query = """
            SELECT e.id_evento, e.tipo, e.detalle, e.fecha_hora, u.usuario
            FROM eventos e
            LEFT JOIN usuarios u ON e.id_usuario = u.id_usuario
        """
        condiciones = []
        parametros = []
        if busqueda:
            condiciones.append("(u.usuario LIKE %s OR e.detalle LIKE %s)")
            parametros.append(f"%{busqueda}%")
            parametros.append(f"%{busqueda}%")
        if tipo:
            condiciones.append("e.tipo = %s")
            parametros.append(tipo)
        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)
        query += " ORDER BY e.id_evento DESC"
        self.db.cursor.execute(query, parametros)
        return self.db.cursor.fetchall()
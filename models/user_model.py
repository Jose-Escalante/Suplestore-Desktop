import mysql.connector
from tkinter import messagebox
import bcrypt
import re
from datetime import datetime

MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 5


def validar_complejidad(contrasena):
    if len(contrasena) < 8:
        return False, "La contrasena debe tener minimo 8 caracteres."
    if not re.search(r"[A-Z]", contrasena):
        return False, "La contrasena debe incluir al menos una mayuscula."
    if not re.search(r"[a-z]", contrasena):
        return False, "La contrasena debe incluir al menos una minuscula."
    if not re.search(r"[0-9]", contrasena):
        return False, "La contrasena debe incluir al menos un numero."
    if not re.search(r"[^A-Za-z0-9]", contrasena):
        return False, "La contrasena debe incluir al menos un simbolo."
    return True, ""


class UserModel:
    def __init__(self, db):
        self.db = db

    def intentar_login(self, usuario, contrasena):
        query = "SELECT * FROM usuarios WHERE usuario = %s"
        self.db.cursor.execute(query, (usuario,))
        row = self.db.cursor.fetchone()
        if not row:
            return {"estado": "incorrecta", "usuario": None}

        ahora = datetime.now()
        bloqueado_hasta = row["bloqueado_hasta"]
        if bloqueado_hasta and bloqueado_hasta > ahora:
            minutos = int((bloqueado_hasta - ahora).total_seconds() // 60) + 1
            return {"estado": "bloqueado", "usuario": None, "minutos": minutos}

        hash_guardado = row["contrasena"]
        contrasena_valida = False
        if hash_guardado and hash_guardado.startswith("$2"):
            contrasena_valida = bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
        elif hash_guardado == contrasena:
            contrasena_valida = True

        if contrasena_valida:
            if hash_guardado and not hash_guardado.startswith("$2"):
                nuevo_hash = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                q = "UPDATE usuarios SET contrasena = %s WHERE id_usuario = %s"
                self.db.cursor.execute(q, (nuevo_hash, row["id_usuario"]))
                row["contrasena"] = nuevo_hash
            q_limpiar = "UPDATE usuarios SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE id_usuario = %s"
            self.db.cursor.execute(q_limpiar, (row["id_usuario"],))
            self.db.commit()
            row["intentos_fallidos"] = 0
            row["bloqueado_hasta"] = None
            return {"estado": "ok", "usuario": row}

        intentos = row["intentos_fallidos"] + 1
        if intentos >= MAX_INTENTOS:
            q_bloquear = (
                "UPDATE usuarios SET intentos_fallidos = 0, "
                "bloqueado_hasta = DATE_ADD(NOW(), INTERVAL %s MINUTE) "
                "WHERE id_usuario = %s"
            )
            self.db.cursor.execute(q_bloquear, (MINUTOS_BLOQUEO, row["id_usuario"]))
            self.db.commit()
            return {"estado": "bloqueado", "usuario": None, "minutos": MINUTOS_BLOQUEO}

        q_fallos = "UPDATE usuarios SET intentos_fallidos = %s WHERE id_usuario = %s"
        self.db.cursor.execute(q_fallos, (intentos, row["id_usuario"]))
        self.db.commit()
        return {"estado": "incorrecta", "usuario": None, "restantes": MAX_INTENTOS - intentos}

    def validar_login(self, usuario, contrasena):
        resultado = self.intentar_login(usuario, contrasena)
        return resultado["usuario"] if resultado["estado"] == "ok" else None

    def obtener_usuarios(self):
        query = "SELECT id_usuario, usuario, rol FROM usuarios"
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()

    def agregar_usuario(self, usuario, contrasena, rol, permisos):
        try:
            hash_pwd = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            query = "INSERT INTO usuarios (usuario, contrasena, cambio_obligatorio, rol) VALUES (%s, %s, 1, %s)"
            self.db.cursor.execute(query, (usuario, hash_pwd, rol))
            self.db.commit()
            id_nuevo_usuario = self.db.cursor.lastrowid
            q_permisos = "INSERT INTO permisos_usuario (id_usuario, modulo_inventario, modulo_clientes, modulo_ventas, modulo_categorias, modulo_usuarios, modulo_historial) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.db.cursor.execute(q_permisos, (
                id_nuevo_usuario,
                permisos["inventario"],
                permisos["clientes"],
                permisos["ventas"],
                permisos["categorias"],
                permisos["usuarios"],
                permisos["historial"]
            ))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo agregar el usuario (Verifique si ya existe):\n{err}")
            return False

    def actualizar_usuario(self, id_usuario, usuario, contrasena, rol, permisos):
        try:
            if contrasena:
                hash_pwd = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                query = "UPDATE usuarios SET usuario = %s, contrasena = %s, cambio_obligatorio = 1, rol = %s WHERE id_usuario = %s"
                self.db.cursor.execute(query, (usuario, hash_pwd, rol, id_usuario))
            else:
                query = "UPDATE usuarios SET usuario = %s, rol = %s WHERE id_usuario = %s"
                self.db.cursor.execute(query, (usuario, rol, id_usuario))
            q_permisos = "UPDATE permisos_usuario SET modulo_inventario = %s, modulo_clientes = %s, modulo_ventas = %s, modulo_categorias = %s, modulo_usuarios = %s, modulo_historial = %s WHERE id_usuario = %s"
            self.db.cursor.execute(q_permisos, (
                permisos["inventario"],
                permisos["clientes"],
                permisos["ventas"],
                permisos["categorias"],
                permisos["usuarios"],
                permisos["historial"],
                id_usuario
            ))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo actualizar el usuario:\n{err}")
            return False

    def resetear_contrasena(self, id_usuario, contrasena):
        try:
            hash_pwd = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            query = "UPDATE usuarios SET contrasena = %s, cambio_obligatorio = 1 WHERE id_usuario = %s"
            self.db.cursor.execute(query, (hash_pwd, id_usuario))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo resetear la contrasena:\n{err}")
            return False

    def verificar_contrasena(self, id_usuario, contrasena):
        try:
            query = "SELECT contrasena FROM usuarios WHERE id_usuario = %s"
            self.db.cursor.execute(query, (id_usuario,))
            row = self.db.cursor.fetchone()
            if not row:
                return False
            hash_guardado = row["contrasena"]
            if hash_guardado and hash_guardado.startswith("$2"):
                return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
            return hash_guardado == contrasena
        except Exception:
            return False

    def cambiar_contrasena(self, id_usuario, contrasena):
        try:
            hash_pwd = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            query = "UPDATE usuarios SET contrasena = %s, cambio_obligatorio = 0 WHERE id_usuario = %s"
            self.db.cursor.execute(query, (hash_pwd, id_usuario))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo cambiar la contrasena:\n{err}")
            return False

    def obtener_permisos_usuario(self, id_usuario):
        try:
            query = "SELECT * FROM permisos_usuario WHERE id_usuario = %s"
            self.db.cursor.execute(query, (id_usuario,))
            return self.db.cursor.fetchone()
        except mysql.connector.Error:
            return None

    def eliminar_usuario(self, id_usuario):
        try:
            q_permisos = "DELETE FROM permisos_usuario WHERE id_usuario = %s"
            self.db.cursor.execute(q_permisos, (id_usuario,))
            query = "DELETE FROM usuarios WHERE id_usuario = %s"
            self.db.cursor.execute(query, (id_usuario,))
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el usuario:\n{err}")
            return False

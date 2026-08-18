import os
import sys
import mysql.connector
from pathlib import Path
from tkinter import messagebox


def _cargar_env():
    bases = [Path(__file__).resolve().parent.parent]
    if getattr(sys, "frozen", False):
        bases.insert(0, Path(sys.executable).resolve().parent)
    for base in bases:
        ruta_env = base / ".env"
        if not ruta_env.exists():
            continue
        for linea in ruta_env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            os.environ.setdefault(clave.strip(), valor.strip())
        return


class DatabaseConnection:
    def __init__(self):
        _cargar_env()
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME")
        if not host or not user or not database:
            messagebox.showerror("Error de Conexion", "Faltan datos de conexion en el archivo .env (DB_HOST, DB_USER, DB_NAME).")
            exit()
        try:
            self.conexion = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexion", f"No se pudo conectar a la BD:\n{err}")
            exit()

    def commit(self):
        self.conexion.commit()

    def rollback(self):
        self.conexion.rollback()

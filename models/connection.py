import os
import mysql.connector
from pathlib import Path
from tkinter import messagebox


def _cargar_env():
    ruta_env = Path(__file__).resolve().parent.parent / ".env"
    if not ruta_env.exists():
        return
    for linea in ruta_env.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        os.environ.setdefault(clave.strip(), valor.strip())


class DatabaseConnection:
    def __init__(self):
        _cargar_env()
        try:
            self.conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "suplestore_db")
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Conexion", f"No se pudo conectar a la BD:\n{err}")
            exit()

    def commit(self):
        self.conexion.commit()

    def rollback(self):
        self.conexion.rollback()

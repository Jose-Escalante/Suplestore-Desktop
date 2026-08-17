import mysql.connector
from tkinter import messagebox
from datetime import datetime


class BackupModel:
    def __init__(self, db):
        self.db = db

    def _obtener_tablas_base(self):
        self.db.cursor.execute("""
            SELECT table_name AS nombre FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
        """)
        tablas = [r["nombre"] for r in self.db.cursor.fetchall()]
        dependencias = {t: set() for t in tablas}
        self.db.cursor.execute("""
            SELECT TABLE_NAME, REFERENCED_TABLE_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        for r in self.db.cursor.fetchall():
            tabla = r["TABLE_NAME"]
            padre = r["REFERENCED_TABLE_NAME"]
            if tabla in dependencias and padre in dependencias:
                dependencias[tabla].add(padre)
        orden = []
        visitados = set()

        def visitar(t):
            if t in visitados:
                return
            visitados.add(t)
            for p in dependencias.get(t, ()):
                visitar(p)
            orden.append(t)

        for t in tablas:
            visitar(t)
        return orden

    def _obtener_vistas(self):
        self.db.cursor.execute("""
            SELECT table_name AS nombre FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_type = 'VIEW'
        """)
        return [r["nombre"] for r in self.db.cursor.fetchall()]

    @staticmethod
    def _valor_sql(valor):
        import datetime as dt
        if valor is None:
            return "NULL"
        if isinstance(valor, bool):
            return "1" if valor else "0"
        if isinstance(valor, (int, float)):
            return str(valor)
        if isinstance(valor, dt.datetime):
            return f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'"
        if isinstance(valor, (dt.date,)):
            return f"'{valor.strftime('%Y-%m-%d')}'"
        return "'" + str(valor).replace("\\", "\\\\").replace("'", "\\'") + "'"

    def exportar_respaldo(self, ruta):
        try:
            tablas = self._obtener_tablas_base()
            vistas = self._obtener_vistas()
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"-- Respaldo Suplestore Tachira - {fecha}\n")
                f.write(f"-- Generado automaticamente por la aplicacion\n")
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                for t in tablas:
                    self.db.cursor.execute(f"SHOW CREATE TABLE `{t}`")
                    fila = self.db.cursor.fetchone()
                    ddl = list(fila.values())[1]
                    f.write(ddl + ";\n")
                    self.db.cursor.execute(f"SELECT * FROM `{t}`")
                    filas = self.db.cursor.fetchall()
                    if filas:
                        columnas = list(filas[0].keys())
                        cols_sql = ", ".join(f"`{c}`" for c in columnas)
                        for r in filas:
                            valores = ", ".join(self._valor_sql(r[c]) for c in columnas)
                            f.write(f"INSERT INTO `{t}` ({cols_sql}) VALUES ({valores});\n")
                    f.write("\n")
                for v in vistas:
                    self.db.cursor.execute(f"SHOW CREATE VIEW `{v}`")
                    fila = self.db.cursor.fetchone()
                    ddl = list(fila.values())[1]
                    f.write(ddl + ";\n\n")
                f.write("SET FOREIGN_KEY_CHECKS=1;\n")
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Error de Base de Datos", f"No se pudo exportar el respaldo:\n{err}")
            return False

    def importar_respaldo(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            if "SET FOREIGN_KEY_CHECKS=0" not in contenido:
                messagebox.showerror("Respaldos invalido", "El archivo no parece un respaldo de Suplestore valido.")
                return False

            self.db.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            tablas = self._obtener_tablas_base()
            for v in self._obtener_vistas():
                self.db.cursor.execute(f"DROP TABLE IF EXISTS `{v}`")
            for t in reversed(tablas):
                self.db.cursor.execute(f"DROP TABLE IF EXISTS `{t}`")

            for bloque in contenido.split(";\n"):
                sentencia = bloque.strip()
                if sentencia and not sentencia.startswith("--"):
                    if sentencia.startswith("INSERT"):
                        self.db.cursor.execute(sentencia)
                    elif sentencia.startswith("CREATE"):
                        self.db.cursor.execute(sentencia)
            self.db.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            self.db.rollback()
            self.db.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            self.db.commit()
            messagebox.showerror("Error de Base de Datos", f"No se pudo importar el respaldo:\n{err}")
            return False
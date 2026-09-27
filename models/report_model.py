from datetime import date, timedelta


class ReportModel:
    def __init__(self, db):
        self.db = db

    def _rango(self, periodo):
        hoy = date.today()
        if periodo == "semana":
            inicio = hoy - timedelta(days=6)
        elif periodo == "anio":
            inicio = hoy - timedelta(days=364)
        else:
            inicio = hoy - timedelta(days=29)
        return inicio.isoformat(), hoy.isoformat()

    def metricas_kpi(self):
        try:
            self.db.cursor.execute("SELECT COALESCE(SUM(monto_total), 0) AS valor FROM notas_entrega WHERE DATE(fecha_hora) = CURDATE()")
            ventas_hoy = self.db.cursor.fetchone()["valor"] or 0
            self.db.cursor.execute("SELECT COALESCE(SUM(monto_total), 0) AS valor FROM notas_entrega WHERE YEAR(fecha_hora) = YEAR(CURDATE()) AND MONTH(fecha_hora) = MONTH(CURDATE())")
            ventas_mes = self.db.cursor.fetchone()["valor"] or 0
            self.db.cursor.execute("SELECT COUNT(*) AS total FROM notas_entrega")
            notas = self.db.cursor.fetchone()["total"] or 0
            self.db.cursor.execute("SELECT p.nombre_producto AS nombre, SUM(d.cantidad) AS unidades FROM detalle_nota d JOIN productos p ON d.id_producto = p.id_producto GROUP BY p.id_producto, p.nombre_producto ORDER BY unidades DESC LIMIT 1")
            fila = self.db.cursor.fetchone()
            top = f"{fila['nombre']} ({fila['unidades']} uds)" if fila else "Sin ventas"
        except Exception:
            ventas_hoy, ventas_mes, notas, top = 0, 0, 0, "Sin datos"
        return {"ventas_hoy": ventas_hoy, "ventas_mes": ventas_mes, "notas": notas, "top_producto": top}

    def ventas_por_periodo(self, periodo):
        self.db.cursor.execute(
            "SELECT DATE(n.fecha_hora) AS dia, COUNT(*) AS notas, SUM(n.monto_total) AS total "
            "FROM notas_entrega n WHERE DATE(n.fecha_hora) BETWEEN %s AND %s "
            "GROUP BY DATE(n.fecha_hora) ORDER BY dia DESC",
            self._rango(periodo))
        return self.db.cursor.fetchall()

    def _totales_productos(self, periodo):
        self.db.cursor.execute(
            "SELECT p.nombre_producto, COALESCE(v.unidades, 0) AS unidades, COALESCE(v.ingresos, 0) AS ingresos "
            "FROM productos p LEFT JOIN ("
            " SELECT d.id_producto, SUM(d.cantidad) AS unidades, SUM(d.subtotal) AS ingresos "
            " FROM detalle_nota d JOIN notas_entrega n ON d.numero_nota = n.numero_nota "
            " WHERE DATE(n.fecha_hora) BETWEEN %s AND %s GROUP BY d.id_producto"
            ") v ON v.id_producto = p.id_producto",
            self._rango(periodo))
        return self.db.cursor.fetchall()

    def productos_mas_vendidos(self, periodo):
        filas = self._totales_productos(periodo)
        return sorted(filas, key=lambda r: r["unidades"], reverse=True)

    def productos_menos_vendidos(self, periodo):
        filas = self._totales_productos(periodo)
        return sorted(filas, key=lambda r: r["unidades"])

    def ventas_por_cliente(self, periodo):
        self.db.cursor.execute(
            "SELECT CONCAT_WS(' ', NULLIF(c.nombre, ''), NULLIF(c.apellido, '')) AS nombre, COUNT(*) AS notas, SUM(n.monto_total) AS total "
            "FROM notas_entrega n JOIN clientes c ON n.id_cliente = c.id_cliente "
            "WHERE DATE(n.fecha_hora) BETWEEN %s AND %s "
            "GROUP BY c.id_cliente, c.nombre, c.apellido ORDER BY total DESC",
            self._rango(periodo))
        return self.db.cursor.fetchall()

    def ventas_por_vendedor(self, periodo):
        self.db.cursor.execute(
            "SELECT u.usuario, COUNT(*) AS notas, SUM(n.monto_total) AS total "
            "FROM notas_entrega n JOIN usuarios u ON n.id_usuario = u.id_usuario "
            "WHERE DATE(n.fecha_hora) BETWEEN %s AND %s "
            "GROUP BY u.id_usuario, u.usuario ORDER BY total DESC",
            self._rango(periodo))
        return self.db.cursor.fetchall()

    def ventas_por_metodo_pago(self, periodo):
        self.db.cursor.execute(
            "SELECT n.metodo_pago, COUNT(*) AS notas, SUM(n.monto_total) AS total "
            "FROM notas_entrega n WHERE DATE(n.fecha_hora) BETWEEN %s AND %s "
            "GROUP BY n.metodo_pago ORDER BY total DESC",
            self._rango(periodo))
        return self.db.cursor.fetchall()

    def descuentos_aplicados(self, periodo):
        self.db.cursor.execute(
            "SELECT COUNT(*) AS notas, "
            "COUNT(CASE WHEN n.descuento > 0 THEN 1 END) AS notas_con_descuento, "
            "COALESCE(SUM(n.descuento), 0) AS total_descontado "
            "FROM notas_entrega n WHERE DATE(n.fecha_hora) BETWEEN %s AND %s",
            self._rango(periodo))
        fila = self.db.cursor.fetchone()
        return [fila] if fila else []

    def productos_stock_bajo(self, limite=5):
        self.db.cursor.execute(
            "SELECT p.nombre_producto, COALESCE(SUM(l.stock), 0) AS stock_total "
            "FROM productos p LEFT JOIN lotes l ON l.id_producto = p.id_producto AND l.estado = 'Activo' "
            "GROUP BY p.id_producto, p.nombre_producto "
            "HAVING stock_total <= %s ORDER BY stock_total ASC",
            (limite,))
        return self.db.cursor.fetchall()

    def clientes_inactivos(self, dias=90):
        self.db.cursor.execute(
            "SELECT CONCAT_WS(' ', NULLIF(c.nombre, ''), NULLIF(c.apellido, '')) AS nombre, c.cedula, c.telefono, MAX(n.fecha_hora) AS ultima_venta "
            "FROM clientes c LEFT JOIN notas_entrega n ON n.id_cliente = c.id_cliente "
            "GROUP BY c.id_cliente, c.nombre, c.apellido, c.cedula, c.telefono "
            "HAVING MAX(n.fecha_hora) IS NULL OR MAX(n.fecha_hora) < DATE_SUB(NOW(), INTERVAL %s DAY) "
            "ORDER BY ultima_venta ASC",
            (dias,))
        return self.db.cursor.fetchall()

    def vencimientos_lotes(self, dias=None):
        if dias is None:
            self.db.cursor.execute(
                "SELECT p.nombre_producto, l.id_lote AS lote, l.stock, "
                "l.fecha_vencimiento AS vencimiento, "
                "(TO_DAYS(l.fecha_vencimiento) - TO_DAYS(CURDATE())) AS dias "
                "FROM lotes l JOIN productos p ON l.id_producto = p.id_producto "
                "WHERE l.estado = 'Activo' AND l.stock > 0 "
                "ORDER BY l.fecha_vencimiento ASC")
        else:
            self.db.cursor.execute(
                "SELECT p.nombre_producto, l.id_lote AS lote, l.stock, "
                "l.fecha_vencimiento AS vencimiento, "
                "(TO_DAYS(l.fecha_vencimiento) - TO_DAYS(CURDATE())) AS dias "
                "FROM lotes l JOIN productos p ON l.id_producto = p.id_producto "
                "WHERE l.estado = 'Activo' AND l.stock > 0 "
                "AND (TO_DAYS(l.fecha_vencimiento) - TO_DAYS(CURDATE())) BETWEEN 0 AND %s "
                "ORDER BY l.fecha_vencimiento ASC",
                (dias,))
        return self.db.cursor.fetchall()
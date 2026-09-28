-- ============================================================================
-- CONSULTAS SQL QUE EJECUTA LA APLICACION SISTEMA SUPLESTORE TACHIRA
-- ----------------------------------------------------------------------------
-- Documento de apoyo para la defensa. Recopila TODAS las consultas que la
-- aplicacion ejecuta desde los modelos (capa Modelo del patron MVC).
--
-- Como leer este documento:
--   - Cada consulta es exactamente la que aparece en el codigo Python.
--   - El simbolo %s es un PARAMETRO PREPARADO: Python lo reemplaza con el
--     valor real de forma segura (sentencias preparadas), lo que protege la
--     aplicacion contra inyeccion SQL. Nunca se concatena texto del usuario.
--   - Las consultas SELECT pueden ejecutarse sin riesgo. Las de INSERT,
--     UPDATE y DELETE se muestran solo como referencia: ejecutarlas
--     modificaria la base de datos de produccion.
--   - La aplicacion NO usa procedimientos almacenados ni funciones: todas
--     las consultas van directas desde Python (mysql.connector).
--
-- Modulos (modelos):
--   1. Autenticacion y seguridad      models/user_model.py
--   2. Usuarios (CRUD)                models/user_model.py
--   3. Clientes (CRUD)                models/client_model.py
--   4. Categorias (CRUD)              models/category_model.py
--   5. Productos, lotes e inventario  models/product_model.py
--   6. Ventas y notas de entrega      models/sale_model.py
--   7. Bitacora de eventos            models/event_model.py
--   8. Respaldo de datos              models/backup_model.py
--   9. Reportes gerenciales           models/report_model.py
-- ============================================================================


-- ============================================================================
-- 1. AUTENTICACION Y SEGURIDAD
-- ============================================================================

-- 1.1. Obtener el id de un rol a partir de su nombre.
--      (Se usa al crear/editar usuarios: el nombre del rol seleccionado
--      en pantalla se convierte en el id_rol que guarda la tabla usuarios.)
SELECT `id_rol` FROM `roles` WHERE `nombre_rol` = %s;          -- %s = 'Administrador' | 'Vendedor' | 'Gerente'

-- 1.2. LOGIN: valida credenciales y trae el usuario con su rol.
--      Este JOIN es la razon por la que la tabla `roles` esta normalizada:
--      el rol llega como texto legible (Administrador/Vendedor/Gerente) sin
--      duplicar el nombre en cada fila de usuarios.
SELECT u.*, r.nombre_rol AS `rol`
FROM `usuarios` u
JOIN `roles` r ON u.id_rol = r.id_rol
WHERE u.usuario = %s;                                           -- %s = 'admin'

-- 1.3. Tras un login exitoso se limpian los intentos fallidos y el bloqueo.
UPDATE `usuarios`
SET `intentos_fallidos` = 0, `bloqueado_hasta` = NULL
WHERE `id_usuario` = %s;

-- 1.4. BLOQUEO: si el usuario acumula 5 intentos fallidos (MAX_INTENTOS=5)
--      se le bloquea por 5 minutos (MINUTOS_BLOQUEO=5). El bloqueo se
--      evalua con la funcion DATE_ADD, por eso el cambio de contraseña
--      tambien refleja el corto tiempo del bloqueo en la interfaz.
UPDATE `usuarios`
SET `intentos_fallidos` = 0,
    `bloqueado_hasta` = DATE_ADD(NOW(), INTERVAL %s MINUTE)
WHERE `id_usuario` = %s;                                        -- %s = 5 (minutos), id_usuario

-- 1.5. Registro de un intento fallido (< 5): se incrementa el contador.
UPDATE `usuarios` SET `intentos_fallidos` = %s WHERE `id_usuario` = %s;

-- 1.6. Migracion automatica de contrasenas en texto plano a hash bcrypt:
--      cuando el hash guardado no empieza con "$2", la app lo reemplaza
--      por un hash bcrypt generado en ese momento.
UPDATE `usuarios` SET `contrasena` = %s WHERE `id_usuario` = %s;

-- 1.7. Verificar la contrasena actual del usuario (se usa en el modal de
--      cambio de contraseña y en el reset que exige la clave del admin).
SELECT `contrasena` FROM `usuarios` WHERE `id_usuario` = %s;

-- 1.8. Cambiar la contraseña del propio usuario (cambio_obligatorio = 0:
--      ya no se le exigira cambiarla en el proximo login).
UPDATE `usuarios`
SET `contrasena` = %s, `cambio_obligatorio` = 0
WHERE `id_usuario` = %s;

-- 1.9. Reset de contrasena por el administrador: deja una clave temporal
--      y marca `cambio_obligatorio = 1` para forzar el cambio en el proximo
--      ingreso del usuario.
UPDATE `usuarios`
SET `contrasena` = %s, `cambio_obligatorio` = 1
WHERE `id_usuario` = %s;

-- 1.10. Permisos por modulo de un usuario (un registro por usuario).
SELECT * FROM `permisos_usuario` WHERE `id_usuario` = %s;

-- 1.11. NIVELES DE ACCESO: matriz de permisos por usuario (3 roles).
--       Gerente: inventario, clientes, ventas, categorias, historial y reportes.
--       Sin usuarios ni respaldos (solo el Administrador los tiene).
SELECT u.id_usuario, u.usuario, r.nombre_rol AS `rol`,
       p.`modulo_inventario`, p.`modulo_clientes`, p.`modulo_ventas`,
       p.`modulo_categorias`, p.`modulo_usuarios`, p.`modulo_respaldos`,
       p.`modulo_historial`, p.`modulo_reportes`
FROM `usuarios` u
JOIN `roles` r ON u.id_rol = r.id_rol
JOIN `permisos_usuario` p ON p.id_usuario = u.id_usuario
ORDER BY u.id_usuario;


-- ============================================================================
-- 2. USUARIOS (CRUD)
-- ============================================================================

-- 2.1. Listar usuarios con su rol (para el modulo de administracion).
SELECT u.id_usuario, u.usuario, r.nombre_rol AS `rol`
FROM `usuarios` u
JOIN `roles` r ON u.id_rol = r.id_rol;

-- 2.2. Crear usuario: se inserta en `usuarios` con rol y luego se crea
--      la fila de permisos. Son 2 INSERT dentro de la misma operacion.
--      (La contrasena viaja como hash bcrypt; nunca texto plano.)
INSERT INTO `usuarios` (`usuario`, `contrasena`, `cambio_obligatorio`, `id_rol`)
VALUES (%s, %s, 1, %s);

INSERT INTO `permisos_usuario`
  (`id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`,
   `modulo_categorias`, `modulo_usuarios`, `modulo_respaldos`,
   `modulo_historial`, `modulo_reportes`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);

-- 2.3. Actualizar usuario (con nueva contrasena y rol).
UPDATE `usuarios`
SET `usuario` = %s, `contrasena` = %s, `cambio_obligatorio` = 1, `id_rol` = %s
WHERE `id_usuario` = %s;

-- 2.3b. Actualizar usuario SIN cambiar contrasena.
UPDATE `usuarios` SET `usuario` = %s, `id_rol` = %s WHERE `id_usuario` = %s;

-- 2.3c. Actualizar los permisos del usuario.
UPDATE `permisos_usuario`
SET `modulo_inventario` = %s, `modulo_clientes` = %s, `modulo_ventas` = %s,
    `modulo_categorias` = %s, `modulo_usuarios` = %s, `modulo_respaldos` = %s,
    `modulo_historial` = %s, `modulo_reportes` = %s
WHERE `id_usuario` = %s;

-- 2.4. Eliminar usuario: primero los permisos (FK), luego el usuario.
--      La tabla eventos tiene la FK con ON DELETE SET NULL: si el usuario
--      tiene eventos registrados, la columna id_usuario del evento pasa a
--      NULL (el historial conserva el nombre en la columna usuario).
DELETE FROM `permisos_usuario` WHERE `id_usuario` = %s;
DELETE FROM `usuarios` WHERE `id_usuario` = %s;


-- ============================================================================
-- 3. CLIENTES (CRUD)
-- ============================================================================

-- 3.1. Listar clientes.
SELECT `id_cliente`, `nombre`, `cedula`, `telefono` FROM `clientes` ORDER BY `id_cliente`;

-- 3.2. Buscar cliente por cedula (la cedula es UNIQUE; usado en el modulo
--      de ventas para autocompletar el cliente).
SELECT `id_cliente`, `nombre`, `cedula`, `telefono`
FROM `clientes`
WHERE `cedula` = %s;

-- 3.3. Registrar cliente.
INSERT INTO `clientes` (`nombre`, `cedula`, `telefono`) VALUES (%s, %s, %s);

-- 3.4. Actualizar cliente.
UPDATE `clientes` SET `nombre` = %s, `cedula` = %s, `telefono` = %s
WHERE `id_cliente` = %s;

-- 3.5. Eliminar cliente.
DELETE FROM `clientes` WHERE `id_cliente` = %s;


-- ============================================================================
-- 4. CATEGORIAS (CRUD)
-- ============================================================================

-- 4.1. Listar categorias.
SELECT * FROM `categorias` ORDER BY `id_categoria`;

-- 4.2. Registrar categoria.
INSERT INTO `categorias` (`nombre_categoria`) VALUES (%s);

-- 4.3. Eliminar categoria (dara error si tiene productos asociados,
--      gracias a la FK).
DELETE FROM `categorias` WHERE `id_categoria` = %s;


-- ============================================================================
-- 5. PRODUCTOS, LOTES E INVENTARIO
-- ============================================================================

-- 5.1. Inventario general: LEE DE LA VISTA vista_inventario_general.
--      (La vista agrega el stock total sumando los lotes activos.)
SELECT * FROM `vista_inventario_general`;

-- 5.2. Registrar producto + su primer lote (2 INSERT encadenados).
INSERT INTO `productos` (`nombre_producto`, `id_categoria`) VALUES (%s, %s);
INSERT INTO `lotes` (`id_producto`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`)
VALUES (%s, %s, %s, %s, %s, 'Activo');

-- 5.3. Verificar si un producto tiene algun lote activo con stock.
SELECT COUNT(*) AS `total`
FROM `lotes`
WHERE `id_producto` = %s AND `estado` = 'Activo' AND `stock` > 0;

-- 5.4. Agregar un lote nuevo: primero se deja inactivo el lote actual
--      (el modelo de negocio usa UN lote activo a la vez como lote base)
--      y luego se inserta el nuevo lote Activo.
UPDATE `lotes` SET `estado` = 'Inactivo'
WHERE `id_producto` = %s AND `estado` <> 'Inactivo';
INSERT INTO `lotes` (`id_producto`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`)
VALUES (%s, %s, %s, %s, %s, 'Activo');

-- 5.5. Lotes de un producto (historial completo).
SELECT * FROM `lotes` WHERE `id_producto` = %s;

-- 5.6. Lotes ACTIVOS de un producto.
SELECT * FROM `lotes` WHERE `id_producto` = %s AND `estado` = 'Activo';

-- 5.7. Actualizar datos del producto.
UPDATE `productos` SET `nombre_producto` = %s, `id_categoria` = %s
WHERE `id_producto` = %s;

-- 5.8. Eliminar producto: primero sus lotes (dos DELETE), la FK exige
--      respetar el orden.
DELETE FROM `lotes` WHERE `id_producto` = %s;
DELETE FROM `productos` WHERE `id_producto` = %s;

-- 5.9. Actualizar un lote (stock, costo, precio, vencimiento).
UPDATE `lotes`
SET `stock` = %s, `costo` = %s, `precio` = %s, `fecha_vencimiento` = %s
WHERE `id_lote` = %s;

-- 5.10. Alertas de vencimiento: LEE DE LA VISTA (lotes activos con stock
--       que vencen en 0 a 90 dias).
SELECT * FROM `vista_alertas_vencimiento`;


-- ============================================================================
-- 6. VENTAS Y NOTAS DE ENTREGA
-- ============================================================================

-- 6.1. Conteo de notas de entrega (se muestra en el panel de control).
SELECT COUNT(*) AS `total` FROM `notas_entrega`;

-- 6.2. Siguiente numero de control de nota: lee el AUTO_INCREMENT real de
--      la tabla notas_entrega desde information_schema. Asi el control es
--      el propio numero_nota: correlativo global, nunca se reinicia por anio
--      y nunca se reutiliza (la app lo muestra con 4 digitos: 0009).
SELECT COALESCE(AUTO_INCREMENT, 1) AS `siguiente`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'notas_entrega';

-- 6.3. TRANSACCION DE VENTA (registrar_venta_y_nota).
--      Es la operacion mas importante: 1 INSERT de cabecera + por cada item
--      una consulta de lotes, actualizaciones de stock y 1 INSERT de
--      detalle. Todo se confirma con commit() o se revierte con rollback().
--      ---------------------------------------------------------------
-- 6.3.1. INSERT de la cabecera de la nota. El numero_nota lo asigna
--        AUTO_INCREMENT (PK) y ES el numero de control de la nota.
INSERT INTO `notas_entrega`
  (`id_cliente`, `id_usuario`, `monto_total`, `descuento`, `tipo_descuento`,
   `porcentaje_descuento`, `metodo_pago`, `monto_cancelado`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);

-- 6.3.2. Por CADA item del carrito: seleccionar el LOTE ACTIVO con stock del
--        producto (regla de negocio: un solo lote activo por producto).
--        El ORDER BY queda como resguardo; en la practica solo hay un lote.
SELECT `id_lote`, `stock`
FROM `lotes`
WHERE `id_producto` = %s AND `estado` = 'Activo' AND `stock` > 0
ORDER BY `fecha_vencimiento` ASC;

-- 6.3.3. Si el lote se agota con esta venta: el stock pasa a 0 y el estado
--        NO cambia (sigue 'Activo'); recien al registrar un lote nuevo con
--        "Actualizar Lote" (modulo Inventario) el anterior pasa a 'Inactivo'.
UPDATE `lotes` SET `stock` = 0 WHERE `id_lote` = %s;

-- 6.3.4. Si el lote aun queda stock: solo se actualiza la cantidad.
UPDATE `lotes` SET `stock` = %s WHERE `id_lote` = %s;

-- 6.3.5. INSERT de cada linea de detalle (se repite por cada lote usado).
INSERT INTO `detalle_nota`
  (`numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`,
   `subtotal`, `descuento`, `porcentaje_descuento`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
--      ------------------------------------------------------------------

-- 6.4. Historial de ventas (modulo Ventas): JOIN de notas con cliente y
--      vendedor (usuario). El numero de control se formatea con LPAD.
SELECT n.numero_nota AS `id_venta`,
       LPAD(n.numero_nota, 4, '0') AS `numero_control`,
       c.nombre AS `cliente`, c.cedula, u.usuario AS `vendedor`,
       n.metodo_pago, n.monto_total AS `total`, n.descuento,
       n.tipo_descuento, n.porcentaje_descuento, n.monto_cancelado,
       n.fecha_hora AS `fecha`
FROM `notas_entrega` n
JOIN `clientes` c ON n.id_cliente = c.id_cliente
JOIN `usuarios` u ON n.id_usuario = u.id_usuario
ORDER BY n.fecha_hora DESC;

-- 6.5. Historial de ventas de UN cliente (filtro por id_cliente).
SELECT n.numero_nota AS `id_venta`,
       LPAD(n.numero_nota, 4, '0') AS `numero_control`,
       c.nombre AS `cliente`, c.cedula, u.usuario AS `vendedor`,
       n.metodo_pago, n.monto_total AS `total`, n.descuento,
       n.tipo_descuento, n.porcentaje_descuento, n.monto_cancelado,
       n.fecha_hora AS `fecha`
FROM `notas_entrega` n
JOIN `clientes` c ON n.id_cliente = c.id_cliente
JOIN `usuarios` u ON n.id_usuario = u.id_usuario
WHERE n.id_cliente = %s
ORDER BY n.fecha_hora DESC;

-- 6.6. Cabecera de una nota (para imprimir el PDF de la nota de entrega).
SELECT n.numero_nota, n.metodo_pago, n.monto_total, n.descuento,
       n.tipo_descuento, n.porcentaje_descuento, n.monto_cancelado,
       n.fecha_hora,
       LPAD(n.numero_nota, 4, '0') AS `numero_control`,
       c.nombre AS `cliente`, c.cedula, c.telefono
FROM `notas_entrega` n
JOIN `clientes` c ON n.id_cliente = c.id_cliente
WHERE n.numero_nota = %s;

-- 6.7. Detalle de una nota (lineas de producto, para el PDF).
SELECT p.nombre_producto, d.precio_unitario, d.cantidad, d.descuento,
       d.porcentaje_descuento, d.subtotal
FROM `detalle_nota` d
JOIN `productos` p ON d.id_producto = p.id_producto
WHERE d.numero_nota = %s;


-- ============================================================================
-- 7. BITACORA DE EVENTOS
-- ============================================================================

-- 7.1. Registrar un evento (login, logout, venta, cambio de contrasena,
--      respaldo exportado/importado).
INSERT INTO `eventos` (`id_usuario`, `tipo`, `detalle`) VALUES (%s, %s, %s);

-- 7.2. Listar eventos (bitacora). LEFT JOIN con usuarios porque la FK
--      tiene ON DELETE SET NULL: si el usuario se elimina, su id pasa a
--      NULL y el evento se conserva. Soporta filtros opcionales de
--      busqueda (LIKE) y tipo; la consulta se arma dinamicamente.
SELECT e.id_evento, e.tipo, e.detalle, e.fecha_hora, u.usuario
FROM `eventos` e
LEFT JOIN `usuarios` u ON e.id_usuario = u.id_usuario
-- Filtros opcionales (se agregan dinamicamente):
--   WHERE (u.usuario LIKE %s OR e.detalle LIKE %s)      -> busqueda
--   AND   e.tipo = %s                                   -> filtro por tipo
ORDER BY e.id_evento DESC;


-- ============================================================================
-- 8. RESPALDO DE DATOS (models/backup_model.py)
-- ============================================================================

-- 8.1. Listar las tablas base del esquema (para exportarlas en orden).
SELECT table_name AS `nombre`
FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE';

-- 8.2. Relaciones de FK entre tablas (el respaldo las ordena para poder
--      importarlas sin violar las llaves foraneas).
SELECT TABLE_NAME, REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 8.3. Listar las vistas (se exportan con SHOW CREATE VIEW).
SELECT table_name AS `nombre`
FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_type = 'VIEW';

-- 8.4. Exportar el DDL de cada tabla y vista:
SHOW CREATE TABLE `notas_entrega`;
SHOW CREATE VIEW `vista_inventario_general`;

-- 8.5. Importar un respaldo: se vuelcan todas las filas de cada tabla.
SELECT * FROM `clientes`;

-- 8.6. Al importar se desactivan temporalmente las FKs para recrear el
--      esquema completo y luego se restauran.
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `detalle_nota`;
SET FOREIGN_KEY_CHECKS = 1;


-- ============================================================================
-- 9. REPORTES GERENCIALES (models/report_model.py)
--      La mayoria recibe un rango de fechas. La app calcula ventanas moviles
--      desde hoy hacia atras: semana (7 dias), mes (30 dias) o anio (365 dias),
--      segun el selector del modulo Reportes.
-- ============================================================================

-- 9.1. KPI del modulo: tarjetas resumen (ventas de hoy, del mes, notas
--      totales y producto mas vendido).
SELECT COALESCE(SUM(`monto_total`), 0) AS `ventas_hoy`
FROM `notas_entrega` WHERE DATE(`fecha_hora`) = CURDATE();

SELECT COALESCE(SUM(`monto_total`), 0) AS `ventas_mes`
FROM `notas_entrega`
WHERE YEAR(`fecha_hora`) = YEAR(CURDATE()) AND MONTH(`fecha_hora`) = MONTH(CURDATE());

SELECT COUNT(*) AS `notas` FROM `notas_entrega`;

SELECT p.nombre_producto, SUM(d.cantidad) AS `unidades`
FROM `detalle_nota` d
JOIN `productos` p ON d.id_producto = p.id_producto
GROUP BY p.id_producto, p.nombre_producto
ORDER BY `unidades` DESC LIMIT 1;

-- 9.2. Ventas por periodo: una fila por dia con notas y total.
SELECT DATE(n.fecha_hora) AS `dia`, COUNT(*) AS `notas`, SUM(n.monto_total) AS `total`
FROM `notas_entrega` n
WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
GROUP BY DATE(n.fecha_hora)
ORDER BY `dia` DESC;

-- 9.3. Productos mas vendidos del periodo: unidades e ingresos.
SELECT p.nombre_producto, COALESCE(v.unidades, 0) AS `unidades`,
       COALESCE(v.ingresos, 0) AS `ingresos`
FROM `productos` p
LEFT JOIN (
    SELECT d.id_producto, SUM(d.cantidad) AS unidades, SUM(d.subtotal) AS ingresos
    FROM `detalle_nota` d
    JOIN `notas_entrega` n ON d.numero_nota = n.numero_nota
    WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
    GROUP BY d.id_producto
) v ON v.id_producto = p.id_producto
ORDER BY `unidades` DESC;

-- 9.4. Productos MENOS vendidos (o sin ventas) del periodo.
--      La subconsulta filtra por fecha ANTES de agrupar: los productos sin
--      ventas en el periodo aparecen con 0, sin contaminar con ventas de
--      otra fecha.
SELECT p.nombre_producto, COALESCE(v.unidades, 0) AS `unidades`,
       COALESCE(v.ingresos, 0) AS `ingresos`
FROM `productos` p
LEFT JOIN (
    SELECT d.id_producto, SUM(d.cantidad) AS unidades, SUM(d.subtotal) AS ingresos
    FROM `detalle_nota` d
    JOIN `notas_entrega` n ON d.numero_nota = n.numero_nota
    WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
    GROUP BY d.id_producto
) v ON v.id_producto = p.id_producto
ORDER BY `unidades` ASC;

-- 9.5. Ventas por cliente del periodo.
SELECT c.nombre, COUNT(*) AS `notas`, SUM(n.monto_total) AS `total`
FROM `notas_entrega` n
JOIN `clientes` c ON n.id_cliente = c.id_cliente
WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
GROUP BY c.id_cliente, c.nombre
ORDER BY `total` DESC;

-- 9.6. Ventas por vendedor del periodo.
SELECT u.usuario, COUNT(*) AS `notas`, SUM(n.monto_total) AS `total`
FROM `notas_entrega` n
JOIN `usuarios` u ON n.id_usuario = u.id_usuario
WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
GROUP BY u.id_usuario, u.usuario
ORDER BY `total` DESC;

-- 9.7. Ventas por metodo de pago del periodo.
SELECT n.`metodo_pago`, COUNT(*) AS `notas`, SUM(n.monto_total) AS `total`
FROM `notas_entrega` n
WHERE DATE(n.fecha_hora) BETWEEN %s AND %s
GROUP BY n.metodo_pago
ORDER BY `total` DESC;

-- 9.8. Descuentos aplicados en el periodo (total descontado en USD y
--      cantidad de notas que llevaron descuento).
SELECT COUNT(*) AS `notas`,
       COUNT(CASE WHEN n.`descuento` > 0 THEN 1 END) AS `notas_con_descuento`,
       COALESCE(SUM(n.`descuento`), 0) AS `total_descontado`
FROM `notas_entrega` n
WHERE DATE(n.fecha_hora) BETWEEN %s AND %s;

-- 9.9. Productos con stock bajo (suma de lotes activos <= limite).
SELECT p.nombre_producto, COALESCE(SUM(l.stock), 0) AS `stock`
FROM `productos` p
LEFT JOIN `lotes` l ON l.id_producto = p.id_producto AND l.estado = 'Activo'
GROUP BY p.id_producto, p.nombre_producto
HAVING `stock` <= %s
ORDER BY `stock` ASC;

-- 9.10. Clientes inactivos: sin compras o cuya ultima compra supera el
--       periodo indicado (ej. 30/60/90 dias).
SELECT c.nombre, c.cedula, c.telefono,
       MAX(n.fecha_hora) AS `ultima_venta`
FROM `clientes` c
LEFT JOIN `notas_entrega` n ON n.id_cliente = c.id_cliente
GROUP BY c.id_cliente, c.nombre, c.cedula, c.telefono
HAVING MAX(n.fecha_hora) IS NULL
    OR MAX(n.fecha_hora) < DATE_SUB(NOW(), INTERVAL %s DAY)
ORDER BY `ultima_venta` ASC;

-- 9.11. Vencimientos de lotes: por defecto muestra TODOS los lotes activos
--       con stock, ordenados del que vence primero. El filtro opcional de
--       dias (30/60/90) agrega BETWEEN 0 AND %s para acotar el rango.
SELECT p.nombre_producto, l.id_lote AS `lote`, l.stock,
       l.fecha_vencimiento AS `vencimiento`,
       (TO_DAYS(l.fecha_vencimiento) - TO_DAYS(CURDATE())) AS `dias`
FROM `lotes` l
JOIN `productos` p ON l.id_producto = p.id_producto
WHERE l.estado = 'Activo' AND l.stock > 0
ORDER BY l.fecha_vencimiento ASC;


-- ============================================================================
-- ANEXO A. VISTAS QUE CONSULTA LA APLICACION (definidas en suplestore_db_full.sql)
-- ============================================================================

-- A.1. Vista de inventario general: sumariza el stock por producto
--      sumando SOLO los lotes activos.
CREATE OR REPLACE VIEW `vista_inventario_general` AS
SELECT
  p.`id_producto`      AS `id`,
  p.`nombre_producto`  AS `Producto`,
  c.`nombre_categoria` AS `Categoria`,
  COALESCE(SUM(l.`stock`), 0) AS `Stock`
FROM `productos` p
JOIN `categorias` c ON p.`id_categoria` = c.`id_categoria`
LEFT JOIN `lotes` l
  ON p.`id_producto` = l.`id_producto` AND l.`estado` = 'Activo'
GROUP BY p.`id_producto`, p.`nombre_producto`, c.`nombre_categoria`;

-- A.2. Vista de alertas de vencimiento: lotes activos con stock que
--      vencen en los proximos 0 a 90 dias.
CREATE OR REPLACE VIEW `vista_alertas_vencimiento` AS
SELECT
  p.`nombre_producto`   AS `Producto`,
  l.`id_lote`           AS `Lote_ID`,
  l.`stock`             AS `Stock`,
  l.`fecha_vencimiento` AS `Vencimiento`,
  (TO_DAYS(l.`fecha_vencimiento`) - TO_DAYS(CURDATE())) AS `Dias_Restantes`
FROM `lotes` l
JOIN `productos` p ON l.`id_producto` = p.`id_producto`
WHERE l.`estado` = 'Activo'
  AND l.`stock` > 0
  AND (TO_DAYS(l.`fecha_vencimiento`) - TO_DAYS(CURDATE())) BETWEEN 0 AND 90
ORDER BY l.`fecha_vencimiento`;
-- ============================================================================
-- SCRIPT COMPLETO: Base de Datos Suplestore Tachira
-- Descripcion: Creacion de BD, tablas, datos iniciales, vistas,
--              procedimientos almacenados y funciones de validacion.
-- Uso: Ejecutar completo en MySQL 8.0+ 
--       > mysql -u root -p < suplestore_db_full.sql
-- ============================================================================

-- ============================================================================
-- 1. CREACION DE LA BASE DE DATOS
-- ============================================================================
CREATE DATABASE IF NOT EXISTS `suplestore_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_spanish_ci;

USE `suplestore_db`;

-- ============================================================================
-- 2. TABLAS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 2.1. usuarios: almacena credenciales y rol de cada usuario del sistema
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario`   INT         NOT NULL AUTO_INCREMENT,
  `usuario`      VARCHAR(50) NOT NULL,
  `contrasena`   VARCHAR(255) NOT NULL,
  `cambio_obligatorio` TINYINT(1) NOT NULL DEFAULT 0,
  `intentos_fallidos` INT NOT NULL DEFAULT 0,
  `bloqueado_hasta` DATETIME DEFAULT NULL,
  `rol`          ENUM('Administrador','Vendedor') NOT NULL DEFAULT 'Vendedor',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `uk_usuario` (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.2. permisos_usuario: permisos por modulo para cada usuario (1=acceso)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `permisos_usuario` (
  `id_permiso`       INT NOT NULL AUTO_INCREMENT,
  `id_usuario`       INT NOT NULL,
  `modulo_inventario` TINYINT(1) DEFAULT 0,
  `modulo_clientes`  TINYINT(1) DEFAULT 0,
  `modulo_ventas`    TINYINT(1) DEFAULT 0,
  `modulo_categorias` TINYINT(1) DEFAULT 0,
  `modulo_usuarios`  TINYINT(1) DEFAULT 0,
  `modulo_historial` TINYINT(1) DEFAULT 0,
  PRIMARY KEY (`id_permiso`),
  KEY `fk_permisos_usuario` (`id_usuario`),
  CONSTRAINT `fk_permisos_usuario` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.3. categorias: clasificacion de productos
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `categorias` (
  `id_categoria`    INT         NOT NULL AUTO_INCREMENT,
  `nombre_categoria` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `uk_nombre_categoria` (`nombre_categoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.4. clientes: personas naturales o juridicas que realizan compras
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientes` (
  `id_cliente` INT         NOT NULL AUTO_INCREMENT,
  `nombre`     VARCHAR(150) NOT NULL,
  `cedula`     VARCHAR(20) NOT NULL,
  `telefono`   VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `uk_cedula` (`cedula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.5. productos: items del inventario, pertenecen a una categoria
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `productos` (
  `id_producto`    INT         NOT NULL AUTO_INCREMENT,
  `nombre_producto` VARCHAR(150) NOT NULL,
  `id_categoria`   INT         NOT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `fk_productos_categoria` (`id_categoria`),
  CONSTRAINT `fk_productos_categoria` FOREIGN KEY (`id_categoria`)
    REFERENCES `categorias` (`id_categoria`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.6. lotes: unidades de un producto con stock, costo, precio y vencimiento
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lotes` (
  `id_lote`          INT            NOT NULL AUTO_INCREMENT,
  `id_producto`      INT            NOT NULL,
  `stock`            INT            NOT NULL DEFAULT 0,
  `costo`            DECIMAL(10,2)  NOT NULL,
  `precio`           DECIMAL(10,2)  NOT NULL,
  `fecha_vencimiento` DATE          NOT NULL,
  `estado`           ENUM('Activo','Agotado','Inactivo') DEFAULT 'Activo',
  PRIMARY KEY (`id_lote`),
  KEY `fk_lotes_producto` (`id_producto`),
  CONSTRAINT `fk_lotes_producto` FOREIGN KEY (`id_producto`)
    REFERENCES `productos` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.7. notas_entrega: cabecera de cada venta o nota de entrega
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notas_entrega` (
  `numero_nota`    INT           NOT NULL AUTO_INCREMENT,
  `id_cliente`     INT           NOT NULL,
  `id_usuario`     INT           NOT NULL,
  `fecha_hora`     DATETIME      DEFAULT CURRENT_TIMESTAMP,
  `anio`           SMALLINT      NOT NULL,
  `secuencia`      INT           NOT NULL,
  `monto_total`    DECIMAL(10,2) NOT NULL,
  `descuento`      DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `metodo_pago`    VARCHAR(50)   NOT NULL,
  `monto_cancelado` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`numero_nota`),
  UNIQUE KEY `uk_anio_secuencia` (`anio`, `secuencia`),
  KEY `fk_notas_cliente` (`id_cliente`),
  KEY `fk_notas_usuario` (`id_usuario`),
  CONSTRAINT `fk_notas_cliente` FOREIGN KEY (`id_cliente`)
    REFERENCES `clientes` (`id_cliente`) ON UPDATE CASCADE,
  CONSTRAINT `fk_notas_usuario` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.8. detalle_nota: lineas de producto de cada nota de entrega
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `detalle_nota` (
  `id_detalle`     INT           NOT NULL AUTO_INCREMENT,
  `numero_nota`    INT           NOT NULL,
  `id_producto`    INT           NOT NULL,
  `id_lote`        INT           NOT NULL,
  `precio_unitario` DECIMAL(10,2) NOT NULL,
  `cantidad`       INT           NOT NULL,
  `subtotal`       DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `fk_detalle_nota` (`numero_nota`),
  KEY `fk_detalle_producto` (`id_producto`),
  KEY `fk_detalle_lote` (`id_lote`),
  CONSTRAINT `fk_detalle_nota` FOREIGN KEY (`numero_nota`)
    REFERENCES `notas_entrega` (`numero_nota`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_producto` FOREIGN KEY (`id_producto`)
    REFERENCES `productos` (`id_producto`) ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_lote` FOREIGN KEY (`id_lote`)
    REFERENCES `lotes` (`id_lote`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.9. secuencia_notas: consecutivo de notas de entrega por anio (reinicio anual)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `secuencia_notas` (
  `anio`        SMALLINT NOT NULL,
  `consecutivo` INT      NOT NULL,
  PRIMARY KEY (`anio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ----------------------------------------------------------------------------
-- 2.10. eventos: bitacora de actividades del sistema (logs)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `eventos` (
  `id_evento`  INT           NOT NULL AUTO_INCREMENT,
  `id_usuario` INT           DEFAULT NULL,
  `tipo`       VARCHAR(50)   NOT NULL,
  `detalle`    VARCHAR(255)  DEFAULT NULL,
  `fecha_hora` DATETIME      DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_evento`),
  KEY `fk_eventos_usuario` (`id_usuario`),
  CONSTRAINT `fk_eventos_usuario` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuarios` (`id_usuario`) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

-- ============================================================================
-- 3. DATOS INICIALES
-- ============================================================================

-- 3.1. Usuario administrador por defecto (contrasena encriptada con bcrypt)
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `contrasena`, `cambio_obligatorio`, `rol`) VALUES
(1, 'admin', '$2b$12$SAq2ICEdCuOwAyYLI86rFOsVtE8E0wk.F6TCgCEJMoraSWJkygTSa', 0, 'Administrador');

-- 3.2. Permisos totales para el administrador
INSERT INTO `permisos_usuario` (`id_usuario`, `modulo_inventario`, `modulo_clientes`, `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`) VALUES
(1, 1, 1, 1, 1, 1, 1);

-- 3.3. Cliente generico para ventas sin cliente definido
INSERT INTO `clientes` (`id_cliente`, `nombre`, `cedula`, `telefono`) VALUES
(1, 'Cliente General', 'V-00000000', '0414-0000000');

-- 3.4. Reinicio de auto-increment para tablas vacias
ALTER TABLE `categorias`  AUTO_INCREMENT = 1;
ALTER TABLE `productos`   AUTO_INCREMENT = 1;
ALTER TABLE `lotes`       AUTO_INCREMENT = 1;
ALTER TABLE `notas_entrega`  AUTO_INCREMENT = 1;
ALTER TABLE `detalle_nota`   AUTO_INCREMENT = 1;

-- ============================================================================
-- 4. VISTAS
-- ============================================================================

-- 4.1. Vista del inventario general (producto, categoria, stock total)
CREATE OR REPLACE VIEW `vista_inventario_general` AS
SELECT
  p.`id_producto`      AS `id_producto`,
  p.`nombre_producto`  AS `Producto`,
  c.`nombre_categoria` AS `Categoria`,
  COALESCE(SUM(l.`stock`), 0) AS `Stock_Total`
FROM `productos` p
JOIN `categorias` c ON p.`id_categoria` = c.`id_categoria`
LEFT JOIN `lotes` l ON p.`id_producto` = l.`id_producto` AND l.`estado` = 'Activo'
GROUP BY p.`id_producto`, p.`nombre_producto`, c.`nombre_categoria`;

-- 4.2. Vista de alertas de vencimiento (productos con vencimiento en 0-90 dias)
CREATE OR REPLACE VIEW `vista_alertas_vencimiento` AS
SELECT
  p.`nombre_producto`          AS `Producto`,
  l.`id_lote`                  AS `Lote_ID`,
  l.`stock`                    AS `Stock`,
  l.`fecha_vencimiento`        AS `Vencimiento`,
  DATEDIFF(l.`fecha_vencimiento`, CURDATE()) AS `Dias_Restantes`
FROM `lotes` l
JOIN `productos` p ON l.`id_producto` = p.`id_producto`
WHERE l.`estado` = 'Activo'
  AND l.`stock` > 0
  AND DATEDIFF(l.`fecha_vencimiento`, CURDATE()) BETWEEN 0 AND 90
ORDER BY l.`fecha_vencimiento`;

-- ============================================================================
-- 5. FUNCIONES DE VALIDACION
-- ============================================================================

DELIMITER $$

-- 5.1. Verifica si una cedula ya existe (opcionalmente excluye un id_cliente)
CREATE FUNCTION IF NOT EXISTS `fn_cedula_unica`(
  p_cedula     VARCHAR(20),
  p_excluir_id INT
) RETURNS BOOLEAN
  DETERMINISTIC
  READS SQL DATA
BEGIN
  DECLARE v_exist INT;
  IF p_excluir_id IS NULL THEN
    SELECT COUNT(*) INTO v_exist FROM `clientes` WHERE `cedula` = p_cedula;
  ELSE
    SELECT COUNT(*) INTO v_exist
    FROM `clientes`
    WHERE `cedula` = p_cedula AND `id_cliente` != p_excluir_id;
  END IF;
  RETURN v_exist = 0;
END$$

-- 5.2. Verifica si un nombre de usuario ya existe (opcionalmente excluye un id_usuario)
CREATE FUNCTION IF NOT EXISTS `fn_usuario_unico`(
  p_usuario    VARCHAR(50),
  p_excluir_id INT
) RETURNS BOOLEAN
  DETERMINISTIC
  READS SQL DATA
BEGIN
  DECLARE v_exist INT;
  IF p_excluir_id IS NULL THEN
    SELECT COUNT(*) INTO v_exist FROM `usuarios` WHERE `usuario` = p_usuario;
  ELSE
    SELECT COUNT(*) INTO v_exist
    FROM `usuarios`
    WHERE `usuario` = p_usuario AND `id_usuario` != p_excluir_id;
  END IF;
  RETURN v_exist = 0;
END$$

-- 5.3. Verifica si un nombre de categoria ya existe (opcionalmente excluye un id_categoria)
CREATE FUNCTION IF NOT EXISTS `fn_categoria_unica`(
  p_nombre     VARCHAR(100),
  p_excluir_id INT
) RETURNS BOOLEAN
  DETERMINISTIC
  READS SQL DATA
BEGIN
  DECLARE v_exist INT;
  IF p_excluir_id IS NULL THEN
    SELECT COUNT(*) INTO v_exist FROM `categorias` WHERE `nombre_categoria` = p_nombre;
  ELSE
    SELECT COUNT(*) INTO v_exist
    FROM `categorias`
    WHERE `nombre_categoria` = p_nombre AND `id_categoria` != p_excluir_id;
  END IF;
  RETURN v_exist = 0;
END$$

-- 5.4. Calcula el stock total activo de un producto sumando todos sus lotes
CREATE FUNCTION IF NOT EXISTS `fn_stock_producto`(p_id_producto INT) RETURNS INT
  DETERMINISTIC
  READS SQL DATA
BEGIN
  DECLARE v_stock INT;
  SELECT COALESCE(SUM(`stock`), 0) INTO v_stock
  FROM `lotes`
  WHERE `id_producto` = p_id_producto AND `estado` = 'Activo';
  RETURN v_stock;
END$$

-- ============================================================================
-- 6. PROCEDIMIENTOS ALMACENADOS - USUARIOS
-- ============================================================================

-- 6.1. Login: valida credenciales y devuelve datos del usuario
CREATE PROCEDURE IF NOT EXISTS `sp_validar_login`(
  IN p_usuario    VARCHAR(50),
  IN p_contrasena VARCHAR(255)
)
BEGIN
  SELECT `id_usuario`, `usuario`, `rol`
  FROM `usuarios`
  WHERE `usuario` = p_usuario AND `contrasena` = p_contrasena;
END$$

-- 6.2. Obtener todos los usuarios (sin contrasena por seguridad)
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_usuarios`()
BEGIN
  SELECT `id_usuario`, `usuario`, `rol` FROM `usuarios` ORDER BY `id_usuario`;
END$$

-- 6.3. Obtener un usuario por su ID
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_usuario`(IN p_id_usuario INT)
BEGIN
  SELECT `id_usuario`, `usuario`, `rol` FROM `usuarios` WHERE `id_usuario` = p_id_usuario;
END$$

-- 6.4. Insertar un nuevo usuario con sus permisos
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_usuario`(
  IN p_usuario    VARCHAR(50),
  IN p_contrasena VARCHAR(255),
  IN p_rol        VARCHAR(20),
  IN p_perm_inv   TINYINT,
  IN p_perm_cli   TINYINT,
  IN p_perm_ven   TINYINT,
  IN p_perm_cat   TINYINT,
  IN p_perm_usu   TINYINT,
  IN p_perm_his   TINYINT
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  INSERT INTO `usuarios` (`usuario`, `contrasena`, `rol`)
  VALUES (p_usuario, p_contrasena, p_rol);
  SET @id_nuevo = LAST_INSERT_ID();
  INSERT INTO `permisos_usuario` (`id_usuario`, `modulo_inventario`, `modulo_clientes`,
    `modulo_ventas`, `modulo_categorias`, `modulo_usuarios`, `modulo_historial`)
  VALUES (@id_nuevo, p_perm_inv, p_perm_cli, p_perm_ven, p_perm_cat, p_perm_usu, p_perm_his);
  COMMIT;
  SELECT @id_nuevo AS id_usuario_insertado;
END$$

-- 6.5. Actualizar un usuario (si contrasena vacia no la modifica)
CREATE PROCEDURE IF NOT EXISTS `sp_actualizar_usuario`(
  IN p_id_usuario  INT,
  IN p_usuario     VARCHAR(50),
  IN p_contrasena  VARCHAR(255),
  IN p_rol         VARCHAR(20),
  IN p_perm_inv    TINYINT,
  IN p_perm_cli    TINYINT,
  IN p_perm_ven    TINYINT,
  IN p_perm_cat    TINYINT,
  IN p_perm_usu    TINYINT,
  IN p_perm_his    TINYINT
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  IF p_contrasena IS NOT NULL AND p_contrasena != '' THEN
    UPDATE `usuarios`
    SET `usuario` = p_usuario, `contrasena` = p_contrasena, `rol` = p_rol
    WHERE `id_usuario` = p_id_usuario;
  ELSE
    UPDATE `usuarios`
    SET `usuario` = p_usuario, `rol` = p_rol
    WHERE `id_usuario` = p_id_usuario;
  END IF;
  UPDATE `permisos_usuario`
  SET `modulo_inventario` = p_perm_inv, `modulo_clientes` = p_perm_cli,
      `modulo_ventas` = p_perm_ven, `modulo_categorias` = p_perm_cat,
      `modulo_usuarios` = p_perm_usu, `modulo_historial` = p_perm_his
  WHERE `id_usuario` = p_id_usuario;
  COMMIT;
END$$

-- 6.6. Eliminar un usuario (CASCADE elimina permisos automaticamente)
CREATE PROCEDURE IF NOT EXISTS `sp_eliminar_usuario`(IN p_id_usuario INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  DELETE FROM `usuarios` WHERE `id_usuario` = p_id_usuario;
  COMMIT;
END$$

-- 6.7. Obtener permisos de un usuario
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_permisos`(IN p_id_usuario INT)
BEGIN
  SELECT `modulo_inventario`, `modulo_clientes`, `modulo_ventas`,
         `modulo_categorias`, `modulo_usuarios`, `modulo_historial`
  FROM `permisos_usuario`
  WHERE `id_usuario` = p_id_usuario;
END$$

-- ============================================================================
-- 7. PROCEDIMIENTOS ALMACENADOS - CLIENTES
-- ============================================================================

-- 7.1. Obtener todos los clientes
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_clientes`()
BEGIN
  SELECT `id_cliente`, `nombre`, `cedula`, `telefono`
  FROM `clientes`
  ORDER BY `id_cliente`;
END$$

-- 7.2. Buscar clientes por nombre, cedula o telefono
CREATE PROCEDURE IF NOT EXISTS `sp_buscar_clientes`(IN p_termino VARCHAR(100))
BEGIN
  SET p_termino = CONCAT('%', p_termino, '%');
  SELECT `id_cliente`, `nombre`, `cedula`, `telefono`
  FROM `clientes`
  WHERE `nombre` LIKE p_termino OR `cedula` LIKE p_termino OR `telefono` LIKE p_termino
  ORDER BY `nombre`;
END$$

-- 7.3. Insertar un nuevo cliente
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_cliente`(
  IN p_nombre   VARCHAR(150),
  IN p_cedula   VARCHAR(20),
  IN p_telefono VARCHAR(20)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  INSERT INTO `clientes` (`nombre`, `cedula`, `telefono`)
  VALUES (p_nombre, p_cedula, p_telefono);
  COMMIT;
  SELECT LAST_INSERT_ID() AS id_cliente_insertado;
END$$

-- 7.4. Actualizar un cliente
CREATE PROCEDURE IF NOT EXISTS `sp_actualizar_cliente`(
  IN p_id_cliente INT,
  IN p_nombre     VARCHAR(150),
  IN p_cedula     VARCHAR(20),
  IN p_telefono   VARCHAR(20)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  UPDATE `clientes`
  SET `nombre` = p_nombre, `cedula` = p_cedula, `telefono` = p_telefono
  WHERE `id_cliente` = p_id_cliente;
  COMMIT;
END$$

-- 7.5. Eliminar un cliente
CREATE PROCEDURE IF NOT EXISTS `sp_eliminar_cliente`(IN p_id_cliente INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  DELETE FROM `clientes` WHERE `id_cliente` = p_id_cliente;
  COMMIT;
END$$

-- ============================================================================
-- 8. PROCEDIMIENTOS ALMACENADOS - CATEGORIAS
-- ============================================================================

-- 8.1. Obtener todas las categorias
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_categorias`()
BEGIN
  SELECT `id_categoria`, `nombre_categoria`
  FROM `categorias`
  ORDER BY `id_categoria`;
END$$

-- 8.2. Insertar una nueva categoria
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_categoria`(IN p_nombre VARCHAR(100))
BEGIN
  INSERT INTO `categorias` (`nombre_categoria`) VALUES (p_nombre);
  SELECT LAST_INSERT_ID() AS id_categoria_insertada;
END$$

-- 8.3. Actualizar una categoria
CREATE PROCEDURE IF NOT EXISTS `sp_actualizar_categoria`(
  IN p_id_categoria INT,
  IN p_nombre       VARCHAR(100)
)
BEGIN
  UPDATE `categorias`
  SET `nombre_categoria` = p_nombre
  WHERE `id_categoria` = p_id_categoria;
END$$

-- 8.4. Eliminar una categoria (falla si tiene productos asociados)
CREATE PROCEDURE IF NOT EXISTS `sp_eliminar_categoria`(IN p_id_categoria INT)
BEGIN
  DELETE FROM `categorias` WHERE `id_categoria` = p_id_categoria;
END$$

-- ============================================================================
-- 9. PROCEDIMIENTOS ALMACENADOS - PRODUCTOS Y LOTES (INVENTARIO)
-- ============================================================================

-- 9.1. Obtener vista del inventario general
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_inventario`()
BEGIN
  SELECT * FROM `vista_inventario_general`;
END$$

-- 9.2. Obtener todos los productos
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_productos`()
BEGIN
  SELECT p.`id_producto`, p.`nombre_producto`, c.`nombre_categoria`, c.`id_categoria`
  FROM `productos` p
  JOIN `categorias` c ON p.`id_categoria` = c.`id_categoria`
  ORDER BY p.`nombre_producto`;
END$$

-- 9.3. Insertar un producto (sin lote)
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_producto`(
  IN p_nombre      VARCHAR(150),
  IN p_id_categoria INT
)
BEGIN
  INSERT INTO `productos` (`nombre_producto`, `id_categoria`)
  VALUES (p_nombre, p_id_categoria);
  SELECT LAST_INSERT_ID() AS id_producto_insertado;
END$$

-- 9.4. Actualizar un producto
CREATE PROCEDURE IF NOT EXISTS `sp_actualizar_producto`(
  IN p_id_producto  INT,
  IN p_nombre       VARCHAR(150),
  IN p_id_categoria  INT
)
BEGIN
  UPDATE `productos`
  SET `nombre_producto` = p_nombre, `id_categoria` = p_id_categoria
  WHERE `id_producto` = p_id_producto;
END$$

-- 9.5. Eliminar producto y sus lotes (CASCADE)
CREATE PROCEDURE IF NOT EXISTS `sp_eliminar_producto`(IN p_id_producto INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  DELETE FROM `lotes` WHERE `id_producto` = p_id_producto;
  DELETE FROM `productos` WHERE `id_producto` = p_id_producto;
  COMMIT;
END$$

-- 9.6. Insertar un lote para un producto existente
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_lote`(
  IN p_id_producto      INT,
  IN p_stock            INT,
  IN p_costo            DECIMAL(10,2),
  IN p_precio           DECIMAL(10,2),
  IN p_fecha_vencimiento DATE
)
BEGIN
  INSERT INTO `lotes` (`id_producto`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`)
  VALUES (p_id_producto, p_stock, p_costo, p_precio, p_fecha_vencimiento, 'Activo');
  SELECT LAST_INSERT_ID() AS id_lote_insertado;
END$$

-- 9.7. Actualizar un lote
CREATE PROCEDURE IF NOT EXISTS `sp_actualizar_lote`(
  IN p_id_lote           INT,
  IN p_stock             INT,
  IN p_costo             DECIMAL(10,2),
  IN p_precio            DECIMAL(10,2),
  IN p_fecha_vencimiento DATE
)
BEGIN
  UPDATE `lotes`
  SET `stock` = p_stock, `costo` = p_costo, `precio` = p_precio,
      `fecha_vencimiento` = p_fecha_vencimiento
  WHERE `id_lote` = p_id_lote;
END$$

-- 9.8. Registrar producto + lote en una sola transaccion
CREATE PROCEDURE IF NOT EXISTS `sp_registrar_producto_con_lote`(
  IN p_nombre_prod       VARCHAR(150),
  IN p_id_categoria       INT,
  IN p_stock             INT,
  IN p_costo             DECIMAL(10,2),
  IN p_precio            DECIMAL(10,2),
  IN p_fecha_vencimiento DATE
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  INSERT INTO `productos` (`nombre_producto`, `id_categoria`)
  VALUES (p_nombre_prod, p_id_categoria);
  SET @id_prod = LAST_INSERT_ID();
  INSERT INTO `lotes` (`id_producto`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`)
  VALUES (@id_prod, p_stock, p_costo, p_precio, p_fecha_vencimiento, 'Activo');
  COMMIT;
  SELECT @id_prod AS id_producto_insertado, LAST_INSERT_ID() AS id_lote_insertado;
END$$

-- 9.9. Obtener lotes de un producto
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_lotes_por_producto`(IN p_id_producto INT)
BEGIN
  SELECT `id_lote`, `stock`, `costo`, `precio`, `fecha_vencimiento`, `estado`
  FROM `lotes`
  WHERE `id_producto` = p_id_producto
  ORDER BY `fecha_vencimiento`;
END$$

-- 9.10. Cambiar estado de un lote
CREATE PROCEDURE IF NOT EXISTS `sp_cambiar_estado_lote`(
  IN p_id_lote INT,
  IN p_estado  VARCHAR(20)
)
BEGIN
  UPDATE `lotes` SET `estado` = p_estado WHERE `id_lote` = p_id_lote;
END$$

-- 9.11. Obtener alertas de vencimiento
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_alertas_vencimiento`()
BEGIN
  SELECT * FROM `vista_alertas_vencimiento`;
END$$

-- ============================================================================
-- 10. PROCEDIMIENTOS ALMACENADOS - VENTAS / NOTAS DE ENTREGA
-- ============================================================================

-- 10.1. Registrar una venta completa con descuento de stock por lote (FIFO)
CREATE PROCEDURE IF NOT EXISTS `sp_registrar_venta`(
  IN p_id_usuario    INT,
  IN p_id_cliente    INT,
  IN p_metodo_pago   VARCHAR(50),
  IN p_monto_total   DECIMAL(10,2),
  IN p_monto_cancelado DECIMAL(10,2)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;
  START TRANSACTION;
  INSERT INTO `notas_entrega` (`id_cliente`, `id_usuario`, `monto_total`, `metodo_pago`, `monto_cancelado`)
  VALUES (p_id_cliente, p_id_usuario, p_monto_total, p_metodo_pago, p_monto_cancelado);
  COMMIT;
  SELECT LAST_INSERT_ID() AS numero_nota_generado;
END$$

-- 10.2. Insertar detalle de nota (linea de producto vendido)
CREATE PROCEDURE IF NOT EXISTS `sp_insertar_detalle_nota`(
  IN p_numero_nota    INT,
  IN p_id_producto    INT,
  IN p_id_lote        INT,
  IN p_precio_unitario DECIMAL(10,2),
  IN p_cantidad       INT,
  IN p_subtotal       DECIMAL(10,2)
)
BEGIN
  INSERT INTO `detalle_nota` (`numero_nota`, `id_producto`, `id_lote`, `precio_unitario`, `cantidad`, `subtotal`)
  VALUES (p_numero_nota, p_id_producto, p_id_lote, p_precio_unitario, p_cantidad, p_subtotal);
END$$

-- 10.3. Descontar stock de un lote especifico (usado durante la venta)
CREATE PROCEDURE IF NOT EXISTS `sp_descontar_stock_lote`(
  IN p_id_lote INT,
  IN p_cantidad INT
)
BEGIN
  DECLARE v_stock_actual INT;
  SELECT `stock` INTO v_stock_actual FROM `lotes` WHERE `id_lote` = p_id_lote;
  IF v_stock_actual - p_cantidad <= 0 THEN
    UPDATE `lotes`
    SET `stock` = 0, `estado` = 'Agotado'
    WHERE `id_lote` = p_id_lote;
  ELSE
    UPDATE `lotes`
    SET `stock` = `stock` - p_cantidad
    WHERE `id_lote` = p_id_lote;
  END IF;
END$$

-- 10.4. Obtener todas las notas de entrega con datos del cliente y vendedor
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_historial_ventas`()
BEGIN
  SELECT
    n.`numero_nota`   AS `id_venta`,
    c.`nombre`        AS `cliente`,
    u.`usuario`       AS `vendedor`,
    n.`metodo_pago`,
    n.`monto_total`   AS `total`,
    n.`monto_cancelado`,
    n.`fecha_hora`    AS `fecha`
  FROM `notas_entrega` n
  JOIN `clientes` c ON n.`id_cliente` = c.`id_cliente`
  JOIN `usuarios` u ON n.`id_usuario` = u.`id_usuario`
  ORDER BY n.`fecha_hora` DESC;
END$$

-- 10.5. Obtener una nota de entrega por su numero
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_nota_por_numero`(IN p_numero_nota INT)
BEGIN
  SELECT
    n.`numero_nota`, n.`fecha_hora`, n.`monto_total`,
    n.`metodo_pago`, n.`monto_cancelado`,
    c.`nombre` AS `cliente`, c.`cedula`,
    u.`usuario` AS `vendedor`
  FROM `notas_entrega` n
  JOIN `clientes` c ON n.`id_cliente` = c.`id_cliente`
  JOIN `usuarios` u ON n.`id_usuario` = u.`id_usuario`
  WHERE n.`numero_nota` = p_numero_nota;
END$$

-- 10.6. Obtener los detalles (productos) de una nota de entrega
CREATE PROCEDURE IF NOT EXISTS `sp_obtener_detalles_nota`(IN p_numero_nota INT)
BEGIN
  SELECT
    p.`nombre_producto`,
    d.`precio_unitario`,
    d.`cantidad`,
    d.`subtotal`
  FROM `detalle_nota` d
  JOIN `productos` p ON d.`id_producto` = p.`id_producto`
  WHERE d.`numero_nota` = p_numero_nota;
END$$

-- ============================================================================
-- 11. PROCEDIMIENTOS ALMACENADOS - REPORTES Y CONSULTAS AVANZADAS
-- ============================================================================

-- 11.1. Ventas realizadas en un rango de fechas
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_ventas_por_fecha`(
  IN p_fecha_desde DATE,
  IN p_fecha_hasta DATE
)
BEGIN
  SELECT
    n.`numero_nota`, n.`fecha_hora`, n.`monto_total`,
    n.`metodo_pago`, n.`monto_cancelado`,
    c.`nombre` AS `cliente`, u.`usuario` AS `vendedor`
  FROM `notas_entrega` n
  JOIN `clientes` c ON n.`id_cliente` = c.`id_cliente`
  JOIN `usuarios` u ON n.`id_usuario` = u.`id_usuario`
  WHERE DATE(n.`fecha_hora`) BETWEEN p_fecha_desde AND p_fecha_hasta
  ORDER BY n.`fecha_hora`;
END$$

-- 11.2. Ventas de un cliente especifico
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_ventas_por_cliente`(IN p_id_cliente INT)
BEGIN
  SELECT
    n.`numero_nota`, n.`fecha_hora`, n.`monto_total`,
    n.`metodo_pago`, n.`monto_cancelado`,
    u.`usuario` AS `vendedor`
  FROM `notas_entrega` n
  JOIN `usuarios` u ON n.`id_usuario` = u.`id_usuario`
  WHERE n.`id_cliente` = p_id_cliente
  ORDER BY n.`fecha_hora` DESC;
END$$

-- 11.3. Ventas realizadas por un usuario/vendedor
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_ventas_por_usuario`(IN p_id_usuario INT)
BEGIN
  SELECT
    n.`numero_nota`, n.`fecha_hora`, n.`monto_total`,
    n.`metodo_pago`, n.`monto_cancelado`,
    c.`nombre` AS `cliente`
  FROM `notas_entrega` n
  JOIN `clientes` c ON n.`id_cliente` = c.`id_cliente`
  WHERE n.`id_usuario` = p_id_usuario
  ORDER BY n.`fecha_hora` DESC;
END$$

-- 11.4. Resumen diario: total de ventas, cantidad de notas, metodo de pago
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_diario`(IN p_fecha DATE)
BEGIN
  SELECT
    COUNT(*)                           AS `total_notas`,
    COALESCE(SUM(`monto_total`), 0)     AS `ingreso_total`,
    COALESCE(SUM(`monto_cancelado`), 0) AS `total_cobrado`,
    GROUP_CONCAT(DISTINCT `metodo_pago` SEPARATOR ', ') AS `metodos_pago_usados`
  FROM `notas_entrega`
  WHERE DATE(`fecha_hora`) = p_fecha;
END$$

-- 11.5. Resumen mensual: ingreso total por dia del mes
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_mensual`(IN p_anio INT, IN p_mes INT)
BEGIN
  SELECT
    DATE(`fecha_hora`) AS `dia`,
    COUNT(*)           AS `notas_realizadas`,
    COALESCE(SUM(`monto_total`), 0) AS `ingreso_diario`
  FROM `notas_entrega`
  WHERE YEAR(`fecha_hora`) = p_anio AND MONTH(`fecha_hora`) = p_mes
  GROUP BY DATE(`fecha_hora`)
  ORDER BY `dia`;
END$$

-- 11.6. Top productos mas vendidos en un rango de fechas (o todos)
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_productos_mas_vendidos`(
  IN p_limite       INT,
  IN p_fecha_desde  DATE,
  IN p_fecha_hasta  DATE
)
BEGIN
  IF p_fecha_desde IS NULL OR p_fecha_hasta IS NULL THEN
    SELECT
      p.`nombre_producto`,
      SUM(d.`cantidad`) AS `total_vendido`,
      COUNT(DISTINCT d.`numero_nota`) AS `veces_facturado`
    FROM `detalle_nota` d
    JOIN `productos` p ON d.`id_producto` = p.`id_producto`
    GROUP BY p.`nombre_producto`
    ORDER BY `total_vendido` DESC
    LIMIT p_limite;
  ELSE
    SELECT
      p.`nombre_producto`,
      SUM(d.`cantidad`) AS `total_vendido`,
      COUNT(DISTINCT d.`numero_nota`) AS `veces_facturado`
    FROM `detalle_nota` d
    JOIN `productos` p ON d.`id_producto` = p.`id_producto`
    JOIN `notas_entrega` n ON d.`numero_nota` = n.`numero_nota`
    WHERE DATE(n.`fecha_hora`) BETWEEN p_fecha_desde AND p_fecha_hasta
    GROUP BY p.`nombre_producto`
    ORDER BY `total_vendido` DESC
    LIMIT p_limite;
  END IF;
END$$

-- 11.7. Inventario con valorizacion (costo total, precio total, ganancia potencial)
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_inventario_valorizado`()
BEGIN
  SELECT
    p.`nombre_producto` AS `Producto`,
    cat.`nombre_categoria` AS `Categoria`,
    COALESCE(SUM(l.`stock`), 0) AS `Stock_Total`,
    COALESCE(SUM(l.`stock` * l.`costo`), 0) AS `Costo_Total`,
    COALESCE(SUM(l.`stock` * l.`precio`), 0) AS `Precio_Total_Venta`,
    COALESCE(SUM(l.`stock` * (l.`precio` - l.`costo`)), 0) AS `Ganancia_Potencial`
  FROM `productos` p
  JOIN `categorias` cat ON p.`id_categoria` = cat.`id_categoria`
  LEFT JOIN `lotes` l ON p.`id_producto` = l.`id_producto` AND l.`estado` = 'Activo'
  GROUP BY p.`id_producto`, p.`nombre_producto`, cat.`nombre_categoria`
  ORDER BY p.`nombre_producto`;
END$$

-- 11.8. Productos con stock bajo (menor o igual al limite)
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_stock_bajo`(IN p_limite_stock INT)
BEGIN
  SELECT
    p.`nombre_producto` AS `Producto`,
    cat.`nombre_categoria` AS `Categoria`,
    COALESCE(SUM(l.`stock`), 0) AS `Stock_Actual`
  FROM `productos` p
  JOIN `categorias` cat ON p.`id_categoria` = cat.`id_categoria`
  LEFT JOIN `lotes` l ON p.`id_producto` = l.`id_producto` AND l.`estado` = 'Activo'
  GROUP BY p.`id_producto`, p.`nombre_producto`, cat.`nombre_categoria`
  HAVING `Stock_Actual` <= p_limite_stock
  ORDER BY `Stock_Actual`;
END$$

-- 11.9. Productos proximos a vencer (dentro de X dias)
CREATE PROCEDURE IF NOT EXISTS `sp_reporte_proximos_vencer`(IN p_dias INT)
BEGIN
  SELECT
    p.`nombre_producto` AS `Producto`,
    l.`id_lote`         AS `Lote`,
    l.`stock`           AS `Stock`,
    l.`fecha_vencimiento` AS `Vencimiento`,
    DATEDIFF(l.`fecha_vencimiento`, CURDATE()) AS `Dias_Restantes`
  FROM `lotes` l
  JOIN `productos` p ON l.`id_producto` = p.`id_producto`
  WHERE l.`estado` = 'Activo'
    AND l.`stock` > 0
    AND DATEDIFF(l.`fecha_vencimiento`, CURDATE()) BETWEEN 0 AND p_dias
  ORDER BY l.`fecha_vencimiento`;
END$$

-- 11.10. Historial de compras de un cliente con total acumulado
CREATE PROCEDURE IF NOT EXISTS `sp_historial_compras_cliente`(IN p_id_cliente INT)
BEGIN
  SELECT
    n.`numero_nota`, n.`fecha_hora`, n.`monto_total`,
    n.`metodo_pago`, n.`monto_cancelado`
  FROM `notas_entrega` n
  WHERE n.`id_cliente` = p_id_cliente
  ORDER BY n.`fecha_hora` DESC;
  -- Total acumulado del cliente
  SELECT COALESCE(SUM(`monto_total`), 0) AS total_gastado,
         COUNT(*) AS total_compras
  FROM `notas_entrega`
  WHERE `id_cliente` = p_id_cliente;
END$$

DELIMITER ;

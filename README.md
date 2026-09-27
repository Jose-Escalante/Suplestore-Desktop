# Suplestore Táchira

Sistema de gestión de ventas, inventario y clientes para el comercio **Suplestore Táchira** en San Cristóbal, Venezuela.

Aplicación de escritorio construida con Python + Tkinter (CustomTkinter) y MySQL.

## Alcance del sistema

El sistema consta de **ocho módulos de trabajo** interconectados y gobernados por un esquema de permisos por rol (Administrador o Vendedor):

1. **Inicio de sesión y seguridad**: acceso con contraseñas cifradas (bcrypt), bloqueo temporal de 5 minutos tras 5 intentos fallidos, cambio obligatorio de contraseña en el primer ingreso y aviso de lotes próximos a vencer (< 90 días).
2. **Inventario y categorías**: catálogo de productos por lotes con consumo FIFO y CRUD de categorías.
3. **Ventas**: carrito de compra con descuentos (por producto o globales, en % o $), pagos en efectivo / punto de venta / pago móvil y emisión automática de la **nota de entrega en PDF** como comprobante de la venta (numeración correlativa global única). Incluye el historial de notas de entrega con filtros y exportación a Excel.
4. **Clientes**: CRUD con validación de cédula duplicada y de teléfono.
5. **Usuarios**: gestión de usuarios, roles y permisos por módulo.
6. **Historial (bitácora)**: registro automático de eventos críticos del sistema.
7. **Reportes gerenciales**: tarjetas KPI, gráficos de barras y exportación a Excel.
8. **Copias de seguridad**: exportación y restauración de la base de datos (`.sql`).

> **Importante**: el sistema **no emite facturas ni tiene módulo de facturación**. El comprobante de cada venta es la **nota de entrega**, generada dentro del módulo **Ventas**; su historial (con reimpresión y descarga) es una funcionalidad de ese mismo módulo, no un módulo independiente.

## Funcionalidades

**Acceso y seguridad**
- **Login** con alertas de intentos restantes y encriptación de contraseñas (bcrypt).
- **Bloqueo temporal**: 5 intentos fallidos bloquean la cuenta por 5 minutos.
- **Contraseñas seguras**: mínimo 8 caracteres con mayúscula, minúscula, número y símbolo.
- **Cambio de contraseña obligatorio** en el primer ingreso o tras un reseteo (`cambio_obligatorio`).
- **Reseteo de contraseña** por el administrador (exige su clave actual y deja una clave temporal).
- Permisos por módulo para cada usuario (Administrador / Vendedor).

**Panel de control**
- Acceso por módulos según permisos: Inventario, Clientes, Ventas, Usuarios, Categorías, Historial, Reportes y Respaldo BD.

**Inventario**
- Gestión de productos y lotes: stock, costos, precios y fechas de vencimiento.
- Consumo de stock por lotes en orden FIFO.
- **Aviso de productos sin stock**: se muestran en rojo y con contador en el inventario; en ventas no permite venderlos.

**Ventas**
- Carrito de compras con agregar/editar/eliminar productos y validación de stock.
- **Descuento por producto** (% o $) y **descuento global** (% o $) en el pago.
- Métodos de pago: Efectivo ($), Punto de Venta y Pago Móvil.
- Emisión de **nota de entrega en PDF** con número de control correlativo global (por ejemplo `0009`), único e irrepetible.

**Historial de notas de entrega (dentro del módulo Ventas)**
- Historial de ventas con búsqueda por cédula del cliente y **filtro por período** (Todas, Hoy, Última Semana, Último Mes, Último Año) combinable con la cédula, con resumen de notas y total del período filtrado, y botón **"Limpiar Filtros"**.
- Ver detalles de productos, **reimprimir** PDF y **descargar el PDF** a una ruta elegida.
- **Exportar a Excel** (`.xlsx`) de las ventas listadas (respeta el filtro aplicado).

**Clientes y Categorías**
- CRUD de clientes (nombre, apellido, cédula, teléfono).
- **Validación de teléfono** (opcional, 11 dígitos que inician en "04") y **verificación de cédula duplicada** al registrar o modificar, para no fallar ni saltar ids.
- CRUD de categorías de productos.

**Historial (bitácora)**
- Registro automático de eventos: inicios/cierre de sesión, ventas, cambios y reseteos de contraseña y respaldos.
- Filtros por usuario, detalle y tipo de evento. Visible solo para administradores. Útil como evidencia ante sabotajes.

**Reportes gerenciales**
- Módulo independiente (permiso propio `modulo_reportes`) con filtro de periodo semanal, mensual y anual (ventanas móviles de 7, 30 y 365 días); el período **Último Año agrupa por mes** para que el gráfico no se empalme.
- Reportes: ventas por período, productos más y menos vendidos, ventas por cliente/vendedor/método de pago, descuentos aplicados, stock bajo, clientes inactivos y vencimientos de lotes.
- Tarjetas KPI (ventas de hoy, ventas del mes, notas registradas y producto top), **gráficos de barras** con matplotlib (tema oscuro acorde a la app) en **todos los reportes** (el de vencimientos marca en naranja los lotes que vencen en ≤ 30 días) y **exportación a Excel** de cada reporte.

**Copias de seguridad**
- Exportar la base de datos a un archivo `.sql` y restaurarla desde uno (con confirmación de reemplazo).

**Alertas automáticas**
- Aviso de lotes próximos a vencer (< 90 días) al iniciar sesión.

## Arquitectura: MVC

```
Suplestore Desktop/
├── main.py                        # Punto de entrada
├── AGENTS.md                      # Guía para agentes IA
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Documentación general
├── suplestore_db_full.sql         # Script de inicialización de BD
├── .env                           # Credenciales de BD (no se sube a git)
├── .gitignore
├── models/                        # CAPA MODELO (cada archivo con una responsabilidad)
│   ├── __init__.py
│   ├── connection.py              # DatabaseConnection (conexión MySQL, lee .env)
│   ├── database_model.py          # FACADE: unifica los sub-modelos
│   ├── user_model.py              # UserModel: usuarios, permisos, login y seguridad
│   ├── client_model.py            # ClientModel: clientes CRUD
│   ├── category_model.py          # CategoryModel: categorías CRUD
│   ├── product_model.py           # ProductModel: productos y lotes
│   ├── sale_model.py              # SaleModel: ventas, notas y descuentos
│   ├── event_model.py             # EventModel: bitácora de eventos
│   ├── backup_model.py            # BackupModel: exportar/importar respaldos SQL
│   └── report_model.py            # ReportModel: consultas agregadas de reportes
├── controllers/
│   └── app_controller.py          # CAPA CONTROLADOR: estado, navegación, permisos
├── services/
│   ├── nota_entrega.py            # Generación de notas de entrega en PDF
│   ├── excel_export.py            # Exportación de ventas a Excel
│   └── graficos.py                # Gráficos de barras para Reportes (matplotlib)
└── views/                         # CAPA VISTA
    ├── login_view.py              # Inicio de sesión
    ├── cambio_password_view.py    # Cambio de contraseña obligatorio
    ├── panel_view.py              # Panel de control (incluye modal de respaldo)
    ├── categorias_view.py         # CRUD categorías
    ├── usuarios_view.py           # CRUD usuarios + reset de contraseña
    ├── clientes_view.py           # CRUD clientes
    ├── ventas_view.py             # Ventas, carrito, pago e historial de notas
    ├── inventario_view.py         # Inventario y lotes
    ├── historial_view.py          # Historial de eventos (bitácora)
    └── reportes_view.py           # Reportes gerenciales (KPI + gráficos + tablas + Excel)
```

### Flujo de datos

```
Vista (View) → Controlador (Controller) → DatabaseModel (facade)
                                                  │
                                        ┌─────────┼─────────┐
                                        │         │         │
                                   UserModel  SaleModel  EventModel ...
```

## Requisitos

- Python 3.8+
- MySQL 5.7+ (desarrollado y probado sobre MySQL 8.0/9.x)
- Conexión de red al servidor MySQL

## Instalación

```bash
pip install -r requirements.txt
```

Dependencias: `mysql-connector-python`, `customtkinter`, `PIL/pillow`, `tkcalendar`, `reportlab`, `bcrypt` y `openpyxl`.

## Configuración de base de datos

Ejecutar el script de inicialización `suplestore_db_full.sql` para crear la base de datos `suplestore_db` con sus tablas, vistas y datos iniciales mínimos (usuario admin, categorías, productos y lotes base; sin datos de ventas).

Las credenciales de conexión se configuran únicamente en un archivo `.env` en la raíz del proyecto (no se sube a git); la app no se conecta sin él.

## Usuario inicial

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin   | admin123   | Administrador |

## Ejecución

```bash
python main.py
```

## Créditos

Desarrollado por José Escalante, Giornaldo Gómez y Brandon Correa.
# Suplestore Táchira

Sistema de gestión de ventas, inventario y clientes para el comercio **Suplestore Táchira** en San Cristóbal, Venezuela.

Aplicación de escritorio construida con Python + Tkinter (CustomTkinter) y MySQL.

## Funcionalidades

**Acceso y seguridad**
- **Login** con alertas de intentos restantes y encriptación de contraseñas (bcrypt).
- **Bloqueo temporal**: 5 intentos fallidos bloquean la cuenta por 5 minutos.
- **Contraseñas seguras**: mínimo 8 caracteres con mayúscula, minúscula, número y símbolo.
- **Cambio de contraseña obligatorio** en el primer ingreso o tras un reseteo (`cambio_obligatorio`).
- **Reseteo de contraseña** por el administrador (exige su clave actual y deja una clave temporal).
- Permisos por módulo para cada usuario (Administrador / Vendedor).

**Panel de control**
- Acceso por módulos según permisos: Inventario, Clientes, Ventas, Usuarios, Categorías, Historial y Respaldo BD.

**Inventario**
- Gestión de productos y lotes: stock, costos, precios y fechas de vencimiento.
- Consumo de stock por lotes en orden FIFO.
- **Aviso de productos sin stock**: se muestran en rojo y con contador en el inventario; en ventas no permite venderlos.

**Ventas**
- Carrito de compras con agregar/editar/eliminar productos y validación de stock.
- **Descuento por producto** (% o $) y **descuento global** (% o $) en el pago.
- Métodos de pago: Efectivo ($), Punto de Venta y Pago Móvil.
- Emisión de **nota de entrega en PDF** con consecutivo anual `NNNN-YY`.

**Notas de entrega**
- Historial de ventas con búsqueda por cédula del cliente.
- Ver detalles de productos, **reimprimir** PDF y **descargar el PDF** a una ruta elegida.
- **Exportar a Excel** (`.xlsx`) de las ventas listadas.

**Clientes y Categorías**
- CRUD de clientes (nombre, cédula, teléfono).
- CRUD de categorías de productos.

**Historial (bitácora)**
- Registro automático de eventos: inicios/cierre de sesión, ventas, cambios y reseteos de contraseña y respaldos.
- Filtros por usuario, detalle y tipo de evento. Visible solo para administradores. Útil como evidencia ante sabotajes.

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
│   └── backup_model.py            # BackupModel: exportar/importar respaldos SQL
├── controllers/
│   └── app_controller.py          # CAPA CONTROLADOR: estado, navegación, permisos
├── services/
│   ├── nota_entrega.py            # Generación de notas de entrega en PDF
│   └── excel_export.py            # Exportación de ventas a Excel
└── views/                         # CAPA VISTA
    ├── login_view.py              # Inicio de sesión
    ├── cambio_password_view.py    # Cambio de contraseña obligatorio
    ├── panel_view.py              # Panel de control (incluye modal de respaldo)
    ├── categorias_view.py         # CRUD categorías
    ├── usuarios_view.py           # CRUD usuarios + reset de contraseña
    ├── clientes_view.py           # CRUD clientes
    ├── ventas_view.py             # Ventas, carrito, pago e historial de notas
    ├── inventario_view.py         # Inventario y lotes
    └── historial_view.py          # Historial de eventos (bitácora)
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
- MySQL 5.7+ / 8.0
- Conexión de red al servidor MySQL

## Instalación

```bash
pip install -r requirements.txt
```

Dependencias: `mysql-connector-python`, `customtkinter`, `PIL/pillow`, `tkcalendar`, `reportlab`, `bcrypt` y `openpyxl`.

## Configuración de base de datos

Ejecutar el script de inicialización `suplestore_db_full.sql` para crear la base de datos `suplestore_db` con sus tablas, vistas y datos iniciales (usuario admin).

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
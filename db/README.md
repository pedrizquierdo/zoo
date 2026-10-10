# Esquema de base de datos

Este directorio contiene los scripts de inicialización de MySQL para el proyecto Zoo.

Los archivos dentro de `db/init/` se ejecutan automáticamente por MySQL cuando el contenedor se crea por primera vez. Se usan prefijos numéricos para asegurar el orden de ejecución:

1. `01_crear_tabla_animales.sql`: crea la tabla `animales`.
2. `02_insertar_animales_ejemplo.sql`: inserta datos iniciales de ejemplo.

## Base de datos

| Propiedad | Valor |
|---|---|
| Base de datos | `zoo` |
| Servicio MySQL en Compose | `db` |
| Usuario de aplicación | `zoo_user` |
| Codificación | `utf8mb4` |
| Collation | `utf8mb4_unicode_ci` |

## Tabla `animales`

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT`, `NOT NULL` | Identificador único del animal |
| `nombre` | `VARCHAR(100)` | `NOT NULL` | Nombre del animal |
| `especie` | `VARCHAR(100)` | `NOT NULL` | Especie del animal |
| `edad` | `INT` | `NOT NULL` | Edad del animal |
| `habitat` | `VARCHAR(100)` | `NOT NULL` | Hábitat donde vive el animal |

## Datos iniciales

El archivo `02_insertar_animales_ejemplo.sql` agrega animales de ejemplo para que la aplicación no aparezca vacía durante las pruebas.

## Permisos

El usuario `zoo_user` se crea automáticamente usando las variables de entorno de MySQL:

- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

La imagen oficial de MySQL otorga permisos al usuario sobre la base configurada en `MYSQL_DATABASE`, por lo que no es necesario agregar permisos manuales mientras la aplicación solo use la base `zoo`.

## Relación con `app.py`

Actualmente `app.py` usa una lista de animales en memoria. Cuando se implemente la conexión con MySQL, esa lista deberá reemplazarse por consultas a la tabla `animales`.

Las operaciones esperadas serán:

- `SELECT` para listar animales.
- `INSERT` para crear animales.
- `UPDATE` para editar animales.
- `DELETE` para eliminar animales.

La tabla `animales` ya define el campo `id` como `AUTO_INCREMENT`, por lo que la aplicación no debe generar el identificador manualmente.

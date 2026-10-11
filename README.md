# Proyecto Zoo
Este proyecto sirve para administrar un **zoológico**

## Instalación
Para montar este proyecto instala las dependencias del archivo requirements.txt usando el siguiente comando:

pip install -r requirements.txt

## Saludo 
Espero lo disfrutes y no rompas nada

## Plan de pruebas

Rama de trabajo: `feature/tests-docs`.
Archivos correspondientes: `README.md` y la carpeta `tests/`.

1. Crear un animal con datos válidos.
   - Usar nombre Simba, especie León, edad 3 y hábitat Sabana.
   - Debe guardarse y aparecer en el listado.

2. Crear un animal con campos vacíos o edad no numérica.
   - Probar cada campo vacío, con espacios y una edad como "abc".
   - Debe mostrar los errores correspondientes y no guardar el animal.
   - También se comprueban edades decimales y negativas.

3. Editar un animal y confirmar que se guardan los cambios.
   - Cambiar nombre, especie, edad y hábitat.
   - Los cambios deben aparecer en el listado y guardarse en la base.
   - Una edición inválida debe mostrar errores y conservar los datos anteriores.

4. Eliminar un animal y confirmar que desaparece.
   - El animal debe desaparecer del listado y de la base.
   - La confirmación de eliminación se revisa manualmente en el navegador.

5. Abrir un ID inexistente.
   - Visitar /animales/999999/editar.
   - Debe devolver HTTP 404.
   - Editar o eliminar un ID inexistente también debe devolver 404.

6. Probar nombres con acentos, ñ y comillas.
   - Usar José, Ñoño, León "Rey" y O'Connor.
   - Deben guardarse y mostrarse correctamente al crear y editar.

## Pruebas automáticas

Las pruebas utilizan pytest y el cliente de pruebas de Flask.

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar desde la raíz del proyecto:

```bash
python -m pytest tests/ -v
```

Archivos:

- tests/conftest.py: configura el cliente de Flask y una base de pruebas.
- tests/test_animales.py: contiene las pruebas del CRUD y sus validaciones.

Cada prueba utiliza una base SQLite en memoria independiente.
La configuración de pruebas sustituye temporalmente el motor de conexión
antes de importar app.py. Así se ejecutan las rutas y consultas reales
sin conectarse a MySQL ni modificar sus datos.

Estas pruebas no ejecutan JavaScript ni comprueban características
específicas de MySQL. La confirmación de eliminación y el funcionamiento
con MySQL se revisan manualmente.
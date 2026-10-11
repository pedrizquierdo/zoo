import os
import time

from flask import Flask, abort, redirect, render_template, request, url_for
from sqlalchemy import Integer, String, create_engine, select
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

app = Flask(__name__)

INTENTOS_CONEXION = 10
ESPERA_ENTRE_INTENTOS = 3  # segundos


def url_mysql():
    """Arma la URL de conexión a MySQL a partir de las variables de entorno."""
    obligatorias = ["DB_USER", "DB_PASSWORD", "DB_NAME"]
    faltantes = [nombre for nombre in obligatorias if not os.environ.get(nombre)]
    if faltantes:
        raise RuntimeError(f"Faltan variables de entorno para conectar a MySQL: {', '.join(faltantes)}")

    return URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )


def esperar_mysql(engine):
    """Reintenta la conexión mientras MySQL arranca."""
    for intento in range(1, INTENTOS_CONEXION + 1):
        try:
            with engine.connect():
                print("Conectado a MySQL")
                return
        except OperationalError as error:
            print(f"MySQL no responde (intento {intento}/{INTENTOS_CONEXION}): {error.orig}")
            if intento == INTENTOS_CONEXION:
                raise
            time.sleep(ESPERA_ENTRE_INTENTOS)


class Base(DeclarativeBase):
    pass


class Animal(Base):
    __tablename__ = "animales"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    especie: Mapped[str] = mapped_column(String(100))
    edad: Mapped[int] = mapped_column(Integer)
    habitat: Mapped[str] = mapped_column(String(100))


engine = create_engine(url_mysql(), pool_pre_ping=True)
esperar_mysql(engine)
Base.metadata.create_all(engine)


def datos_formulario():
    """Lee y valida los campos del formulario. Devuelve (datos, errores)."""
    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "especie": request.form.get("especie", "").strip(),
        "edad": request.form.get("edad", "").strip(),
        "habitat": request.form.get("habitat", "").strip(),
    }
    errores = [f"El campo {campo} es obligatorio" for campo, valor in datos.items() if not valor]
    if datos["edad"]:
        if datos["edad"].isdigit():
            datos["edad"] = int(datos["edad"])
        else:
            errores.append("La edad debe ser un número entero positivo")
    return datos, errores


# Listar
@app.route("/")
def index():
    with Session(engine) as session:
        animales = session.scalars(select(Animal).order_by(Animal.id)).all()
    return render_template("index.html", animales=animales)


# Crear
@app.route("/animales/nuevo", methods=["GET", "POST"])
def crear_animal():
    if request.method == "POST":
        datos, errores = datos_formulario()
        if not errores:
            with Session(engine) as session:
                session.add(Animal(**datos))
                session.commit()
            return redirect(url_for("index"))
        return render_template("form.html", titulo="Nuevo animal", animal=datos, errores=errores)
    return render_template("form.html", titulo="Nuevo animal", animal={}, errores=[])


# Actualizar
@app.route("/animales/<int:id>/editar", methods=["GET", "POST"])
def editar_animal(id):
    with Session(engine) as session:
        animal = session.get(Animal, id) or abort(404)
        if request.method == "POST":
            datos, errores = datos_formulario()
            if not errores:
                for campo, valor in datos.items():
                    setattr(animal, campo, valor)
                session.commit()
                return redirect(url_for("index"))
            return render_template("form.html", titulo="Editar animal", animal=datos, errores=errores)
        return render_template("form.html", titulo="Editar animal", animal=animal, errores=[])


# Eliminar
@app.route("/animales/<int:id>/eliminar", methods=["POST"])
def eliminar_animal(id):
    with Session(engine) as session:
        animal = session.get(Animal, id) or abort(404)
        session.delete(animal)
        session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    # host 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000, debug=True)

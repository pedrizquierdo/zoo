from sqlalchemy import Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Animal(Base):
    __tablename__ = "animales"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    especie: Mapped[str] = mapped_column(String(100))
    edad: Mapped[int] = mapped_column(Integer)
    habitat: Mapped[str] = mapped_column(String(100))


def validar_animal(form):
    """Lee y valida los campos de un formulario. Devuelve (datos, errores)."""
    datos = {
        "nombre": form.get("nombre", "").strip(),
        "especie": form.get("especie", "").strip(),
        "edad": form.get("edad", "").strip(),
        "habitat": form.get("habitat", "").strip(),
    }
    errores = [f"El campo {campo} es obligatorio" for campo, valor in datos.items() if not valor]
    if datos["edad"]:
        if datos["edad"].isdigit():
            datos["edad"] = int(datos["edad"])
        else:
            errores.append("La edad debe ser un número entero positivo")
    return datos, errores


def listar_animales(engine):
    """Devuelve todos los animales ordenados por ID."""
    with Session(engine) as session:
        return session.scalars(select(Animal).order_by(Animal.id)).all()


def obtener_animal(engine, id):
    """Devuelve el animal con ese ID, o None si no existe."""
    with Session(engine) as session:
        return session.get(Animal, id)


def crear_animal(engine, datos):
    """Guarda un animal nuevo con los datos del formulario."""
    with Session(engine) as session:
        session.add(Animal(**datos))
        session.commit()


def actualizar_animal(engine, id, datos):
    """Actualiza un animal. Devuelve False si no existe."""
    with Session(engine) as session:
        animal = session.get(Animal, id)
        if animal is None:
            return False
        for campo, valor in datos.items():
            setattr(animal, campo, valor)
        session.commit()
        return True


def eliminar_animal(engine, id):
    """Elimina un animal. Devuelve False si no existe."""
    with Session(engine) as session:
        animal = session.get(Animal, id)
        if animal is None:
            return False
        session.delete(animal)
        session.commit()
        return True

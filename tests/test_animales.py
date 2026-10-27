"""Pruebas del CRUD contra MySQL, usando el cliente de pruebas de Flask.

Necesitan una base MySQL de pruebas (las variables DB_* en el entorno).
Cada prueba vacía la tabla animales: nunca correrlas contra datos reales.
"""

from html import unescape

import pytest
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from animales import Animal
from app import app, engine


@pytest.fixture
def client():
    # Empezar cada prueba con la tabla vacía
    with Session(engine) as session:
        session.execute(delete(Animal))
        session.commit()
    with app.test_client() as client:
        yield client


def datos_validos():
    return {"nombre": "Simba", "especie": "León", "edad": "3", "habitat": "Sabana"}


def registros():
    """Devuelve los animales guardados como diccionarios."""
    with Session(engine) as session:
        return [
            {
                "id": animal.id,
                "nombre": animal.nombre,
                "especie": animal.especie,
                "edad": animal.edad,
                "habitat": animal.habitat,
            }
            for animal in session.scalars(select(Animal)).all()
        ]


def crear(client, datos):
    """Crea un animal desde el formulario y devuelve su ID."""
    response = client.post("/animales/nuevo", data=datos)

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    return registros()[-1]["id"]


def test_listado_vacio(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Todavía no hay animales registrados." in response.get_data(as_text=True)


def test_crear_animal(client):
    animal_id = crear(client, datos_validos())

    assert registros() == [{"id": animal_id, **datos_validos(), "edad": 3}]

    listado = client.get("/").get_data(as_text=True)
    assert "Simba" in listado
    assert "León" in listado


def test_crear_animal_invalido_no_guarda(client):
    response = client.post("/animales/nuevo", data={**datos_validos(), "edad": "abc"})

    assert response.status_code == 200
    assert "La edad debe ser un número entero positivo" in response.get_data(as_text=True)
    assert registros() == []


def test_editar_animal(client):
    animal_id = crear(client, datos_validos())

    response = client.get(f"/animales/{animal_id}/editar")
    assert response.status_code == 200
    assert "Simba" in response.get_data(as_text=True)

    nuevos = {"nombre": "Nala", "especie": "Leona", "edad": "5", "habitat": "Pradera"}
    response = client.post(f"/animales/{animal_id}/editar", data=nuevos)

    assert response.status_code == 302
    assert registros() == [{"id": animal_id, **nuevos, "edad": 5}]


def test_editar_animal_invalido_no_cambia(client):
    animal_id = crear(client, datos_validos())
    antes = registros()

    response = client.post(f"/animales/{animal_id}/editar", data={**datos_validos(), "edad": "abc"})

    assert response.status_code == 200
    assert registros() == antes


def test_eliminar_animal(client):
    animal_id = crear(client, datos_validos())

    response = client.post(f"/animales/{animal_id}/eliminar")

    assert response.status_code == 302
    assert registros() == []


@pytest.mark.parametrize("metodo,accion", [("get", "editar"), ("post", "editar"), ("post", "eliminar")])
def test_id_inexistente_devuelve_404(client, metodo, accion):
    response = getattr(client, metodo)(f"/animales/999999/{accion}")

    assert response.status_code == 404


@pytest.mark.parametrize("nombre", ["José", "Ñoño", 'León "Rey"', "O'Connor"])
def test_nombres_especiales(client, nombre):
    crear(client, {**datos_validos(), "nombre": nombre})

    assert registros()[0]["nombre"] == nombre
    assert nombre in unescape(client.get("/").get_data(as_text=True))

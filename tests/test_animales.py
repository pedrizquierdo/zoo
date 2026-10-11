"""Pruebas funcionales del CRUD con el cliente HTTP de Flask."""

from html import unescape

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session


def registros(app):
    """Consulta los animales guardados en la base de pruebas."""
    with Session(app.engine) as session:
        return [
            {
                "id": animal.id,
                "nombre": animal.nombre,
                "especie": animal.especie,
                "edad": animal.edad,
                "habitat": animal.habitat,
            }
            for animal in session.scalars(select(app.Animal)).all()
        ]


def crear(client, app, datos):
    """Crea un animal y devuelve su ID."""
    response = client.post("/animales/nuevo", data=datos)

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    return registros(app)[0]["id"]


def test_crear_animal_valido(client, zoo_app, datos_validos):
    crear(client, zoo_app, datos_validos)
    animales = registros(zoo_app)

    assert len(animales) == 1
    assert animales[0] == {
        "id": animales[0]["id"],
        **datos_validos,
        "edad": 3,
    }

    response = client.get("/")

    assert response.status_code == 200
    assert "Simba" in response.get_data(as_text=True)
    assert "León" in response.get_data(as_text=True)


@pytest.mark.parametrize("campo", ["nombre", "especie", "edad", "habitat"])
@pytest.mark.parametrize("valor", ["", "   "])
def test_campos_vacios(client, zoo_app, datos_validos, campo, valor):
    datos_validos[campo] = valor

    response = client.post("/animales/nuevo", data=datos_validos)

    assert response.status_code == 200
    assert (
        f"El campo {campo} es obligatorio"
        in response.get_data(as_text=True)
    )
    assert registros(zoo_app) == []


def test_todos_los_campos_ausentes(client, zoo_app):
    response = client.post("/animales/nuevo", data={})

    assert response.status_code == 200

    for campo in ("nombre", "especie", "edad", "habitat"):
        assert (
            f"El campo {campo} es obligatorio"
            in response.get_data(as_text=True)
        )

    assert registros(zoo_app) == []


@pytest.mark.parametrize("edad", ["abc", "3.5", "-1"])
def test_edad_invalida(client, zoo_app, datos_validos, edad):
    datos_validos["edad"] = edad

    response = client.post("/animales/nuevo", data=datos_validos)

    assert response.status_code == 200
    assert (
        "La edad debe ser un número entero positivo"
        in response.get_data(as_text=True)
    )
    assert registros(zoo_app) == []


def test_editar_guarda_cambios(client, zoo_app, datos_validos):
    animal_id = crear(client, zoo_app, datos_validos)

    response = client.get(f"/animales/{animal_id}/editar")

    assert response.status_code == 200
    assert "Simba" in response.get_data(as_text=True)

    nuevos = {
        "nombre": "Nala",
        "especie": "Leona",
        "edad": "5",
        "habitat": "Pradera",
    }

    response = client.post(
        f"/animales/{animal_id}/editar",
        data=nuevos,
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert registros(zoo_app) == [
        {"id": animal_id, **nuevos, "edad": 5}
    ]

    listado = client.get("/").get_data(as_text=True)

    assert "Nala" in listado
    assert "Simba" not in listado


def test_edicion_invalida_conserva_datos(
    client, zoo_app, datos_validos
):
    animal_id = crear(client, zoo_app, datos_validos)
    antes = registros(zoo_app)

    response = client.post(
        f"/animales/{animal_id}/editar",
        data={**datos_validos, "edad": "abc"},
    )

    assert response.status_code == 200
    assert (
        "La edad debe ser un número entero positivo"
        in response.get_data(as_text=True)
    )
    assert registros(zoo_app) == antes


def test_eliminar_animal(client, zoo_app, datos_validos):
    animal_id = crear(client, zoo_app, datos_validos)

    response = client.post(f"/animales/{animal_id}/eliminar")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert registros(zoo_app) == []

    listado = client.get("/").get_data(as_text=True)

    assert "Simba" not in listado
    assert "Todavía no hay animales registrados." in listado


@pytest.mark.parametrize(
    "metodo,accion",
    [
        ("get", "editar"),
        ("post", "editar"),
        ("post", "eliminar"),
    ],
)
def test_id_inexistente_devuelve_404(
    client, zoo_app, metodo, accion
):
    response = getattr(client, metodo)(
        f"/animales/999999/{accion}"
    )

    assert response.status_code == 404
    assert registros(zoo_app) == []


@pytest.mark.parametrize(
    "nombre",
    ["José", "Ñoño", 'León "Rey"', "O'Connor"],
)
def test_nombres_especiales(
    client, zoo_app, datos_validos, nombre
):
    datos_validos["nombre"] = nombre
    animal_id = crear(client, zoo_app, datos_validos)

    assert registros(zoo_app)[0]["nombre"] == nombre

    for ruta in ("/", f"/animales/{animal_id}/editar"):
        response = client.get(ruta)

        assert response.status_code == 200
        assert nombre in unescape(response.get_data(as_text=True))

    nuevo_nombre = nombre + " editado"

    response = client.post(
        f"/animales/{animal_id}/editar",
        data={**datos_validos, "nombre": nuevo_nombre},
    )

    assert response.status_code == 302
    assert registros(zoo_app)[0]["nombre"] == nuevo_nombre
    assert nuevo_nombre in unescape(
        client.get("/").get_data(as_text=True)
    )
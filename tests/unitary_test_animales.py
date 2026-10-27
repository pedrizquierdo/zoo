"""Pruebas unitarias del CRUD de animales, sin acceder a una base de datos."""

from unittest.mock import MagicMock, sentinel

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import animales
from animales import Animal


@pytest.fixture
def sesion(monkeypatch):
    """Sustituye la sesion de SQLAlchemy por un doble aislado por prueba."""
    factory = MagicMock()
    session = MagicMock(spec=Session)
    factory.return_value.__enter__.return_value = session
    monkeypatch.setattr(animales, "Session", factory)
    return session


@pytest.fixture
def animal():
    return Animal(
        id=1, nombre="Simba", especie="Leon", edad=3, habitat="Sabana"
    )


@pytest.mark.parametrize("hay_animales", [True, False])
def test_listar_animales(sesion, animal, hay_animales):
    esperados = [animal] if hay_animales else []
    sesion.scalars.return_value.all.return_value = esperados

    resultado = animales.listar_animales(sentinel.engine)

    assert resultado == esperados
    consulta = sesion.scalars.call_args.args[0]
    assert consulta.compare(select(Animal).order_by(Animal.id))
    sesion.commit.assert_not_called()


def test_obtener_animal_existente(sesion, animal):
    sesion.get.return_value = animal

    assert animales.obtener_animal(sentinel.engine, 1) is animal

    sesion.get.assert_called_once_with(Animal, 1)
    sesion.commit.assert_not_called()


def test_obtener_animal_inexistente(sesion):
    sesion.get.return_value = None

    assert animales.obtener_animal(sentinel.engine, 999) is None

    sesion.get.assert_called_once_with(Animal, 999)


def test_crear_animal(sesion):
    datos = {
        "nombre": "Simba", "especie": "Leon", "edad": 3, "habitat": "Sabana"
    }

    animales.crear_animal(sentinel.engine, datos)

    sesion.add.assert_called_once()
    creado = sesion.add.call_args.args[0]
    assert isinstance(creado, Animal)
    for campo, valor in datos.items():
        assert getattr(creado, campo) == valor
    sesion.commit.assert_called_once_with()


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "Nala", "especie": "Leona", "edad": 5, "habitat": "Pradera"},
        {"edad": 4},
    ],
)
def test_actualizar_animal_existente(sesion, animal, cambios):
    sesion.get.return_value = animal
    esperados = {
        "nombre": animal.nombre, "especie": animal.especie,
        "edad": animal.edad, "habitat": animal.habitat, **cambios,
    }

    assert animales.actualizar_animal(sentinel.engine, 1, cambios) is True

    sesion.get.assert_called_once_with(Animal, 1)
    assert animal.id == 1
    for campo, valor in esperados.items():
        assert getattr(animal, campo) == valor
    sesion.commit.assert_called_once_with()


def test_actualizar_animal_inexistente(sesion):
    sesion.get.return_value = None

    assert animales.actualizar_animal(
        sentinel.engine, 999, {"nombre": "Nala"}
    ) is False

    sesion.get.assert_called_once_with(Animal, 999)
    sesion.commit.assert_not_called()


def test_eliminar_animal_existente(sesion, animal):
    sesion.get.return_value = animal

    assert animales.eliminar_animal(sentinel.engine, 1) is True

    sesion.get.assert_called_once_with(Animal, 1)
    sesion.delete.assert_called_once_with(animal)
    sesion.commit.assert_called_once_with()


def test_eliminar_animal_inexistente(sesion):
    sesion.get.return_value = None

    assert animales.eliminar_animal(sentinel.engine, 999) is False

    sesion.get.assert_called_once_with(Animal, 999)
    sesion.delete.assert_not_called()
    sesion.commit.assert_not_called()

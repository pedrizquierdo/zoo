"""Pruebas de validar_animal. No necesitan base de datos."""

import pytest

from animales import validar_animal


def datos_validos():
    return {"nombre": "Simba", "especie": "León", "edad": "3", "habitat": "Sabana"}


def test_datos_validos():
    datos, errores = validar_animal(datos_validos())

    assert errores == []
    assert datos == {"nombre": "Simba", "especie": "León", "edad": 3, "habitat": "Sabana"}


def test_quita_espacios():
    datos, errores = validar_animal({"nombre": "  Simba  ", "especie": "León", "edad": " 3 ", "habitat": "Sabana"})

    assert errores == []
    assert datos["nombre"] == "Simba"
    assert datos["edad"] == 3


@pytest.mark.parametrize("campo", ["nombre", "especie", "edad", "habitat"])
@pytest.mark.parametrize("valor", ["", "   "])
def test_campo_vacio(campo, valor):
    form = datos_validos()
    form[campo] = valor

    datos, errores = validar_animal(form)

    assert errores == [f"El campo {campo} es obligatorio"]


def test_formulario_vacio():
    datos, errores = validar_animal({})

    assert len(errores) == 4


@pytest.mark.parametrize("edad", ["abc", "3.5", "-1"])
def test_edad_invalida(edad):
    form = datos_validos()
    form["edad"] = edad

    datos, errores = validar_animal(form)

    assert errores == ["La edad debe ser un número entero positivo"]

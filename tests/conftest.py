"""Cliente Flask con una base aislada por prueba, sin conectar a MySQL."""

import importlib.util
import sys
from pathlib import Path

import pytest
import sqlalchemy
from sqlalchemy.pool import StaticPool


@pytest.fixture
def zoo_app(monkeypatch):
    engine = sqlalchemy.create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # app.py crea el motor al importarse.
    # Durante las pruebas usamos SQLite en memoria.
    monkeypatch.setattr(
        sqlalchemy,
        "create_engine",
        lambda *args, **kwargs: engine,
    )

    for key in ("DB_USER", "DB_PASSWORD", "DB_NAME"):
        monkeypatch.setenv(key, "pytest")

    monkeypatch.setenv("DB_PORT", "3306")

    path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("zoo_test_app", path)
    module = importlib.util.module_from_spec(spec)

    monkeypatch.setitem(sys.modules, spec.name, module)

    try:
        spec.loader.exec_module(module)
        module.app.config.update(TESTING=True)
        yield module
    finally:
        engine.dispose()


@pytest.fixture
def client(zoo_app):
    with zoo_app.app.test_client() as client:
        yield client


@pytest.fixture
def datos_validos():
    return {
        "nombre": "Simba",
        "especie": "León",
        "edad": "3",
        "habitat": "Sabana",
    }
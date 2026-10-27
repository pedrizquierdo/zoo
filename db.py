import os
import time

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError

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


engine = create_engine(url_mysql(), pool_pre_ping=True)
esperar_mysql(engine)

-- Se usa utf8mb4 para guardar acentos, ñ y caracteres especiales.
-- La collation utf8mb4_unicode_ci permite comparar texto sin distinguir mayúsculas/minúsculas.

CREATE TABLE IF NOT EXISTS animales (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    especie VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    habitat VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

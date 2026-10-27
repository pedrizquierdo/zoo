from flask import Flask, abort, redirect, render_template, request, url_for

import animales
from animales import Animal, Base
from db import engine

app = Flask(__name__)

Base.metadata.create_all(engine)


# Listar
@app.route("/")
def index():
    return render_template("index.html", animales=animales.listar_animales(engine))


# Crear
@app.route("/animales/nuevo", methods=["GET", "POST"])
def crear_animal():
    if request.method == "POST":
        datos, errores = animales.validar_animal(request.form)
        if not errores:
            animales.crear_animal(engine, datos)
            return redirect(url_for("index"))
        return render_template("form.html", titulo="Nuevo animal", animal=datos, errores=errores)
    return render_template("form.html", titulo="Nuevo animal", animal={}, errores=[])


# Actualizar
@app.route("/animales/<int:id>/editar", methods=["GET", "POST"])
def editar_animal(id):
    animal = animales.obtener_animal(engine, id) or abort(404)
    if request.method == "POST":
        datos, errores = animales.validar_animal(request.form)
        if not errores:
            animales.actualizar_animal(engine, id, datos) or abort(404)
            return redirect(url_for("index"))
        return render_template("form.html", titulo="Editar animal", animal=datos, errores=errores)
    return render_template("form.html", titulo="Editar animal", animal=animal, errores=[])


# Eliminar
@app.route("/animales/<int:id>/eliminar", methods=["POST"])
def eliminar_animal(id):
    animales.eliminar_animal(engine, id) or abort(404)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # host 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000, debug=True)

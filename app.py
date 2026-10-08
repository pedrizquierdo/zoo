from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

# Tabla de animales hardcodeada (vive en memoria: se reinicia al reiniciar la app)
animales = [
    {"id": 1, "nombre": "Simba", "especie": "León", "edad": 5, "habitat": "Sabana"},
    {"id": 2, "nombre": "Dumbo", "especie": "Elefante", "edad": 12, "habitat": "Sabana"},
    {"id": 3, "nombre": "Kowalski", "especie": "Pingüino", "edad": 3, "habitat": "Polar"},
    {"id": 4, "nombre": "Baloo", "especie": "Oso", "edad": 8, "habitat": "Bosque"},
]
siguiente_id = 5


def buscar_animal(id):
    animal = next((a for a in animales if a["id"] == id), None)
    if animal is None:
        abort(404)
    return animal


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
    return render_template("index.html", animales=animales)


# Crear
@app.route("/animales/nuevo", methods=["GET", "POST"])
def crear_animal():
    global siguiente_id
    if request.method == "POST":
        datos, errores = datos_formulario()
        if not errores:
            animales.append({"id": siguiente_id, **datos})
            siguiente_id += 1
            return redirect(url_for("index"))
        return render_template("form.html", titulo="Nuevo animal", animal=datos, errores=errores)
    return render_template("form.html", titulo="Nuevo animal", animal={}, errores=[])


# Actualizar
@app.route("/animales/<int:id>/editar", methods=["GET", "POST"])
def editar_animal(id):
    animal = buscar_animal(id)
    if request.method == "POST":
        datos, errores = datos_formulario()
        if not errores:
            animal.update(datos)
            return redirect(url_for("index"))
        return render_template("form.html", titulo="Editar animal", animal=datos, errores=errores)
    return render_template("form.html", titulo="Editar animal", animal=animal, errores=[])


# Eliminar
@app.route("/animales/<int:id>/eliminar", methods=["POST"])
def eliminar_animal(id):
    animales.remove(buscar_animal(id))
    return redirect(url_for("index"))


if __name__ == "__main__":
    # host 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000, debug=True)

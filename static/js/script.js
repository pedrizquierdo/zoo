// Pide confirmación antes de enviar los formularios de eliminar
document.querySelectorAll("form.eliminar").forEach((form) => {
    form.addEventListener("submit", (evento) => {
        if (!confirm(`¿Eliminar a ${form.dataset.nombre}?`)) {
            evento.preventDefault();
        }
    });
});

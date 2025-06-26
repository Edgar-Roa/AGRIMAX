document.addEventListener("DOMContentLoaded", () => {
    // Eliminar producto
    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", () => {
            const productoId = button.dataset.id;

            if (confirm("¿Estás seguro de que deseas eliminar este producto?")) {
                fetch(`/eliminar_producto/${productoId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Producto eliminado correctamente");
                        location.reload(); // Recargar para reflejar los cambios
                    } else {
                        alert(data.message || "Error al eliminar producto");
                    }
                })
                .catch(error => console.error("Error eliminando producto:", error));
            }
        });
    });

    // Mostrar formulario de edición
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", () => {
            const productoId = button.dataset.id;
            const formContainer = document.getElementById(`edit-form-${productoId}`);
            if (formContainer) {
                formContainer.style.display = "block";
            } else {
                console.error(`No se encontró el formulario para el producto con ID ${productoId}`);
            }
        });
    });

    // Cancelar edición
    document.querySelectorAll(".cancel-btn").forEach(button => {
        button.addEventListener("click", () => {
            const formContainer = button.closest(".edit-form");
            if (formContainer) {
                formContainer.style.display = "none";
            } else {
                console.error("No se encontró el contenedor del formulario para cancelar la edición.");
            }
        });
    });

    // Modificar producto
    document.querySelectorAll(".edit-form").forEach(form => {
        form.addEventListener("submit", event => {
            event.preventDefault();
            const formData = new FormData(form);
            const productoId = formData.get("producto_id");

            fetch(`/modificar_productos/${productoId}`, {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Producto modificado correctamente");
                    location.reload(); // Recargar para reflejar los cambios
                } else {
                    alert(data.message || "Error al modificar producto");
                }
            })
            .catch(error => console.error("Error modificando producto:", error));
        });
    });
});
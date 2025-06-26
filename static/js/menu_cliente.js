function notificarAgregado(event) {
            event.preventDefault();
            let formulario = event.target;

            let notificacion = document.getElementById("notificacion");
            notificacion.style.display = "block";

            setTimeout(() => {
                notificacion.style.display = "none";
                formulario.submit();
            }, 2000);
        }

function addToCart(productId, productName, productPrice, productImage) {
    const quantityInput = document.querySelector(`input[name="cantidad"][data-id="${productId}"]`);
    const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

    let cart = JSON.parse(localStorage.getItem('cart')) || [];

    const idNum = parseInt(productId);
    const priceNum = parseFloat(productPrice);

    const existingProduct = cart.find(product => product.id === idNum);

    if (existingProduct) {
        existingProduct.quantity += quantity;
    } else {
        cart.push({
            id: idNum,
            name: productName,
            price: priceNum,
            quantity: quantity,
            image: productImage // Guardamos la imagen correctamente
        });
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    showNotification(`${quantity}x ${productName} agregado al carrito ✅`);
}

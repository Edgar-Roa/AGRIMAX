document.addEventListener('DOMContentLoaded', function () {
    const cartContainer = document.getElementById('cart-container');
    const totalPriceElement = document.getElementById('total-price');
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    let total = 0;

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>Tu carrito está vacío.</p>";
        return;
    }

    cart.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = "cart-item";
        productElement.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="cart-image">
            <div class="cart-info">
                <p><strong>${product.name}</strong></p>
                <p>Precio: $${product.price}</p>
                <p>Cantidad: ${product.quantity}</p>
                <p>Subtotal: $${(product.price * product.quantity).toFixed(2)}</p>
            </div>
            <button onclick="removeFromCart('${product.id}')" class="btn-eliminar">Eliminar</button>
        `;
        cartContainer.appendChild(productElement);

        total += parseFloat(product.price) * product.quantity;
    });

    totalPriceElement.innerText = `Total: $${total.toFixed(2)}`;
});

function removeFromCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    cart = cart.filter(product => product.id.toString() !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    location.reload();
}

function clearCart() {
    localStorage.removeItem('cart');
    location.reload();
}

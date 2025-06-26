
// Cerrar menú al hacer clic fuera de él
document.addEventListener('click', function(event) {
    var menuContent = document.getElementById('menuContent');
    var menuButton = document.querySelector('.menu-button');
    
    if (menuContent.style.display === "block" && 
        !menuContent.contains(event.target) && 
        !menuButton.contains(event.target)) {
        menuContent.style.display = "none";
    }
});

// Funciones para modales
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
}

window.onclick = function(event) {
    if (event.target.className === 'product-modal') {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}
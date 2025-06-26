// Función para alternar el menú hamburguesa
function toggleMenu() {
    const dropdownMenu = document.getElementById('menuContent');
    if (dropdownMenu.style.display === "block") {
        dropdownMenu.style.display = "none";
    } else {
        dropdownMenu.style.display = "block";
    }
}

// Cerrar el menú al hacer clic fuera de él
document.addEventListener('click', (event) => {
    const hamburger = document.querySelector('.hamburger');
    const dropdownMenu = document.getElementById('menuContent');
    
    if (dropdownMenu.style.display === "block" && 
        !dropdownMenu.contains(event.target) && 
        !hamburger.contains(event.target)) {
        dropdownMenu.style.display = "none";
    }
});
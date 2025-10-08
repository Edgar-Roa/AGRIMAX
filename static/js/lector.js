function leerTexto(texto) {
  const mensaje = new SpeechSynthesisUtterance(texto);
  mensaje.lang = 'es-MX';
  mensaje.rate = 1;
  mensaje.pitch = 1;
  speechSynthesis.speak(mensaje);
}

function leerTabActivo() {
  const modoLectorActivo = document.body.classList.contains('modo-lector');
  if (!modoLectorActivo) return;

  const seccionActiva = document.querySelector('.config-section.active');
  if (seccionActiva) {
    const texto = seccionActiva.innerText;
    leerTexto(texto);
  }
}

// Leer al cargar la página
window.onload = leerTabActivo;

// Leer al cambiar de tab
document.querySelectorAll('.config-menu li').forEach(tab => {
  tab.addEventListener('click', () => {
    setTimeout(leerTabActivo, 300);
  });
});

function leerContenidoPrincipal() {
  const modoLectorActivo = document.body.classList.contains('modo-lector');
  if (!modoLectorActivo) return;

  const contenido = document.querySelector('.config-section.active') ||
                    document.querySelector('main') ||
                    document.querySelector('.contenido') ||
                    document.body;

  if (contenido) {
    const texto = contenido.innerText;
    const mensaje = new SpeechSynthesisUtterance(texto);
    mensaje.lang = 'es-MX';
    mensaje.rate = 1;
    speechSynthesis.speak(mensaje);
  }
}

window.onload = leerContenidoPrincipal;
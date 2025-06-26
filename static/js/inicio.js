        document.addEventListener('DOMContentLoaded', function() {
            const track = document.querySelector('.carousel-track');
            const slides = Array.from(document.querySelectorAll('.carousel-slide'));
            const indicators = Array.from(document.querySelectorAll('.carousel-indicator'));
            const prevBtn = document.querySelector('.carousel-btn.prev');
            const nextBtn = document.querySelector('.carousel-btn.next');
            
            let currentIndex = 0;
            const slideCount = slides.length;
            
            // Función para actualizar la posición del carrusel
            function updateCarousel() {
                track.style.transform = `translateX(-${currentIndex * 100}%)`;
                
                // Actualizar indicadores
                indicators.forEach((indicator, index) => {
                    indicator.classList.toggle('active', index === currentIndex);
                });
            }
            
            // Navegación con botones
            nextBtn.addEventListener('click', function() {
                currentIndex = (currentIndex + 1) % slideCount;
                updateCarousel();
            });
            
            prevBtn.addEventListener('click', function() {
                currentIndex = (currentIndex - 1 + slideCount) % slideCount;
                updateCarousel();
            });
            
            // Navegación con indicadores
            indicators.forEach((indicator, index) => {
                indicator.addEventListener('click', function() {
                    currentIndex = index;
                    updateCarousel();
                });
            });
            
            // Auto-avance (opcional)
            let interval = setInterval(function() {
                currentIndex = (currentIndex + 1) % slideCount;
                updateCarousel();
            }, 5000);
            
            // Pausar auto-avance al interactuar
            track.addEventListener('mouseenter', function() {
                clearInterval(interval);
            });
            
            track.addEventListener('mouseleave', function() {
                interval = setInterval(function() {
                    currentIndex = (currentIndex + 1) % slideCount;
                    updateCarousel();
                }, 5000);
            });
        });
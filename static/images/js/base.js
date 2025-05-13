// Favorite heart animation
document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'favorite-section') {
        const heartIcon = document.querySelector('#favorite-section .fa-heart');
        if (heartIcon) {
            heartIcon.classList.add('heart-animation');
            setTimeout(() => heartIcon.classList.remove('heart-animation'), 500);
        }
    }
});

// Mobile menu toggle
document.getElementById('menu-toggle')?.addEventListener('click', function() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
});
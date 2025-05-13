document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        const hearts = document.querySelectorAll('.fa-heart');
        hearts.forEach(heart => {
            if (heart.closest('#favorite-section')) {
                heart.classList.add('heart-animation');
                setTimeout(() => heart.classList.remove('heart-animation'), 500);
            }
        });
        

    });
});

document.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'favorite-section') {
        const heart = document.querySelector('#favorite-section .fa-heart');
        if (heart) {
            heart.classList.add('animate-pulse');
            setTimeout(() => heart.classList.remove('animate-pulse'), 500);
        }
    }
});
// Auto-hide flash messages after 4 seconds (shorter for mobile)
setTimeout(function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        message.style.transition = 'opacity 0.3s ease';
        message.style.opacity = '0';
        setTimeout(function() {
            if (message.parentNode) {
                message.remove();
            }
        }, 300);
    });
}, 4000);

// Add touch feedback for cards
const cards = document.querySelectorAll('.instructor-card');
cards.forEach(card => {
    card.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.98)';
    }, { passive: true });
    
    card.addEventListener('touchend', function() {
        this.style.transform = 'scale(1)';
    });
    
    card.addEventListener('touchcancel', function() {
        this.style.transform = 'scale(1)';
    });
});

// Prevent zoom on double-tap for better mobile experience
document.addEventListener('touchstart', (e) => {
    if (e.touches.length > 1) {
        e.preventDefault();
    }
}, { passive: false });
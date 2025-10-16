// Скрыть подсказку, если скролл достиг конца списка
document.addEventListener('DOMContentLoaded', function () {
    const wrapper = document.querySelector('.track-list-wrapper');
    const hint = wrapper.querySelector('.scroll-hint');

    function checkScroll() {
        if (wrapper.scrollLeft + wrapper.clientWidth >= wrapper.scrollWidth - 1) {
            // Скрыть подсказку при достижении конца прокрутки
            hint.style.opacity = '0';
        } else {
            hint.style.opacity = '1';
        }
    }

    // Проверяем при скролле и при загрузке
    wrapper.addEventListener('scroll', checkScroll);
    checkScroll();
});

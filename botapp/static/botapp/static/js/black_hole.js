document.addEventListener('DOMContentLoaded', function () {
    const blackHoleElement = document.querySelector('.black-hole-link');
    const flag = localStorage.getItem('blackHoleShown');

    if (flag) {
        // Флаг есть — скрываем элемент
        blackHoleElement.style.display = 'none';
    } else {
        // Показываем анимацию, после чего ставим флаг
        blackHoleElement.style.display = 'block';

        // Можно задать таймаут для скрытия или оставить видимым, если анимация должна плавно закончиться
        // Например, скрыть после 77 секунд (длительность анимации)
        setTimeout(() => {
            blackHoleElement.style.display = 'none';
            localStorage.setItem('blackHoleShown', 'true');
        }, 77000);
    }
});

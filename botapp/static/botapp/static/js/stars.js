// Функция для создания и показа звёздочек в случайных местах экрана
function createRandomStar() {
    const star = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    star.classList.add('star');
    star.style.left = Math.random() * window.innerWidth + 'px';
    star.style.top = Math.random() * window.innerHeight + 'px';
    star.style.width = '13px';
    star.style.height = '13px';
    star.innerHTML = '<use href="#star"></use>';

    document.body.appendChild(star);

    // Удаляем звезду через 3 секунды (после анимации)
    setTimeout(() => {
        star.remove();
    }, 3000);
}

// Создаём несколько звёздочек с интервалом
setInterval(createRandomStar, 600);
const cosmicWind = document.getElementById('cosmic-wind-overlay');

function startWindAnimation() {
  cosmicWind.style.opacity = '1';  // Показать
  const svgWind = cosmicWind.querySelector('.wind-glitch');
  if (svgWind) {
    svgWind.style.animationPlayState = 'running'; // Запустить анимацию
  }
}

function stopWindAnimation() {
  cosmicWind.style.opacity = '0'; // Скрыть
  const svgWind = cosmicWind.querySelector('.wind-glitch');
  if (svgWind) {
    svgWind.style.animationPlayState = 'paused'; // Остановить анимацию
  }
}

function windCycle() {
  startWindAnimation();
  setTimeout(() => {
    stopWindAnimation();
    // Пауза 4 минуты перед следующей активацией
    setTimeout(windCycle, 240000);
  }, 10000); // Дуть 10 секунд
}

window.addEventListener('load', () => {
  // Запуск с задержкой 3 минуты для плавного запуска
  setTimeout(windCycle, 180000);
});

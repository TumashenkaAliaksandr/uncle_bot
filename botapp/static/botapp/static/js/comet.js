document.addEventListener('DOMContentLoaded', () => {
  const comets = [
    { selector: '.comet1', animation: 'comet1Move 5s linear forwards' },
    { selector: '.comet2', animation: 'comet2Move 6s linear forwards' },
    { selector: '.comet3', animation: 'comet3Move 7s linear forwards' },
  ];

  const interval = 30000; // 30 секунд между пролётами
  let index = 0;

  function launchComet() {
    const cometData = comets[index];
    const comet = document.querySelector(cometData.selector);
    if (!comet) return;

    comet.style.display = 'block';
    comet.style.opacity = '1';
    comet.style.animation = cometData.animation;

    function onAnimationEnd() {
      comet.style.display = 'none';
      comet.style.opacity = '0';
      comet.style.animation = 'none';
      comet.removeEventListener('animationend', onAnimationEnd);
    }

    comet.addEventListener('animationend', onAnimationEnd);

    index = (index + 1) % comets.length;
  }

  launchComet(); // Запустить первую сразу
  setInterval(launchComet, interval);
});

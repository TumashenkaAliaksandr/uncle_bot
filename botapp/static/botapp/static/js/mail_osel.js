function typeWriterEffect(element, text, delay = 40, callback) {
  let i = 0;
  element.textContent = '';
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, delay);
    } else if (callback) {
      callback();
    }
  }
  type();
}

function showMarginCitate() {
  const p = document.querySelector('.margin-citate');
  if (!p) return;
  if (p.style.display === 'block') return;

  p.style.display = 'block';
  const message = "📡 Поступил сигнал от Космического Осла - сигнал N72 - ама мама банки ...";

  typeWriterEffect(p, message, 40, () => {
    setTimeout(() => {
      p.style.display = 'none';
      localStorage.setItem('lastMarginCitateShown', Date.now());
    }, 10000);
  });
}

function tryShowMarginCitate() {
  const lastShown = localStorage.getItem('lastMarginCitateShown');
  const now = Date.now();
  if (!lastShown || (now - lastShown > 30 * 60 * 1000)) {
    setTimeout(showMarginCitate, 3 * 60 * 1000);
  }
}

window.addEventListener('load', () => {
  tryShowMarginCitate();
});

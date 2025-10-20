const audio = document.getElementById('audioPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const loopBtn = document.getElementById('loopBtn');
const shuffleBtn = document.getElementById('shuffleBtn');
const currentTimeEl = document.getElementById('currentTime');
const durationEl = document.getElementById('duration');
const volumeIcon = document.getElementById('volumeIcon');
const trackList = document.getElementById('trackList');
const trackCover = document.getElementById('trackCover');
const trackTitle = document.getElementById('trackTitle');
const trackAlbum = document.getElementById('trackAlbum');
const themeToggle = document.getElementById('themeToggle');
const playerContainer = document.getElementById('playerContainer');

const progressBarSvg = document.querySelector('.progress-bar');
const volumeBarSvg = document.querySelector('.volume-bar');
const volumeThumb = document.querySelector('.volume-thumb');

const progressBarLength = progressBarSvg ? progressBarSvg.getTotalLength() : 0;
const volumeBarLength = volumeBarSvg ? volumeBarSvg.getTotalLength() : 0;

let tracks = [];
let currentTrackIdx = 0;
let isLoop = false;
let isShuffle = false;
let playedOnce = false;

// Переменные для отслеживания фокуса и таймера возврата
let focusTimeoutId = null;
const FOCUS_RETURN_DELAY = 4000; // 4 секунды
let lastScrollTime = 0;

// Инициализация треков и навешивание событий
if (trackList) {
  for (let li of trackList.children) {
    tracks.push({
      id: li.dataset.id,
      title: li.textContent.trim(),
      cover: li.querySelector('img') ? li.querySelector('img').src : '',
      element: li
    });
    li.addEventListener('click', () => {
      selectTrack([...trackList.children].indexOf(li), true);
    });
  }
}

function formatTime(timeSec) {
  const t = Math.floor(timeSec);
  return `${Math.floor(t / 60)}:${('0' + (t % 60)).slice(-2)}`;
}

function updateProgressBar(currentTime, duration) {
  if (!progressBarSvg || !duration) return;
  const percent = currentTime / duration;
  const offset = progressBarLength * (1 - percent);
  progressBarSvg.style.strokeDasharray = progressBarLength;
  progressBarSvg.style.strokeDashoffset = offset;
}

function updateVolumeBar(volume) {
  if (!volumeBarSvg || !volumeThumb) return;
  const offset = volumeBarLength * (1 - volume);
  volumeBarSvg.style.strokeDasharray = volumeBarLength;
  volumeBarSvg.style.strokeDashoffset = offset;
  const minX = 10;
  const maxX = 270;
  const cx = minX + (maxX - minX) * volume;
  volumeThumb.setAttribute('cx', cx);
  if (volumeIcon) {
    volumeIcon.textContent = volume === 0 ? '🔇' : (volume < 0.5 ? '🔉' : '🔊');
  }
}

function scrollTrackIntoView(idx) {
  const container = trackList.parentElement; // контейнер с overflow-x:auto
  const element = tracks[idx].element;

  const elementLeft = element.offsetLeft;
  const elementWidth = element.offsetWidth;
  const containerScrollLeft = container.scrollLeft;
  const containerWidth = container.offsetWidth;

  if (elementLeft < containerScrollLeft) {
    container.scrollTo({ left: elementLeft, behavior: 'smooth' });
  } else if (elementLeft + elementWidth > containerScrollLeft + containerWidth) {
    container.scrollTo({ left: elementLeft + elementWidth - containerWidth, behavior: 'smooth' });
  }
}

// Функция возврата прокрутки к активному треку
function returnScrollToActiveTrack() {
  scrollTrackIntoView(currentTrackIdx);
  focusActiveTrack();
}

// Установка фокуса на активный трек
function focusActiveTrack() {
  if (!tracks.length) return;
  const element = tracks[currentTrackIdx].element;
  if (element) {
    element.focus();
  }
}

function selectTrack(idx, resetProgress = true) {
  if (tracks.length === 0) return;
  if (idx < 0) idx = tracks.length - 1;
  if (idx >= tracks.length) idx = 0;
  currentTrackIdx = idx;
  if (resetProgress) audio.currentTime = 0;

  tracks.forEach(t => t.element.classList.remove('active', 'bg-success', 'bg-opacity-25'));
  tracks[idx].element.classList.add('active', 'bg-success', 'bg-opacity-25');

  scrollTrackIntoView(idx);
  focusActiveTrack();

  // Сброс таймера возврата прокрутки
  if (focusTimeoutId) {
    clearTimeout(focusTimeoutId);
    focusTimeoutId = null;
  }

  const audioUrl = tracks[idx].element.dataset.url;
  if (audioUrl) {
    audio.src = audioUrl;
    audio.load();
    if (playedOnce) audio.play();
  } else {
    console.error('Audio URL not found for track id:', tracks[idx].id);
  }

  const coverImg = tracks[idx].element.querySelector('img');
  if (coverImg && trackCover) trackCover.src = coverImg.src;
  if (trackTitle) trackTitle.textContent = tracks[idx].title;
  if (trackAlbum && tracks[idx].element.dataset.album) trackAlbum.textContent = tracks[idx].element.dataset.album;
}

// Обработка скролла в контейнере треков
if (trackList.parentElement) {
  trackList.parentElement.addEventListener('scroll', () => {
    lastScrollTime = Date.now();
    if (focusTimeoutId) {
      clearTimeout(focusTimeoutId);
    }
    focusTimeoutId = setTimeout(() => {
      // Проверяем, прокручен ли контейнер далеко от активного трека
      const container = trackList.parentElement;
      const element = tracks[currentTrackIdx].element;
      const containerScrollLeft = container.scrollLeft;
      const containerWidth = container.offsetWidth;
      const elementLeft = element.offsetLeft;
      const elementWidth = element.offsetWidth;

      const isElementVisible = elementLeft >= containerScrollLeft && (elementLeft + elementWidth) <= (containerScrollLeft + containerWidth);
      if (!isElementVisible) {
        returnScrollToActiveTrack();
      }
    }, FOCUS_RETURN_DELAY);
  });
}

// Управление воспроизведением
playPauseBtn && playPauseBtn.addEventListener('click', () => {
  if (audio.paused) {
    audio.play();
    playedOnce = true;
  } else {
    audio.pause();
  }
});

audio.addEventListener('play', () => {
  if (playPauseBtn) playPauseBtn.textContent = '⏸️';
});
audio.addEventListener('pause', () => {
  if (playPauseBtn) playPauseBtn.textContent = '▶️';
});

audio.addEventListener('timeupdate', () => {
  if (!audio.duration || isNaN(audio.duration) || audio.duration === 0) return;
  if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
  if (durationEl) durationEl.textContent = formatTime(audio.duration - audio.currentTime);
  updateProgressBar(audio.currentTime, audio.duration);
});

const babuinoContainer = document.getElementById('babuinoContainer');
const babuinoVideo = document.getElementById('babuinoVideo');
let babuinoTimeout;

// При начале воспроизведения аудио
audio.addEventListener('play', () => {
  if (!babuinoContainer || !babuinoVideo) return;

  // если уже запущен таймер — сбрасываем
  if (babuinoTimeout) {
    clearTimeout(babuinoTimeout);
    babuinoTimeout = null;
  }

  // показываем и запускаем видео
  babuinoContainer.classList.add('active');
  babuinoVideo.currentTime = 0;
  babuinoVideo.play();

  // скрываем через 14 секунд
  babuinoTimeout = setTimeout(() => {
    babuinoContainer.classList.remove('active');
    babuinoVideo.pause();
  }, 14000);
});

// При паузе — сразу скрываем
audio.addEventListener('pause', () => {
  if (babuinoContainer && babuinoVideo) {
    babuinoContainer.classList.remove('active');
    babuinoVideo.pause();
    if (babuinoTimeout) clearTimeout(babuinoTimeout);
  }
});


const progressContainer = document.querySelector('.progress-svg');
if (progressContainer) {
  progressContainer.addEventListener('click', e => {
    const rect = progressContainer.getBoundingClientRect();
    let clickX = e.clientX - rect.left;
    clickX = Math.max(0, Math.min(clickX, rect.width));
    const percent = clickX / rect.width;
    if (audio.duration) audio.currentTime = percent * audio.duration;
  });
}

prevBtn && prevBtn.addEventListener('click', () => selectTrack(currentTrackIdx - 1));
nextBtn && nextBtn.addEventListener('click', () => {
  if (isShuffle) selectTrack(Math.floor(Math.random() * tracks.length));
  else selectTrack(currentTrackIdx + 1);
});

loopBtn && loopBtn.addEventListener('click', () => {
  isLoop = !isLoop;
  audio.loop = isLoop;
  loopBtn.classList.toggle('active', isLoop);
});

shuffleBtn && shuffleBtn.addEventListener('click', () => {
  isShuffle = !isShuffle;
  shuffleBtn.classList.toggle('active', isShuffle);
});

audio.addEventListener('ended', () => {
  if (!isLoop) nextBtn && nextBtn.click();
});

const volumeContainer = document.querySelector('.volume-svg');
let isVolumeDragging = false;

function volumeSetByClick(clientX) {
  if (!volumeContainer) return;
  const rect = volumeContainer.getBoundingClientRect();
  let clickX = clientX - rect.left;
  const paddingLeft = 10;
  const paddingRight = 270;
  clickX = Math.max(paddingLeft, Math.min(clickX, paddingRight));
  const volume = (clickX - paddingLeft) / (paddingRight - paddingLeft);
  audio.volume = volume;
  updateVolumeBar(volume);
}

if (volumeContainer) {
  volumeContainer.addEventListener('mousedown', e => {
    isVolumeDragging = true;
    volumeSetByClick(e.clientX);
  });
  window.addEventListener('mouseup', () => {
    isVolumeDragging = false;
  });
  window.addEventListener('mousemove', e => {
    if (isVolumeDragging) volumeSetByClick(e.clientX);
  });
}

updateVolumeBar(audio.volume);
updateProgressBar(0, 1);

themeToggle && themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light');
});

const canvas = document.getElementById('visualizer');
const ctx = canvas ? canvas.getContext('2d') : null;
let audioCtx, analyser, src, dataArray;

function setupVisualizer() {
  if (!audioCtx && audio && ctx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    src = audioCtx.createMediaElementSource(audio);
    analyser = audioCtx.createAnalyser();
    src.connect(analyser);
    analyser.connect(audioCtx.destination);
    analyser.fftSize = 128;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
  }
}

audio.addEventListener('play', () => {
  setupVisualizer();
  drawVisualizer();
});

function drawVisualizer() {
  if (!analyser || !ctx || !canvas) return;
  analyser.getByteFrequencyData(dataArray);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const barWidth = canvas.width / dataArray.length;
  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = dataArray[i] * 0.6;
    ctx.fillStyle = 'lime';
    ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 2, barHeight);
  }
  if (!audio.paused) requestAnimationFrame(drawVisualizer);
}

selectTrack(tracks.findIndex(t => t.element.classList.contains('active')), false);

const container = document.getElementById('skyContainer');
const colors = ['#ff4d4d','#4dff88','#4d88ff','#ffdb4d','#ff4da6','#66ffff','#ff9966'];

if(container){
  for(let i=0; i <30; i++){
    const dot = document.createElement('div');
    dot.className = 'pulse-dot';
    const size = 10 + Math.random() * 20;
    dot.style.width = `${size}px`;
    dot.style.height = `${size}px`;
    dot.style.top = `${Math.random() * 90}%`;
    dot.style.left = `${Math.random() * 90}%`;
    dot.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    dot.style.animationDelay = `${Math.random() * 2.5}s`;
    container.appendChild(dot);
  }
}

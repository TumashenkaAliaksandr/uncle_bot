const audio = document.getElementById('audioPlayer');
const playPauseBtn = document.getElementById('playPauseBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const loopBtn = document.getElementById('loopBtn');
const shuffleBtn = document.getElementById('shuffleBtn');
const progressBar = document.getElementById('progressBar');
const currentTimeEl = document.getElementById('currentTime');
const durationEl = document.getElementById('duration');
const volumeBar = document.getElementById('volumeBar');
const volumeIcon = document.getElementById('volumeIcon');
const trackList = document.getElementById('trackList');
const trackCover = document.getElementById('trackCover');
const trackTitle = document.getElementById('trackTitle');
const trackAlbum = document.getElementById('trackAlbum');
const themeToggle = document.getElementById('themeToggle');
const playerContainer = document.getElementById('playerContainer');

let tracks = [];
let currentTrackIdx = 0;
let isLoop = false;
let isShuffle = false;
let playedOnce = false;

// Инициализация треков из списка
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

// Форматирование времени в ММ:СС
function formatTime(sec) {
  sec = Math.floor(sec);
  return `${Math.floor(sec / 60)}:${('0' + (sec % 60)).slice(-2)}`;
}

// Выбор и загрузка трека
function selectTrack(idx, resetProgress = true) {
  if (tracks.length === 0) return;
  if (idx < 0) idx = tracks.length - 1;
  if (idx >= tracks.length) idx = 0;
  currentTrackIdx = idx;

  if (resetProgress) audio.currentTime = 0;
  tracks.forEach(t => t.element.classList.remove('active'));
  tracks[idx].element.classList.add('active');

  fetch(`/track/${tracks[idx].id}/`)
    .then(resp => {
      if (!resp.ok) throw new Error('Network response was not ok');
      return resp.text();
    })
    .then(html => {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newAudio = doc.getElementById('audioPlayer');
      const newCover = doc.getElementById('trackCover');
      const newTitle = doc.getElementById('trackTitle');
      const newAlbum = doc.getElementById('trackAlbum');

      if (newAudio && newAudio.src) audio.src = newAudio.src;
      if (newCover && newCover.src) trackCover.src = newCover.src;
      if (newTitle) trackTitle.textContent = newTitle.textContent;
      if (newAlbum) trackAlbum.textContent = newAlbum.textContent;

      audio.load();
      if (playedOnce) audio.play();
    })
    .catch(err => console.error('Error loading track:', err));
}

// Play/Pause переключение
playPauseBtn && playPauseBtn.addEventListener('click', () => {
  if (audio.paused) {
    audio.play();
    playedOnce = true;
  } else {
    audio.pause();
  }
});

// Обновление кнопки Play/Pause при воспроизведении и паузе
audio.addEventListener('play', () => {
  if (playPauseBtn) playPauseBtn.textContent = '⏸️';
});
audio.addEventListener('pause', () => {
  if (playPauseBtn) playPauseBtn.textContent = '▶️';
});

// Обновление прогресса и времени
audio.addEventListener('timeupdate', () => {
  if (!audio.duration || isNaN(audio.duration)) return;
  progressBar.value = (audio.currentTime / audio.duration) * 100 || 0;
  currentTimeEl.textContent = formatTime(audio.currentTime);
  durationEl.textContent = formatTime(audio.duration);
});

// Прокрутка по прогрессбару
progressBar && progressBar.addEventListener('input', () => {
  if (!audio.duration || isNaN(audio.duration)) return;
  audio.currentTime = (progressBar.value / 100) * audio.duration;
});

// Кнопки предыдущий/следующий
prevBtn && prevBtn.addEventListener('click', () => selectTrack(currentTrackIdx - 1));
nextBtn && nextBtn.addEventListener('click', () => {
  if (isShuffle) {
    selectTrack(Math.floor(Math.random() * tracks.length));
  } else {
    selectTrack(currentTrackIdx + 1);
  }
});

// Переключение повторения
loopBtn && loopBtn.addEventListener('click', () => {
  isLoop = !isLoop;
  audio.loop = isLoop;
  loopBtn.classList.toggle('active', isLoop);
});

// Переключение перемешивания
shuffleBtn && shuffleBtn.addEventListener('click', () => {
  isShuffle = !isShuffle;
  shuffleBtn.classList.toggle('active', isShuffle);
});

// Автоматический переход к следующему треку
audio.addEventListener('ended', () => {
  if (!isLoop) nextBtn && nextBtn.click();
});

// Управление громкостью
volumeBar && volumeBar.addEventListener('input', () => {
  audio.volume = volumeBar.value;
  if (volumeIcon) {
    volumeIcon.textContent = audio.volume === 0 ? '🔇' : (audio.volume < 0.5 ? '🔉' : '🔊');
  }
});
if (volumeBar) volumeBar.value = 1;
audio.volume = 1;

// Переключение темы
themeToggle && themeToggle.addEventListener('click', () => {
  document.body.classList.toggle('light');
});

// Визуализатор аудио
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
  if (playPauseBtn) playPauseBtn.textContent = '⏸️';
  setupVisualizer();
  drawVisualizer();
});

function drawVisualizer() {
  if (!analyser || !ctx || !canvas) return;
  analyser.getByteFrequencyData(dataArray);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  let barWidth = canvas.width / dataArray.length;
  for (let i = 0; i < dataArray.length; i++) {
    let barHeight = dataArray[i] * 0.6;
    ctx.fillStyle = 'lime';
    ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 2, barHeight);
  }
  if (!audio.paused) requestAnimationFrame(drawVisualizer);
}

// Инициализация — выбираем активный трек или первый
selectTrack(tracks.findIndex(t => t.element.classList.contains('active')), false);

// Создание пульсирующих точек в #skyContainer
const container = document.getElementById('skyContainer');
const colors = ['#ff4d4d', '#4dff88', '#4d88ff', '#ffdb4d', '#ff4da6', '#66ffff', '#ff9966'];

if (container) {
  for (let i = 0; i < 30; i++) {
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

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

for (let li of trackList.children) {
    tracks.push({
        id: li.dataset.id,
        title: li.textContent.trim(),
        cover: li.querySelector('img').src,
        element: li
    });
    li.addEventListener('click', () => {
        selectTrack([...trackList.children].indexOf(li), true);
    });
}

function formatTime(sec) {
    sec = Math.floor(sec);
    return `${Math.floor(sec/60)}:${('0'+(sec%60)).slice(-2)}`;
}

function selectTrack(idx, resetProgress=true) {
    if (idx < 0) idx = tracks.length - 1;
    if (idx >= tracks.length) idx = 0;
    currentTrackIdx = idx;
    // Сброс прогресса, если не дослушал
    if (resetProgress) audio.currentTime = 0;
    for (let t of tracks) t.element.classList.remove('active');
    tracks[idx].element.classList.add('active');
    fetch(`/track/${tracks[idx].id}/`)
        .then(resp => resp.text())
        .then(html => {
            // Парсим только нужные данные
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            audio.src = doc.getElementById('audioPlayer').src;
            trackCover.src = doc.getElementById('trackCover').src;
            trackTitle.textContent = doc.getElementById('trackTitle').textContent;
            trackAlbum.textContent = doc.getElementById('trackAlbum').textContent;
            audio.load();
            if (playedOnce) audio.play();
        });
}

playPauseBtn.onclick = () => {
    if (audio.paused) {
        audio.play();
        playPauseBtn.textContent = '⏸️';
        playedOnce = true;
    } else {
        audio.pause();
        playPauseBtn.textContent = '▶️';
    }
};

audio.onplay = () => playPauseBtn.textContent = '⏸️';
audio.onpause = () => playPauseBtn.textContent = '▶️';

audio.addEventListener('timeupdate', () => {
    progressBar.value = audio.currentTime / audio.duration * 100 || 0;
    currentTimeEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration || 0);
});
progressBar.addEventListener('input', () => {
    audio.currentTime = progressBar.value * audio.duration / 100;
});

prevBtn.onclick = () => selectTrack(currentTrackIdx - 1);
nextBtn.onclick = () => selectTrack(isShuffle ? Math.floor(Math.random()*tracks.length) : currentTrackIdx + 1);

loopBtn.onclick = () => {
    isLoop = !isLoop;
    audio.loop = isLoop;
    loopBtn.classList.toggle('active', isLoop);
};
shuffleBtn.onclick = () => {
    isShuffle = !isShuffle;
    shuffleBtn.classList.toggle('active', isShuffle);
};
audio.onended = () => {
    if (!isLoop) nextBtn.onclick();
};

volumeBar.oninput = () => {
    audio.volume = volumeBar.value;
    volumeIcon.textContent = audio.volume == 0 ? '🔇' : (audio.volume < 0.5 ? '🔉' : '🔊');
};
volumeBar.value = 1;
audio.volume = 1;

themeToggle.onclick = () => {
    document.body.classList.toggle('light');
};

// График баланса (визуализация)
const canvas = document.getElementById('visualizer');
const ctx = canvas.getContext('2d');
let audioCtx, analyser, src, dataArray;

function setupVisualizer() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        src = audioCtx.createMediaElementSource(audio);
        analyser = audioCtx.createAnalyser();
        src.connect(analyser);
        analyser.connect(audioCtx.destination);
        analyser.fftSize = 128;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
    }
}
audio.onplay = () => {
    playPauseBtn.textContent = '⏸️';
    setupVisualizer();
    drawVisualizer();
};
function drawVisualizer() {
    if (!analyser) return;
    analyser.getByteFrequencyData(dataArray);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let barWidth = (canvas.width / dataArray.length);
    for (let i = 0; i < dataArray.length; i++) {
        let barHeight = dataArray[i] * 0.6;
        ctx.fillStyle = 'lime';
        ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 2, barHeight);
    }
    if (!audio.paused) requestAnimationFrame(drawVisualizer);
}

// Начальная инициализация
selectTrack(tracks.findIndex(t => t.element.classList.contains('active')), false);


const container = document.getElementById('skyContainer');
const colors = ['#ff4d4d', '#4dff88', '#4d88ff', '#ffdb4d', '#ff4da6', '#66ffff', '#ff9966'];

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

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('bg-slider').appendChild(renderer.domElement);

// Разнообразные геометрии для слайдов
const geometries = [
  new THREE.BoxGeometry(),
  new THREE.SphereGeometry(0.8, 32, 32),
  new THREE.ConeGeometry(0.8, 1.5, 32),
  new THREE.TorusGeometry(0.7, 0.3, 16, 100),
  new THREE.TorusKnotGeometry(0.5, 0.2, 100, 16),
  new THREE.DodecahedronGeometry(0.8),
  new THREE.IcosahedronGeometry(0.8),
  new THREE.OctahedronGeometry(0.8),
];

// Экзотические материалы с эффектами
const materials = [
  new THREE.MeshNormalMaterial(),
  new THREE.MeshStandardMaterial({ color: 0xff4444, roughness: 0.3, metalness: 0.8 }),
  new THREE.MeshStandardMaterial({ color: 0x44ff44, roughness: 0.7, metalness: 0.2 }),
  new THREE.MeshPhysicalMaterial({ color: 0x0044ff, clearcoat: 1, clearcoatRoughness: 0.1, metalness: 0.5 }),
  new THREE.MeshPhongMaterial({ color: 0xffaa00, shininess: 100, specular: 0xffff00 }),
  new THREE.MeshLambertMaterial({ color: 0x00ffaa, emissive: 0x004400 }),
  new THREE.MeshToonMaterial({ color: 0xff00ff }),
  new THREE.MeshStandardMaterial({
    color: 0xffffff,
    metalness: 1,
    roughness: 0,
    envMapIntensity: 1,
    emissive: 0x222222,
    emissiveIntensity: 0.5
  }),
];

// Освещение
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);
const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambientLight);

let currentSlideIndex = 0;
let mesh = new THREE.Mesh(geometries[currentSlideIndex], materials[currentSlideIndex]);
scene.add(mesh);
camera.position.z = 3;

function changeSlide(index) {
  if (index < 0 || index >= geometries.length) return;
  scene.remove(mesh);
  mesh.geometry.dispose();
  mesh.material.dispose();
  mesh = new THREE.Mesh(geometries[index], materials[index]);
  scene.add(mesh);
  currentSlideIndex = index;
}

function animate() {
  requestAnimationFrame(animate);
  mesh.rotation.x += 0.01;
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Аудио и режимы
const audios = document.querySelectorAll('.songs-list audio');
const playModeRadios = document.querySelectorAll('input[name="playMode"]');

let playMode = "single";
let currentAudioIndex = -1;

playModeRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.checked) playMode = radio.value;
  });
});

function playAudioAtIndex(index) {
  if (index < 0 || index >= audios.length) return;

  // Сброс времени и прогресса предыдущей песни
  if (currentAudioIndex !== -1 && currentAudioIndex !== index) {
    audios[currentAudioIndex].pause();
    audios[currentAudioIndex].currentTime = 0;
    resetProgressBar(currentAudioIndex);
  }

  // Сброс времени новой песни, если переключаемся
  if (currentAudioIndex !== index) {
    audios[index].currentTime = 0;
  }

  // Пауза всех аудио кроме выбранного
  audios.forEach((audio, i) => {
    if (i !== index) audio.pause();
  });

  audios[index].play();
  currentAudioIndex = index;
  changeSlide(index);
}

function resetProgressBar(index) {
  const player = audios[index].closest('.audio-player');
  if (!player) return;
  const progressBar = player.querySelector('.progress-bar');
  const timeDisplay = player.querySelector('.time-display');
  if (progressBar) progressBar.value = 0;
  if (timeDisplay && audios[index].duration) {
    timeDisplay.textContent = formatTime(0) + ' / ' + formatTime(audios[index].duration);
  }
}

document.querySelectorAll('.track-item').forEach(item => {
  item.style.cursor = 'pointer';
  item.addEventListener('click', () => {
    const index = parseInt(item.getAttribute('data-slide-index'));
    playAudioAtIndex(index);
  });
});

audios.forEach(audio => {
  audio.addEventListener('play', () => {
    audios.forEach(otherAudio => {
      if (otherAudio !== audio) otherAudio.pause();
    });
  });
});

function getRandomIndex(excludeIndex, max) {
  if (max <= 1) return 0;
  let randIndex = Math.floor(Math.random() * max);
  while (randIndex === excludeIndex) {
    randIndex = Math.floor(Math.random() * max);
  }
  return randIndex;
}

audios.forEach((audio, index) => {
  audio.addEventListener('ended', () => {
    audio.currentTime = 0;
    resetProgressBar(index);

    if (playMode === "single") {
      // В режиме "одна песня" повторяем текущую песню с начала
      playAudioAtIndex(currentAudioIndex);
    } else if (playMode === "loop") {
      let nextIndex = (currentAudioIndex + 1) % audios.length;
      playAudioAtIndex(nextIndex);
    } else if (playMode === "random") {
      let nextIndex = getRandomIndex(currentAudioIndex, audios.length);
      playAudioAtIndex(nextIndex);
    }
  });
});

document.querySelectorAll('.audio-player').forEach(player => {
  const audio = player.querySelector('audio');
  const progressBar = player.querySelector('.progress-bar');
  const timeDisplay = player.querySelector('.time-display');

  audio.addEventListener('loadedmetadata', () => {
    timeDisplay.textContent = formatTime(0) + ' / ' + formatTime(audio.duration);
  });

  audio.addEventListener('timeupdate', () => {
    if (!audio.duration) return;
    const progressPercent = (audio.currentTime / audio.duration) * 100;
    progressBar.value = progressPercent;
    timeDisplay.textContent = formatTime(audio.currentTime) + ' / ' + formatTime(audio.duration);
  });

  progressBar.addEventListener('click', e => {
    const rect = progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = (clickX / rect.width) * audio.duration;
    audio.currentTime = newTime;
  });
});

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
}

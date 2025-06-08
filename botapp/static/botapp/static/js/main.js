const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('bg-slider').appendChild(renderer.domElement);

// Создадим несколько материалов и геометрий для слайдов
const geometries = [
  new THREE.BoxGeometry(),
  new THREE.SphereGeometry(0.8, 32, 32),
  new THREE.ConeGeometry(0.8, 1.5, 32),
];

const materials = [
  new THREE.MeshNormalMaterial(),
  new THREE.MeshStandardMaterial({ color: 0xff4444 }),
  new THREE.MeshStandardMaterial({ color: 0x44ff44 }),
];

// Освещение для материалов с освещением
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);

let currentSlideIndex = 0;
let cube = new THREE.Mesh(geometries[currentSlideIndex], materials[currentSlideIndex]);
scene.add(cube);

camera.position.z = 3;

function changeSlide(index) {
  if (index < 0 || index >= geometries.length) return;
  scene.remove(cube);
  cube.geometry.dispose();
  cube.material.dispose();

  cube = new THREE.Mesh(geometries[index], materials[index]);
  scene.add(cube);
  currentSlideIndex = index;
}

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}

animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Обработчик кликов по песням для смены слайда
document.querySelectorAll('.track-item').forEach(item => {
  item.style.cursor = 'pointer';
  item.addEventListener('click', () => {
    const index = parseInt(item.getAttribute('data-slide-index'));
    changeSlide(index);
  });
});

// Остановка всех аудио при запуске любого другого
const audios = document.querySelectorAll('.songs-list audio');

audios.forEach(audio => {
  audio.addEventListener('play', () => {
    audios.forEach(otherAudio => {
      if (otherAudio !== audio) {
        otherAudio.pause();
      }
    });
  });
});

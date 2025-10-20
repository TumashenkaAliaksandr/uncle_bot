// AUTHOR: код рисует фон со звёздами, несколькими "галактиками" (радиальными градиентами и потоками частиц)
// и поверх рисует SVG линии — случайные соединения (созвездия).

const canvas = document.getElementById('stage');
const ctx = canvas.getContext('2d', {alpha: true});
const svg = document.getElementById('svgLayer');
let DPR = Math.max(1, window.devicePixelRatio || 1);

// настройки по умолчанию
const settings = {
    stars: 600,
    galaxies: 4,
    starColor: '#ffffff',
    bgColor: '#02020a'
};

// адаптация размеров
function resize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    DPR = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.floor(w * DPR);
    canvas.height = Math.floor(h * DPR);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
}

window.addEventListener('resize', resize);
resize();

// утилиты
function rand(min, max) {
    return Math.random() * (max - min) + min
}

function pick(arr) {
    return arr[Math.floor(Math.random() * arr.length)]
}

// создаём массив звёзд (частиц)
let stars = [];

function genStars(count) {
    stars = [];
    for (let i = 0; i < count; i++) {
        const r = Math.pow(Math.random(), 2) * 2.5 + 0.3; // распределение радиуса
        stars.push({
            x: Math.random() * canvas.width / DPR,
            y: Math.random() * canvas.height / DPR,
            r: r,
            vel: (0.02 + Math.random() * 0.12) * (Math.random() < 0.5 ? -1 : 1),
            alpha: rand(0.2, 1),
            twinkleSpeed: rand(0.002, 0.02)
        });
    }
}

// генерируем галактики — как объекты с центром, радиусом, цветовой палитрой и вращением
let galaxies = [];

function genGalaxies(count) {
    galaxies = [];
    const palettes = [
        ['#ffb3c6', '#ffd9e8', '#ff96b6'],
        ['#b3d9ff', '#d9f0ff', '#9fdcff'],
        ['#ffd9b3', '#fff0d9', '#ffd19f'],
        ['#d6b3ff', '#f0d9ff', '#cfa6ff'],
        ['#b3ffd9', '#d9fff0', '#9fffd6']
    ];
    for (let i = 0; i < count; i++) {
        const cx = rand(0.15, 0.85) * canvas.width / DPR;
        const cy = rand(0.15, 0.85) * canvas.height / DPR;
        const rr = rand(Math.min(canvas.width, canvas.height) * 0.08, Math.min(canvas.width, canvas.height) * 0.28);
        galaxies.push({
            x: cx,
            y: cy,
            r: rr,
            angle: rand(0, Math.PI * 2),
            spin: rand(-0.002, 0.002),
            palette: pick(palettes)
        });
    }
}

// рисуем фон (тонкий градиент):
function drawBackground() {
    ctx.save();
    const g = ctx.createLinearGradient(0, 0, 0, canvas.height / DPR);
    g.addColorStop(0, settings.bgColor);
    g.addColorStop(1, '#030319');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, canvas.width / DPR, canvas.height / DPR);
    ctx.restore();
}

// рисуем звёзды
function drawStars(dt) {
    for (let s of stars) {
        // twinkle
        s.alpha += Math.sin(dt * s.twinkleSpeed + (s.x + s.y)) * 0.01;
        s.alpha = Math.max(0.05, Math.min(1, s.alpha));
        ctx.beginPath();
        const grd = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 6);
        grd.addColorStop(0, `rgba(255,255,255,${s.alpha})`);
        grd.addColorStop(0.6, `rgba(200,220,255,${s.alpha * 0.6})`);
        grd.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = grd;
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
    }
}

// рисуем галактики как радиальные завихрения частиц + мягкий ореол
function drawGalaxies(t) {
    for (let g of galaxies) {
        ctx.save();
        // маленький ореол
        const halo = ctx.createRadialGradient(g.x, g.y, 0, g.x, g.y, g.r * 1.2);
        halo.addColorStop(0, 'rgba(255,255,255,0.14)');
        halo.addColorStop(0.25, 'rgba(200,220,255,0.06)');
        halo.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = halo;
        ctx.beginPath();
        ctx.arc(g.x, g.y, g.r * 1.1, 0, Math.PI * 2);
        ctx.fill();

        // рисуем несколько спиральных рукавов — как точки, смещённых по синусу
        const arms = 3 + Math.floor(Math.abs(Math.sin(g.angle)) * 3);
        for (let a = 0; a < arms; a++) {
            const hue = pick(g.palette);
            for (let i = 0; i < 200; i++) {
                const frac = i / 200;
                const radius = frac * g.r;
                const armAngle = g.angle + a * (Math.PI * 2 / arms) + frac * 6; // скручиваем спираль
                const x = g.x + Math.cos(armAngle) * radius + rand(-1.5, 1.5) * frac * 8;
                const y = g.y + Math.sin(armAngle) * radius + rand(-1.5, 1.5) * frac * 8;
                const size = Math.max(0.2, (1 - frac) * 2.2 * (Math.random() < 0.07 ? 2 : 1));
                const alpha = 0.02 + (1 - frac) * 0.35;
                ctx.fillStyle = `rgba(${hexToRgb(hue)},${alpha})`;
                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // вращаем угол
        g.angle += g.spin + 0.0001 * Math.sin(t / 4000);
        ctx.restore();
    }
}

// вспомогательная: хэш цвета в rgb
function hexToRgb(hex) {
    const c = hex.replace('#', '');
    const num = parseInt(c, 16);
    const r = (num >> 16) & 255;
    const g = (num >> 8) & 255;
    const b = num & 255;
    return r + ',' + g + ',' + b;
}

// рисуем мельчайшие светящиеся точки (вспышки)
let flashParticles = [];

function addFlash(x, y) {
    for (let i = 0; i < 40; i++) {
        flashParticles.push({x, y, vx: rand(-2, 2), vy: rand(-2, 2), life: rand(400, 1200), t: 0, r: rand(0.4, 2)});
    }
}

function drawFlashes(dt) {
    for (let i = flashParticles.length - 1; i >= 0; i--) {
        const p = flashParticles[i];
        p.t += dt;
        if (p.t > p.life) {
            flashParticles.splice(i, 1);
            continue
        }
        const k = 1 - p.t / p.life;
        ctx.beginPath();
        ctx.fillStyle = `rgba(255,245,200,${0.6 * k})`;
        ctx.arc(p.x + p.vx * (p.t / 200), p.y + p.vy * (p.t / 200), p.r * k * 2, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Рисуем SVG-констелляции: выбираем несколько ярких точек и соединяем линиями
function drawConstellations() {
    // очистим
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const w = canvas.width / DPR;
    const h = canvas.height / DPR;
    const starsForConst = [];
    // возьмём несколько случайных звёзд для узоров
    for (let i = 0; i < Math.min(25, Math.floor(stars.length / 20)); i++) {
        starsForConst.push(pick(stars));
    }
    // создаём 3-6 созвездий
    const count = Math.max(3, Math.min(8, Math.floor(galaxies.length * 1.5)));
    for (let s = 0; s < count; s++) {
        const k = Math.floor(rand(3, 8));
        const pts = [];
        // выберем k точек в зоне (разброс небольших)
        const cx = rand(0.15, 0.85) * w;
        const cy = rand(0.15, 0.85) * h;
        for (let i = 0; i < k; i++) {
            pts.push({x: cx + rand(-w * 0.12, w * 0.12), y: cy + rand(-h * 0.12, h * 0.12)});
        }
        // линия
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = pts.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');
        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', 'rgba(170,200,255,0.25)');
        path.setAttribute('stroke-width', '1.2');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        svg.appendChild(path);
        // самочки-звёзды
        for (let p of pts) {
            const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            c.setAttribute('cx', p.x);
            c.setAttribute('cy', p.y);
            c.setAttribute('r', rand(1.2, 2.8));
            c.setAttribute('fill', 'rgba(255,255,255,0.9)');
            svg.appendChild(c);
        }
    }
}

// главный цикл рисования
let last = performance.now();

function frame(t) {
    const dt = t - last;
    last = t;
    // рисовать
    drawBackground();
    drawGalaxies(t);
    drawStars(t);
    drawFlashes(dt);

    // лёгкий foreground blur/overlay — тонкая плёнка
    // (не обязательно, оставим простой)

    requestAnimationFrame(frame);
}

// интеграция UI
const starsRange = document.getElementById('starsRange');
const galaxiesRange = document.getElementById('galaxiesRange');
starsRange.addEventListener('input', () => {
    genStars(parseInt(starsRange.value));
    drawConstellations();
});
galaxiesRange.addEventListener('input', () => {
    genGalaxies(parseInt(galaxiesRange.value));
    drawConstellations();
});

// взаимодействие: на тач/клик добавить вспышку
window.addEventListener('pointerdown', e => {
    addFlash(e.clientX, e.clientY);
});

// init
genStars(settings.stars);
genGalaxies(settings.galaxies);
drawConstellations();
requestAnimationFrame(frame);

// доступность: перегенерировать при изменении размеров
window.addEventListener('orientationchange', () => {
    resize();
    genStars(parseInt(starsRange.value));
    genGalaxies(parseInt(galaxiesRange.value));
    drawConstellations();
});

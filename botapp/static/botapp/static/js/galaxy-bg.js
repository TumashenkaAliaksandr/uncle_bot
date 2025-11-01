(function(){
    const canvasBg = document.getElementById('stage');
    const ctxBg = canvasBg.getContext('2d', { alpha: true });
    let DPR = Math.max(1, window.devicePixelRatio || 1);

    const settings = {
        stars: 300, // уменьшено число звезд для оптимальной производительности
        starColor: '#ffffff',
        bgColor: '#02020a'
    };

    function resize() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        DPR = Math.max(1, window.devicePixelRatio || 1);
        canvasBg.width = Math.floor(w * DPR);
        canvasBg.height = Math.floor(h * DPR);
        canvasBg.style.width = w + 'px';
        canvasBg.style.height = h + 'px';
        ctxBg.setTransform(DPR, 0, 0, DPR, 0, 0);
    }
    window.addEventListener('resize', resize);
    resize();

    function rand(min, max) {
        return Math.random() * (max - min) + min;
    }

    let stars = [];
    function genStars(count) {
        stars = [];
        for (let i = 0; i < count; i++) {
            const r = Math.pow(Math.random(), 2) * 1.5 + 0.2;
            stars.push({
                x: Math.random() * canvasBg.width / DPR,
                y: Math.random() * canvasBg.height / DPR,
                r: r,
                alpha: rand(0.3, 1),
                twinkleSpeed: rand(0.004, 0.015)
            });
        }
    }

    function drawBackground() {
        const g = ctxBg.createLinearGradient(0, 0, 0, canvasBg.height / DPR);
        g.addColorStop(0, settings.bgColor);
        g.addColorStop(1, '#030319');
        ctxBg.fillStyle = g;
        ctxBg.fillRect(0, 0, canvasBg.width / DPR, canvasBg.height / DPR);
    }

    function drawStars(dt) {
        ctxBg.clearRect(0, 0, canvasBg.width, canvasBg.height);
        drawBackground();

        // Оптимизация отрисовки: объединяем рисование путем batch
        ctxBg.beginPath();
        for (let s of stars) {
            s.alpha += Math.sin(dt * s.twinkleSpeed + (s.x + s.y)) * 0.005;
            s.alpha = Math.max(0.1, Math.min(1, s.alpha));
            // Используем простые круги без градиентов для производительности
            ctxBg.moveTo(s.x + s.r, s.y);
            ctxBg.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        }
        ctxBg.fillStyle = '#ffffff';
        ctxBg.fill();

        // Для мерцания рисуем поверх с градиентом выборочно для небольшого числа звезд
        for (let i = 0; i < Math.min(30, stars.length); i++) {
            let s = stars[i];
            const grd = ctxBg.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r * 5);
            grd.addColorStop(0, `rgba(255,255,255,${s.alpha})`);
            grd.addColorStop(0.6, `rgba(200,220,255,${s.alpha * 0.5})`);
            grd.addColorStop(1, 'rgba(255,255,255,0)');
            ctxBg.fillStyle = grd;
            ctxBg.beginPath();
            ctxBg.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctxBg.fill();
        }
    }

    let flashParticles = [];
    function addFlash(x, y) {
        for (let i = 0; i < 10; i++) {
            flashParticles.push({
                x, y,
                vx: rand(-0.5, 0.5),
                vy: rand(-0.5, 0.5),
                life: rand(300, 600),
                t: 0,
                r: rand(0.3, 0.8)
            });
        }
    }

    function drawFlashes(dt) {
        for (let i = flashParticles.length - 1; i >= 0; i--) {
            const p = flashParticles[i];
            p.t += dt;
            if (p.t > p.life) {
                flashParticles.splice(i, 1);
                continue;
            }
            const k = 1 - p.t / p.life;
            ctxBg.beginPath();
            ctxBg.fillStyle = `rgba(255,245,200,${0.6 * k})`;
            ctxBg.arc(p.x + p.vx * (p.t / 150), p.y + p.vy * (p.t / 150), p.r * k * 2, 0, 2 * Math.PI);
            ctxBg.fill();
        }
    }

    let last = performance.now();
    function frame(t) {
        const dt = t - last;
        last = t;
        drawStars(dt);
        drawFlashes(dt);
        requestAnimationFrame(frame);
    }

    let starGenTimeout = null;
    const starsRange = document.getElementById('starsRange');
    starsRange.addEventListener('input', () => {
        if (starGenTimeout) clearTimeout(starGenTimeout);
        starGenTimeout = setTimeout(() => {
            genStars(parseInt(starsRange.value));
        }, 150);
    });

    window.addEventListener('pointerdown', e => {
        addFlash(e.clientX, e.clientY);
    });

    genStars(settings.stars);
    requestAnimationFrame(frame);

    window.addEventListener('orientationchange', () => {
        resize();
        genStars(parseInt(starsRange.value));
    });
})();

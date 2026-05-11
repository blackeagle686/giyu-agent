/**
 * Giyu Landing Page Logic - World Class Edition
 * GSAP Animations, Custom Cursor, Magnetic Buttons, & Particles
 */



// --- 2. Magnetic Buttons ---
const magneticButtons = document.querySelectorAll('.primary-btn, .secondary-btn, .cta-btn');

magneticButtons.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        gsap.to(btn, {
            x: x * 0.3,
            y: y * 0.3,
            duration: 0.4,
            ease: "power2.out"
        });
    });

    btn.addEventListener('mouseleave', () => {
        gsap.to(btn, {
            x: 0,
            y: 0,
            duration: 0.7,
            ease: "elastic.out(1, 0.3)"
        });
    });
});


// --- 3. Particle Network Background ---
const canvas = document.getElementById('net-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
let connectionDistance = 160;
const mouse = { x: null, y: null, radius: 180 };

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    connectionDistance = canvas.width < 768 ? 100 : 160;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
});

class Particle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.color = Math.random() > 0.5 ? '#00f2ff' : '#7000ff';
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width) this.x = 0;
        else if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        else if (this.y < 0) this.y = canvas.height;

        if (mouse.x !== null) {
            const dx = mouse.x - this.x;
            const dy = mouse.y - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < mouse.radius) {
                const force = (mouse.radius - dist) / mouse.radius;
                this.x -= (dx / dist) * force * 3;
                this.y -= (dy / dist) * force * 3;
            }
        }
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
    }
}

function initParticles() {
    const count = Math.min((canvas.width * canvas.height) / 15000, 80);
    particles = [];
    for (let i = 0; i < count; i++) {
        particles.push(new Particle());
    }
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();

        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < connectionDistance) {
                const opacity = (1 - (dist / connectionDistance)) * 0.2;
                const grad = ctx.createLinearGradient(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
                grad.addColorStop(0, particles[i].color);
                grad.addColorStop(1, particles[j].color);
                
                ctx.strokeStyle = grad;
                ctx.globalAlpha = opacity;
                ctx.lineWidth = 0.8;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
                ctx.globalAlpha = 1;
            }
        }
    }
    requestAnimationFrame(animateParticles);
}

// --- 4. Preloader & GSAP Initialization ---
window.addEventListener('load', () => {
    // Ensure GSAP plugins are registered
    gsap.registerPlugin(ScrollTrigger);

    // Initialize SplitType for hero text
    const heroTitle = new SplitType('.split-text', { types: 'words, chars' });

    // Preloader Animation Sequence
    const tlLoader = gsap.timeline();

    tlLoader.to('.loader-bar', {
        width: '100%',
        duration: 1.5,
        ease: 'power3.inOut'
    })
    .to('.preloader', {
        yPercent: -100,
        duration: 0.8,
        ease: 'power4.inOut',
        delay: 0.2
    })
    .add(() => {
        // Start particle animation when preloader finishes
        initParticles();
        animateParticles();
    }, "-=0.4")
    // Hero Animations
    .from(heroTitle.words, {
        y: 100,
        opacity: 0,
        duration: 1,
        stagger: 0.05,
        ease: 'back.out(1.7)'
    }, "-=0.2")
    .from('.fade-in-up', {
        y: 30,
        opacity: 0,
        duration: 1,
        stagger: 0.1,
        ease: 'power3.out'
    }, "-=0.6");

    // --- 5. Scroll Animations ---

    // Feature Cards Stagger
    gsap.from('.feature-card', {
        scrollTrigger: {
            trigger: '.features',
            start: 'top 75%'
        },
        y: 50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power3.out'
    });


    // Architecture Section Pin & Reveal
    const archTl = gsap.timeline({
        scrollTrigger: {
            trigger: '.architecture',
            start: 'top 60%',
            end: 'bottom center',
            scrub: 1
        }
    });

    archTl.from('.arch-text', { x: -50, opacity: 0, duration: 1 })
          .from('.arch-visual', { x: 50, opacity: 0, duration: 1 }, "-=1")
          .from('.status-ring', { scale: 0.5, opacity: 0, rotation: 180, duration: 1.5, ease: 'back.out(1.5)' }, "-=0.5")
          .from('.progress-bar .fill', { width: 0, duration: 1, stagger: 0.2 }, "-=1");
});

// Smooth anchor scrolling handled natively by CSS scroll-behavior: smooth

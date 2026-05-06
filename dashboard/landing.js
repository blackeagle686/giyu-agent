/**
 * Giyu Landing Page Logic - World Class Edition
 * GSAP Animations, Custom Cursor, Magnetic Buttons, & Particles
 */

// --- 1. Custom Cursor ---
const cursorDot = document.querySelector('.cursor-dot');
const cursorOutline = document.querySelector('.cursor-outline');
const interactiveElements = document.querySelectorAll('a, button, .feature-card');

window.addEventListener('mousemove', (e) => {
    const posX = e.clientX;
    const posY = e.clientY;

    // Dot follows exactly
    cursorDot.style.left = `${posX}px`;
    cursorDot.style.top = `${posY}px`;

    // Outline follows with slight delay
    cursorOutline.animate({
        left: `${posX}px`,
        top: `${posY}px`
    }, { duration: 500, fill: "forwards" });
});

interactiveElements.forEach(el => {
    el.addEventListener('mouseenter', () => cursorOutline.classList.add('hovering'));
    el.addEventListener('mouseleave', () => cursorOutline.classList.remove('hovering'));
});

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
const particleCount = 25; // Heavily optimized count
const connectionDistance = 140;
const connectionDistanceSq = connectionDistance * connectionDistance; // Precalculated for performance
const mouse = { x: null, y: null, radius: 150 };

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Track mouse for canvas, with throttle
let throttleTimer;
window.addEventListener('mousemove', (event) => {
    if (throttleTimer) return;
    throttleTimer = setTimeout(() => {
        mouse.x = event.x;
        mouse.y = event.y;
        throttleTimer = null;
    }, 16); // ~60fps
});

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 1.5 + 0.5;
        // Slower, more fluid movement
        this.speedX = (Math.random() - 0.5) * 0.3;
        this.speedY = (Math.random() - 0.5) * 0.3;
        this.baseX = this.x;
        this.baseY = this.y;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Wrap around
        if (this.x > canvas.width) this.x = 0;
        else if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        else if (this.y < 0) this.y = canvas.height;

        // Fluid Mouse interaction
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distSq = dx * dx + dy * dy;
        const radiusSq = mouse.radius * mouse.radius;
        
        if (distSq < radiusSq) {
            const distance = Math.sqrt(distSq);
            const force = (mouse.radius - distance) / mouse.radius;
            // Push away softly
            this.x -= dx * force * 0.03;
            this.y -= dy * force * 0.03;
        }
    }

    draw() {
        ctx.fillStyle = 'rgba(20, 184, 166, 0.4)'; // Teal glow
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
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
            const distSq = dx * dx + dy * dy;

            if (distSq < connectionDistanceSq) {
                const distance = Math.sqrt(distSq); // Only calculate sqrt if within range
                const opacity = 1 - (distance / connectionDistance);
                ctx.strokeStyle = `rgba(59, 130, 246, ${opacity * 0.15})`; // Blue links
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
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

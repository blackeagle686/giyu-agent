/**
 * Giyu Optimized 3D Water Simulation — Full-Page Edition
 * Powered by Three.js & Custom GLSL Shaders
 */

(function() {
    const container = document.getElementById('water-canvas-container');
    if (!container) return;

    // --- 1. Scene Setup ---
    const scene = new THREE.Scene();
    
    // Low FOV for cinematic depth
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 3000);
    camera.position.set(0, 300, 800);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ 
        antialias: false, // Performance boost
        alpha: true,
        powerPreference: "high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Cap pixel ratio for performance
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);

    // --- 2. Wave Geometry ---
    // Expanded plane to cover full scroll range
    const geometry = new THREE.PlaneGeometry(3000, 3000, 100, 100);
    geometry.rotateX(-Math.PI / 2);

    // --- 3. Advanced Water Material ---
    const material = new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uScroll: { value: 0 },
            uColorCyan: { value: new THREE.Color("#ff0022ff") },
            uColorPurple: { value: new THREE.Color("#7000ff") },
            uColorDeep: { value: new THREE.Color("#020408") }
        },
        vertexShader: `
            uniform float uTime;
            uniform float uScroll;
            varying float vElevation;
            varying vec2 vUv;

            void main() {
                vUv = uv;
                vec4 modelPosition = modelMatrix * vec4(position, 1.0);

                // Apply scroll-based depth movement
                float scrollOffset = uScroll * 800.0;
                
                // Dynamic multi-layered wave logic
                float elevation = sin(modelPosition.x * 0.008 + uTime * 1.2 + scrollOffset * 0.005) * 40.0;
                elevation += sin(modelPosition.z * 0.01 + uTime * 1.0) * 30.0;
                elevation += cos((modelPosition.x + modelPosition.z) * 0.004 + uTime * 0.7) * 45.0;
                
                // Micro-ripples
                elevation += sin(modelPosition.x * 0.05 - uTime * 2.5) * 4.0;

                modelPosition.y += elevation;
                // Shift plane back as we scroll to keep water visible
                modelPosition.z -= scrollOffset;

                vElevation = elevation;

                vec4 viewPosition = viewMatrix * modelPosition;
                gl_Position = projectionMatrix * viewPosition;
            }
        `,
        fragmentShader: `
            uniform vec3 uColorCyan;
            uniform vec3 uColorPurple;
            uniform vec3 uColorDeep;
            varying float vElevation;
            varying vec2 vUv;

            void main() {
                // Base depth coloring
                float depthFactor = (vElevation + 60.0) / 120.0;
                
                // Cinematic Gradient: Deep -> Purple -> Cyan
                vec3 color = mix(uColorDeep, uColorPurple, depthFactor * 0.6);
                color = mix(color, uColorCyan, pow(depthFactor, 2.5));

                // Add "Glow" on wave peaks
                float peakHighlight = smoothstep(30.0, 60.0, vElevation);
                color += peakHighlight * 0.15;

                // Edge Softening & Distance Fog
                float distanceFade = smoothstep(1.0, 0.4, vUv.y);
                float alpha = 0.8 * distanceFade;
                
                gl_FragColor = vec4(color, alpha);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // --- 4. Interactivity & Optimization ---
    
    // Scroll listener
    let targetScroll = 0;
    window.addEventListener('scroll', () => {
        targetScroll = window.scrollY;
    }, { passive: true });

    // Resize handler
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // --- 5. Animation Loop ---
    const clock = new THREE.Clock();
    let currentScroll = 0;

    function animate() {
        const elapsedTime = clock.getElapsedTime();
        
        // Smoothly interpolate scroll for "Reliable" feel
        currentScroll += (targetScroll - currentScroll) * 0.08;
        material.uniforms.uScroll.value = currentScroll / window.innerHeight;
        
        material.uniforms.uTime.value = elapsedTime;

        // Subtle camera breathing
        camera.position.y = 300 + Math.sin(elapsedTime * 0.4) * 15;
        camera.lookAt(0, 0, 0);

        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    }

    animate();
})();

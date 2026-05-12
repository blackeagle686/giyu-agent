/**
 * Giyu 3D Water Simulation
 * Powered by Three.js & Custom Vertex Shaders
 */

(function() {
    const container = document.getElementById('water-canvas-container');
    if (!container) return;

    const scene = new THREE.Scene();
    
    // Camera Setup - Low angle for "huge wave" effect
    const camera = new THREE.PerspectiveCamera(55, container.offsetWidth / container.offsetHeight, 1, 2000);
    camera.position.set(0, 150, 450);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    container.appendChild(renderer.domElement);

    // Geometry - Large Plane with high segment count for smooth waves
    const geometry = new THREE.PlaneGeometry(2000, 1500, 128, 128);
    geometry.rotateX(-Math.PI / 2);

    // Material - Custom Shader for the "Giyu" Water Effect
    const material = new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uColorCyan: { value: new THREE.Color("#00f2ff") },
            uColorPurple: { value: new THREE.Color("#7000ff") },
            uColorDeep: { value: new THREE.Color("#05070a") }
        },
        vertexShader: `
            uniform float uTime;
            varying float vElevation;
            varying vec2 vUv;

            void main() {
                vUv = uv;
                vec4 modelPosition = modelMatrix * vec4(position, 1.0);

                // Multiple wave layers for complexity
                float elevation = sin(modelPosition.x * 0.01 + uTime * 2.0) * 25.0;
                elevation += sin(modelPosition.z * 0.015 + uTime * 1.5) * 20.0;
                elevation += sin((modelPosition.x + modelPosition.z) * 0.005 + uTime * 0.8) * 35.0;
                
                // Add smaller ripples
                elevation += sin(modelPosition.x * 0.1 - uTime * 3.0) * 2.0;

                modelPosition.y += elevation;
                vElevation = elevation;

                vec4 viewPosition = viewMatrix * modelPosition;
                vec4 projectedPosition = projectionMatrix * viewPosition;

                gl_Position = projectedPosition;
            }
        `,
        fragmentShader: `
            uniform vec3 uColorCyan;
            uniform vec3 uColorPurple;
            uniform vec3 uColorDeep;
            varying float vElevation;
            varying vec2 vUv;

            void main() {
                // Mix colors based on wave height (elevation)
                float mixStrength = (vElevation + 50.0) / 100.0;
                vec3 color = mix(uColorDeep, uColorCyan, mixStrength);
                
                // Add a touch of purple in the middle heights
                float purpleStrength = sin(mixStrength * 3.14) * 0.3;
                color = mix(color, uColorPurple, purpleStrength);

                // Add "foam" highlights on peaks
                if(vElevation > 45.0) {
                    color += 0.2;
                }

                // Transparency fade at edges
                float alpha = smoothstep(0.0, 0.2, vUv.y) * (1.0 - smoothstep(0.8, 1.0, vUv.y));
                
                gl_FragColor = vec4(color, 0.85 * alpha);
            }
        `,
        transparent: true,
        side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Resize Handler
    window.addEventListener('resize', () => {
        camera.aspect = container.offsetWidth / container.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.offsetWidth, container.offsetHeight);
    });

    // Animation Loop
    const clock = new THREE.Clock();

    function animate() {
        const elapsedTime = clock.getElapsedTime();
        material.uniforms.uTime.value = elapsedTime;

        // Subtle camera movement
        camera.position.y = 150 + Math.sin(elapsedTime * 0.5) * 10;
        camera.lookAt(0, 0, 0);

        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    }

    animate();
})();

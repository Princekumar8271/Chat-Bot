// 3D Brain Animation using Three.js

// Initialize the scene once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create a scene
    const scene = new THREE.Scene();
    
    // Create a camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;
    
    // Create a renderer with optimized settings
    const renderer = new THREE.WebGLRenderer({ 
        alpha: true, 
        antialias: false, // Disable antialiasing for better performance
        powerPreference: 'high-performance',
        precision: 'mediump' // Use medium precision for better performance
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x050510, 1); // Darker background with slight blue tint for better contrast
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5)); // Limit pixel ratio for better performance
    
    // Add the renderer to the DOM
    const container = document.getElementById('brain-bg');
    container.appendChild(renderer.domElement);
    
    // Create a more detailed brain model using IcosahedronGeometry
    const geometry = new THREE.IcosahedronGeometry(2, 3); // Higher detail level for brain-like structure
    
    // Add random vertex displacement for more organic look
    const positionAttribute = geometry.attributes.position;
    for (let i = 0; i < positionAttribute.count; i++) {
        const x = positionAttribute.getX(i);
        const y = positionAttribute.getY(i);
        const z = positionAttribute.getZ(i);
        
        // Apply noise-based displacement
        const noise = Math.sin(x * 2) * Math.cos(y * 2) * Math.sin(z * 2) * 0.15;
        positionAttribute.setXYZ(
            i,
            x + (x * noise),
            y + (y * noise),
            z + (z * noise)
        );
    }
    
    // Compute vertex normals for proper lighting
    geometry.computeVertexNormals();
    
    // Create neural connections
    const particlesGeometry = new THREE.BufferGeometry();
    const particleCount = 1000; // Increased particle count for denser visualization
    
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    
    const color = new THREE.Color();
    
    // Create neural connections between particles
    const connections = [];
    const connectionCount = 50; // Increased number of neural connections
    
    for (let i = 0; i < particleCount; i++) {
        // Random positions in a sphere with emphasis on sides
        const radius = 2.5 * Math.random() + 1.5; // Between 1.5 and 4.0
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        
        // Add more particles to the sides by adjusting x position
        let x = radius * Math.sin(phi) * Math.cos(theta);
        if (Math.abs(x) < 1.0) { // For particles near the center
            x *= 0.5; // Reduce central density
        } else {
            x *= 1.2; // Increase side density
        }
        
        positions[i * 3] = x;
        positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = radius * Math.cos(phi);
        
        // Brighter purple to blue gradient colors
        color.setHSL(0.75 + Math.random() * 0.1, 1.0, 0.7 + Math.random() * 0.3);
        
        colors[i * 3] = color.r;
        colors[i * 3 + 1] = color.g;
        colors[i * 3 + 2] = color.b;
        
        // Varied particle sizes for more dynamic appearance
        sizes[i] = Math.random() * 0.15 + 0.05;
    }
    
    // Create connections with preference for side-to-side links
    for (let i = 0; i < connectionCount; i++) {
        const index1 = Math.floor(Math.random() * particleCount);
        const index2 = Math.floor(Math.random() * particleCount);
        
        // Encourage connections between particles on opposite sides
        if (Math.random() < 0.4) { // 40% chance for cross-hemisphere connections
            const x1 = positions[index1 * 3];
            let index2Special = Math.floor(Math.random() * particleCount);
            while (Math.sign(positions[index2Special * 3]) === Math.sign(x1)) {
                index2Special = Math.floor(Math.random() * particleCount);
            }
            connections.push({
                start: index1,
                end: index2Special,
                life: Math.random() * 0.5 + 0.5,
                speed: Math.random() * 0.02 + 0.01
            });
        } else {
            connections.push({
                start: index1,
                end: index2,
                life: Math.random() * 0.5 + 0.5,
                speed: Math.random() * 0.02 + 0.01
            });
        }
    }
    
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    particlesGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
    
    // Enhanced shader material for particles
    const particlesMaterial = new THREE.ShaderMaterial({
        uniforms: {
            time: { value: 0 }
        },
        vertexShader: `
            attribute float size;
            attribute vec3 color;
            varying vec3 vColor;
            uniform float time;
            void main() {
                vColor = color;
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = size * (300.0 / -mvPosition.z) * (1.0 + 0.3 * sin(time + position.x + position.y));
                gl_Position = projectionMatrix * mvPosition;
            }
        `,
        fragmentShader: `
            varying vec3 vColor;
            void main() {
                float dist = length(gl_PointCoord - vec2(0.5, 0.5));
                if (dist > 0.5) discard;
                gl_FragColor = vec4(vColor, 1.0 - dist * 2.0);
            }
        `,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });
    
    const particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);
    
    // Enhanced lines for neural connections
    const linesMaterial = new THREE.LineBasicMaterial({
        color: 0xcc66ff,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending
    });
    
    const linesGroup = new THREE.Group();
    scene.add(linesGroup);
    
    connections.forEach(connection => {
        const startIndex = connection.start;
        const endIndex = connection.end;
        
        const startX = positions[startIndex * 3];
        const startY = positions[startIndex * 3 + 1];
        const startZ = positions[startIndex * 3 + 2];
        
        const endX = positions[endIndex * 3];
        const endY = positions[endIndex * 3 + 1];
        const endZ = positions[endIndex * 3 + 2];
        
        const lineGeometry = new THREE.BufferGeometry();
        const linePositions = new Float32Array([startX, startY, startZ, endX, endY, endZ]);
        lineGeometry.setAttribute('position', new THREE.BufferAttribute(linePositions, 3));
        
        const lineMaterial = linesMaterial.clone();
        
        const line = new THREE.Line(lineGeometry, lineMaterial);
        linesGroup.add(line);
    });
    
    // Enhanced brain material with more realistic properties
    const brainMaterial = new THREE.MeshPhongMaterial({
        color: 0xcc00ff,
        emissive: 0x770099,
        specular: 0xffffff,
        shininess: 80,
        transparent: true,
        opacity: 0.85,
        flatShading: true, // Emphasize the geometric structure
        wireframe: false,
        roughness: 0.7, // Add some surface roughness
        metalness: 0.2 // Slight metallic effect for better light interaction
    });
    
    const brain = new THREE.Mesh(geometry, brainMaterial);
    scene.add(brain);
    
    // Enhanced lighting
    const ambientLight = new THREE.AmbientLight(0x333333);
    scene.add(ambientLight);
    
    const light1 = new THREE.PointLight(0xff00ff, 2.0, 100);
    light1.position.set(5, 5, 5);
    scene.add(light1);
    
    const light2 = new THREE.PointLight(0x8800ff, 2.0, 100);
    light2.position.set(-5, -5, 5);
    scene.add(light2);
    
    const glowLight = new THREE.PointLight(0xaa00ff, 1.5, 10);
    glowLight.position.set(0, 0, 0);
    scene.add(glowLight);
    
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    
    let lastFrameTime = 0;
    const frameThrottle = 1000/30;
    let animationActive = true;
    
    document.addEventListener('visibilitychange', () => {
        animationActive = !document.hidden;
    });
    
    function animate(currentTime) {
        requestAnimationFrame(animate);
        
        if (!animationActive) return;
        
        const deltaTime = currentTime - lastFrameTime;
        if (deltaTime < frameThrottle) return;
        
        lastFrameTime = currentTime;
        
        brain.rotation.y += 0.002;
        brain.rotation.z += 0.001;
        
        particles.rotation.y += 0.001;
        
        particlesMaterial.uniforms.time.value = currentTime * 0.001;
        
        connections.forEach((connection, index) => {
            const line = linesGroup.children[index];
            line.material.opacity = 0.2 + Math.sin(currentTime * connection.speed) * 0.3 * connection.life;
        });
        
        glowLight.intensity = 1.5 + Math.sin(currentTime * 0.001) * 0.5;
        
        renderer.render(scene, camera);
    }
    
    animate(0);
});
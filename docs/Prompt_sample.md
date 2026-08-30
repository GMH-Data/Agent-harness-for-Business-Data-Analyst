# Recreate this site as a single HTML file: Laocoön — Bronze and Time
You are an expert creative front-end developer. Produce a **single self-contained `index.html`**
that reproduces the project below **exactly** — same layout, sections, visuals, motion, and
interaction. Pure HTML/CSS/JS in one file: no build step, no framework, no bundler. Use ES modules
with a CDN importmap for Three.js (r0.160 from unpkg, with the matching `GLTFLoader` addon).
Hardcode every value given here as a fixed constant. Rebuild each component described below as a
section of the one file.
## What it is
A cinematic, scroll-driven landing page titled **"Bronze and Time"** centered on a glowing,
semi-polished **bronze horse** sculpture rendered in WebGL on a deep-black stage. The camera flies
a full 360° orbit around the statue as you scroll through a very tall page (900vh); molten **forge
sparks** rise around it; a slow **liquid-bronze wave shader** breathes in the background, shifting
its palette from molten bronze at the top to deep sapphire blue at the bottom. Over the canvas sits
an editorial overlay: a fixed header (brand + nav + Contact button), four text "slides" that fade in
at scroll milestones with per-letter blur-up animation, a five-line vertical grid with drifting
dots, a stories-style scroll progress bar, and a custom double-ring cursor. Fonts are *Italiana*
(display headings) and *Outfit* (body). The whole thing is dark, slow, and luxurious.
## Page shell & libraries
- `<!DOCTYPE html>`, `lang="en"`, `<title>The Statue of Laocoön</title>`, UTF-8, responsive viewport.
- Load fonts in CSS:
`@import url('https://fonts.googleapis.com/css2?family=Italiana&family=Outfit:wght@300;400;600&family=Playfair+Display:ital,wght@1,500&display=swap');`
- Importmap + module script for Three.js:
```html
<script type="importmap">
{
"imports": {
"three": "https://unpkg.com/three@0.160.0/build/three.module.js",
"three/examples/jsm/loaders/GLTFLoader.js": "https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js"
}
}
</script>
<script type="module"> /* all JS below */ </script>
```
- The page scroll model: `<body>` has `min-height: 900vh` so the page is very tall; the canvas and
all overlay UI are `position: fixed`. Scroll position drives everything (camera orbit, shader,
sparks turbulence, slide reveals, grid dots, progress bar). No smooth-scroll library — smoothing is
done in JS via lerp (see animation loop). All scrollbars are fully hidden (WebKit, Firefox, IE).
- The native cursor is hidden everywhere (`cursor: none` on body and `cursor: none !important` on
`*`), replaced by a custom two-element cursor.
## Global CSS (reset + base)
```css
* { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
html, body {
width: 100%;
margin: 0;
padding: 0;
background-color: #000000;
-ms-overflow-style: none;
scrollbar-width: none;
}
body {
min-height: 900vh;
font-family: 'Outfit', sans-serif;
color: #ffffff;
overflow-x: hidden;
cursor: none;
}
* { cursor: none !important; }
::-webkit-scrollbar { display: none; width: 0; }
#webgl {
position: fixed;
top: 0; left: 0;
width: 100%; height: 100%;
z-index: 1;
outline: none;
}
```
## Layout & sections (in order)
The body markup, in order: two cursor divs, the `.cinematic-container` (header + slides), an image
mask, the grid-lines overlay, and the `<canvas id="webgl">`. Build them all.
### Custom cursor (two divs, top of `<body>`)
```html
<div class="cursor-inner"></div>
<div class="cursor-outer"></div>
```
```css
.cursor-inner {
position: fixed; top: 0; left: 0;
width: 6px; height: 6px;
border: 2px solid rgba(255, 255, 255, 1);
border-radius: 50%;
transform: translate(-50%, -50%);
pointer-events: none;
z-index: 9999;
}
.cursor-outer {
position: fixed; top: 0; left: 0;
width: 40px; height: 40px;
border: 1.5px solid rgba(255, 255, 255, 0.7);
border-radius: 50%;
transform: translate(-50%, -50%);
pointer-events: none;
z-index: 9998;
transition: width 0.3s, height 0.3s, background 0.3s;
}
```
The inner ring snaps to the pointer instantly; the outer ring lerps toward it (see JS).
### `.cinematic-container` (the overlay layer)
```css
.cinematic-container {
position: fixed;
top: 0; left: 0;
width: 100%; height: 100%;
z-index: 10;
pointer-events: none; /* clicks pass through to canvas */
display: flex;
flex-direction: column;
justify-content: space-between;
padding: 0 60px 40px 60px;
box-sizing: border-box;
}
```
### Header `.main-header`
```html
<div class="main-header">
<div class="brand">Laocoön</div>
<nav class="header-nav">
<a href="#slide-1" class="nav-link">Bronze</a>
<span class="nav-dot"></span>
<a href="#slide-2" class="nav-link">Marble</a>
<span class="nav-dot"></span>
<a href="#slide-3" class="nav-link">Fluid</a>
<span class="nav-dot"></span>
<a href="#slide-4" class="nav-link">Digital</a>
</nav>
<div class="header-actions">
<a href="#" class="contact-btn">Contact <span class="btn-circle"></span></a>
</div>
</div>
```
```css
.main-header {
display: flex; justify-content: space-between; align-items: center;
width: 100%; z-index: 20;
pointer-events: auto;
padding: 20px 0;
}
.brand { font-size: 14px; font-weight: 600; letter-spacing: 5px; text-transform: uppercase; }
.header-nav { display: flex; align-items: center; gap: 24px; }
.nav-link {
color: #ffffff; text-decoration: none;
font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
font-weight: 500; transition: color 0.3s;
}
.nav-link:hover { color: #ffffff; }
.nav-dot { width: 3px; height: 3px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; }
.contact-btn {
display: inline-flex; align-items: center; gap: 8px;
padding: 10px 24px;
background: #ffffff; color: #000000;
text-decoration: none;
font-size: 10px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;
border-radius: 20px;
transition: transform 0.3s, background 0.3s;
}
.btn-circle {
display: inline-block; width: 6px; height: 6px;
border: 1px solid #000000; border-radius: 50%; background: transparent;
}
.contact-btn:hover { transform: scale(1.05); background: #f0f0f0; }
```
### The four slides + the image mask
```html
<div class="slide" id="slide-1">
<h2 class="slide-title">Bronze <br>and Time</h2>
<div class="desc-row">
<p class="slide-desc col-1">A timeless material holding centuries of human history. Fluid in hot flames, eternal in its form. Each curve captures a tense, dramatic moment.</p>
<p class="slide-desc col-2">Born of molten fire and creative will, it stands to bridge our ancient memory and modern vision. A fluid energy frozen in still, heavy bronze.</p>
</div>
</div>
<div class="slide-image-mask" id="slide-2-img">
<img src="ASSET_BASE_URL/1.png" alt="Editorial Concept">
</div>
<div class="slide" id="slide-2">
<h2 class="slide-title">Marble <br>Emotion</h2>
<p class="slide-desc">A sculpture frozen at the peak of human suffering and heroic struggle. Laocoön and his sons, bound by ruthless fate.</p>
</div>
<div class="slide" id="slide-3">
<h2 class="slide-title">Liquid Metal</h2>
<p class="slide-desc">Art that breathes. Mesmerizing waves of liquid bronze flow through space, reflecting every contour and tensed muscle of the ancient masterpiece.</p>
</div>
<div class="slide" id="slide-4">
<h2 class="slide-title">Eternal <br>Moment</h2>
<p class="slide-desc">Contemplating antique form through the lens of new dimensions. A classic masterpiece reborn in the currents of radiant digital matter.</p>
</div>
```
(Use the exact verbatim copy above. The `1.png` image uses the bucket URL — see Assets.)
```css
.slide { position: absolute; bottom: 12%; pointer-events: none; }
#slide-1 { left: 0; width: 100%; }
#slide-1 .slide-title { margin-left: 60px; }
#slide-1 .desc-row { position: relative; display: flex; width: 100%; }
#slide-1 .col-1 {
margin-left: 60px;
width: calc(25vw - 60px);
max-width: calc(25vw - 60px);
}
#slide-1 .col-2 {
position: absolute;
left: calc(25vw + 40px);
width: calc(25vw - 60px);
max-width: calc(25vw - 60px);
}
#slide-2 { left: 0; width: 100%; }
#slide-2-img {
position: fixed;
top: 90px;
left: 60px;
width: calc(25vw - 60px);
aspect-ratio: 1 / 1;
overflow: hidden;
z-index: 2;
pointer-events: none;
clip-path: inset(0 0 100% 0);
transition: clip-path 1.8s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.8s ease;
opacity: 0;
}
#slide-2-img img {
width: 100%; height: 100%;
object-fit: cover;
transform: scale(1.15);
transition: transform 1.8s cubic-bezier(0.16, 1, 0.3, 1);
}
#slide-2-img.active { clip-path: inset(0 0 0 0); opacity: 1; }
#slide-2-img.active img { transform: scale(1); }
#slide-2 .slide-title { margin-left: calc(25vw + 40px); }
#slide-2 .slide-desc {
margin-left: calc(50vw + 20px);
width: calc(25vw - 60px);
max-width: calc(25vw - 60px);
}
#slide-3 {
left: calc(50vw + 20px);
width: calc(25vw - 60px);
max-width: calc(25vw - 60px);
}
#slide-3 .slide-title { white-space: nowrap; }
#slide-4 { left: calc(25% + 40px); max-width: 600px; }
.slide-title {
font-family: 'Italiana', serif;
font-size: 116px;
line-height: 1.0;
font-weight: 400;
letter-spacing: 2px;
margin-bottom: 20px;
color: #fff6ed;
}
.slide-desc {
font-size: 16px; line-height: 1.7; font-weight: 300;
color: #d1d5db; letter-spacing: 0.5px;
opacity: 0;
transform: translateY(30px);
transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1),
transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
transition-delay: 0.4s;
}
.slide.active .slide-desc { opacity: 1; transform: translateY(0); }
.slide-title .char {
display: inline-block;
opacity: 0;
transform: translateY(50px);
filter: blur(12px);
transition: opacity 0.8s cubic-bezier(0.25, 1, 0.5, 1),
transform 0.8s cubic-bezier(0.25, 1, 0.5, 1),
filter 0.8s cubic-bezier(0.25, 1, 0.5, 1);
}
.slide.active .slide-title .char { opacity: 1; transform: translateY(0); filter: blur(0); }
.slide.active { pointer-events: auto; }
```
### Grid overlay (horizontal divider + 5 vertical lines with dots + stories progress)
```html
<div class="grid-horizontal-line"></div>
<div class="grid-lines">
<div class="grid-line"><div class="grid-dot top"></div><div class="grid-dot bottom"></div></div>
<div class="grid-line"><div class="grid-dot top"></div><div class="grid-dot bottom"></div></div>
<div class="grid-line"><div class="grid-dot top"></div><div class="grid-dot bottom"></div></div>
<div class="grid-line"><div class="grid-dot top"></div><div class="grid-dot bottom"></div></div>
<div class="grid-line story-progress-container">
<div class="grid-dot top"></div>
<div class="grid-dot bottom"></div>
<div class="story-dashes">
<div class="story-dash"><div class="story-dash-fill" id="dash-fill-1"></div></div>
<div class="story-dash"><div class="story-dash-fill" id="dash-fill-2"></div></div>
<div class="story-dash"><div class="story-dash-fill" id="dash-fill-3"></div></div>
<div class="story-dash"><div class="story-dash-fill" id="dash-fill-4"></div></div>
</div>
</div>
</div>
```
```css
.story-dashes {
position: absolute; top: 50%; left: 50%;
transform: translate(-50%, -50%);
display: flex; flex-direction: column; gap: 12px;
}
.story-dash { width: 2px; height: 40px; background: rgba(255, 255, 255, 0.15); border-radius: 2px; }
.story-dash-fill { width: 100%; height: 0%; background: #ffffff; border-radius: 2px; }
.grid-horizontal-line {
position: fixed; top: 70px; left: 0; right: 0;
width: 100%; height: 1px;
background: rgba(255, 255, 255, 0.12);
z-index: 5; pointer-events: none;
}
.grid-lines {
position: fixed; top: 0; left: 40px; right: 40px;
width: calc(100% - 80px); height: 100vh;
display: flex; justify-content: space-between;
z-index: 5; pointer-events: none;
}
.grid-line {
position: relative; width: 1px; height: 100%;
background: rgba(255, 255, 255, 0.12);
}
.grid-line:nth-child(3) { margin-top: 70px; height: calc(100vh - 70px); }
.grid-dot {
position: absolute; left: 50%;
transform: translate(-50%, -50%);
width: 6px; height: 6px; border-radius: 50%;
background: rgba(255, 255, 255, 0.35);
box-shadow: 0 0 4px rgba(255, 255, 255, 0.15);
}
```
### Canvas (last element)
```html
<canvas id="webgl"></canvas>
```
## The WebGL scene
All of the following runs inside the module script. Globals to declare at top:
```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
const canvas = document.querySelector('#webgl');
let scene, camera, renderer;
let gltfModel; // the statue
let modelPivot; // pivot group for perfect center-rotation
let mixer;
const clock = new THREE.Clock();
let currentScroll = 0; // smoothed accumulated scroll for lerping
let mouseX = 0, mouseY = 0, targetMouseX = 0, targetMouseY = 0;
let cursorX = window.innerWidth / 2, cursorY = window.innerHeight / 2;
let outerCursorX = window.innerWidth / 2, outerCursorY = window.innerHeight / 2;
let bgMaterial;
const shaderUniforms = {
uTime: { value: 0 },
uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
uMouse: { value: new THREE.Vector2(0, 0) },
uScroll: { value: 0 }
};
let sparkParticles;
const sparkCount = 450;
const sparkData = [];
const sizes = { width: window.innerWidth, height: window.innerHeight };
```
### Renderer, scene, camera (verbatim setup)
```js
scene = new THREE.Scene();
scene.background = new THREE.Color('#000000');
scene.fog = new THREE.FogExp2('#000000', 0.01);
camera = new THREE.PerspectiveCamera(50, sizes.width / sizes.height, 0.1, 100);
camera.position.set(0, 0.2, 3.0);
scene.add(camera);
createBackgroundShader(); // adds the wave plane as a child of the camera
renderer = new THREE.WebGLRenderer({
canvas: canvas,
antialias: true,
alpha: false,
powerPreference: "high-performance"
});
renderer.setSize(sizes.width, sizes.height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 2.2;
```
### Dramatic lighting (chiaroscuro) — verbatim
```js
const ambientLight = new THREE.AmbientLight('#ffffff', 0.1);
scene.add(ambientLight);
// Key light: super-bright white from upper-right, casts shadows
const keyLight = new THREE.SpotLight('#ffffff', 18.0);
keyLight.position.set(4, 6, 3);
keyLight.angle = Math.PI / 4;
keyLight.penumbra = 0.9;
keyLight.castShadow = true;
keyLight.shadow.mapSize.width = 2048;
keyLight.shadow.mapSize.height = 2048;
keyLight.shadow.camera.near = 1.0;
keyLight.shadow.camera.far = 15;
keyLight.shadow.bias = -0.001;
scene.add(keyLight);
// Rim light: cool blue from behind-left, defines the silhouette
const rimLight = new THREE.DirectionalLight('#e3f2ff', 10.0);
rimLight.position.set(-5, 3, -4);
scene.add(rimLight);
// Fill light: very faint warm cream from below-front
const fillLight = new THREE.DirectionalLight('#fff3e6', 0.8);
fillLight.position.set(-2, -4, 2);
scene.add(fillLight);
```
### Forge sparks (450 additive point particles) — verbatim
Procedural radial-gradient texture (white core → transparent edge):
```js
function createSparkTexture() {
const canvas = document.createElement('canvas');
canvas.width = 16; canvas.height = 16;
const ctx = canvas.getContext('2d');
const gradient = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
gradient.addColorStop(0.25, 'rgba(255, 255, 255, 0.85)');
gradient.addColorStop(0.6, 'rgba(255, 255, 255, 0.3)');
gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 16, 16);
return new THREE.CanvasTexture(canvas);
}
```
Build the particle cloud — random positions in a box around the model, colors split 60% molten
orange / 40% icy blue, and per-particle physics stored in `sparkData`:
```js
function createSparks() {
const geometry = new THREE.BufferGeometry();
const positions = new Float32Array(sparkCount * 3);
const colors = new Float32Array(sparkCount * 3);
for (let i = 0; i < sparkCount; i++) {
const x = (Math.random() - 0.5) * 6.5;
const y = (Math.random() - 0.5) * 5.0 - 0.5;
const z = (Math.random() - 0.5) * 6.5;
positions[i * 3] = x;
positions[i * 3 + 1] = y;
positions[i * 3 + 2] = z;
if (Math.random() < 0.6) {
// saturated fiery orange
colors[i * 3] = 1.0;
colors[i * 3 + 1] = 0.4 + Math.random() * 0.15;
colors[i * 3 + 2] = 0.05 + Math.random() * 0.1;
} else {
// cosmic icy light-blue (matches rim light)
colors[i * 3] = 0.55 + Math.random() * 0.15;
colors[i * 3 + 1] = 0.82 + Math.random() * 0.12;
colors[i * 3 + 2] = 1.0;
}
sparkData.push({
speedX: (Math.random() - 0.5) * 0.4,
speedY: 0.15 + Math.random() * 0.3,
speedZ: (Math.random() - 0.5) * 0.4,
swaySpeed: 0.5 + Math.random() * 1.5,
swayRadius: 0.05 + Math.random() * 0.15,
phase: Math.random() * Math.PI * 2
});
}
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
const material = new THREE.PointsMaterial({
size: 0.025,
vertexColors: true,
transparent: true,
opacity: 0.85,
blending: THREE.AdditiveBlending,
depthWrite: false,
map: createSparkTexture()
});
sparkParticles = new THREE.Points(geometry, material);
scene.add(sparkParticles);
}
```
### Model load + centering/scaling logic — verbatim
Load the GLB from the bucket (see Assets). Wrap it in a pivot group, set the bronze material
(roughness **0.42**, metalness **0.92**, smooth shading), then auto-scale so the largest dimension
is 3.5 units, recompute the scaled bounding box, recenter the model inside the pivot, and drop the
pivot to `y = -0.4`:
```js
function loadModel() {
const loader = new GLTFLoader();
loader.load(
ASSET_BASE_URL + '/bronze_horse.glb',
(gltf) => {
gltfModel = gltf.scene;
modelPivot = new THREE.Group();
scene.add(modelPivot);
modelPivot.add(gltfModel);
gltfModel.traverse((child) => {
if (child.isMesh) {
child.castShadow = true;
child.receiveShadow = true;
if (child.material) {
child.material.roughness = 0.42; // semi-matte, noble highlights
child.material.metalness = 0.92; // high satin-bronze metallic sheen
child.material.flatShading = false;
if (child.material.map) {
child.material.map.anisotropy = 16;
}
}
}
});
if (gltf.animations && gltf.animations.length > 0) {
mixer = new THREE.AnimationMixer(gltfModel);
gltf.animations.forEach((clip) => { mixer.clipAction(clip).play(); });
}
// 1. scale so max dimension = 3.5
const boxInitial = new THREE.Box3().setFromObject(gltfModel);
const sizeInitial = boxInitial.getSize(new THREE.Vector3());
const maxDim = Math.max(sizeInitial.x, sizeInitial.y, sizeInitial.z);
const targetScale = 3.5 / (maxDim > 0.0001 ? maxDim : 1);
gltfModel.scale.setScalar(targetScale);
// 2. update world matrix so the box accounts for scale
gltfModel.updateMatrixWorld(true);
// 3. exact geometric center of the scaled model
const boxScaled = new THREE.Box3().setFromObject(gltfModel);
const centerScaled = boxScaled.getCenter(new THREE.Vector3());
// 4. recenter model so its center sits at the pivot origin
gltfModel.position.sub(centerScaled);
// 5. lower the pivot for a grounded stance
modelPivot.position.y = -0.4;
},
undefined,
(error) => { console.error('Error loading bronze horse model:', error); }
);
}
```
### Background liquid-bronze wave shader (full-screen plane, child of camera) — VERBATIM
```js
function createBackgroundShader() {
const vertexShader = `
varying vec2 vUv;
void main() {
vUv = uv;
gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;
const fragmentShader = `
varying vec2 vUv;
uniform float uTime;
uniform vec2 uResolution;
uniform vec2 uMouse;
uniform float uScroll;
// 3D Noise function for organic warping (high performance hash-based noise)
float hash(float n) { return fract(sin(n) * 43758.5453123); }
float noise(in vec3 x) {
vec3 p = floor(x);
vec3 f = fract(x);
f = f*f*(3.0-2.0*f);
float n = p.x + p.y*57.0 + 113.0*p.z;
return mix(mix(mix(hash(n+ 0.0), hash(n+ 1.0), f.x),
mix(hash(n+ 57.0), hash(n+ 58.0), f.x), f.y),
mix(mix(hash(n+113.0), hash(n+114.0), f.x),
mix(hash(n+170.0), hash(n+171.0), f.x), f.y), f.z);
}
void main() {
// Normalize UV coordinates
vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution.xy) / uResolution.y;
float aspect = uResolution.x / uResolution.y;
float time = uTime * 0.08; // Extremely slow, calm breathing speed
float scroll = uScroll;
// --- 1. Constant Wave Parameters (Perfect Scroll Stability) ---
// Keep frequencies and angles constant to prevent compressing/speeding waves on scroll
float angle1 = 0.6;
float angle2 = -0.7;
float angle3 = 1.2;
float freq1 = 2.4; // Higher frequency = significantly more lines on screen
float freq2 = 3.2;
float freq3 = 4.0;
// --- 2. Coordinates Distortion (Smooth Rounded Arcs & Scroll Deformation) ---
vec2 warpedUv = uv;
// Scroll directly drives the deformation of the wave shapes!
// As you scroll, the phase of the distortion shifts, smoothly bending the rounded lines.
float scrollDeform = scroll * 5.0; // 5 radians of smooth sweeping deformation
// Large scale, perfectly smooth sine-wave distortions for clean, even, rounded arcs
warpedUv.x += sin(uv.y * 2.5 + time * 0.2 + scrollDeform) * 0.35;
warpedUv.y += cos(uv.x * 2.5 - time * 0.15 - scrollDeform * 0.8) * 0.35;
// Secondary clean curve to create elegant, topographical intersections
warpedUv.x += sin(uv.y * 1.2 - time * 0.1 - scrollDeform * 1.5) * 0.25;
warpedUv.y += cos(uv.x * 1.2 + time * 0.18 + scrollDeform * 1.2) * 0.25;
// Soft global sliding shift based on scroll parallax and mouse movement
// Keep drift multipliers tiny so scroll motion remains extremely gentle
vec2 scrollDrift = vec2(scroll * 0.04, -scroll * 0.02);
vec2 mouseShift = vec2(uMouse.x * aspect * 0.05, uMouse.y * 0.05);
warpedUv += scrollDrift + mouseShift;
// --- 3. Layered Wave Computations ---
// Wave directions
vec2 dir1 = vec2(cos(angle1), sin(angle1));
vec2 dir2 = vec2(cos(angle2), sin(angle2));
vec2 dir3 = vec2(cos(angle3), sin(angle3));
// Layered sine wave calculations with self-warping
float w1 = sin(dot(warpedUv, dir1) * freq1 + time * 1.0);
float w2 = cos(dot(warpedUv, dir2) * freq2 - time * 1.4 + w1 * 0.4);
float w3 = sin(dot(warpedUv, dir3) * freq3 + time * 1.8 + w2 * 0.5);
// Combine layers into a seamless wave scalar field in [-1.0, 1.0]
float waveField = w1 * 0.50 + w2 * 0.35 + w3 * 0.15;
// --- 4. Crisp Metallic Lustre ---
// Wide satin sheen (gives defined body to the folds without haze)
float wideSheen = pow(max(0.0, 1.0 - abs(waveField - 0.1)), 2.5);
// Crisp, thicker specular reflection (defined metallic shine, ensuring thickness with more lines)
float crispSpecular = pow(max(0.0, 1.0 - abs(waveField - 0.15)), 8.0);
// Highlight blend: crisp, defined glowing folds
float crest = wideSheen * 0.5 + crispSpecular * 0.9;
// --- 5. Scroll-Driven Color Palettes: Pure Bronze to Pure Blue ---
// Top Palette (Scroll = 0.0): Rich Molten Bronze
vec3 c0_shadow = vec3(0.0010, 0.0006, 0.0004); // Deepest bronze shadow
vec3 c0_wave1 = vec3(0.085, 0.040, 0.015); // Rich copper-bronze
vec3 c0_wave2 = vec3(0.050, 0.022, 0.008); // Deep bronze body
vec3 c0_crest = vec3(0.45, 0.30, 0.18); // Polished bronze/gold sheen
// Bottom Palette (Scroll = 1.0): Deep Sapphire Blue
vec3 c1_shadow = vec3(0.0004, 0.0006, 0.0012); // Deepest sapphire shadow
vec3 c1_wave1 = vec3(0.015, 0.035, 0.065); // Rich cobalt/teal blue
vec3 c1_wave2 = vec3(0.008, 0.020, 0.045); // Deep sapphire body
vec3 c1_crest = vec3(0.18, 0.35, 0.55); // Polished blue-steel sheen
// Interpolate colors smoothly based on scroll progress
float t = smoothstep(0.0, 1.0, scroll);
vec3 colShadow = mix(c0_shadow, c1_shadow, t);
vec3 colWave1 = mix(c0_wave1, c1_wave1, t);
vec3 colWave2 = mix(c0_wave2, c1_wave2, t);
vec3 colCrest = mix(c0_crest, c1_crest, t);
// --- 6. Final Composition ---
// Blend wave details and wave bodies with deep shadow background
vec3 color = colShadow;
color = mix(color, colWave2, smoothstep(-0.6, 0.2, waveField));
color = mix(color, colWave1, smoothstep(0.0, 0.8, waveField));
// Add the soft satinated crest highlights with rich metallic multiplier
color += colCrest * crest * 1.4;
// Apply a gentle vignette to match cinematic design
float vignette = 1.0 - dot(uv, uv) * 0.12;
color *= vignette;
gl_FragColor = vec4(color, 1.0);
}
`;
bgMaterial = new THREE.ShaderMaterial({
vertexShader: vertexShader,
fragmentShader: fragmentShader,
uniforms: shaderUniforms,
depthWrite: false,
depthTest: false
});
const bgGeometry = new THREE.PlaneGeometry(30, 30);
const bgMesh = new THREE.Mesh(bgGeometry, bgMaterial);
bgMesh.position.set(0.0, 0.0, -8.0); // local camera space, far behind
bgMesh.renderOrder = -10;
camera.add(bgMesh); // attach to camera so it always fills view
}
```
### Resize handler — verbatim
```js
function onWindowResize() {
sizes.width = window.innerWidth;
sizes.height = window.innerHeight;
camera.aspect = sizes.width / sizes.height;
camera.updateProjectionMatrix();
renderer.setSize(sizes.width, sizes.height);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
if (shaderUniforms) shaderUniforms.uResolution.value.set(sizes.width, sizes.height);
}
```
## Interaction & animation loop
### Pointer handling
On `mousemove`: snap the inner cursor to `event.clientX/Y` (set its `left`/`top`); store normalized
mouse target `targetMouseX = clientX/innerWidth*2-1`, `targetMouseY = clientY/innerHeight*2-1`.
```js
window.addEventListener('mousemove', (event) => {
cursorX = event.clientX;
cursorY = event.clientY;
const cursorInner = document.querySelector('.cursor-inner');
if (cursorInner) { cursorInner.style.left = `${cursorX}px`; cursorInner.style.top = `${cursorY}px`; }
targetMouseX = (event.clientX / window.innerWidth) * 2 - 1;
targetMouseY = (event.clientY / window.innerHeight) * 2 - 1;
});
window.addEventListener('resize', onWindowResize);
```
### Per-letter title split (call before first frame)
Split each `.slide-title` into per-character `<span class="char">` with a staggered
`transition-delay` of `index * 0.035s`, preserving `<br>` tags and spaces:
```js
function splitTitlesIntoChars() {
const titles = document.querySelectorAll('.slide-title');
titles.forEach(title => {
const text = title.innerHTML;
let newHTML = '';
let delayCounter = 0;
const parts = text.split(/(<br\s*\/?>)/i);
parts.forEach(part => {
if (part.toLowerCase().startsWith('<br')) {
newHTML += part;
} else {
for (let i = 0; i < part.length; i++) {
if (part[i] === ' ') {
newHTML += ' ';
} else {
newHTML += `<span class="char" style="transition-delay: ${delayCounter * 0.035}s">${part[i]}</span>`;
delayCounter++;
}
}
}
});
title.innerHTML = newHTML;
});
}
```
### The `animate()` loop (verbatim logic)
```js
function animate() {
requestAnimationFrame(animate);
const deltaTime = clock.getDelta();
if (mixer) mixer.update(deltaTime);
// 1. target scroll [0..1], cross-browser
const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
const scrollTop = window.scrollY !== undefined ? window.scrollY
: (window.pageYOffset !== undefined ? window.pageYOffset : document.documentElement.scrollTop);
const targetScroll = maxScroll > 0 ? scrollTop / maxScroll : 0;
// smooth physical lerp (inertia)
currentScroll += (targetScroll - currentScroll) * 0.025;
// smooth model rotation lerp
mouseX += (targetMouseX - mouseX) * 0.05;
mouseY += (targetMouseY - mouseY) * 0.05;
// outer cursor ring lerps toward inner
outerCursorX += (cursorX - outerCursorX) * 0.2;
outerCursorY += (cursorY - outerCursorY) * 0.2;
const cursorOuter = document.querySelector('.cursor-outer');
if (cursorOuter) { cursorOuter.style.left = `${outerCursorX}px`; cursorOuter.style.top = `${outerCursorY}px`; }
// gentle interactive model tilt from mouse
if (modelPivot) {
modelPivot.rotation.y = mouseX * 0.25;
modelPivot.rotation.x = mouseY * 0.15;
}
// 2. sparks physics, accelerated/turbulent on fast scroll
if (sparkParticles) {
const positions = sparkParticles.geometry.attributes.position.array;
const time = clock.getElapsedTime();
const scrollVelocity = Math.abs(targetScroll - currentScroll);
const speedMultiplier = 1.0 + scrollVelocity * 9.0;
const turbulence = scrollVelocity * 0.8;
for (let i = 0; i < sparkCount; i++) {
const idx = i * 3;
const data = sparkData[i];
positions[idx] += data.speedX * deltaTime * speedMultiplier;
positions[idx + 1] += data.speedY * deltaTime * speedMultiplier;
positions[idx + 2] += data.speedZ * deltaTime * speedMultiplier;
const currentSway = data.swayRadius * (1.0 + turbulence * 4.0);
positions[idx] += Math.sin(time * data.swaySpeed + data.phase) * currentSway * deltaTime;
positions[idx + 2] += Math.cos(time * data.swaySpeed + data.phase) * currentSway * deltaTime;
// recycle when out of bounds
if (positions[idx + 1] > 3.0 || Math.abs(positions[idx]) > 3.5 || Math.abs(positions[idx + 2]) > 3.5) {
positions[idx + 1] = -2.5;
positions[idx] = (Math.random() - 0.5) * 3.0;
positions[idx + 2] = (Math.random() - 0.5) * 3.0;
}
}
sparkParticles.geometry.attributes.position.needsUpdate = true;
}
// 3. camera orbits the model 360° driven by scroll
const phi = currentScroll * Math.PI * 2.0;
const y = 0.35 + Math.sin(currentScroll * Math.PI) * 0.8;
const radius = 4.2 - Math.sin(currentScroll * Math.PI) * 0.6;
const x = radius * Math.sin(phi);
const z = radius * Math.cos(phi);
// shift the framing left on the first screen to clear room for the text columns
let transitionProgress = Math.min(1.0, currentScroll / 0.28);
let easeFactor = (Math.cos(transitionProgress * Math.PI) + 1.0) * 0.5; // 1.0 → 0.0
const lookAtXOffset = -0.9 * easeFactor;
const targetLookAt = new THREE.Vector3(lookAtXOffset, -0.15, 0);
const targetPos = new THREE.Vector3(x, y, z);
camera.position.lerp(targetPos, 0.025);
camera.lookAt(targetLookAt);
// background shader uniforms
if (shaderUniforms) {
shaderUniforms.uTime.value = clock.getElapsedTime();
shaderUniforms.uMouse.value.set(mouseX, -mouseY);
shaderUniforms.uScroll.value = currentScroll;
}
updateSlides(currentScroll);
updateGridDots(currentScroll);
renderer.render(scene, camera);
}
```
### Grid dots drift — verbatim
```js
function updateGridDots(scroll) {
const dots = document.querySelectorAll('.grid-dot');
dots.forEach((dot, i) => {
const startY = (i * 17) % 80 + 10;
let speed = 90 + (i * 55) % 180;
if (i % 2 === 0) speed = -speed;
let y = startY + scroll * speed;
y = ((y % 100) + 100) % 100;
dot.style.top = `${y}%`;
});
}
```
### Slides + stories progress — verbatim
```js
function updateSlides(scroll) {
const slide1 = document.getElementById('slide-1');
const slide2 = document.getElementById('slide-2');
const slide3 = document.getElementById('slide-3');
const slide4 = document.getElementById('slide-4');
for (let i = 1; i <= 4; i++) {
const fill = document.getElementById(`dash-fill-${i}`);
if (fill) {
const start = (i - 1) * 0.25;
const end = i * 0.25;
let progress = (scroll - start) / (end - start);
progress = Math.max(0, Math.min(1, progress));
fill.style.height = `${progress * 100}%`;
}
}
function isActive(val, start, end) { return val >= start && val <= end; }
if (slide1) slide1.classList.toggle('active', isActive(scroll, -0.10, 0.12));
if (slide2) {
const active2 = isActive(scroll, 0.28, 0.40);
slide2.classList.toggle('active', active2);
const slide2Img = document.getElementById('slide-2-img');
if (slide2Img) slide2Img.classList.toggle('active', active2);
}
if (slide3) slide3.classList.toggle('active', isActive(scroll, 0.56, 0.68));
if (slide4) slide4.classList.toggle('active', isActive(scroll, 0.84, 1.05));
}
```
### Nav click → smooth scroll-to — verbatim
```js
function setupNavigation() {
const navLinks = document.querySelectorAll('.nav-link');
const targetScrolls = [0.0, 0.34, 0.62, 0.94];
navLinks.forEach((link, index) => {
link.addEventListener('click', (e) => {
e.preventDefault();
const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
const targetY = maxScroll * targetScrolls[index];
window.scrollTo({ top: targetY, behavior: 'smooth' });
});
});
}
```
### Bootstrap
```js
window.addEventListener('DOMContentLoaded', () => {
splitTitlesIntoChars(); // (or call inside init before animate)
// ... build scene: createScene/camera/shader, renderer, lighting, sparks, loadModel ...
onWindowResize(); // optional initial sync
animate();
setupNavigation();
});
```
Order matters: split titles, create scene + camera, `createBackgroundShader()`, renderer + tone
mapping, lighting, sparks, then `loadModel()`, then start `animate()` and wire navigation.
## The loader / reveal
There is no separate loading screen. The reveal is the natural sequence: the black stage + breathing
bronze wave shader render immediately; the bronze horse fades into presence as the GLB resolves
(centered, scaled, lit by the key/rim/fill rig); slide-1 ("Bronze and Time") is active at the top —
its title animates in per-letter from below with a 12px→0 blur and 50px→0 rise (0.035s stagger per
char), and its two description columns float up (translateY 30px→0, 0.4s delay). As you scroll, each
subsequent slide repeats the blur-up reveal at its milestone, the editorial image (slide-2) wipes
open top-to-bottom via `clip-path` with a 1.15→1 parallax zoom, sparks swirl faster, and the shader
palette migrates bronze→sapphire.
## Fixed parameters (bake these in)
- Background: pure black `#000000`; `FogExp2('#000000', 0.01)`.
- Camera: `PerspectiveCamera(50, aspect, 0.1, 100)`, start `(0, 0.2, 3.0)`.
- Renderer: antialias on, pixelRatio `min(dpr, 2)`, `PCFSoftShadowMap`, `ACESFilmicToneMapping`,
exposure `2.2`.
- Lights: ambient `#ffffff @ 0.1`; key SpotLight `#ffffff @ 18.0` at `(4,6,3)`, angle `PI/4`,
penumbra `0.9`, shadow map 2048², near 1.0 far 15, bias -0.001; rim DirectionalLight
`#e3f2ff @ 10.0` at `(-5,3,-4)`; fill DirectionalLight `#fff3e6 @ 0.8` at `(-2,-4,2)`.
- Bronze material: `roughness 0.42`, `metalness 0.92`, `flatShading false`, map anisotropy 16.
- Model: auto-scale max dim → `3.5`; recenter via scaled bounding box; pivot `y = -0.4`.
- Sparks: `sparkCount = 450`, `PointsMaterial` size `0.025`, opacity `0.85`, additive,
`depthWrite:false`, vertexColors; 60% orange / 40% icy-blue; recycle bounds `y>3.0` or
`|x|>3.5`/`|z|>3.5` → respawn at `y=-2.5`, `x,z = ±1.5`.
- Camera orbit: `phi = scroll * 2π`; `y = 0.35 + sin(scroll·π)*0.8`;
`radius = 4.2 - sin(scroll·π)*0.6`; lookAt `(lookAtXOffset, -0.15, 0)`,
`lookAtXOffset = -0.9 * easeFactor`, ease over `scroll/0.28`; `camera.position.lerp(target, 0.025)`.
- Smoothing lerps: scroll `0.025`, mouse `0.05`, outer cursor `0.2`.
- Model tilt from mouse: `rotation.y = mouseX*0.25`, `rotation.x = mouseY*0.15`.
- Slide active ranges: s1 `[-0.10, 0.12]`, s2 `[0.28, 0.40]`, s3 `[0.56, 0.68]`, s4 `[0.84, 1.05]`.
- Nav target scrolls: `[0.0, 0.34, 0.62, 0.94]`.
- Title font 116px Italiana; body 16px Outfit weight 300; title color `#fff6ed`; desc `#d1d5db`.
- Page height `min-height: 900vh`. Layout padding `0 60px 40px 60px`; columns based on `25vw` grid.
- Shader: time scale `0.08`; freqs `2.4 / 3.2 / 4.0`; angles `0.6 / -0.7 / 1.2`; wave weights
`0.50 / 0.35 / 0.15`; `scrollDeform = scroll*5.0`; palette bronze→sapphire (values in shader);
vignette `1.0 - dot(uv,uv)*0.12`; crest multiplier `1.4`; plane `PlaneGeometry(30,30)` at
camera-local `z = -8.0`, `renderOrder -10`, `depthWrite/depthTest false`.
## Assets
Define once near the top of the script:
```js
const ASSET_BASE_URL = "https://api.getlayers.ai/storage/v1/object/public/public/assets/laocoon-59f84455c6";
```
| Asset | Usage | URL |
|-------|-------|-----|
| `bronze_horse.glb` | The bronze statue loaded via `GLTFLoader` (material tweaks + scale 3.5 + recenter) | `https://api.getlayers.ai/storage/v1/object/public/public/assets/laocoon-59f84455c6/bronze_horse.glb` |
| `1.png` | Editorial image inside slide-2 mask (`#slide-2-img img` src) | `https://api.getlayers.ai/storage/v1/object/public/public/assets/laocoon-59f84455c6/1.png` |
Point the `GLTFLoader` at `ASSET_BASE_URL + '/bronze_horse.glb'` and set the `<img>` src to
`ASSET_BASE_URL + '/1.png'` (or hardcode the full URL). The spark texture is generated procedurally
in code (no file). Fonts come from Google Fonts (Italiana, Outfit) via the CSS `@import`.
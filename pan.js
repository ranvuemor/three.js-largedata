import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { VRButton } from 'three/addons/webxr/VRButton.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color( 0xf0f0ff );
const light = new THREE.HemisphereLight( 0xfff0f0, 0x606066 );
light.position.set( 1, 1, 1 );
scene.add( light );

//const player = new THREE.Object3D();
//scene.add(player);
const camera = new THREE.PerspectiveCamera( 50, window.innerWidth / window.innerHeight, 0.1, 500 );
//player.add(camera);

const lines = new THREE.LineDashedMaterial({color: 0x0f0f00});
const points = [];
for (let i = 0; i < 500; i++){
    const x = Math.random();
    const y = Math.random();
    const z = Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = - Math.random();
    const y = - Math.random();
    const z = - Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = -Math.random();
    const y = Math.random();
    const z = Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = -Math.random();
    const y = -Math.random();
    const z = Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = -Math.random();
    const y = Math.random();
    const z = -Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = Math.random();
    const y = -Math.random();
    const z = Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = Math.random();
    const y = -Math.random();
    const z = -Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

for (let i = 0; i < 500; i++){
    const x = Math.random();
    const y = Math.random();
    const z = -Math.random();
    console.log(x, y, z);
    points.push(new THREE.Vector3(x, y, z));
}

const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
const line = new THREE.Line(lineGeometry, lines);
scene.add(line);
line.position.set(0, 0, -20);
console.log("Line: ", line.position.x, line.position.y, line.position.z);

const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setPixelRatio( window.devicePixelRatio );
renderer.setSize( window.innerWidth, window.innerHeight );
renderer.xr.eneabled = true;
renderer.xr.setReferenceSpaceType( 'local' );
document.body.appendChild( renderer.domElement );
document.body.appendChild( VRButton.createButton( renderer ) );

const controls = new OrbitControls( camera, renderer.domElement );
controls.update();

window.addEventListener( 'resize', onWindowResize );

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function render(){
    //player.lookAt((new THREE.Vector3(0, 0, 0)));
    renderer.render(scene, camera);
}

renderer.setAnimationLoop(render);
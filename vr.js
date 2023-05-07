import * as THREE from 'three';
//import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { VRButton } from 'three/addons/webxr/VRButton.js';

let renderer, camera, scene;

init();
animate();

function init(){
    scene = new THREE.Scene();
    scene.add(new THREE.AmbientLight(0xcccccc));
    scene.add(new THREE.DirectionalLight(0xffffff, 0.6));
    scene.background = new THREE.Color(0x0000ff);

    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 2000 );
    camera.layers.enable( 1 ); 
    const texture = new THREE.TextureLoader().load('metallic-holographic-background.jpg'); 

    const geometry1 = new THREE.SphereGeometry( 500, 60, 40 );
				
    geometry1.scale( - 1, 1, 1 );

    const uvs1 = geometry1.attributes.uv.array;

    for ( let i = 0; i < uvs1.length; i += 2 ) {

        uvs1[ i ] *= 0.5;

    }

    const material1 = new THREE.MeshBasicMaterial( { map: texture } );

    const mesh1 = new THREE.Mesh( geometry1, material1 );
    mesh1.rotation.y = - Math.PI / 2;
    mesh1.layers.set( 1 ); // display in left eye only
    scene.add( mesh1 );

    const geometry2 = new THREE.SphereGeometry( 500, 60, 40 );
    geometry2.scale( - 1, 1, 1 );

    const uvs2 = geometry2.attributes.uv.array;

    for ( let i = 0; i < uvs2.length; i += 2 ) {

        uvs2[ i ] *= 0.5;
        uvs2[ i ] += 0.5;

    }

    const material2 = new THREE.MeshBasicMaterial( { map: texture } );

    const mesh2 = new THREE.Mesh( geometry2, material2 );
    mesh2.rotation.y = - Math.PI / 2;
    mesh2.layers.set( 2 ); // display in right eye only
    scene.add( mesh2 );

    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.xr.enabled = true;
    renderer.xr.setReferenceSpaceType( 'local' );

    document.body.appendChild( VRButton.createButton( renderer.domElement ) );

    window.addEventListener( 'resize', onWindowResize );
}



function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

    renderer.setAnimationLoop( render );

}

function render() {

    renderer.render( scene, camera );

}
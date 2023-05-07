import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const canvas = document.getElementsByTagName("canvas")[0];
///const logger = document.getElementById('data');
const loader = new THREE.FileLoader();
const scene = new THREE.Scene();
scene.matrixWorldAutoUpdate = true;
const ambientLight = new THREE.AmbientLight(0xcccccc);
scene.add(ambientLight);
scene.add(new THREE.DirectionalLight(0xffffff, 0.6));
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/ window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({
  canvas: canvas,
  antialias: true,
});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = false;
//controls.target.set(0, 0, 0);

const material = new THREE.PointsMaterial({ vertexColors: true });

loader.load("./output.json", function(jsonData) {
  const geometry = new THREE.BufferGeometry();
  const positions = [];
  const colors = [];
  const sizes = [];
  var data = JSON.parse(jsonData);
  for(let obj of data){
    const R = 6.371
    const lon = obj.lon;
    const lat = obj.lat;
    const elev = obj.elevation;
    const x = R * Math.cos(lat) * Math.cos(lon);
    const y = R * Math.cos(lat) * Math.sin(lon);
    const z = (R * Math.sin(lat)) + (elev/1000);
    const r = obj.red / 255;
    const g = obj.green / 255;
    const b = obj.blue / 255;
    if (r != 0 && g != 0 && b !=0){
        positions.push(x, y, z);
        colors.push(r, g, b);
        sizes.push(1);
    }
    
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.setAttribute( 'size', new THREE.Float32BufferAttribute( sizes, 1 ).setUsage( THREE.DynamicDrawUsage ) );
  const points = new THREE.Points(geometry, material);
  scene.add(points);
  points.position.set(0, -0, -0);

  const boundingBox = new THREE.Box3().setFromPoints(geometry.attributes.position.array);
  //boundingBox.position.set(0, 0, 0);
  //const center = boundingBox.getCenter(new THREE.Vector3());
  const wireframeGeometry = new THREE.Box3Helper(boundingBox, 0xffff00);
  scene.add(wireframeGeometry);
  wireframeGeometry.position.set(170, -10, -75);
  //camera.lookAt(center);
  camera.position.z = 4;
  
//   const box = new THREE.BoxGeometry(1, 1, 1);
//   const boxmat = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
//   const cube = new THREE.Mesh(box, boxmat);
//   scene.add(cube);

  window.addEventListener('resize', onWindowResize, false)
  function onWindowResize() {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
      renderer.render(scene, camera);
  }

  document.addEventListener("keydown", onDocumentKeyDown, false);
  function onDocumentKeyDown(event){
      var keycode = event.which;
      if (keycode == 82){
          controls.reset();
          camera.position.z = 4;
          camera.updateProjectionMatrix()
          renderer.render(scene,camera);
      }
      else if (keycode == 37){
        controls.target.x -= 1;
        camera.position.x -= 1;
        camera.updateProjectionMatrix()
      }
      else if (keycode == 38){
        controls.target.y += 1;
        camera.position.y += 1;
        camera.updateProjectionMatrix()
      }
      else if (keycode == 39){
        controls.target.x += 1;
        camera.position.x += 1;
        camera.updateProjectionMatrix()
      }
      else if (keycode == 40){
        controls.target.y -= 1;
        camera.position.y -= 1;
        camera.updateProjectionMatrix()
      }
      else if (keycode == 73){
        controls.target.z -= 1;
        camera.position.z -= 1;
        camera.updateProjectionMatrix()
      }
      else if (keycode == 79){
        controls.target.z += 1;
        camera.position.z += 1;
        camera.updateProjectionMatrix()
      }
  }

  function render() {
    renderer.render(scene, camera);
  }

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    render();
  }

  animate();
})

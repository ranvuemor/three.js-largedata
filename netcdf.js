var sceneFirstPass, sceneSecondPass, materialSecondPass, rtTexture;
container = document.getElementById( 'container' );
var camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 0.01, 3000.0 );
camera.position.z = 2.0;
const controls = new THREE.OrbitControls(camera, container);
controls.enableDamping = false;
controls.target.set(0, 0, 0);
controls.enablePan = true;
controls.keys = {
	LEFT: 'ArrowLeft', //left arrow
	UP: 'ArrowUp', // up arrow
	RIGHT: 'ArrowRight', // right arrow
	BOTTOM: 'ArrowDown' // down arrow
}
        var screenSize = new THREE.Vector2( window.innerWidth, window.innerHeight );
				//Use NearestFilter to eliminate interpolation.  At the cube edges, interpolated world coordinates
				//will produce bogus ray directions in the fragment shader, and thus extraneous colors.
				rtTexture = new THREE.WebGLRenderTarget( screenSize.x, screenSize.y,
														{ 	minFilter: THREE.NearestFilter,
															magFilter: THREE.NearestFilter,
															wrapS:  THREE.ClampToEdgeWrapping,
															wrapT:  THREE.ClampToEdgeWrapping,
															format: THREE.RGBFormat,
															type: THREE.FloatType,
															generateMipmaps: false} );


				var materialFirstPass = new THREE.ShaderMaterial( {
					vertexShader: document.getElementById( 'vertexShaderFirstPass' ).textContent,
					fragmentShader: document.getElementById( 'fragmentShaderFirstPass' ).textContent,
					side: THREE.BackSide
				} );

				materialSecondPass = new THREE.ShaderMaterial( {
					vertexShader: document.getElementById( 'vertexShaderSecondPass' ).textContent,
					fragmentShader: document.getElementById( 'fragmentShaderSecondPass' ).textContent,
					side: THREE.FrontSide,
					uniforms: {	tex:  { type: "t", value: rtTexture }}
				 });

				sceneFirstPass = new THREE.Scene();
				sceneSecondPass = new THREE.Scene();

				var boxGeometry = new THREE.BoxGeometry(1.0, 1.0, 1.0);
				boxGeometry.doubleSided = true;

				var meshFirstPass = new THREE.Mesh( boxGeometry, materialFirstPass );
				var meshSecondPass = new THREE.Mesh( boxGeometry, materialSecondPass );

				sceneFirstPass.add( meshFirstPass );
				sceneSecondPass.add( meshSecondPass );

				renderer = new THREE.WebGLRenderer();
				container.appendChild( renderer.domElement );
const loader = new THREE.FileLoader();
var jsonData;
var geometry = new THREE.BufferGeometry();
const positions = [];
const colors = [];
const sizes = [];
//const p = [];
const boundingBox = new THREE.Box3();
logger.innerText = "Welcome";
loader.load('./output.json', function(data){
  //var arr = Object.keys(data);
  //logger.innerText =+ arr.length.toString();
  //window.alert("lenght: " + arr.length.toString());
  jsonData = JSON.parse(data);
  var count1 = 0, count2 = 0;
  for(var obj of jsonData){
    if (obj.red != 0 && obj.green != 0 && obj.blue != 0){
      var point = obj;
      count1++;
      var vertex = new THREE.Vector3(point.lon / 2, point.elevation /2, point.lat /2);
      //p.push(vertex);
      positions.push(vertex.x, vertex.y, vertex.z);
      const color = new THREE.Color(point.red / 255, point.green / 255, point.blue / 255);
      colors.push(color.r, color.g, color.b);
      sizes.push(20);
    } 
    else{
      count2++;
    }
  }
})

//var scene = new THREE.Scene();
//scene.matrixWorldAutoUpdate = true;
//const ambientLight = new THREE.AmbientLight(0xcccccc);
//scene.add(ambientLight);
//scene.add(new THREE.DirectionalLight(0xffffff, 0.6));

// var renderer = new THREE.WebGLRenderer({
//   canvas: canvas,
//   antialias: true,
// });
// renderer.setSize(window.innerWidth, window.innerHeight);
// renderer.setClearColor(0xffffff);
// document.body.appendChild(renderer.domElement);

geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

const lines = new THREE.LineDashedMaterial({color: 0x0000ff});
const lineGeometry = new THREE.BufferGeometry().setFromPoints(geometry.attributes.position.array);
const line = new THREE.Line(lineGeometry, lines);
scene.add(line);
line.position.set(0, 0, 0)

// const shaderMaterial = new THREE.ShaderMaterial( {


//   blending: THREE.AdditiveBlending,
//   depthTest: false,
//   transparent: false,
//   vertexColors: true

// } );



// geometry.setAttribute( 'size', new THREE.Float32BufferAttribute( sizes, 1 ).setUsage( THREE.DynamicDrawUsage ) );

// // const material = new THREE.PointsMaterial({ color: '0xff0000' });
// // material.opacity = 1.0;
// const points = new THREE.Points(geometry, shaderMaterial);
// points.position.set(0, 0, 0)

// try{
//   scene.add(points);
//   window.alert("added");
// }
// catch(error){
//   window.alert(error);
// }

//const ran = new THREE.Vector3(-160, 100, 95);
// boundingBox.setFromPoints(geometry.attributes.position.array);
// const center = boundingBox.getCenter(new THREE.Vector3());
//camera.lookAt(center);
window.alert(camera.position.x);
window.alert(camera.position.y);
window.alert(camera.position.z);

// const wireframeGeometry = new THREE.Box3Helper(boundingBox, 0xffff00);

// // Add wireframe box to the scene
// scene.add(wireframeGeometry);

const box = new THREE.BoxGeometry( 1, 1, 1 );
const boxmat = new THREE.MeshBasicMaterial( { color: 0x00ff00 } );
const cube = new THREE.Mesh( box, boxmat );
//cube.position.set(ran);
//camera.lookAt(ran);

scene.add( cube );
cube.position.set(0, 0, 0);



const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

window.addEventListener( 'mousemove', onMouseMove, false );
const sphereGeometry = new THREE.SphereGeometry( 0.025, 32, 32 );
const sphereMaterial = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
scene.add(sphere);

// Create the rayline material outside the onMouseMove function
const raylineMat = new THREE.LineDashedMaterial({ color: 0xff0000 });

// Create the rayline object outside the onMouseMove function
const rayline = new THREE.Line(new THREE.BufferGeometry(), raylineMat);
rayline.position.copy(camera.position);
rayline.visible = false;
scene.add(rayline);

function onMouseMove (event){
  //event.preventDefault();
  pointer.x = (event.clientX/window.innerWidth)*2-1;
  pointer.y = -(event.clientY/window.innerHeight)*2+1;
  //pointer.z = 0.5;

  raycaster.setFromCamera(pointer, camera);
  raycaster.far = 100.0;
  // draw line from camera to the point of intersection
  
  const intersects = raycaster.intersectObjects([line], false);
  if (intersects.length > 0){
      sphere.position.copy(intersects[0].point);
      const raypoints = [camera.position.clone(), intersects[0].point.clone()];
      timeLogger.innerText(raypoints[0].z.toString + raypoints[1].z.toString);
      try {
          rayline.geometry.setFromPoints(raypoints);
          rayline.visible = true;
          //window.alert("Ray added");
      }
      catch (e){
          window.alert(e);
      }
                  
  } else {
      rayline.visible = false;
      //window.alert("No intersection");
  }

}

function render(){
  				//Render first pass and store the world space coords of the back face fragments into the texture.
				renderer.render( sceneFirstPass, camera, rtTexture, true );

				//Render the second pass and perform the volume rendering.
				renderer.render( sceneSecondPass, camera );
}

function animate(){
  requestAnimationFrame(animate);
  //controls.update();
  render();
}

animate();

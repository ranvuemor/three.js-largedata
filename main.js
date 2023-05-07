import * as THREE from 'three';
//import { ThreeGlobeGeneric } from 'three-globe';
import WebGL from 'three/addons/capabilities/WebGL.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

if ( WebGL.isWebGLAvailable() ) {

    var canvas = document.getElementsByTagName("canvas")[0];

    var size = {
		getWidth: function(){return canvas.offsetWidth;},
		getHeight: function(){return canvas.offsetHeight;}
	};

    var windowSize = function(withScrollBar) {
		var wid = 0;
		var hei = 0;
		if (typeof window.innerWidth != "undefined") {
			wid = window.innerWidth;
			hei = window.innerHeight;
		}
		else {
			if (document.documentElement.clientWidth == 0) {
				wid = document.body.clientWidth;
				hei = document.body.clientHeight;
			}
			else {
				wid = document.documentElement.clientWidth;
				hei = document.documentElement.clientHeight;
			}
		}
		return { width: wid - (withScrollBar ? (wid - document.body.offsetWidth + 1) : 0), height: hei };
	};

	const scene = new THREE.Scene();
    scene.matrixWorldAutoUpdate = true;
    const ambientLight = new THREE.AmbientLight(0xcccccc);
    scene.add(ambientLight);
    scene.add(new THREE.DirectionalLight(0xffffff, 0.6));
    const camera = new THREE.PerspectiveCamera( 75, size.getWidth() / size.getHeight(), 0.1, 1000 );

    var img = new Image();
    img.onload = function () {
        scene.background = new THREE.TextureLoader().load(img.src);
        setBackground(scene, img.width, img.height);
    };
    img.src = "background.jpg";

    var setBackground = function(scene, backgroundImageWidth, backgroundImageHeight) {
    
        if (scene.background) {
    
            var size = windowSize(true);
            var factor = (backgroundImageWidth / backgroundImageHeight) / (size.width / size.height);
    
            scene.background.offset.x = factor > 1 ? (1 - 1 / factor) / 2 : 0;
            scene.background.offset.y = factor > 1 ? 0 : (1 - factor) / 2;
    
            scene.background.repeat.x = factor > 1 ? 1 / factor : 1;
            scene.background.repeat.y = factor > 1 ? 1 : factor;
        }
    };

    const renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
    });
    var resize = function () {
		canvas.style.width = windowSize(true).width + "px";
		canvas.style.height = windowSize().height + "px";
		if(scene.background) {
			setBackground(scene, img.width, img.height);
		}
		camera.aspect = size.getWidth() / size.getHeight();
		camera.updateProjectionMatrix();
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.setSize(size.getWidth(), size.getHeight());
	};
	resize();
    window.addEventListener("resize", resize);

    document.body.appendChild( renderer.domElement );

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = false;
    controls.target.set(0, 0, 0);
    controls.enablePan = true;
    controls.keys = {
        LEFT: 'ArrowLeft', //left arrow
        UP: 'ArrowUp', // up arrow
        RIGHT: 'ArrowRight', // right arrow
        BOTTOM: 'ArrowDown' // down arrow
    }

    // var wire;
    // const fbxloader = new FBXLoader();
    // fbxloader.load('Barbed_Wire_Free.fbx', (object) => {
    //     const tex = new THREE.TextureLoader().load('/public/Metal_007_Base_Color.png');
    //     const mat = new THREE.MeshBasicMaterial({map:tex});
    //     object.material = mat;
    //     object.scale.set(.0005, .0005, .0005);
    //     wire = object;
    //     scene.add(object);
    // },
    // (xhr) => {
    //     console.log((xhr.loaded / xhr.total) * 100 + '% loaded')
    // },
    // (error) => {
    //     console.log(error)
    // })

    const geometry = new THREE.BoxGeometry( 1, 1, 1 );
    const texture = new THREE.TextureLoader().load('metallic-holographic-background.jpg'); 
    const material = new THREE.MeshBasicMaterial( { map:texture } );
    const cube = new THREE.Mesh( geometry, material );
    
    scene.add( cube );
    //cube.position.set(0, 0, 1);

    camera.position.set(0, 0, 3.0);
    //camera.rotation.x = - (Math.PI / 180) * 10;

    const lines = new THREE.LineDashedMaterial({color: 0x0000ff});
    const points = [];
    points.push(new THREE.Vector3(-1, -1, -1))
    points.push(new THREE.Vector3(1, -1, -1))
    points.push(new THREE.Vector3(1, 1, -1));
    points.push(new THREE.Vector3(-1, 1, -1));
    points.push(new THREE.Vector3(-1, -1, -1))
    points.push(new THREE.Vector3(-1, -1, 1));
    points.push(new THREE.Vector3(1, -1, 1))
    points.push(new THREE.Vector3(1, 1, 1));
    points.push(new THREE.Vector3(-1, 1, 1));
    points.push(new THREE.Vector3(-1, -1, 1));
    points.push(new THREE.Vector3(1, -1, 1))
    points.push(new THREE.Vector3(1, -1, -1))
    points.push(new THREE.Vector3(1, 1, -1));
    points.push(new THREE.Vector3(1, 1, 1));
    points.push(new THREE.Vector3(-1, 1, 1));
    points.push(new THREE.Vector3(-1, 1, -1));

    
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(lineGeometry, lines);
    scene.add(line);
    line.position.set(0, 0, 0);

    //document.body.appendChild(VRButton.createButton(renderer));
    //renderer.xr.enabled = true;
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
    //window.alert("Welcome");
    const timeLogger = document.getElementById('time');

    function onMouseMove (event){
        //event.preventDefault();
        pointer.x = (event.clientX/window.innerWidth)*2-1;
        pointer.y = -(event.clientY/window.innerHeight)*2+1;
        //pointer.z = 0.5;

        raycaster.setFromCamera(pointer, camera);
        raycaster.far = 100.0;
        // draw line from camera to the point of intersection
        
        const intersects = raycaster.intersectObjects([cube], false);
        if (intersects.length > 0){
            sphere.position.copy(intersects[0].point);
            const raypoints = [camera.position.clone(), intersects[0].point.clone()];
            timeLogger.innerText = raypoints[0].z.toString + raypoints[1].z.toString;
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
        
        renderer.render(scene, camera);
    }
    
    

    function animate() {
        requestAnimationFrame( animate );
        controls.update();

        // line.rotation.x += -0.01;
        // line.rotation.y += -0.01;
        // line.rotation.z += -0.01;
        // wire.rotation.x += 0.01;
        // wire.rotation.y += 0.01;
        // wire.rotation.z += 0.01;
        cube.rotation.x += 0.01;
        cube.rotation.y += 0.01;
        cube.rotation.z += 0.01;
        render()
        
        //renderer.setAnimationLoop(renderer.render(scene, camera));
    }
	animate();

} else {

	const warning = WebGL.getWebGLErrorMessage();
	document.getElementById( 'container' ).appendChild( warning );

}
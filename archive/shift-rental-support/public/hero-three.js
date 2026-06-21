/* global THREE */
// Fleet Command Center — Three.js hero background (r128)
// Intentionally global-scope friendly for a static HTML page.

(function () {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let scene;
  let camera;
  let renderer;
  let controls;
  let time = 0;
  const vehicles = [];
  const vehicleTrails = [];
  let raycaster;
  let mouse;
  let hoveredVehicle = null;
  const dataStreams = [];
  let animationId = null;
  let isVisible = true;

  const COLORS = {
    bg: 0x0a0a0a,
    fog: 0x0a0a0a,
    ground: 0x0c0c0c,
    grid: 0x151515,
    road: 0x111111,
    roadGlow: 0x1a1a1a,
    centerLine: 0x444444,
    primary: 0xf5a623,
    secondary: 0x5ac8fa,
    success: 0x34c759,
    danger: 0xff3b30,
    purple: 0xaf52de,
    building: 0x222222,
    buildingGlow: 0xf5a623,
  };

  const ROADS = [
    { id: "h-main", from: [-110, 0], to: [110, 0], width: 8 },
    { id: "v-main", from: [0, -110], to: [0, 110], width: 8 },
    { id: "diag-1", from: [-85, -85], to: [85, 85], width: 5 },
    { id: "diag-2", from: [85, -85], to: [-85, 85], width: 5 },
  ];

  const BUILDINGS = [
    { x: -75, z: -16, type: "spire", h: 18, w: 4 },
    { x: -45, z: -18, type: "crystal", h: 12, w: 6 },
    { x: -15, z: -22, type: "platform", h: 5, w: 10 },
    { x: 20, z: -17, type: "spire", h: 15, w: 3.5 },
    { x: 50, z: -19, type: "crystal", h: 11, w: 5.5 },
    { x: 80, z: -16, type: "spire", h: 20, w: 4 },
    { x: -65, z: 16, type: "crystal", h: 13, w: 5 },
    { x: -35, z: 18, type: "spire", h: 16, w: 4 },
    { x: 10, z: 22, type: "platform", h: 6, w: 11 },
    { x: 40, z: 17, type: "crystal", h: 10, w: 6 },
    { x: 70, z: 19, type: "spire", h: 17, w: 4 },
    { x: -18, z: -75, type: "spire", h: 19, w: 3.5 },
    { x: -20, z: -45, type: "crystal", h: 12, w: 5 },
    { x: -22, z: 35, type: "platform", h: 5, w: 9 },
    { x: -18, z: 65, type: "spire", h: 16, w: 4 },
    { x: -20, z: 95, type: "crystal", h: 14, w: 5.5 },
    { x: 18, z: -65, type: "crystal", h: 14, w: 5 },
    { x: 20, z: -35, type: "spire", h: 17, w: 4 },
    { x: 22, z: 45, type: "platform", h: 5, w: 10 },
    { x: 18, z: 75, type: "spire", h: 15, w: 3.5 },
    { x: 20, z: 100, type: "crystal", h: 18, w: 6 },
    { x: -60, z: -60, type: "platform", h: 4, w: 8 },
    { x: 60, z: -60, type: "spire", h: 14, w: 3.5 },
    { x: -60, z: 60, type: "spire", h: 16, w: 4 },
    { x: 60, z: 60, type: "platform", h: 5, w: 9 },
  ];

  const VEHICLE_CONFIGS = [
    { roadId: "h-main", speed: 0.16, offset: 0, color: COLORS.success, lane: 1 },
    { roadId: "h-main", speed: -0.18, offset: 0.25, color: COLORS.secondary, lane: -1 },
    { roadId: "h-main", speed: 0.14, offset: 0.5, color: COLORS.primary, lane: 1 },
    { roadId: "h-main", speed: -0.15, offset: 0.75, color: COLORS.danger, lane: -1 },
    { roadId: "v-main", speed: 0.17, offset: 0.1, color: COLORS.purple, lane: 1 },
    { roadId: "v-main", speed: -0.16, offset: 0.35, color: COLORS.success, lane: -1 },
    { roadId: "v-main", speed: 0.15, offset: 0.6, color: COLORS.secondary, lane: 1 },
    { roadId: "v-main", speed: -0.17, offset: 0.85, color: COLORS.primary, lane: -1 },
    { roadId: "diag-1", speed: 0.14, offset: 0.15, color: COLORS.danger, lane: 1 },
    { roadId: "diag-1", speed: -0.15, offset: 0.6, color: COLORS.purple, lane: -1 },
    { roadId: "diag-2", speed: 0.13, offset: 0.2, color: COLORS.secondary, lane: 1 },
    { roadId: "diag-2", speed: -0.14, offset: 0.65, color: COLORS.success, lane: -1 },
  ];

  function init() {
    const container = document.getElementById("hero-canvas-container");
    if (!container) return;
    if (typeof THREE === "undefined") {
      const loading = document.getElementById("loading");
      if (loading) loading.textContent = "WEBGL UNAVAILABLE";
      return;
    }

    scene = new THREE.Scene();
    scene.background = new THREE.Color(COLORS.bg);
    scene.fog = new THREE.FogExp2(COLORS.fog, 0.0025);

    camera = new THREE.PerspectiveCamera(
      38,
      container.clientWidth / Math.max(1, container.clientHeight),
      0.1,
      1000
    );
    camera.position.set(150, 95, 150);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.5;
    container.appendChild(renderer.domElement);

    if (THREE.OrbitControls) {
      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 80;
      controls.maxDistance = 320;
      controls.maxPolarAngle = Math.PI / 2 - 0.1;
      controls.target.set(0, 5, 0);
      controls.enablePan = false;
      // Critical for landing pages: OrbitControls listens to wheel events and will
      // preventDefault() for zooming — which makes the page feel "stuck" on the hero.
      controls.enableZoom = false;
      controls.autoRotate = !reduceMotion;
      controls.autoRotateSpeed = 0.35;
    }

    setupLighting();
    createGround();
    createRoads();
    createBuildings();
    createHub();
    createVehicles();
    createAtmosphere();

    const loading = document.getElementById("loading");
    if (loading) loading.style.display = "none";

    raycaster = new THREE.Raycaster();
    raycaster.params.Points.threshold = 2;
    mouse = new THREE.Vector2();
    renderer.domElement.addEventListener("mousemove", onMouseMove);

    window.addEventListener("resize", onWindowResize);

    setupVisibilityObserver();

    if (!reduceMotion) animate();
    else renderer.render(scene, camera);
  }

  function setupVisibilityObserver() {
    const container = document.getElementById("hero-canvas-container");
    if (!container || typeof IntersectionObserver === "undefined") return;

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          isVisible = entry.isIntersecting;
        });
      },
      { threshold: 0.1 }
    );

    observer.observe(container);
  }

  function setupLighting() {
    scene.add(new THREE.AmbientLight(0x282828, 0.55));

    const sun = new THREE.DirectionalLight(0xffffff, 0.85);
    sun.position.set(80, 120, 60);
    sun.castShadow = true;
    sun.shadow.mapSize.set(4096, 4096);
    sun.shadow.camera.left = -150;
    sun.shadow.camera.right = 150;
    sun.shadow.camera.top = 150;
    sun.shadow.camera.bottom = -150;
    scene.add(sun);

    scene.add(new THREE.DirectionalLight(0x3a3a3a, 0.3).position.set(-60, 40, -60));
    scene.add(new THREE.HemisphereLight(0x353535, COLORS.bg, 0.45));

    const hubLight = new THREE.PointLight(COLORS.primary, 3, 120);
    hubLight.position.set(0, 25, 0);
    scene.add(hubLight);
  }

  function createGround() {
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(260, 260),
      new THREE.MeshStandardMaterial({
        color: COLORS.ground,
        roughness: 0.9,
        metalness: 0.1,
      })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.5;
    ground.receiveShadow = true;
    scene.add(ground);

    const grid = new THREE.GridHelper(260, 52, COLORS.grid, 0x101010);
    grid.position.y = -0.45;
    grid.material.opacity = 0.35;
    grid.material.transparent = true;
    scene.add(grid);
  }

  function createRoads() {
    const roadMat = new THREE.MeshStandardMaterial({
      color: COLORS.road,
      roughness: 0.7,
      metalness: 0.2,
    });

    const glowMat = new THREE.MeshBasicMaterial({
      color: COLORS.roadGlow,
      transparent: true,
      opacity: 0.35,
    });

    ROADS.forEach(function (road) {
      const start = new THREE.Vector3(road.from[0], 0, road.from[1]);
      const end = new THREE.Vector3(road.to[0], 0, road.to[1]);
      const dist = start.distanceTo(end);
      const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
      const direction = new THREE.Vector3().subVectors(end, start).normalize();

      const mesh = new THREE.Mesh(new THREE.BoxGeometry(dist, 0.4, road.width), roadMat);
      mesh.position.copy(mid);
      mesh.lookAt(end);
      mesh.receiveShadow = true;
      mesh.userData = { roadId: road.id, start: start, end: end, width: road.width };
      scene.add(mesh);

      const glow = new THREE.Mesh(new THREE.BoxGeometry(dist, 0.1, road.width + 0.5), glowMat);
      glow.position.copy(mid);
      glow.position.y = -0.15;
      glow.lookAt(end);
      scene.add(glow);

      createParallelDottedLine(start, end, direction, dist);
    });
  }

  function createParallelDottedLine(start, end, direction, totalDist) {
    const dashLength = 3;
    const gapLength = 2;
    const segmentLength = dashLength + gapLength;
    const numSegments = Math.floor(totalDist / segmentLength);

    const dashGeo = new THREE.BoxGeometry(dashLength, 0.06, 0.18);
    const dashMat = new THREE.MeshBasicMaterial({
      color: COLORS.centerLine,
      transparent: true,
      opacity: 0.7,
    });

    for (let i = 0; i < numSegments; i++) {
      const t = (i * segmentLength + dashLength / 2) / totalDist;
      const pos = new THREE.Vector3().copy(start).add(direction.clone().multiplyScalar(t * totalDist));
      pos.y = 0.22;

      const dash = new THREE.Mesh(dashGeo, dashMat);
      dash.position.copy(pos);
      dash.lookAt(end);
      scene.add(dash);
    }
  }

  function createBuildings() {
    BUILDINGS.forEach(function (b) {
      let geo;
      let mat;
      let coreGeo;

      if (b.type === "crystal") {
        geo = new THREE.ConeGeometry(b.w / 2, b.h, 4);
        coreGeo = new THREE.ConeGeometry(b.w / 3.5, b.h * 0.8, 4);
        mat = new THREE.MeshPhysicalMaterial({
          color: COLORS.building,
          metalness: 0.15,
          roughness: 0.1,
          transmission: 0.5,
          transparent: true,
          opacity: 0.75,
          thickness: 1.2,
          emissive: COLORS.buildingGlow,
          emissiveIntensity: 0.18,
        });
      } else if (b.type === "spire") {
        geo = new THREE.CylinderGeometry(b.w / 4, b.w / 2, b.h, 6);
        coreGeo = new THREE.CylinderGeometry(b.w / 5, b.w / 3.5, b.h * 0.9, 6);
        mat = new THREE.MeshPhysicalMaterial({
          color: COLORS.building,
          metalness: 0.2,
          roughness: 0.08,
          transmission: 0.45,
          transparent: true,
          opacity: 0.8,
          thickness: 1,
          emissive: COLORS.buildingGlow,
          emissiveIntensity: 0.25,
        });
      } else if (b.type === "platform") {
        geo = new THREE.BoxGeometry(b.w, b.h, b.w);
        mat = new THREE.MeshPhysicalMaterial({
          color: COLORS.building,
          metalness: 0.15,
          roughness: 0.15,
          transmission: 0.4,
          transparent: true,
          opacity: 0.85,
          thickness: 1.2,
          emissive: COLORS.buildingGlow,
          emissiveIntensity: 0.15,
        });
      }

      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(b.x, b.h / 2, b.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      scene.add(mesh);

      if (coreGeo) {
        const coreMat = new THREE.MeshBasicMaterial({
          color: COLORS.buildingGlow,
          transparent: true,
          opacity: 0.35,
        });
        const core = new THREE.Mesh(coreGeo, coreMat);
        core.position.set(b.x, b.h / 2, b.z);
        scene.add(core);
      }
    });
  }

  function createHub() {
    const platform = new THREE.Mesh(
      new THREE.CylinderGeometry(12, 12, 0.5, 48),
      new THREE.MeshPhysicalMaterial({
        color: 0x252525,
        roughness: 0.35,
        metalness: 0.6,
        transmission: 0.35,
        transparent: true,
        opacity: 0.92,
        emissive: COLORS.primary,
        emissiveIntensity: 0.25,
      })
    );
    platform.position.set(0, 0.25, 0);
    platform.receiveShadow = true;
    scene.add(platform);

    const ringMat = new THREE.MeshBasicMaterial({
      color: COLORS.primary,
      transparent: true,
      opacity: 0.55,
      side: THREE.DoubleSide,
    });

    [9, 6, 3].forEach(function (r, i) {
      const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.15, r, 48), ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.set(0, 0.52 + i * 0.1, 0);
      ring.userData = { pulse: true, delay: i * 0.4 };
      scene.add(ring);
    });

    const beacon = new THREE.Mesh(
      new THREE.CylinderGeometry(0.5, 0.5, 35, 16),
      new THREE.MeshBasicMaterial({
        color: COLORS.primary,
        transparent: true,
        opacity: 0.15,
      })
    );
    beacon.position.set(0, 17.5, 0);
    scene.add(beacon);

    const center = new THREE.Mesh(
      new THREE.CircleGeometry(1.8, 32),
      new THREE.MeshBasicMaterial({
        color: COLORS.primary,
        transparent: true,
        opacity: 0.92,
      })
    );
    center.rotation.x = -Math.PI / 2;
    center.position.set(0, 0.55, 0);
    center.userData = { pulse: true };
    scene.add(center);
  }

  function createVehicles() {
    VEHICLE_CONFIGS.forEach(function (config, index) {
      const road = ROADS.find(function (r) {
        return r.id === config.roadId;
      });
      if (!road) return;

      const vehicle = createVehicleMesh(config);

      const start = new THREE.Vector3(road.from[0], 0.6, road.from[1]);
      const end = new THREE.Vector3(road.to[0], 0.6, road.to[1]);
      const direction = new THREE.Vector3().subVectors(end, start).normalize();

      const laneOffset = config.lane * 2.5;
      const perp = new THREE.Vector3(-direction.z, 0, direction.x).multiplyScalar(laneOffset);

      const totalDist = start.distanceTo(end);
      const initialPos = new THREE.Vector3()
        .copy(start)
        .add(direction.clone().multiplyScalar(totalDist * config.offset))
        .add(perp);

      vehicle.position.copy(initialPos);
      vehicle.lookAt(end.clone().add(perp));

      vehicle.userData = {
        road: road,
        start: start,
        end: end,
        direction: direction,
        perp: new THREE.Vector3(-direction.z, 0, direction.x),
        speed: config.speed,
        progress: config.offset,
        totalDist: totalDist,
        color: config.color,
        lane: config.lane,
        vehicleIndex: index,
      };

      scene.add(vehicle);
      vehicles.push(vehicle);

      createVehicleTrail(config, index);
      createDataStream(config, index);
    });
  }

  function createVehicleTrail(config, vehicleIndex) {
    const TRAIL_LENGTH = 20;
    const trail = [];

    for (let i = 0; i < TRAIL_LENGTH; i++) {
      const opacity = 0.4 * (1 - i / TRAIL_LENGTH);
      const size = 0.5 * (1 - i / TRAIL_LENGTH) + 0.15;

      const trailGeo = new THREE.SphereGeometry(size, 8, 8);
      const trailMat = new THREE.MeshBasicMaterial({
        color: config.color,
        transparent: true,
        opacity: opacity,
      });
      const trailDot = new THREE.Mesh(trailGeo, trailMat);
      trailDot.visible = false;
      scene.add(trailDot);
      trail.push(trailDot);
    }

    vehicleTrails[vehicleIndex] = {
      dots: trail,
      positions: [],
    };
  }

  function createVehicleMesh(config) {
    const group = new THREE.Group();

    const bodyGeo = new THREE.SphereGeometry(0.85, 16, 16);
    const bodyMat = new THREE.MeshBasicMaterial({
      color: config.color,
      transparent: true,
      opacity: 1.0,
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    group.add(body);

    const glowGeo = new THREE.SphereGeometry(1.6, 16, 16);
    const glowMat = new THREE.MeshBasicMaterial({
      color: config.color,
      transparent: true,
      opacity: 0.45,
    });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    group.add(glow);

    const coneGeo = new THREE.ConeGeometry(0.55, 3, 12, 1, true);
    const coneMat = new THREE.MeshBasicMaterial({
      color: config.color,
      transparent: true,
      opacity: 0.2,
      side: THREE.DoubleSide,
    });
    const cone = new THREE.Mesh(coneGeo, coneMat);
    cone.rotation.x = -Math.PI / 2;
    cone.position.z = 1.8;
    group.add(cone);

    const light = new THREE.PointLight(config.color, 1.8, 22);
    light.position.y = 0.5;
    group.add(light);

    return group;
  }

  function updateVehicles() {
    vehicles.forEach(function (vehicle) {
      const data = vehicle.userData;
      const vehicleIndex = data.vehicleIndex;

      const currentPos = vehicle.position.clone();

      data.progress += data.speed * 0.016;
      if (data.progress > 1) data.progress = 0;
      if (data.progress < 0) data.progress = 1;

      const basePos = new THREE.Vector3()
        .copy(data.start)
        .add(data.direction.clone().multiplyScalar(data.totalDist * data.progress));

      const offset = data.perp.clone().multiplyScalar(data.lane * 2.5);
      vehicle.position.copy(basePos.add(offset));

      const pulse = 1 + Math.sin(time * 3 + data.progress * 10) * 0.12;
      vehicle.children[0].scale.setScalar(pulse);
      vehicle.children[1].scale.setScalar(pulse * 1.05);

      updateVehicleTrail(vehicleIndex, currentPos);
    });
  }

  function updateVehicleTrail(vehicleIndex, newPosition) {
    const trail = vehicleTrails[vehicleIndex];
    if (!trail) return;

    trail.positions.unshift(newPosition.clone());
    if (trail.positions.length > trail.dots.length) {
      trail.positions.pop();
    }

    for (let i = 0; i < trail.dots.length; i++) {
      if (i < trail.positions.length) {
        trail.dots[i].position.copy(trail.positions[i]);
        trail.dots[i].visible = true;
      } else {
        trail.dots[i].visible = false;
      }
    }
  }

  function createDataStream(config, vehicleIndex) {
    const curve = new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(0, 0.6, 0),
      new THREE.Vector3(0, 15, 0),
      new THREE.Vector3(0, 2, 0)
    );

    const points = curve.getPoints(30);
    const geometry = new THREE.BufferGeometry().setFromPoints(points);

    const material = new THREE.LineDashedMaterial({
      color: config.color,
      dashSize: 2,
      gapSize: 3,
      opacity: 0.5,
      transparent: true,
      linewidth: 1,
    });

    const line = new THREE.Line(geometry, material);
    line.computeLineDistances();
    scene.add(line);

    dataStreams[vehicleIndex] = {
      line: line,
      curve: curve,
      offset: Math.random() * 10,
      speed: 0.3 + Math.random() * 0.2,
    };
  }

  function updateDataStreams() {
    dataStreams.forEach(function (stream, index) {
      if (!stream || !vehicles[index]) return;

      const vehicle = vehicles[index];
      const vehiclePos = vehicle.position.clone();

      stream.curve.v0.copy(vehiclePos);

      const midX = (vehiclePos.x + 0) * 0.5;
      const midZ = (vehiclePos.z + 0) * 0.5;
      const arcHeight = Math.min(vehiclePos.distanceTo(new THREE.Vector3(0, 0, 0)) * 0.3, 25);
      stream.curve.v1.set(midX, arcHeight, midZ);

      const points = stream.curve.getPoints(30);
      stream.line.geometry.setFromPoints(points);
      stream.line.computeLineDistances();

      stream.offset += stream.speed;
      stream.line.material.dashOffset = -stream.offset;

      const distToHub = vehiclePos.distanceTo(new THREE.Vector3(0, 0, 0));
      const opacity = Math.max(0.15, Math.min(0.6, 1 - distToHub / 120));
      stream.line.material.opacity = opacity;
    });
  }

  function createAtmosphere() {
    const geo = new THREE.BufferGeometry();
    const pos = [];
    for (let i = 0; i < 300; i++) {
      pos.push(
        (Math.random() - 0.5) * 240,
        Math.random() * 55 + 5,
        (Math.random() - 0.5) * 240
      );
    }
    geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));

    const mat = new THREE.PointsMaterial({
      color: 0x555555,
      size: 0.4,
      transparent: true,
      opacity: 0.3,
      sizeAttenuation: true,
    });

    scene.add(new THREE.Points(geo, mat));
  }

  function animate() {
    animationId = window.requestAnimationFrame(animate);

    if (!isVisible) return;

    time += 0.016;

    updateVehicles();
    updateDataStreams();
    updateHover();

    scene.traverse(function (child) {
      if (child.userData.pulse) {
        const s = 1 + Math.sin(time * 2 + (child.userData.delay || 0)) * 0.08;
        child.scale.set(s, s, 1);
      }
      if (child.userData.float) {
        child.position.y += Math.sin(time + child.userData.offset) * 0.008;
      }
    });

    if (controls) controls.update();
    renderer.render(scene, camera);
  }

  function onWindowResize() {
    const container = document.getElementById("hero-canvas-container");
    if (!container || !camera || !renderer) return;
    camera.aspect = container.clientWidth / Math.max(1, container.clientHeight);
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  }

  function onMouseMove(event) {
    const container = document.getElementById("hero-canvas-container");
    if (!container) return;
    const rect = container.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  }

  function updateHover() {
    if (!raycaster || !mouse || !camera) return;
    raycaster.setFromCamera(mouse, camera);

    const vehicleBodies = vehicles.map(function (v) {
      return v.children[0];
    });
    const intersects = raycaster.intersectObjects(vehicleBodies);

    const tooltip = document.getElementById("tooltip");

    if (intersects.length > 0) {
      const hitBody = intersects[0].object;
      const vehicle = hitBody.parent;
      const data = vehicle.userData;

      if (hoveredVehicle !== vehicle) {
        hoveredVehicle = vehicle;

        vehicle.children[0].material.opacity = 1;
        vehicle.children[1].material.opacity = 0.7;

        const vehicleId = "FL-" + String(data.vehicleIndex + 1).padStart(3, "0");
        document.getElementById("tooltip-id").textContent = vehicleId;
        document.getElementById("tooltip-speed").textContent = String(Math.abs(Math.round(data.speed * 200)));
        document.getElementById("tooltip-route").textContent = data.road.id.toUpperCase();
        document.getElementById("tooltip-dot").style.backgroundColor =
          "#" + data.color.toString(16).padStart(6, "0");

        const statusEl = document.getElementById("tooltip-status");
        if (statusEl) statusEl.textContent = "Active";

        tooltip.style.display = "block";
      }

      const container = document.getElementById("hero-canvas-container");
      const rect = container.getBoundingClientRect();
      tooltip.style.left = (mouse.x * 0.5 + 0.5) * rect.width + 15 + "px";
      tooltip.style.top = (-mouse.y * 0.5 + 0.5) * rect.height - 10 + "px";
    } else {
      if (hoveredVehicle) {
        hoveredVehicle.children[0].material.opacity = 1;
        hoveredVehicle.children[1].material.opacity = 0.45;
        hoveredVehicle = null;
      }
      tooltip.style.display = "none";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

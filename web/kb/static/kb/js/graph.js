    // 3D GRAPH VISUALIZATION (THREE.JS)
    // =========================================================================
    var graphInitialized = false;
    var scene, camera, renderer, controls;
    var nodeMeshes = [];
    var edgeLines = [];
    var labelSprites = [];
    var raycaster, mouse;
    var autoRotate = true;
    var hoveredNode = null;
    var nodesMap = {};
    var assertionEdgeMaterial = null;

    function init3DGraph() {
      const container = document.getElementById('graph-view');
      const canvas = document.getElementById('canvas3d');

      const width = container.clientWidth || window.innerWidth;
      const height = container.clientHeight || (window.innerHeight - 66);

      scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0xe8e0d4, 0.0018);

      camera = new THREE.PerspectiveCamera(52, width / height, 1, 3000);
      camera.position.set(0, 160, 420);

      renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.maxDistance = 1200;
      controls.minDistance = 30;

      const ambientLight = new THREE.AmbientLight(0xffffff, 1.1);
      scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
      dirLight.position.set(150, 250, 150);
      scene.add(dirLight);

      const pointLight = new THREE.PointLight(0xC4B49A, 1.35, 800);
      pointLight.position.set(0, 50, 0);
      scene.add(pointLight);

      raycaster = new THREE.Raycaster();
      mouse = new THREE.Vector2();

      buildGraphElements();

      window.addEventListener('resize', onWindowResize);
      canvas.addEventListener('mousemove', onCanvasMouseMove);
      canvas.addEventListener('click', onCanvasClick);

      graphInitialized = true;
      animate();
    }

    function refresh3DGraphData() {
      if (!scene) return;
      // Remove old meshes, lines, sprites
      nodeMeshes.forEach(m => scene.remove(m));
      edgeLines.forEach(l => scene.remove(l));
      labelSprites.forEach(s => scene.remove(s));
      buildGraphElements();
    }

    function buildGraphElements() {
      nodesMap = {};
      nodeMeshes = [];
      edgeLines = [];
      labelSprites = [];

      const concepts = KB_DATA.concepts || [];
      const instances = KB_DATA.instances || [];
      const assertions = KB_DATA.assertions || [];

      const totalConcepts = concepts.length || 1;
      concepts.forEach((c, idx) => {
        const phi = Math.acos(-1 + (2 * idx) / totalConcepts);
        const theta = Math.sqrt(totalConcepts * Math.PI) * phi;
        const radius = 135 + (idx % 3) * 22;

        const x = radius * Math.cos(theta) * Math.sin(phi);
        const y = radius * Math.sin(theta) * Math.sin(phi) * 0.7;
        const z = radius * Math.cos(phi);

        nodesMap[c.id] = {
          id: c.id,
          name: conceptLabel(c) || c.id,
          type: 'concept',
          data: c,
          x: x,
          y: y,
          z: z
        };
      });

      instances.forEach((inst, idx) => {
        const parent = nodesMap[inst.instanceOf];
        let x, y, z;
        if (parent) {
          const angle = (idx * 1.3) % (Math.PI * 2);
          const dist = 38 + (idx % 4) * 9;
          x = parent.x + Math.cos(angle) * dist;
          y = parent.y + (Math.sin(angle) * dist * 0.8) + ((idx % 3) - 1) * 16;
          z = parent.z + Math.sin(angle) * dist;
        } else {
          const angle = (idx / (instances.length || 1)) * Math.PI * 2;
          x = Math.cos(angle) * 230;
          y = ((idx % 5) - 2) * 25;
          z = Math.sin(angle) * 230;
        }

        nodesMap[inst.id] = {
          id: inst.id,
          name: inst.id,
          type: 'instance',
          data: inst,
          x: x,
          y: y,
          z: z
        };
      });

      const conceptGeo = new THREE.SphereGeometry(4.6, 28, 28);
      const conceptMat = new THREE.MeshStandardMaterial({
        color: 0x4A6FA5,
        roughness: 0.38,
        metalness: 0.08
      });

      const instanceGeo = new THREE.OctahedronGeometry(3.4, 0);
      const instanceMat = new THREE.MeshStandardMaterial({
        color: 0x4F7A62,
        roughness: 0.38,
        metalness: 0.08
      });

      Object.values(nodesMap).forEach(node => {
        const isConcept = node.type === 'concept';
        const mesh = new THREE.Mesh(isConcept ? conceptGeo : instanceGeo, isConcept ? conceptMat.clone() : instanceMat.clone());
        mesh.position.set(node.x, node.y, node.z);
        mesh.userData = node;
        scene.add(mesh);
        nodeMeshes.push(mesh);
        node.mesh = mesh;

        if (isConcept && (node.id.length <= 15 || node.id.includes('CHAPTER') || node.id.includes('ALGORITHM') || node.id.includes('QUESTION'))) {
          const sprite = createTextSprite(node.id, '#2A241C');
          sprite.position.set(node.x, node.y + 7.5, node.z);
          scene.add(sprite);
          labelSprites.push(sprite);
        }
      });

      // 1. subclassOf -> Amber
      const subclassMat = new THREE.LineBasicMaterial({
        color: 0xA07840,
        transparent: true,
        opacity: 0.7,
        linewidth: 1.5
      });

      concepts.forEach(c => {
        if (c.subclassOf && c.subclassOf !== c.id && nodesMap[c.subclassOf] && nodesMap[c.id]) {
          const line = createCurvedLine(nodesMap[c.id], nodesMap[c.subclassOf], subclassMat);
          scene.add(line);
          edgeLines.push(line);
        }
      });

      // 2. instanceOf -> Royal Purple
      const instanceOfMat = new THREE.LineBasicMaterial({
        color: 0x6B5B8A,
        transparent: true,
        opacity: 0.5,
        linewidth: 1
      });

      instances.forEach(inst => {
        if (inst.instanceOf && nodesMap[inst.instanceOf] && nodesMap[inst.id]) {
          const line = createStraightLine(nodesMap[inst.id], nodesMap[inst.instanceOf], instanceOfMat);
          scene.add(line);
          edgeLines.push(line);
        }
      });

      // 3. Assertions -> Primary color
      assertionEdgeMaterial = new THREE.LineBasicMaterial({
        color: new THREE.Color(currentTheme.primary),
        transparent: true,
        opacity: 0.95,
        linewidth: 2.5
      });

      assertions.forEach(ast => {
        if (nodesMap[ast.source] && nodesMap[ast.target]) {
          const line = createCurvedLine(nodesMap[ast.source], nodesMap[ast.target], assertionEdgeMaterial, 16);
          scene.add(line);
          edgeLines.push(line);
        }
      });
    }

    function createStraightLine(p1, p2, material) {
      const points = [
        new THREE.Vector3(p1.x, p1.y, p1.z),
        new THREE.Vector3(p2.x, p2.y, p2.z)
      ];
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      return new THREE.Line(geometry, material);
    }

    function createCurvedLine(p1, p2, material, curveElev = 8) {
      const v1 = new THREE.Vector3(p1.x, p1.y, p1.z);
      const v2 = new THREE.Vector3(p2.x, p2.y, p2.z);
      const mid = new THREE.Vector3().addVectors(v1, v2).multiplyScalar(0.5);
      mid.y += curveElev;

      const curve = new THREE.QuadraticBezierCurve3(v1, mid, v2);
      const points = curve.getPoints(16);
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      return new THREE.Line(geometry, material);
    }

    function createTextSprite(text, color = '#0f172a') {
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 64;
      const ctx = canvas.getContext('2d');
      ctx.font = '500 20px Source Sans 3, sans-serif';
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, 128, 32);

      const texture = new THREE.CanvasTexture(canvas);
      texture.minFilter = THREE.LinearFilter;
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: 0.9 });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.scale.set(24, 6, 1);
      return sprite;
    }

    function onWindowResize() {
      const container = document.getElementById('graph-view');
      if (!container || !camera || !renderer) return;
      const width = container.clientWidth;
      const height = container.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    }

    function onCanvasMouseMove(e) {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      const tooltip = document.getElementById('tooltip3d');
      if (intersects.length > 0) {
        const node = intersects[0].object.userData;
        hoveredNode = intersects[0].object;
        tooltip.style.display = 'block';
        tooltip.style.left = (e.clientX + 14) + 'px';
        tooltip.style.top = (e.clientY + 14) + 'px';
        tooltip.innerHTML = `<b>${node.id}</b> <span style="opacity:0.8">(${node.type.toUpperCase()})</span>`;
        document.body.style.cursor = 'pointer';
      } else {
        hoveredNode = null;
        tooltip.style.display = 'none';
        document.body.style.cursor = 'default';
      }
    }

    function onCanvasClick(e) {
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);
      if (intersects.length > 0) {
        const node = intersects[0].object.userData;
        openDrawer(node);
      }
    }

    function openDrawer(node) {
      const drawer = document.getElementById('drawer3d');
      const badge = document.getElementById('drawerBadge');
      const idEl = document.getElementById('drawerId');
      const body = document.getElementById('drawerBody');
      const jumpBtn = document.getElementById('drawerJumpBtn');

      badge.innerText = node.type === 'concept' ? 'Khái niệm' : 'Đối tượng';
      badge.className = 'badge ' + (node.type === 'concept' ? 'badge-concept' : 'badge-instance');
      idEl.innerText = node.id;

      let html = '';
      const data = node.data || {};

      if (node.type === 'concept') {
        html += `<div style="color: var(--text-muted); font-size: 14px; font-weight: 600;">${data.name || ''}</div>`;
        if (data.domain) html += `<div class="info-line"><span class="info-line-label">Miền dữ liệu:</span><div class="info-line-value">${data.domain}</div></div>`;
        if (data.subclassOf) html += `<div class="info-line"><span class="info-line-label">Kế thừa:</span><div class="info-line-value"><b style="color: var(--subclass-color);">${data.subclassOf}</b></div></div>`;
        
        if (Array.isArray(data.attributes) && data.attributes.length > 0) {
          html += '<div style="margin-top: 0.35rem; font-weight: 700; font-size: 13px; color: var(--text-sub);">Thuộc tính định nghĩa:</div>';
          html += '<div class="attributes-box">';
          data.attributes.forEach(attr => {
            html += `<div class="attr-row"><span class="attr-name">${attr.name}</span><span class="attr-type-pill">${attr.value_type}</span></div>`;
          });
          html += '</div>';
        }
      } else {
        html += `<div class="info-line"><span class="info-line-label">Thuộc khái niệm:</span><div class="info-line-value"><b style="color: var(--concept-color);">${data.instanceOf || 'N/A'}</b></div></div>`;
        if (Array.isArray(data.attributes) && data.attributes.length > 0) {
          html += '<div style="margin-top: 0.35rem; font-weight: 700; font-size: 13px; color: var(--text-sub);">Giá trị thuộc tính:</div>';
          html += '<div class="attributes-box">';
          data.attributes.forEach(attr => {
            const isDesc = attr.name === 'description' || (typeof attr.value === 'string' && attr.value.length > 60);
            html += `
              <div class="attr-row" style="${isDesc ? 'flex-direction: column;' : ''}">
                <span class="attr-name">${attr.name}:</span>
                <div class="attr-value">${isDesc ? `<div class="text-quote-box">${attr.value}</div>` : `<b>${attr.value}</b>`}</div>
              </div>
            `;
          });
          html += '</div>';
        }
      }

      body.innerHTML = html;
      drawer.style.display = 'flex';

      jumpBtn.onclick = () => {
        switchView('inspector');
        if (node.type === 'concept') {
          selectDataset('concepts');
        } else {
          selectDataset('instances');
        }
        document.getElementById('searchInput').value = node.id;
        applyFilters();
      };
    }

    function closeDrawer() {
      document.getElementById('drawer3d').style.display = 'none';
    }

    function focusNodeIn3D(nodeId) {
      const node = nodesMap[nodeId];
      if (!node) return;

      openDrawer(node);

      const targetPos = new THREE.Vector3(node.x, node.y, node.z);
      controls.target.copy(targetPos);
      camera.position.set(node.x + 35, node.y + 25, node.z + 65);
      controls.update();
    }

    function resetCamera() {
      controls.target.set(0, 0, 0);
      camera.position.set(0, 160, 420);
      controls.update();
    }

    function toggleAutoRotate() {
      autoRotate = !autoRotate;
      document.getElementById('autoRotateBtn').innerText = `Xoay tự động: ${autoRotate ? 'Bật' : 'Tắt'}`;
    }

    function animate() {
      requestAnimationFrame(animate);

      if (autoRotate && !hoveredNode) {
        scene.rotation.y += 0.0012;
      }

      controls.update();
      renderer.render(scene, camera);
    }

    // =========================================================================

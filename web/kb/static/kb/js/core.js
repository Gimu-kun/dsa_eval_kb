    // =========================================================================
    // DYNAMIC & REAL-TIME KNOWLEDGE BASE DATA LOADING
    // =========================================================================
    var KB_DATA = {
      concepts: [],
      hierarchy: [],
      instances: [],
      relations: [],
      assertions: [],
      rules: [],
      operands: [],
      functions: []
    };

    var currentDataset = 'concepts';
    var lastDataFingerprint = '';
    var autoSyncEnabled = true;
    var autoSyncTimer = null;

    function conceptLabel(item) {
      if (!item) return '';
      const attrs = item.attributes || [];
      const named = attrs.find(a => a && a.name === 'name' && a.default != null && a.default !== '');
      if (named) return String(named.default);
      return item.name || item.id || '';
    }

    async function fetchJSONFile(url) {
      try {
        const res = await fetch(url);
        if (!res.ok) return null;
        return await res.json();
      } catch (err) {
        return null;
      }
    }

    async function fetchFirstAvailable(urls) {
      for (const u of urls) {
        const d = await fetchJSONFile(u);
        if (d) return d;
      }
      return null;
    }

    async function fetchKBData(manualTrigger = false) {
      const t = Date.now();
      // Load all JSON files dynamically via fetch with cache-busting timestamp
      const [cData, ontIData, dataIData, rData, ontAData, dataAData, ruData, hData, fData, ontOpData, dataOpData] = await Promise.all([
        fetchJSONFile(`/api/ontology/concepts.json?_t=${t}`),
        fetchJSONFile(`/api/ontology/instances.json?_t=${t}`),
        fetchJSONFile(`/api/data/instances.json?_t=${t}`),
        fetchJSONFile(`/api/ontology/relations.json?_t=${t}`),
        fetchJSONFile(`/api/ontology/assertions.json?_t=${t}`),
        fetchJSONFile(`/api/data/assertions.json?_t=${t}`),
        fetchJSONFile(`/api/ontology/rules.json?_t=${t}`),
        fetchFirstAvailable([`/api/ontology/hierarchy.json?_t=${t}`, `/api/ontology/hierarchy.json?_t=${t}`]),
        fetchJSONFile(`/api/ontology/functions.json?_t=${t}`),
        fetchJSONFile(`/api/ontology/operands.json?_t=${t}`),
        fetchJSONFile(`/api/data/operands.json?_t=${t}`)
      ]);

      const hierarchy = (hData && (hData.hierarchy || hData.hierarchies)) ? (hData.hierarchy || hData.hierarchies) : [];
      const hierarchyMap = {};
      hierarchy.forEach(item => {
        const sub = item.subclass || item.subclassOf;
        const sup = item.superclass || item.parent;
        if (sub && sup) hierarchyMap[sub] = sup;
      });

      const concepts = (cData && cData.concepts) ? cData.concepts : [];
      concepts.forEach(c => {
        c.subclassOf = hierarchyMap[c.id] || c.subclassOf || null;
      });

      // Merge instances from ontology and data (keyed by id)
      const instanceMap = new Map();
      ((ontIData && ontIData.instances) || []).forEach(i => { if (i && i.id) instanceMap.set(i.id, i); });
      ((dataIData && dataIData.instances) || []).forEach(i => { if (i && i.id) instanceMap.set(i.id, i); });
      const instances = Array.from(instanceMap.values());

      const relations = (rData && rData.relations) ? rData.relations : [];

      // Merge assertions from ontology and data (keyed by source + relation + target)
      const assertionMap = new Map();
      ((ontAData && ontAData.assertions) || []).forEach(a => {
        if (a) assertionMap.set(`${a.source}__${a.relation}__${a.target}`, a);
      });
      ((dataAData && dataAData.assertions) || []).forEach(a => {
        if (a) assertionMap.set(`${a.source}__${a.relation}__${a.target}`, a);
      });
      const assertions = Array.from(assertionMap.values());

      const rules = (ruData && ruData.rules) ? ruData.rules : [];
      const functions = (fData && fData.functions) ? fData.functions : [];

      // Merge operands from ontology and data (keyed by id)
      const operandMap = new Map();
      ((ontOpData && ontOpData.operands) || []).forEach(op => { if (op && op.id) operandMap.set(op.id, op); });
      ((dataOpData && dataOpData.operands) || []).forEach(op => { if (op && op.id) operandMap.set(op.id, op); });
      const operands = Array.from(operandMap.values());

      // Create fingerprint to detect changes
      const fingerprint = `${concepts.length}_${hierarchy.length}_${instances.length}_${relations.length}_${assertions.length}_${rules.length}_${functions.length}_${operands.length}_${JSON.stringify(concepts).length}_${JSON.stringify(instances).length}`;

      if (fingerprint !== lastDataFingerprint || manualTrigger) {
        lastDataFingerprint = fingerprint;

        KB_DATA.concepts = concepts;
        KB_DATA.hierarchy = hierarchy;
        KB_DATA.instances = instances;
        KB_DATA.relations = relations;
        KB_DATA.assertions = assertions;
        KB_DATA.rules = rules;
        KB_DATA.functions = functions;
        KB_DATA.operands = operands;

        // Update header & sidebar counters
        updateHeaderAndSidebarStats();

        // Refresh dropdown filter options and cards
        setupFilterDropdown();
        applyFilters();
        populateTopicFilter();
        renderQuestionExplorer();
        renderDashboard();

        // If 3D graph is already active, refresh nodes
        if (graphInitialized) {
          refresh3DGraphData();
        }

        if (manualTrigger) {
          showLiveNotification('Updated!');
        }
      }
    }

    function updateHeaderAndSidebarStats() {
      const cLen = KB_DATA.concepts.length;
      const iLen = KB_DATA.instances.length;
      const rLen = KB_DATA.relations.length;
      const aLen = KB_DATA.assertions.length;
      const ruLen = KB_DATA.rules.length;

      const hLen = (KB_DATA.hierarchy || []).length;

      // Header stats
      const statC = document.getElementById('stat-concepts');
      const statH = document.getElementById('stat-hierarchy');
      const statI = document.getElementById('stat-instances');
      if (statC) statC.innerText = cLen;
      if (statH) statH.innerText = hLen;
      if (statI) statI.innerText = iLen;

      // Sidebar badges
      const bC = document.getElementById('badge-concepts');
      const bH = document.getElementById('badge-hierarchy');
      if (bH) bH.innerText = hLen;
      const bI = document.getElementById('badge-instances');
      const bR = document.getElementById('badge-relations');
      const bA = document.getElementById('badge-assertions');
      const bRu = document.getElementById('badge-rules');
      const bOp = document.getElementById('badge-operands');
      const bF = document.getElementById('badge-functions');
      const fLen = (KB_DATA.functions || []).length;
      const opLen = (KB_DATA.operands || []).length;
      if (bC) bC.innerText = cLen;
      if (bI) bI.innerText = iLen;
      if (bR) bR.innerText = rLen;
      if (bA) bA.innerText = aLen;
      if (bRu) bRu.innerText = ruLen;
      if (bOp) bOp.innerText = opLen;
      if (bF) bF.innerText = fLen;

      // HUD 3D stats
      const hudC = document.getElementById('hud-count-concepts');
      const hudI = document.getElementById('hud-count-instances');
      if (hudC) hudC.innerText = cLen;
      if (hudI) hudI.innerText = iLen;
    }

    function toggleAutoSync() {
      autoSyncEnabled = !autoSyncEnabled;
      const dot = document.getElementById('liveDot');
      const text = document.getElementById('liveStatusText');

      if (autoSyncEnabled) {
        dot.className = 'live-dot';
        text.innerText = 'Live 3s';
        startAutoSync();
        fetchKBData(true);
      } else {
        dot.className = 'live-dot paused';
        text.innerText = 'Live: Tạm dừng';
        clearInterval(autoSyncTimer);
      }
    }

    function startAutoSync() {
      clearInterval(autoSyncTimer);
      autoSyncTimer = setInterval(() => {
        if (autoSyncEnabled) {
          fetchKBData(false);
        }
      }, 3000);
    }

    function showLiveNotification(msg) {
      const text = document.getElementById('liveStatusText');
      const orig = text.innerText;
      text.innerText = msg;
      setTimeout(() => {
        text.innerText = autoSyncEnabled ? 'Live 3s' : 'Tạm dừng';
      }, 2000);
    }

    // =========================================================================

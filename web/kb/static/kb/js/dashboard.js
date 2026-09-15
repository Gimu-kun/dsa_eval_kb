    var ontoFilter = 'dsa';
    var ontoSelectedId = null;
    var ontoExpandAllFlag = null;
    var ontoOpenIds = new Set();

    function isABoxId(id) {
      const s = String(id || '');
      return s.startsWith('I_Q_') || s.startsWith('I_EA_') || s.startsWith('I_ER_') || /^I_/.test(s);
    }

    function relEndList(rel, field) {
      const v = rel && rel[field];
      if (Array.isArray(v)) return v.filter(Boolean);
      return v ? [v] : [];
    }

    function conceptDomain(id) {
      const c = conceptById(id);
      return c && c.domain ? c.domain : '';
    }

    function isAssessmentRel(rel) {
      const ids = relEndList(rel, 'source').concat(relEndList(rel, 'target'));
      return ids.some(id => conceptDomain(id) === 'Assessment');
    }

    function dashColor(i) {
      return ['#6B7F6E', '#4A6FA5', '#A07840', '#6B5B8A', '#8B5E4A', '#4F7A62', '#7A8B6F', '#5C6B8A'][i % 8];
    }

    function svgDonut(parts, size) {
      const total = parts.reduce((s, p) => s + p.value, 0) || 1;
      const cx = size / 2, cy = size / 2, r = size * 0.34, sw = size * 0.16;
      let acc = 0;
      const circ = 2 * Math.PI * r;
      const rings = parts.map((p, i) => {
        const frac = p.value / total;
        const dash = frac * circ;
        const gap = circ - dash;
        const rot = (acc / total) * 360 - 90;
        acc += p.value;
        return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${p.color || dashColor(i)}" stroke-width="${sw}" stroke-dasharray="${dash} ${gap}" stroke-dashoffset="0" transform="rotate(${rot} ${cx} ${cy})"></circle>`;
      }).join('');
      return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" aria-hidden="true">${rings}<text x="${cx}" y="${cy - 2}" text-anchor="middle" font-size="15" font-weight="700" fill="currentColor">${total}</text><text x="${cx}" y="${cy + 14}" text-anchor="middle" font-size="10" fill="#8A7F72">tổng</text></svg>`;
    }

    function htmlBars(rows) {
      const max = Math.max(1, ...rows.map(r => r.value));
      return `<div class="dash-bars">${rows.map(r => `
        <div class="dash-bar-row" title="${escapeHtml(r.label)}: ${r.value}">
          <span>${escapeHtml(r.label)}</span>
          <div class="dash-bar-track"><em style="width:${Math.round(r.value / max * 100)}%;background:${r.color || 'var(--primary)'};"></em></div>
          <b>${r.value}</b>
        </div>`).join('')}</div>`;
    }

    function htmlLegend(parts) {
      const total = parts.reduce((s, p) => s + p.value, 0) || 1;
      return `<div class="dash-legend">${parts.map(p => {
        const pct = Math.round(p.value / total * 100);
        return `<span><i style="background:${p.color}"></i>${escapeHtml(p.label)} · ${p.value} (${pct}%)</span>`;
      }).join('')}</div>`;
    }

    function computeDashStats() {
      const concepts = KB_DATA.concepts || [];
      const relations = KB_DATA.relations || [];
      const assertions = KB_DATA.assertions || [];
      const instances = KB_DATA.instances || [];
      const dsa = concepts.filter(c => c.domain === 'DSA');
      const assess = concepts.filter(c => c.domain === 'Assessment');
      const tboxA = assertions.filter(a => !isABoxId(a.source) && !isABoxId(a.target));
      const aboxA = assertions.filter(a => isABoxId(a.source) || isABoxId(a.target));
      const qs = instances.filter(i => String(i.id || '').startsWith('I_Q_') || i.instanceOf === 'O_C_QUESTION');
      const eas = instances.filter(i => String(i.id || '').startsWith('I_EA_') || i.instanceOf === 'O_C_EXPECTED_ANSWER');
      const ers = instances.filter(i => String(i.id || '').startsWith('I_ER_') || i.instanceOf === 'O_C_EXPECTED_RULE');
      const qStats = { C1: 0, C2: 0, C3: 0, R: 0, U: 0, AP: 0, DES: 0, PRO: 0, APP: 0, E: 0, M: 0, H: 0 };
      qs.forEach(q => {
        const code = String(q.id || '').replace(/^I_/, '');
        const p = parseQuestionCode(code);
        if (p.chapter) qStats[p.chapter] += 1;
        if (p.bloom) qStats[p.bloom] += 1;
        if (p.type) qStats[p.type] += 1;
        if (p.diff) qStats[p.diff] += 1;
      });
      const relCount = {};
      tboxA.forEach(a => { relCount[a.relation] = (relCount[a.relation] || 0) + 1; });
      const topRels = Object.entries(relCount).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([id, n], i) => {
        const rel = relations.find(r => r.id === id);
        return { label: (rel && rel.name) || id.replace(/^REL_/, ''), value: n, color: dashColor(i), id };
      });
      const chapterTopics = {};
      tboxA.filter(a => a.relation === 'REL_CHAPTER_HAS_TOPIC').forEach(a => {
        chapterTopics[a.source] = (chapterTopics[a.source] || 0) + 1;
      });
      const erTargets = new Set(assertions.filter(a => a.relation === 'REL_EXPECTED_RULE_REQUIRES_CONCEPT').map(a => a.target));
      const dsaCovered = dsa.filter(c => erTargets.has(c.id)).length;
      const dsaRels = relations.filter(r => !isAssessmentRel(r));
      const assessRels = relations.filter(r => isAssessmentRel(r));
      return {
        concepts, dsa, assess, relations, dsaRels, assessRels, tboxA, aboxA, qs, eas, ers, qStats, topRels, chapterTopics, dsaCovered,
        hierarchy: (KB_DATA.hierarchy || []).length,
        rules: (KB_DATA.rules || []).length,
        functions: (KB_DATA.functions || []).length,
        operands: (KB_DATA.operands || []).length
      };
    }

    function renderDashboard() {
      const kpis = document.getElementById('dashKpis');
      const charts = document.getElementById('dashCharts');
      if (!kpis || !charts) return;
      const s = computeDashStats();
      kpis.innerHTML = [
        ['Khái niệm', s.concepts.length, `${s.dsa.length} DSA · ${s.assess.length} đánh giá`],
        ['Quan hệ gốc', s.relations.length, `${s.dsaRels.length} tri thức · ${s.assessRels.length} đánh giá`],
        ['Kế thừa subclassOf', s.hierarchy, 'cạnh T-Box'],
        ['Phán đoán T-Box', s.tboxA.length, `${s.aboxA.length} A-Box câu hỏi/EA`],
        ['Câu hỏi', s.qs.length, `${s.eas.length} lời giải · ${s.ers.length} luật chấm`],
        ['Luật miền', s.rules, `${s.functions} hàm · ${s.operands} toán hạng`],
        ['Topic / chương', Object.values(s.chapterTopics).reduce((a, b) => a + b, 0), 'REL_CHAPTER_HAS_TOPIC'],
        ['Concept được chấm', `${s.dsaCovered}/${s.dsa.length}`, 'có ER requiresConcept']
      ].map(([k, v, sub]) => `<div class="dash-kpi"><span>${k}</span><b>${v}</b><em>${sub}</em></div>`).join('');

      const domainParts = [
        { label: 'DSA', value: s.dsa.length, color: '#4A6FA5' },
        { label: 'Đánh giá', value: s.assess.length, color: '#A07840' }
      ];
      const boxParts = [
        { label: 'T-Box (O_C_ ↔ O_C_)', value: s.tboxA.length, color: '#6B5B8A' },
        { label: 'A-Box câu hỏi / EA / ER', value: s.aboxA.length, color: '#8B5E4A' }
      ];
      const instParts = [
        { label: 'Question', value: s.qs.length, color: '#4A6FA5' },
        { label: 'Expected Answer', value: s.eas.length, color: '#4F7A62' },
        { label: 'Expected Rule', value: s.ers.length, color: '#8B5E4A' }
      ];
      const coverParts = [
        { label: 'Có trong luật chấm', value: s.dsaCovered, color: '#6B7F6E' },
        { label: 'Chưa gắn ER', value: Math.max(0, s.dsa.length - s.dsaCovered), color: '#D6CBBA' }
      ];
      const chRows = [
        { label: 'Chương 1', value: s.qStats.C1, color: '#6B7F6E' },
        { label: 'Chương 2', value: s.qStats.C2, color: '#4A6FA5' },
        { label: 'Chương 3', value: s.qStats.C3, color: '#A07840' }
      ];
      const bloomRows = [
        { label: 'Remember', value: s.qStats.R, color: '#4A6FA5' },
        { label: 'Understand', value: s.qStats.U, color: '#6B7F6E' },
        { label: 'Apply', value: s.qStats.AP, color: '#A07840' }
      ];
      const typeRows = [
        { label: 'Descriptive', value: s.qStats.DES, color: '#6B5B8A' },
        { label: 'Procedure', value: s.qStats.PRO, color: '#4F7A62' },
        { label: 'Application', value: s.qStats.APP, color: '#8B5E4A' }
      ];
      const diffRows = [
        { label: 'Easy', value: s.qStats.E, color: '#6B7F6E' },
        { label: 'Medium', value: s.qStats.M, color: '#A07840' },
        { label: 'Hard', value: s.qStats.H, color: '#8B5E4A' }
      ];
      const topicRows = [
        { label: 'Tổng quan', value: s.chapterTopics.O_C_CHAPTER_OVERVIEW || 0, color: '#6B7F6E' },
        { label: 'Tìm kiếm & SX', value: s.chapterTopics.O_C_CHAPTER_SEARCHING_AND_SORTING || 0, color: '#4A6FA5' },
        { label: 'DSLK', value: s.chapterTopics.O_C_CHAPTER_LINKED_LIST || 0, color: '#A07840' }
      ];

      charts.innerHTML = `
        <div class="dash-card">
          <h3>Khái niệm theo miền</h3>
          <div class="dash-cap">T-Box: DSA là tri thức môn học, Đánh giá là schema đề thi.</div>
          <div class="dash-donut-wrap">${svgDonut(domainParts, 148)}${htmlLegend(domainParts)}</div>
        </div>
        <div class="dash-card">
          <h3>Phán đoán T-Box / A-Box</h3>
          <div class="dash-cap">A-Box là instance sinh khi tạo câu hỏi và lời giải mong đợi.</div>
          <div class="dash-donut-wrap">${svgDonut(boxParts, 148)}${htmlLegend(boxParts)}</div>
        </div>
        <div class="dash-card">
          <h3>Câu hỏi theo chương</h3>
          <div class="dash-cap">81 câu, phân theo prefix Q_C1 / C2 / C3.</div>
          ${htmlBars(chRows)}
        </div>
        <div class="dash-card">
          <h3>Bloom · dạng · độ khó</h3>
          <div class="dash-cap">Phân bố ngân hàng câu hỏi hiện có.</div>
          ${htmlBars(bloomRows)}
          <div style="height:0.55rem"></div>
          ${htmlBars(typeRows)}
          <div style="height:0.55rem"></div>
          ${htmlBars(diffRows)}
        </div>
        <div class="dash-card">
          <h3>Topic theo chương</h3>
          <div class="dash-cap">Số assertion REL_CHAPTER_HAS_TOPIC.</div>
          ${htmlBars(topicRows)}
        </div>
        <div class="dash-card">
          <h3>Quan hệ T-Box dùng nhiều nhất</h3>
          <div class="dash-cap">Chỉ đếm phán đoán giữa các O_C_, không gồm I_Q_/I_EA_/I_ER_.</div>
          ${htmlBars(s.topRels)}
        </div>
        <div class="dash-card">
          <h3>Instance đánh giá</h3>
          <div class="dash-cap">A-Box sinh từ câu hỏi / EA / ExpectedRule — không nằm trên sơ đồ cây.</div>
          <div class="dash-donut-wrap">${svgDonut(instParts, 148)}${htmlLegend(instParts)}</div>
        </div>
        <div class="dash-card">
          <h3>Phủ luật chấm trên DSA</h3>
          <div class="dash-cap">Khái niệm DSA được I_ER_ gắn qua requiresConcept.</div>
          <div class="dash-donut-wrap">${svgDonut(coverParts, 148)}${htmlLegend(coverParts)}</div>
        </div>
      `;
      renderOntoSchema();
      renderOntoTree();
      renderOntoRelPanel();
    }

    function setOntoFilter(mode) {
      ontoFilter = mode;
      ['dsa', 'assessment', 'all'].forEach(m => {
        const el = document.getElementById('dashFilter' + (m === 'dsa' ? 'Dsa' : m === 'assessment' ? 'Assess' : 'All'));
        if (el) el.classList.toggle('active', m === mode);
      });
      ontoExpandAllFlag = null;
      ontoOpenIds = new Set();
      renderOntoSchema();
      renderOntoTree();
      renderOntoRelPanel();
    }

    function ontoAllowConcept(c) {
      if (!c) return false;
      if (ontoFilter === 'dsa') return c.domain === 'DSA';
      if (ontoFilter === 'assessment') return c.domain === 'Assessment';
      return true;
    }

    function ontoRootId(id, parentOf) {
      let cur = id, guard = 0;
      while (parentOf[cur] && guard < 40) {
        cur = parentOf[cur];
        guard += 1;
      }
      return cur;
    }

    function renderOntoSchema() {
      const host = document.getElementById('dashSchemaSvg');
      if (!host) return;
      const { parentOf, childrenOf } = hierarchyIndex();
      const allowed = new Set((KB_DATA.concepts || []).filter(ontoAllowConcept).map(c => c.id));
      const roots = (KB_DATA.concepts || []).filter(c => ontoAllowConcept(c) && !parentOf[c.id]).sort((a, b) => conceptLabel(a).localeCompare(conceptLabel(b), 'vi'));
      const relBySrc = {};
      (KB_DATA.relations || []).forEach(rel => {
        relEndList(rel, 'source').forEach(src => {
          relBySrc[src] = (relBySrc[src] || 0) + 1;
        });
      });
      host.innerHTML = `<div class="dash-roots">${roots.map(c => {
        const nChild = (childrenOf[c.id] || []).filter(id => allowed.has(id)).length;
        const nRel = relBySrc[c.id] || 0;
        const active = ontoSelectedId === c.id ? ' active' : '';
        return `<button type="button" class="dash-root${active}" onclick="selectOntoNode('${c.id}')">
          <b>${escapeHtml(conceptLabel(c) || c.id)}</b>
          <span>${nChild} lớp con${nRel ? ' · ' + nRel + ' quan hệ gốc' : ''}</span>
        </button>`;
      }).join('')}</div>`;
    }

    function ontoMatchQuery(c, q) {
      if (!q) return true;
      const blob = foldText([c.id, conceptLabel(c), attrVal(c, 'description')].join(' '));
      return blob.includes(q);
    }

    function ontoExpandAll(open) {
      ontoExpandAllFlag = open;
      ontoOpenIds = new Set();
      if (open) {
        (KB_DATA.concepts || []).forEach(c => { if (ontoAllowConcept(c)) ontoOpenIds.add(c.id); });
      }
      renderOntoTree();
    }

    function selectOntoNode(id) {
      ontoSelectedId = id || null;
      renderOntoSchema();
      renderOntoTree();
      renderOntoRelPanel();
      const el = document.querySelector('.onto-node.active');
      if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
    }

    function renderOntoTree() {
      const host = document.getElementById('dashTree');
      if (!host) return;
      const q = foldText((document.getElementById('dashTreeSearch') || {}).value || '');
      const { parentOf, childrenOf } = hierarchyIndex();
      const allowed = (KB_DATA.concepts || []).filter(ontoAllowConcept);
      const allowedIds = new Set(allowed.map(c => c.id));
      const relBySrc = {};
      (KB_DATA.relations || []).forEach(rel => {
        relEndList(rel, 'source').forEach(src => {
          if (!relBySrc[src]) relBySrc[src] = [];
          relBySrc[src].push(rel);
        });
      });

      const matchIds = new Set();
      if (q) {
        allowed.forEach(c => { if (ontoMatchQuery(c, q)) matchIds.add(c.id); });
        matchIds.forEach(id => {
          let cur = parentOf[id];
          while (cur) { matchIds.add(cur); cur = parentOf[cur]; }
        });
      }

      const roots = allowed.filter(c => !parentOf[c.id] || !allowedIds.has(parentOf[c.id]))
        .sort((a, b) => conceptLabel(a).localeCompare(conceptLabel(b), 'vi'));

      function subtreeCount(id) {
        let n = 1;
        (childrenOf[id] || []).forEach(ch => { if (allowedIds.has(ch)) n += subtreeCount(ch); });
        return n;
      }

      function isOpen(id, depth) {
        if (q) return matchIds.has(id);
        if (ontoExpandAllFlag === true) return true;
        if (ontoExpandAllFlag === false) return false;
        if (ontoOpenIds.has(id)) return true;
        if (ontoSelectedId) {
          let cur = parentOf[ontoSelectedId];
          while (cur) {
            if (cur === id) return true;
            cur = parentOf[cur];
          }
        }
        return depth < 1;
      }

      function renderNode(id, depth) {
        const c = conceptById(id);
        if (!c || !allowedIds.has(id)) return '';
        if (q && !matchIds.has(id)) return '';
        const kids = (childrenOf[id] || []).filter(k => allowedIds.has(k)).sort();
        const open = isOpen(id, depth) && kids.length > 0;
        const nRel = (relBySrc[id] || []).length;
        const childHtml = open ? `<ul>${kids.map(k => renderNode(k, depth + 1)).join('')}</ul>` : '';
        return `<li>
          <div class="onto-row">
            <button class="onto-toggle${kids.length ? '' : ' leaf'}" onclick="event.stopPropagation(); ontoToggleNode('${id}')">${open ? '▾' : '▸'}</button>
            <button class="onto-node${ontoSelectedId === id ? ' active' : ''}" onclick="selectOntoNode('${id}')">
              <span class="nm">${escapeHtml(conceptLabel(c) || id)}</span>
              <span class="id">${escapeHtml(id)}</span>
              ${nRel ? `<span class="cnt">${nRel} quan hệ</span>` : ''}
            </button>
          </div>
          ${childHtml}
        </li>`;
      }

      const visibleRoots = q ? roots.filter(c => matchIds.has(c.id)) : roots;
      host.innerHTML = `<ul class="onto-tree">${visibleRoots.map(c => renderNode(c.id, 0)).join('')}</ul>
        <div class="dash-cap" style="padding:0.45rem 0.35rem 0;">${allowed.length} khái niệm · ${roots.length} gốc · không gồm instance câu hỏi/EA</div>`;
    }

    function ontoToggleNode(id) {
      ontoExpandAllFlag = null;
      if (ontoOpenIds.has(id)) ontoOpenIds.delete(id);
      else ontoOpenIds.add(id);
      renderOntoTree();
    }

    function renderOntoRelPanel() {
      const relHost = document.getElementById('dashRelList');
      const detHost = document.getElementById('dashNodeDetail');
      if (!relHost || !detHost) return;
      const { parentOf, childrenOf } = hierarchyIndex();
      const allowedIds = new Set((KB_DATA.concepts || []).filter(ontoAllowConcept).map(c => c.id));
      const rels = (KB_DATA.relations || []).filter(r => {
        const srcs = relEndList(r, 'source');
        const tgts = relEndList(r, 'target');
        if (ontoFilter === 'dsa') return srcs.every(id => conceptDomain(id) === 'DSA') && tgts.every(id => conceptDomain(id) === 'DSA');
        if (ontoFilter === 'assessment') return isAssessmentRel(r);
        return true;
      });

      const grouped = {};
      rels.forEach(rel => {
        relEndList(rel, 'source').forEach(src => {
          if (!grouped[src]) grouped[src] = [];
          grouped[src].push(rel);
        });
      });

      function chip(id) {
        return `<button class="onto-chip" type="button" onclick="selectOntoNode('${id}')">${escapeHtml(conceptLabel(conceptById(id)) || id)}</button>`;
      }

      if (ontoSelectedId && conceptById(ontoSelectedId)) {
        const c = conceptById(ontoSelectedId);
        const parent = parentOf[c.id];
        const kids = (childrenOf[c.id] || []).filter(id => allowedIds.has(id));
        const directOut = rels.filter(r => relEndList(r, 'source').includes(c.id));
        const directIn = rels.filter(r => relEndList(r, 'target').includes(c.id));
        const tboxHits = (KB_DATA.assertions || []).filter(a => !isABoxId(a.source) && !isABoxId(a.target) && (a.source === c.id || a.target === c.id));
        detHost.innerHTML = `
          <div class="dash-card" style="box-shadow:none;">
            <h3>${escapeHtml(conceptLabel(c) || c.id)}</h3>
            <div class="dash-cap">${escapeHtml(c.id)} · ${escapeHtml(c.domain || '')}</div>
            ${parent ? `<div class="dash-cap">Lớp cha: ${chip(parent)}</div>` : '<div class="dash-cap">Lớp gốc</div>'}
            ${kids.length ? `<div class="q-section-label">Lớp con (${kids.length})</div><div>${kids.map(chip).join(' ')}</div>` : ''}
            <div class="q-section-label">Quan hệ gốc đi ra (${directOut.length})</div>
            ${directOut.map(r => `<div class="onto-rel-line">${chip(c.id)} <b>${escapeHtml(r.name)}</b> ${relEndList(r, 'target').map(chip).join(' ')}</div>`).join('') || '<div class="dash-detail-empty">Không có quan hệ gốc đi ra.</div>'}
            <div class="q-section-label">Quan hệ gốc đi vào (${directIn.length})</div>
            ${directIn.map(r => `<div class="onto-rel-line">${relEndList(r, 'source').map(chip).join(' ')} <b>${escapeHtml(r.name)}</b> ${chip(c.id)}</div>`).join('') || '<div class="dash-detail-empty">Không có quan hệ gốc đi vào.</div>'}
            <div class="q-section-label">Assertion T-Box (${tboxHits.length})</div>
            <div class="dash-cap">Chỉ O_C_ ↔ O_C_, đã loại instance câu hỏi/EA.</div>
            ${tboxHits.slice(0, 12).map(a => `<div class="onto-rel-line">${chip(a.source)} <b>${escapeHtml((KB_DATA.relations.find(r => r.id === a.relation) || {}).name || a.relation)}</b> ${chip(a.target)}</div>`).join('') || '<div class="dash-detail-empty">Chưa có assertion T-Box.</div>'}
            ${tboxHits.length > 12 ? `<div class="dash-cap">… ${tboxHits.length - 12} assertion nữa</div>` : ''}
            <div style="margin-top:0.7rem;"><button class="btn" type="button" onclick="jumpToConceptFromDash('${c.id}')">Mở trong Kiểm tra dữ liệu</button></div>
          </div>`;
      } else {
        detHost.innerHTML = '<div class="dash-detail-empty">Chọn một khái niệm trên cây hoặc sơ đồ gốc để xem chi tiết. Bên dưới là toàn bộ quan hệ gốc (định nghĩa REL_*), không gồm instance câu hỏi/EA.</div>';
      }

      const srcIds = Object.keys(grouped).filter(id => allowedIds.has(id) || grouped[id].length).sort((a, b) => (conceptLabel(conceptById(a)) || a).localeCompare(conceptLabel(conceptById(b)) || b, 'vi'));
      if (ontoSelectedId) {
        relHost.innerHTML = `<button class="btn" type="button" onclick="selectOntoNode('')" style="margin:0.35rem 0 0.7rem;">← Tất cả quan hệ gốc</button>`;
      } else {
        relHost.innerHTML = `
        <div class="dash-card" style="box-shadow:none;margin-bottom:0.7rem;">
          <h3>Quan hệ gốc</h3>
          <div class="dash-cap">${rels.length} định nghĩa REL_* trong phạm vi đang lọc.</div>
          ${srcIds.map(src => `
            <div class="onto-rel-group">
              <h4>${escapeHtml(conceptLabel(conceptById(src)) || src)}</h4>
              ${grouped[src].map(r => `<div class="onto-rel-line">${chip(src)} <b>${escapeHtml(r.name)}</b> ${relEndList(r, 'target').map(chip).join(' ')}</div>`).join('')}
            </div>`).join('') || '<div class="dash-detail-empty">Không có quan hệ gốc.</div>'}
        </div>`;
      }
    }

    function jumpToConceptFromDash(id) {
      switchView('inspector');
      selectDataset('concepts');
      const search = document.getElementById('searchInput');
      if (search) search.value = id;
      applyFilters();
    }

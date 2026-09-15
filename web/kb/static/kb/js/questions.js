    // QUESTION + EXPECTED ANSWER EXPLORER
    // =========================================================================
    var selectedQuestionId = null;
    var qRetrievalActive = false;
    var qPanelMode = 'question';
    var selectedBranchNodeId = null;
    var RETRIEVE_LIMIT = 10;
    var RETRIEVE_MIN_SCORE = 0.70;
    var RETRIEVE_CONCEPT_W = 0.62;
    var RETRIEVE_TEXT_W = 0.38;
    var WEIGHT_PALETTE = ['#6B7F6E', '#4A6FA5', '#A07840', '#6B5B8A', '#8B5E4A', '#4F7A62'];
    var Q_CHAPTER = {
      C1: 'Chương 1 · Tổng quan CTDL&GT',
      C2: 'Chương 2 · Tìm kiếm và sắp xếp',
      C3: 'Chương 3 · Danh sách liên kết'
    };
    var Q_CHAPTER_CONCEPT = {
      C1: 'O_C_CHAPTER_OVERVIEW',
      C2: 'O_C_CHAPTER_SEARCHING_AND_SORTING',
      C3: 'O_C_CHAPTER_LINKED_LIST'
    };
    var Q_BLOOM = { R: 'remember', U: 'understand', AP: 'apply' };
    var Q_TYPE = { DES: 'descriptive', PRO: 'procedure', APP: 'application' };
    var Q_DIFF = { E: 'easy', M: 'medium', H: 'hard' };
    var Q_STOPWORDS = new Set(['la','cua','va','mot','cac','trong','voi','khi','thi','cho','den','tu','nay','do','duoc','co','khong','hay','mo','ta','the','nao','ve','nhung','neu','hoac','tren','duoi','sau','truoc','bang','deu','a','an','of','and','or','to','in','on','for','is','are','be','by','with','from']);

    function escapeHtml(s) {
      if (s == null) return '';
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    function instById(id) {
      return (KB_DATA.instances || []).find(i => i.id === id) || null;
    }

    function conceptById(id) {
      return (KB_DATA.concepts || []).find(c => c.id === id) || null;
    }

    function ruleById(id) {
      return (KB_DATA.rules || []).find(r => r.id === id) || null;
    }

    function fnById(id) {
      return (KB_DATA.functions || []).find(f => f.id === id) || null;
    }

    function attrVal(obj, name) {
      if (!obj || !Array.isArray(obj.attributes)) return null;
      const a = obj.attributes.find(x => x && x.name === name);
      return a ? (a.value != null ? a.value : a.default) : null;
    }

    function assertionsOf(source, rel) {
      return (KB_DATA.assertions || []).filter(a => a.source === source && (!rel || a.relation === rel));
    }

    function parseQuestionCode(qid) {
      const m = String(qid || '').match(/^Q_(C[123])_(R|U|AP)_(DES|PRO|APP)_(E|M|H)$/);
      if (!m) return { chapter: '', bloom: '', type: '', diff: '' };
      return { chapter: m[1], bloom: m[2], type: m[3], diff: m[4] };
    }

    function foldText(s) {
      return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function questionTokens(text) {
      const toks = new Set();
      const matches = String(text || '').match(/[0-9a-zA-Z_àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+/gi) || [];
      matches.forEach(raw => {
        const folded = foldText(raw);
        if (folded.length >= 2 && !Q_STOPWORDS.has(folded)) toks.add(folded);
      });
      return toks;
    }

    function hierarchyIndex() {
      const parentOf = {};
      const childrenOf = {};
      (KB_DATA.hierarchy || []).forEach(h => {
        const sub = h.subclass || h.subclassOf;
        const sup = h.superclass || h.parent;
        if (!sub || !sup) return;
        parentOf[sub] = sup;
        if (!childrenOf[sup]) childrenOf[sup] = [];
        childrenOf[sup].push(sub);
      });
      return { parentOf, childrenOf };
    }

    function conceptTextBlob(cid) {
      const c = conceptById(cid);
      return [cid, conceptLabel(c) || '', attrVal(c, 'description') || ''].join(' ');
    }

    function topicBranchFrom(topicId) {
      if (!topicId) return null;
      const { parentOf, childrenOf } = hierarchyIndex();
      const ancestors = [];
      const descendants = [];
      const seen = new Set([topicId]);
      let cur = parentOf[topicId];
      let depth = 1;
      while (cur && !seen.has(cur)) {
        seen.add(cur);
        ancestors.push({ id: cur, name: conceptLabel(conceptById(cur)) || cur, depth });
        cur = parentOf[cur];
        depth += 1;
      }
      const stack = (childrenOf[topicId] || []).slice();
      while (stack.length) {
        const node = stack.pop();
        if (seen.has(node)) continue;
        seen.add(node);
        descendants.push({
          id: node,
          name: conceptLabel(conceptById(node)) || node,
          parent: parentOf[node] || ''
        });
        (childrenOf[node] || []).forEach(ch => stack.push(ch));
      }
      descendants.sort((a, b) => a.id.localeCompare(b.id));
      return {
        topic_id: topicId,
        topic_name: conceptLabel(conceptById(topicId)) || topicId,
        ancestors,
        descendants,
        branch_ids: [topicId].concat(ancestors.map(a => a.id), descendants.map(d => d.id))
      };
    }

    function populateTopicFilter() {
      const sel = document.getElementById('qFilterTopic');
      if (!sel) return;
      const prev = sel.value || 'all';
      const grouped = { C1: [], C2: [], C3: [], other: [] };
      const seen = new Set();
      const { childrenOf } = hierarchyIndex();
      function walkDesc(id, acc) {
        (childrenOf[id] || []).forEach(ch => {
          if (acc.has(ch)) return;
          acc.add(ch);
          walkDesc(ch, acc);
        });
      }
      (KB_DATA.assertions || []).forEach(a => {
        if (a.relation !== 'REL_CHAPTER_HAS_TOPIC' || !a.target) return;
        const chKey = Object.keys(Q_CHAPTER_CONCEPT).find(k => Q_CHAPTER_CONCEPT[k] === a.source) || 'other';
        const ids = new Set([a.target]);
        walkDesc(a.target, ids);
        ids.forEach(cid => {
          if (seen.has(cid)) return;
          seen.add(cid);
          (grouped[chKey] || grouped.other).push(cid);
        });
      });
      let html = '<option value="all">Mọi topic</option>';
      [['C1', 'Chương 1'], ['C2', 'Chương 2'], ['C3', 'Chương 3'], ['other', 'Khác']].forEach(([key, label]) => {
        const arr = grouped[key] || [];
        if (!arr.length) return;
        arr.sort((a, b) => (conceptLabel(conceptById(a)) || a).localeCompare(conceptLabel(conceptById(b)) || b, 'vi'));
        html += `<optgroup label="${label}">`;
        arr.forEach(cid => {
          const name = conceptLabel(conceptById(cid)) || cid;
          html += `<option value="${escapeHtml(cid)}">${escapeHtml(name)}</option>`;
        });
        html += '</optgroup>';
      });
      sel.innerHTML = html;
      if ([...sel.options].some(o => o.value === prev)) sel.value = prev;
    }

    function scoreQuestionAgainstBranch(q, branch) {
      if (!branch) {
        return { score: 1, concept_score: 1, text_score: 1, matched_concepts: q.concepts || [] };
      }
      const topic = branch.topic_id;
      const ancestors = new Set(branch.ancestors.map(a => a.id));
      const descendants = new Set(branch.descendants.map(d => d.id));
      const concepts = q.concepts || [];
      let best = 0;
      const matched = [];
      concepts.forEach(cid => {
        if (cid === topic) { best = Math.max(best, 1); matched.push(cid); }
        else if (descendants.has(cid)) { best = Math.max(best, 0.88); matched.push(cid); }
        else if (ancestors.has(cid)) { best = Math.max(best, 0.58); matched.push(cid); }
      });
      const overlap = matched.length ? (new Set(matched).size / Math.max(new Set(concepts).size, 1)) : 0;
      const conceptScore = matched.length ? (0.85 * best) + (0.15 * overlap) : 0;

      const topicTokens = new Set();
      branch.branch_ids.forEach(cid => {
        questionTokens(conceptTextBlob(cid)).forEach(t => topicTokens.add(t));
      });
      const qTokens = q.tokens || new Set();
      let textScore = 0;
      if (qTokens.size && topicTokens.size) {
        let inter = 0;
        qTokens.forEach(t => { if (topicTokens.has(t)) inter += 1; });
        const union = qTokens.size + topicTokens.size - inter;
        const jaccard = inter / Math.max(union, 1);
        const overlap = inter / Math.max(topicTokens.size, 1);
        textScore = (0.55 * jaccard) + (0.45 * overlap);
      }
      return {
        score: (RETRIEVE_CONCEPT_W * conceptScore) + (RETRIEVE_TEXT_W * textScore),
        concept_score: conceptScore,
        text_score: textScore,
        matched_concepts: matched
      };
    }

    function questionIdFromInstance(instId) {
      const s = String(instId || '');
      if (s.startsWith('I_Q_')) return s.slice(2);
      const er = s.match(/^I_ER_(Q_.+)_(\\d+)$/);
      if (er) return er[1];
      if (s.startsWith('I_EA_')) return s.replace(/^I_EA_/, '');
      return null;
    }

    function jumpToInspector(dataset, query) {
      switchView('inspector');
      selectDataset(dataset);
      if (query) {
        const search = document.getElementById('searchInput');
        if (search) search.value = query;
        applyFilters();
      }
    }

    function openQuestionFromInstance(instId) {
      const qid = questionIdFromInstance(instId);
      selectedQuestionId = qid;
      switchView('questions');
    }

    function collectQuestions() {
      return (KB_DATA.instances || [])
        .filter(i => i.instanceOf === 'O_C_QUESTION')
        .map(inst => {
          const qid = attrVal(inst, 'name') || inst.id.replace(/^I_/, '');
          const meta = parseQuestionCode(qid);
          const typeA = assertionsOf(inst.id, 'REL_QUESTION_HAS_QUESTION_TYPE')[0];
          const diffA = assertionsOf(inst.id, 'REL_QUESTION_HAS_DIFFICULTY')[0];
          const bloomA = assertionsOf(inst.id, 'REL_QUESTION_HAS_BLOOM_LEVEL')[0];
          const eaA = assertionsOf(inst.id, 'REL_QUESTION_HAS_EXPECTED_ANSWER')[0];
          const typeC = typeA ? conceptById(typeA.target) : null;
          const diffC = diffA ? conceptById(diffA.target) : null;
          const bloomC = bloomA ? conceptById(bloomA.target) : null;
          const concepts = [];
          const erText = [];
          if (eaA && eaA.target) {
            assertionsOf(eaA.target, 'REL_EXPECTED_ANSWER_HAS_SCORING_RULE').forEach(scoreA => {
              const er = instById(scoreA.target);
              if (er) {
                erText.push(attrVal(er, 'name') || '');
                erText.push(attrVal(er, 'missExplanation') || '');
              }
              assertionsOf(scoreA.target, 'REL_EXPECTED_RULE_REQUIRES_CONCEPT').forEach(req => {
                if (req.target) concepts.push(req.target);
              });
            });
          }
          const uniqConcepts = [...new Set(concepts)];
          const eaInst = eaA ? instById(eaA.target) : null;
          const content = attrVal(inst, 'content') || '';
          const blob = [qid, content, attrVal(eaInst, 'description') || '', ...erText, ...uniqConcepts.map(cid => conceptLabel(conceptById(cid)) || cid)].join(' ');
          return {
            inst,
            qid,
            content,
            chapter: meta.chapter,
            bloom: meta.bloom,
            type: meta.type,
            diff: meta.diff,
            typeLabel: attrVal(typeC, 'name') || Q_TYPE[meta.type] || '',
            diffLabel: attrVal(diffC, 'name') || Q_DIFF[meta.diff] || '',
            bloomLabel: attrVal(bloomC, 'name') || Q_BLOOM[meta.bloom] || '',
            typeId: typeA ? typeA.target : '',
            diffId: diffA ? diffA.target : '',
            bloomId: bloomA ? bloomA.target : '',
            eaId: eaA ? eaA.target : null,
            concepts: uniqConcepts,
            tokens: questionTokens(blob)
          };
        })
        .sort((a, b) => {
          const ch = { C1: 0, C2: 1, C3: 2 };
          const bl = { R: 0, U: 1, AP: 2 };
          const ty = { DES: 0, PRO: 1, APP: 2 };
          const df = { E: 0, M: 1, H: 2 };
          return (ch[a.chapter] - ch[b.chapter])
            || (bl[a.bloom] - bl[b.bloom])
            || (ty[a.type] - ty[b.type])
            || (df[a.diff] - df[b.diff])
            || a.qid.localeCompare(b.qid);
        });
    }

    function filterQuestionList() {
      renderQuestionExplorer(true);
    }

    function onTopicFilterChange() {
      const topic = document.getElementById('qFilterTopic')?.value || 'all';
      qRetrievalActive = topic !== 'all';
      selectedBranchNodeId = (topic !== 'all') ? topic : null;
      if (topic === 'all') qPanelMode = 'question';
      renderQuestionExplorer(true);
    }

    function runQuestionRetrieval() {
      qRetrievalActive = true;
      const topic = document.getElementById('qFilterTopic')?.value || 'all';
      if (topic !== 'all') selectedBranchNodeId = topic;
      renderQuestionExplorer(true);
    }

    function clearQuestionRetrieval() {
      qRetrievalActive = false;
      qPanelMode = 'question';
      selectedBranchNodeId = null;
      const topic = document.getElementById('qFilterTopic');
      if (topic) topic.value = 'all';
      renderQuestionExplorer(true);
    }

    function selectBranchView() {
      const topic = document.getElementById('qFilterTopic')?.value || 'all';
      if (!qRetrievalActive || topic === 'all') return;
      qPanelMode = 'branch';
      if (!selectedBranchNodeId) selectedBranchNodeId = topic;
      renderQuestionExplorer(true);
    }

    function selectBranchNode(cid) {
      qPanelMode = 'branch';
      selectedBranchNodeId = cid;
      renderQuestionExplorer(true);
    }

    function relationById(id) {
      return (KB_DATA.relations || []).find(r => r.id === id) || null;
    }

    function formatOpSignature(op) {
      if (!op) return '';
      if (typeof op === 'string') return op;
      const fmt = (p) => {
        if (!p) return '';
        const t = p.valueType || p.value_type || 'any';
        return `${p.name}: ${t}`;
      };
      const inputs = (op.input || []).map(fmt).join(', ');
      const out = op.output
        ? (Array.isArray(op.output) ? op.output.map(fmt).join(', ') : fmt(op.output))
        : 'void';
      return `${op.name || 'op'}(${inputs}) → ${out}`;
    }

    function ellipsize(s, n) {
      const t = String(s || '');
      return t.length > n ? t.slice(0, n - 1) + '…' : t;
    }

    function layoutTopicTree(branch) {
      const { parentOf, childrenOf } = hierarchyIndex();
      const branchSet = new Set(branch.branch_ids);
      const topic = branch.topic_id;
      const ancestorChain = branch.ancestors.slice().reverse().map(a => a.id);
      const levels = ancestorChain.map(id => [id]);
      levels.push([topic]);
      const depthOf = {};
      ancestorChain.forEach((id, i) => { depthOf[id] = i; });
      depthOf[topic] = ancestorChain.length;
      const queue = [topic];
      while (queue.length) {
        const n = queue.shift();
        (childrenOf[n] || []).filter(c => branchSet.has(c)).forEach(c => {
          if (depthOf[c] != null) return;
          depthOf[c] = depthOf[n] + 1;
          queue.push(c);
        });
      }
      const maxD = Math.max.apply(null, Object.values(depthOf));
      for (let d = ancestorChain.length + 1; d <= maxD; d++) {
        const row = branch.branch_ids.filter(id => depthOf[id] === d);
        if (row.length) levels.push(row);
      }
      const NODE_W = 168, NODE_H = 46, GAP_X = 18, GAP_Y = 50, PAD = 18;
      const maxCols = Math.max.apply(null, levels.map(l => l.length).concat([1]));
      const width = Math.max(PAD * 2 + maxCols * NODE_W + (maxCols - 1) * GAP_X, 380);
      const height = PAD * 2 + levels.length * NODE_H + Math.max(levels.length - 1, 0) * GAP_Y;
      const pos = {};
      levels.forEach((ids, li) => {
        const rowW = ids.length * NODE_W + Math.max(ids.length - 1, 0) * GAP_X;
        let x = (width - rowW) / 2;
        const y = PAD + li * (NODE_H + GAP_Y);
        ids.forEach(id => {
          pos[id] = { x, y, w: NODE_W, h: NODE_H };
          x += NODE_W + GAP_X;
        });
      });
      const edges = [];
      branch.branch_ids.forEach(id => {
        const p = parentOf[id];
        if (p && branchSet.has(p) && pos[p] && pos[id]) edges.push({ from: p, to: id });
      });
      return { width, height, pos, edges, NODE_W, NODE_H, ancestorChain };
    }

    function renderTopicTreeSvg(branch) {
      const layout = layoutTopicTree(branch);
      const topic = branch.topic_id;
      const ancestorIds = new Set(branch.ancestors.map(a => a.id));
      const descendantIds = new Set(branch.descendants.map(d => d.id));
      const selected = selectedBranchNodeId && layout.pos[selectedBranchNodeId]
        ? selectedBranchNodeId
        : topic;
      const marker = `
        <defs>
          <marker id="qTreeArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"></path>
          </marker>
        </defs>`;
      const edgeHtml = layout.edges.map(e => {
        const a = layout.pos[e.from], b = layout.pos[e.to];
        const x1 = a.x + a.w / 2, y1 = a.y + a.h;
        const x2 = b.x + b.w / 2, y2 = b.y;
        const mid = (y1 + y2) / 2;
        return `<path class="q-tree-edge" d="M ${x1} ${y1} C ${x1} ${mid}, ${x2} ${mid}, ${x2} ${y2}" marker-end="url(#qTreeArrow)"></path>`;
      }).join('');
      const nodeHtml = Object.keys(layout.pos).map(id => {
        const p = layout.pos[id];
        const c = conceptById(id);
        const name = conceptLabel(c) || id;
        let role = 'node';
        if (id === topic) role = 'topic';
        else if (ancestorIds.has(id)) role = 'ancestor';
        else if (descendantIds.has(id)) role = 'descendant';
        const sel = id === selected ? ' selected' : '';
        return `
          <g class="q-tree-node ${role}${sel}" onclick="selectBranchNode('${id}')">
            <title>${escapeHtml(name)} · ${escapeHtml(id)}</title>
            <rect x="${p.x}" y="${p.y}" rx="9" ry="9" width="${p.w}" height="${p.h}"></rect>
            <text class="nm" x="${p.x + p.w / 2}" y="${p.y + 19}" text-anchor="middle">${escapeHtml(ellipsize(name, 22))}</text>
            <text class="id" x="${p.x + p.w / 2}" y="${p.y + 34}" text-anchor="middle">${escapeHtml(ellipsize(id.replace(/^O_C_/, ''), 20))}</text>
          </g>`;
      }).join('');
      return `
        <div class="q-tree-wrap">
          <svg viewBox="0 0 ${layout.width} ${layout.height}" width="${layout.width}" height="${layout.height}" style="color: var(--subclass-color); display: block; margin: 0 auto;">
            ${marker}${edgeHtml}${nodeHtml}
          </svg>
        </div>
        <div class="q-tree-legend">
          <span><i style="background: var(--subclass-bg); border-color: var(--subclass-border);"></i>Lớp cha (truy hồi ngược)</span>
          <span><i style="background: color-mix(in srgb, var(--primary) 16%, var(--bg-card)); border-color: var(--primary);"></i>Topic đang chọn</span>
          <span><i style="background: var(--concept-bg); border-color: var(--concept-border);"></i>Lớp con</span>
          <span>Cạnh = subclassOf · nhấp node để xem chi tiết</span>
        </div>`;
    }

    function renderBranchConceptFacts(cid, branch) {
      const c = conceptById(cid);
      const name = conceptLabel(c) || cid;
      const desc = attrVal(c, 'description') || '';
      const parent = c && (c.subclassOf || c.subclass_of);
      const attrs = (c && Array.isArray(c.attributes)) ? c.attributes : [];
      const ops = (c && Array.isArray(c.operation)) ? c.operation : [];
      const invs = (c && Array.isArray(c.invariant)) ? c.invariant : [];
      const branchSet = new Set(branch.branch_ids);
      const isConceptId = (id) => !!(id && conceptById(id));
      const outgoing = (KB_DATA.assertions || []).filter(a => a.source === cid && isConceptId(a.target));
      const incoming = (KB_DATA.assertions || []).filter(a => a.target === cid && a.source !== cid && isConceptId(a.source));
      const attrHtml = attrs.length
        ? attrs.map(a => {
            const val = (a.value != null && a.value !== '') ? a.value : a.default;
            const extra = val != null && val !== '' ? ` = ${val}` : '';
            return `<div class="q-rel-line"><b>${escapeHtml(a.name || '')}</b> : ${escapeHtml(a.value_type || 'any')}${escapeHtml(String(extra))}${a.required ? ' · bắt buộc' : ''}</div>`;
          }).join('')
        : '<span class="q-item-meta">Không khai báo thuộc tính.</span>';
      const opHtml = ops.length
        ? ops.map(op => `<div class="q-rel-line">${escapeHtml(formatOpSignature(op))}${op && op.description ? `<div class="q-item-meta">${escapeHtml(op.description)}</div>` : ''}</div>`).join('')
        : '<span class="q-item-meta">Không có operation.</span>';
      const invHtml = invs.length
        ? invs.map(inv => `<div class="q-rel-line">${typeof inv === 'string' ? escapeHtml(inv) : escapeHtml(inv.name || '') + (inv.description ? ' — ' + escapeHtml(inv.description) : '')}</div>`).join('')
        : '';
      const relLine = (a, dir) => {
        const rel = relationById(a.relation);
        const relName = (rel && rel.name) || a.relation;
        const other = dir === 'out' ? a.target : a.source;
        const otherC = conceptById(other);
        const otherName = conceptLabel(otherC) || other;
        const inBranch = branchSet.has(other);
        const otherClick = inBranch
          ? `selectBranchNode('${other}')`
          : `jumpToInspector('concepts','${other}')`;
        const selfName = conceptLabel(conceptById(cid)) || cid;
        return `<div class="q-rel-line">${dir === 'out' ? escapeHtml(selfName) : escapeHtml(otherName)} <b>${escapeHtml(relName)}</b> ${dir === 'out' ? escapeHtml(otherName) : escapeHtml(selfName)}${inBranch ? ' · trong nhánh' : ''} ${pill('relation', `<code>${escapeHtml(a.relation)}</code>`, `jumpToInspector('relations','${a.relation}')`)} ${pill('concept', `<code>${escapeHtml(other)}</code>`, otherClick)}</div>`;
      };
      const outHtml = outgoing.length
        ? outgoing.map(a => relLine(a, 'out')).join('')
        : '<span class="q-item-meta">Không có assertion đi ra.</span>';
      const inHtml = incoming.length
        ? incoming.slice(0, 24).map(a => relLine(a, 'in')).join('') + (incoming.length > 24 ? `<div class="q-item-meta">… còn ${incoming.length - 24} assertion</div>` : '')
        : '<span class="q-item-meta">Không có assertion đi vào.</span>';
      const role = cid === branch.topic_id ? 'Topic' : (branch.ancestors.some(a => a.id === cid) ? 'Lớp cha' : 'Lớp con');
      return `
        <section class="q-hero">
          <div class="q-kicker">Thực thể trong nhánh · ${escapeHtml(role)}</div>
          <div class="q-hero-id">${escapeHtml(name)}</div>
          <div class="q-pills">
            ${pill('concept', `<code>${escapeHtml(cid)}</code>`, `jumpToInspector('concepts','${cid}')`)}
            ${c && c.domain ? pill('instance', `miền ${escapeHtml(c.domain)}`) : ''}
            ${parent ? pill('fn', `subclassOf ${escapeHtml(parent)}`, `selectBranchNode('${parent}')`) : pill('fn', 'lớp gốc')}
          </div>
          ${desc ? `<div class="q-content">${escapeHtml(desc)}</div>` : ''}
        </section>
        <div class="q-section-label">Thuộc tính (${attrs.length})</div>
        <div class="q-fact">${attrHtml}</div>
        <div class="q-section-label">Operation (${ops.length})</div>
        <div class="q-fact">${opHtml}</div>
        ${invHtml ? `<div class="q-section-label">Invariant</div><div class="q-fact">${invHtml}</div>` : ''}
        <div class="q-section-label">Quan hệ đi ra (${outgoing.length})</div>
        <div class="q-fact">${outHtml}</div>
        <div class="q-section-label">Quan hệ đi vào (${incoming.length})</div>
        <div class="q-fact">${inHtml}</div>`;
    }

    function renderBranchDetail(branch) {
      if (!branch) {
        return '<div class="q-empty">Chọn một topic rồi truy hồi để xem nhánh cây con.</div>';
      }
      const nodeId = (selectedBranchNodeId && branch.branch_ids.includes(selectedBranchNodeId))
        ? selectedBranchNodeId
        : branch.topic_id;
      const internal = (KB_DATA.assertions || []).filter(a =>
        branch.branch_ids.includes(a.source) && branch.branch_ids.includes(a.target)
        && conceptById(a.source) && conceptById(a.target)
      );
      const internalHtml = internal.length
        ? internal.map(a => {
            const rel = relationById(a.relation);
            const relName = (rel && rel.name) || a.relation;
            const src = conceptLabel(conceptById(a.source)) || a.source;
            const tgt = conceptLabel(conceptById(a.target)) || a.target;
            return `<div class="q-rel-line">${escapeHtml(src)} <b>${escapeHtml(relName)}</b> ${escapeHtml(tgt)}</div>`;
          }).join('')
        : '<span class="q-item-meta">Không có assertion nội bộ giữa các thực thể trong nhánh (ngoài cạnh subclassOf trên sơ đồ).</span>';
      return `
        <section class="q-hero">
          <div class="q-kicker">Nhánh ontology đã truy hồi</div>
          <div class="q-hero-id">${escapeHtml(branch.topic_name)}</div>
          <div class="q-pills">
            ${pill('concept', `<code>${escapeHtml(branch.topic_id)}</code>`, `jumpToInspector('concepts','${branch.topic_id}')`)}
            ${pill('fn', `${branch.ancestors.length} lớp cha`)}
            ${pill('relation', `${branch.descendants.length} lớp con`)}
            ${pill('instance', `${branch.branch_ids.length} thực thể`)}
          </div>
        </section>
        <div class="q-section-label">Sơ đồ nhánh (subclassOf) — nhấp node để xem chi tiết</div>
        ${renderTopicTreeSvg(branch)}
        ${renderBranchConceptFacts(nodeId, branch)}
        <div class="q-section-label">Quan hệ nội bộ nhánh (${internal.length})</div>
        <div class="q-fact">${internalHtml}</div>
      `;
    }

    function renderBranchBox(branch, candidateCount, shownCount) {
      const box = document.getElementById('qBranchBox');
      if (!box) return;
      if (!qRetrievalActive) {
        box.hidden = true;
        box.innerHTML = '';
        box.classList.remove('active');
        return;
      }
      const lines = [];
      if (branch) {
        lines.push(`<b>Nhánh topic</b> ${escapeHtml(branch.topic_name)} <code>${escapeHtml(branch.topic_id)}</code>`);
        lines.push(`${branch.branch_ids.length} thực thể · ↑ ${branch.ancestors.length} cha · ↓ ${branch.descendants.length} lớp con`);
        lines.push(`Ứng viên: ${candidateCount} · ≥ ${Math.round(RETRIEVE_MIN_SCORE * 100)}%: ${shownCount}/${RETRIEVE_LIMIT}`);
        lines.push('<div class="q-branch-hint">Nhấn để xem sơ đồ nhánh →</div>');
      } else {
        lines.push('<b>Không chọn topic</b> — chưa có cây con để vẽ.');
        lines.push(`Ứng viên sau lọc: ${candidateCount} · trả về: ${shownCount}/${RETRIEVE_LIMIT}`);
      }
      box.innerHTML = lines.join('<br>');
      box.hidden = false;
      box.classList.toggle('active', qPanelMode === 'branch' && !!branch);
      box.disabled = !branch;
    }

    function renderQuestionExplorer(keepSelection) {
      const listEl = document.getElementById('qList');
      const detailEl = document.getElementById('qDetail');
      if (!listEl || !detailEl) return;

      const qAll = collectQuestions();
      const qSearch = (document.getElementById('qSearchInput')?.value || '').trim().toLowerCase();
      const fCh = document.getElementById('qFilterChapter')?.value || 'all';
      const fBl = document.getElementById('qFilterBloom')?.value || 'all';
      const fTy = document.getElementById('qFilterType')?.value || 'all';
      const fDf = document.getElementById('qFilterDiff')?.value || 'all';
      const fTopic = document.getElementById('qFilterTopic')?.value || 'all';
      const branch = (qRetrievalActive && fTopic !== 'all') ? topicBranchFrom(fTopic) : null;

      const candidates = qAll.filter(q => {
        if (fCh !== 'all' && q.chapter !== fCh) return false;
        if (fBl !== 'all' && q.bloom !== fBl) return false;
        if (fTy !== 'all' && q.type !== fTy) return false;
        if (fDf !== 'all' && q.diff !== fDf) return false;
        if (qSearch) {
          const hay = `${q.qid} ${q.content} ${q.typeLabel} ${q.bloomLabel} ${q.diffLabel} ${(q.concepts || []).join(' ')}`.toLowerCase();
          if (!hay.includes(qSearch)) return false;
        }
        return true;
      });

      let filtered = candidates;
      if (qRetrievalActive) {
        filtered = candidates.map(q => {
          const scored = scoreQuestionAgainstBranch(q, branch);
          return Object.assign({}, q, scored);
        }).sort((a, b) => (b.score - a.score) || a.qid.localeCompare(b.qid));
        if (branch) {
          filtered = filtered.filter(q => (q.score || 0) >= RETRIEVE_MIN_SCORE);
        }
        filtered = filtered.slice(0, RETRIEVE_LIMIT);
      }

      renderBranchBox(branch, candidates.length, filtered.length);

      if (qPanelMode === 'branch' && branch) {
        if (!selectedBranchNodeId || !branch.branch_ids.includes(selectedBranchNodeId)) {
          selectedBranchNodeId = branch.topic_id;
        }
      } else if (!keepSelection || !filtered.some(q => q.qid === selectedQuestionId)) {
        if (selectedQuestionId && filtered.some(q => q.qid === selectedQuestionId)) {
          /* keep */
        } else if (!filtered.some(q => q.qid === selectedQuestionId)) {
          selectedQuestionId = filtered[0] ? filtered[0].qid : null;
        }
      }

      let html = '';
      if (qRetrievalActive) {
        if (branch) {
          const branchActive = qPanelMode === 'branch' ? ' active' : '';
          html += `<div class="q-group-title">Nhánh ontology</div>`;
          html += `
            <div class="q-item${branchActive}" onclick="selectBranchView()">
              <div class="q-item-top">
                <div class="q-item-id">${escapeHtml(branch.topic_name)}</div>
              </div>
              <div class="q-item-meta">${branch.branch_ids.length} thực thể · ↑ ${branch.ancestors.length} cha · ↓ ${branch.descendants.length} lớp con</div>
            </div>`;
        }
        html += `<div class="q-group-title">Top ${filtered.length} · tương đồng ≥ ${Math.round(RETRIEVE_MIN_SCORE * 100)}%</div>`;
        filtered.forEach((q, idx) => {
          const active = (qPanelMode !== 'branch' && q.qid === selectedQuestionId) ? ' active' : '';
          const pct = Math.round((q.score || 0) * 100);
          html += `
            <div class="q-item${active}" onclick="selectQuestion('${q.qid}')">
              <div class="q-item-top">
                <div class="q-item-id">${idx + 1}. ${escapeHtml(q.qid)}</div>
                <span class="q-score">${pct}%</span>
              </div>
              <div class="q-item-meta">${escapeHtml(q.bloomLabel)} · ${escapeHtml(q.typeLabel)} · ${escapeHtml(q.diffLabel)}</div>
            </div>`;
        });
        if (!filtered.length) {
          html += `<div class="q-empty" style="padding:1.1rem 0.5rem;">Không có câu ≥ ${Math.round(RETRIEVE_MIN_SCORE * 100)}% tương đồng.</div>`;
        }
      } else {
        const groups = { C1: [], C2: [], C3: [], other: [] };
        filtered.forEach(q => {
          (groups[q.chapter] || groups.other).push(q);
        });
        Object.keys(groups).forEach(key => {
          const arr = groups[key];
          if (!arr.length) return;
          const title = Q_CHAPTER[key] || 'Khác';
          html += `<div class="q-group-title">${escapeHtml(title)} (${arr.length})</div>`;
          arr.forEach(q => {
            const active = q.qid === selectedQuestionId ? ' active' : '';
            html += `
              <div class="q-item${active}" onclick="selectQuestion('${q.qid}')">
                <div class="q-item-id">${escapeHtml(q.qid)}</div>
                <div class="q-item-meta">${escapeHtml(q.bloomLabel)} · ${escapeHtml(q.typeLabel)} · ${escapeHtml(q.diffLabel)}</div>
              </div>`;
          });
        });
      }
      if (!html) html = '<div class="q-empty" style="padding:1.5rem 0.5rem;">Không có câu hỏi khớp bộ lọc.</div>';
      listEl.innerHTML = html;

      if (qPanelMode === 'branch' && branch) {
        detailEl.innerHTML = renderBranchDetail(branch);
        requestAnimationFrame(() => {
          const wrap = document.querySelector('.q-tree-wrap');
          const node = document.querySelector('.q-tree-node.selected') || document.querySelector('.q-tree-node.topic');
          if (!wrap || !node) return;
          const nr = node.getBoundingClientRect();
          const wr = wrap.getBoundingClientRect();
          wrap.scrollTop += (nr.top + nr.height / 2) - (wr.top + wr.height / 2);
          wrap.scrollLeft += (nr.left + nr.width / 2) - (wr.left + wr.width / 2);
        });
      } else {
        const selected = (qRetrievalActive ? filtered : qAll).find(q => q.qid === selectedQuestionId) || qAll.find(q => q.qid === selectedQuestionId);
        detailEl.innerHTML = selected ? renderQuestionDetail(selected) : '<div class="q-empty">Chọn một câu hỏi bên trái để xem lời giải mong đợi.</div>';
      }
    }

    function selectQuestion(qid) {
      qPanelMode = 'question';
      selectedQuestionId = qid;
      renderQuestionExplorer(true);
    }

    function pill(kind, label, onclick) {
      const oc = onclick ? ` onclick="${onclick}; event.stopPropagation();"` : '';
      return `<button class="q-pill ${kind}"${oc}>${label}</button>`;
    }

    function renderQuestionDetail(q) {
      const rubrics = assertionsOf(q.inst.id, 'REL_QUESTION_HAS_RUBRICS').map(a => {
        const c = conceptById(a.target);
        const w = (a.attributes || []).find(x => x.name === 'weight');
        return {
          id: a.target,
          name: attrVal(c, 'name') || a.target,
          weight: w ? Number(w.value) : 0
        };
      });

      const ea = q.eaId ? instById(q.eaId) : null;
      const scoring = ea ? assertionsOf(ea.id, 'REL_EXPECTED_ANSWER_HAS_SCORING_RULE') : [];
      const rules = scoring.map((a, idx) => {
        const er = instById(a.target);
        const concepts = assertionsOf(a.target, 'REL_EXPECTED_RULE_REQUIRES_CONCEPT').map(x => x.target);
        return {
          idx,
          id: a.target,
          inst: er,
          name: attrVal(er, 'name') || a.target,
          weight: Number(attrVal(er, 'weight') || 0),
          miss: attrVal(er, 'missExplanation') || '',
          wrong: attrVal(er, 'wrongExplanation') || '',
          domainRuleId: attrVal(er, 'domainRuleId'),
          functionId: attrVal(er, 'functionId'),
          concepts
        };
      });
      const weightSum = rules.reduce((s, r) => s + (Number.isFinite(r.weight) ? r.weight : 0), 0);
      const sumOk = Math.abs(weightSum - 1) < 1e-6;

      let stack = '';
      rules.forEach((r, i) => {
        const pct = Math.max(0, r.weight) * 100;
        const color = WEIGHT_PALETTE[i % WEIGHT_PALETTE.length];
        stack += `<div class="weight-seg" style="width:${pct}%;background:${color};" title="${escapeHtml(r.name)} ${pct.toFixed(0)}%"></div>`;
      });

      const rubricHtml = rubrics.length ? `
        <div class="q-section-label">Rubric đánh giá (evaluatedBy)</div>
        <div class="rubric-box">
          ${rubrics.map(r => `
            <div class="rubric-item">
              <span><b>${escapeHtml(r.name)}</b><code>${Math.round(r.weight * 100)}%</code></span>
              <div class="mini-bar"><i style="width:${Math.round(r.weight * 100)}%"></i></div>
            </div>`).join('')}
        </div>` : '';

      const ruleCards = rules.map((r, i) => {
        const color = WEIGHT_PALETTE[i % WEIGHT_PALETTE.length];
        const domain = r.domainRuleId ? ruleById(r.domainRuleId) : null;
        const fn = r.functionId ? fnById(r.functionId) : null;
        const conceptPills = r.concepts.map(cid => {
          const c = conceptById(cid);
          const label = conceptLabel(c) || cid;
          return pill('concept', `<code>${escapeHtml(cid)}</code> ${escapeHtml(label)}`, `jumpToInspector('concepts','${cid}')`);
        }).join('');
        return `
          <div class="flow-rel">hasScoringRule · ${Math.round(r.weight * 100)}%</div>
          <article class="er-card" style="border-left-color:${color};">
            <div class="er-top">
              <div>
                <div class="er-name">${escapeHtml(r.name)}</div>
                <div class="er-id">${escapeHtml(r.id)}</div>
              </div>
              <div class="er-weight">${Number(r.weight).toFixed(2)}</div>
            </div>
            <div class="q-pills">
              ${conceptPills || '<span class="q-item-meta">Không gắn khái niệm</span>'}
              ${r.domainRuleId ? pill('rule', `luật ${escapeHtml(r.domainRuleId)}${domain && domain.name ? ' · ' + escapeHtml(domain.name) : ''}`, `jumpToInspector('rules','${r.domainRuleId}')`) : ''}
              ${r.functionId ? pill('fn', `hàm ${escapeHtml(r.functionId)}${fn && fn.name ? ' · ' + escapeHtml(fn.name) : ''}`, `jumpToInspector('functions','${r.functionId}')`) : ''}
            </div>
            <div class="er-explain">
              <div><b>Thiếu</b>${escapeHtml(r.miss)}</div>
              <div><b>Sai</b>${escapeHtml(r.wrong)}</div>
            </div>
          </article>`;
      }).join('');

      return `
        <section class="q-hero">
          <div class="q-kicker">Câu hỏi</div>
          <div class="q-hero-id">${escapeHtml(q.qid)}</div>
          <div class="q-pills">
            ${pill('instance', `<code>${escapeHtml(q.inst.id)}</code>`, `jumpToInspector('instances','${q.inst.id}')`)}
            ${q.bloomId ? pill('concept', `Bloom · ${escapeHtml(q.bloomLabel)}`, `jumpToInspector('concepts','${q.bloomId}')`) : ''}
            ${q.typeId ? pill('concept', `Dạng · ${escapeHtml(q.typeLabel)}`, `jumpToInspector('concepts','${q.typeId}')`) : ''}
            ${q.diffId ? pill('concept', `Độ khó · ${escapeHtml(q.diffLabel)}`, `jumpToInspector('concepts','${q.diffId}')`) : ''}
            ${pill('relation', escapeHtml(Q_CHAPTER[q.chapter] || q.chapter))}
            ${q.score != null && qRetrievalActive ? pill('fn', `tương đồng ${(q.score * 100).toFixed(0)}% · khái niệm ${((q.concept_score || 0) * 100).toFixed(0)}% · văn bản ${((q.text_score || 0) * 100).toFixed(0)}%`) : ''}
          </div>
          <div class="q-content">${escapeHtml(q.content)}</div>
        </section>

        ${rubricHtml}

        <div class="flow-rel">hasExpectedAnswer</div>
        <section class="ea-card">
          <div class="weight-head">
            <div>
              <div class="q-kicker">Lời giải mong đợi</div>
              <div class="er-id" style="margin-top:0.2rem;">${ea ? escapeHtml(ea.id) : 'Chưa gắn Expected Answer'}</div>
            </div>
            <div class="weight-sum ${sumOk ? 'ok' : 'bad'}">Σ luật = ${weightSum.toFixed(2)}${sumOk ? ' ✓' : ''}</div>
          </div>
          <div class="weight-stack">${stack || '<div class="weight-seg" style="width:100%;background:#ddd;"></div>'}</div>
          ${ea && attrVal(ea, 'description') ? `<div class="ea-desc">${escapeHtml(attrVal(ea, 'description'))}</div>` : ''}
        </section>

        <div class="q-section-label">Luật chấm (${rules.length})</div>
        ${ruleCards || '<div class="q-empty" style="padding:1.5rem 0;">Chưa có ExpectedRule.</div>'}
      `;
    }

    // Window focus triggers immediate data check
    window.addEventListener('focus', () => {
      if (autoSyncEnabled) {
        fetchKBData(false);
      }
    });

    // Initial load

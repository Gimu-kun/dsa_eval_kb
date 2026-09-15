    function selectDataset(name) {
      currentDataset = name;
      document.querySelectorAll('.dataset-item').forEach(el => {
        el.classList.remove('active');
        const oc = el.getAttribute('onclick') || '';
        if (oc.includes("'" + name + "'")) el.classList.add('active');
      });

      setupFilterDropdown();
      const search = document.getElementById('searchInput');
      const sort = document.getElementById('sortSelect');
      if (search) search.value = '';
      if (sort) sort.value = 'default';
      applyFilters();
    }

    function setupFilterDropdown() {
      const select = document.getElementById('filterSelect');
      select.innerHTML = '<option value="all">Tất cả mục</option>';

      if (currentDataset === 'hierarchy') {
        const parents = [...new Set((KB_DATA.hierarchy || []).map(h => h.superclass || h.parent).filter(Boolean))].sort();
        parents.forEach(p => {
          select.innerHTML += `<option value="parent:${p}">Lớp cha: ${p}</option>`;
        });
      } else if (currentDataset === 'concepts') {
        select.innerHTML += `
          <option value="has_subclass">Có kế thừa (subclassOf)</option>
          <option value="root">Lớp gốc (Root Concept)</option>
          <option value="has_attr">Có thuộc tính (Attributes)</option>
          <option value="no_attr">Không có thuộc tính</option>
        `;
      } else if (currentDataset === 'instances') {
        const instances = KB_DATA.instances || [];
        const classes = [...new Set(instances.map(i => i.instanceOf).filter(Boolean))].sort();
        classes.forEach(cls => {
          select.innerHTML += `<option value="class:${cls}">Thuộc khái niệm: ${cls}</option>`;
        });
      } else if (currentDataset === 'assertions') {
        const assertions = KB_DATA.assertions || [];
        const rels = [...new Set(assertions.map(a => a.relation).filter(Boolean))].sort();
        rels.forEach(rel => {
          select.innerHTML += `<option value="rel:${rel}">Quan hệ: ${rel}</option>`;
        });
      } else if (currentDataset === 'relations') {
        const relations = KB_DATA.relations || [];
        const sources = [...new Set(relations.map(r => r.source).filter(Boolean))].sort();
        sources.forEach(src => {
          select.innerHTML += `<option value="src:${src}">Nguồn từ: ${src}</option>`;
        });
      }
    }

    function handleSearch() {
      const val = document.getElementById('searchInput').value;
      document.getElementById('clearSearchBtn').style.display = val ? 'inline-block' : 'none';
      applyFilters();
    }

    function clearSearch() {
      document.getElementById('searchInput').value = '';
      document.getElementById('clearSearchBtn').style.display = 'none';
      applyFilters();
    }

    function resetFilters() {
      document.getElementById('searchInput').value = '';
      document.getElementById('clearSearchBtn').style.display = 'none';
      document.getElementById('filterSelect').value = 'all';
      document.getElementById('sortSelect').value = 'default';
      applyFilters();
    }

    function jumpTo3D(nodeId) {
      switchView('graph');
      focusNodeIn3D(nodeId);
    }

    function applyFilters() {
      const container = document.getElementById('cardsContainer');
      container.innerHTML = '';

      const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
      const filterVal = document.getElementById('filterSelect').value;
      const sortVal = document.getElementById('sortSelect').value;

      let rawItems = KB_DATA[currentDataset] || [];
      let totalCount = rawItems.length;

      let items = rawItems.filter(item => {
        if (!query) return true;
        if (item.id && item.id.toLowerCase().includes(query)) return true;
        if (item.name && item.name.toLowerCase().includes(query)) return true;
        if (conceptLabel(item).toLowerCase().includes(query)) return true;
        if (item.instanceOf && item.instanceOf.toLowerCase().includes(query)) return true;
        if (item.subclassOf && item.subclassOf.toLowerCase().includes(query)) return true;
        if (item.domain && item.domain.toLowerCase().includes(query)) return true;
        if (Array.isArray(item.attributes)) {
          for (const attr of item.attributes) {
            if (attr.name && attr.name.toLowerCase().includes(query)) return true;
            if (attr.value && String(attr.value).toLowerCase().includes(query)) return true;
          }
        } else if (item.attributes && typeof item.attributes === 'object') {
          for (const [k, v] of Object.entries(item.attributes)) {
            if (k.toLowerCase().includes(query)) return true;
            if (String(v).toLowerCase().includes(query)) return true;
          }
        }
        if (item.relation && item.relation.toLowerCase().includes(query)) return true;
        if (item.source && item.source.toLowerCase().includes(query)) return true;
        if (item.target && String(item.target).toLowerCase().includes(query)) return true;
        if (item.subclass && item.subclass.toLowerCase().includes(query)) return true;
        if (item.superclass && item.superclass.toLowerCase().includes(query)) return true;
        return false;
      });

      if (filterVal !== 'all') {
        if (filterVal === 'has_subclass') {
          items = items.filter(i => !!i.subclassOf);
        } else if (filterVal === 'root') {
          items = items.filter(i => !i.subclassOf);
        } else if (filterVal === 'has_attr') {
          items = items.filter(i => i.attributes && i.attributes.length > 0);
        } else if (filterVal === 'no_attr') {
          items = items.filter(i => !i.attributes || i.attributes.length === 0);
        } else if (filterVal.startsWith('parent:')) {
          const p = filterVal.replace('parent:', '');
          items = items.filter(i => (i.superclass || i.parent) === p);
        } else if (filterVal.startsWith('class:')) {
          const cls = filterVal.replace('class:', '');
          items = items.filter(i => i.instanceOf === cls);
        } else if (filterVal.startsWith('rel:')) {
          const rel = filterVal.replace('rel:', '');
          items = items.filter(i => i.relation === rel);
        } else if (filterVal.startsWith('src:')) {
          const src = filterVal.replace('src:', '');
          items = items.filter(i => i.source === src);
        }
      }

      if (sortVal === 'asc') {
        items = [...items].sort((a, b) => (a.id || a.relation || '').localeCompare(b.id || b.relation || ''));
      } else if (sortVal === 'desc') {
        items = [...items].sort((a, b) => (b.id || b.relation || '').localeCompare(a.id || a.relation || ''));
      }

      document.getElementById('resultCounter').innerText = `Hiển thị ${items.length} / ${totalCount} mục`;

      if (items.length === 0) {
        container.innerHTML = `
          <div style="background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 12px; text-align: center; padding: 3.5rem 2rem; color: var(--text-muted); width: 100%;">
            <div style="font-size: 2.8rem; margin-bottom: 0.65rem;">🔍</div>
            <div style="font-weight: 650; font-size: 15px; color: var(--text-heading);">Không tìm thấy dữ liệu phù hợp</div>
            <div style="font-size: 14px; margin-top: 0.35rem; color: var(--text-muted);">Hãy thử nhập từ khoá khác hoặc bấm "Đặt lại bộ lọc" để xem toàn bộ danh sách.</div>
          </div>
        `;
        return;
      }

      items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'data-card';

        if (currentDataset === 'hierarchy') {
        const parents = [...new Set((KB_DATA.hierarchy || []).map(h => h.superclass || h.parent).filter(Boolean))].sort();
        parents.forEach(p => {
          select.innerHTML += `<option value="parent:${p}">Lớp cha: ${p}</option>`;
        });
      } else if (currentDataset === 'concepts') {
          renderConceptCard(card, item);
        } else if (currentDataset === 'instances') {
          renderInstanceCard(card, item);
        } else if (currentDataset === 'relations') {
          renderRelationCard(card, item);
        } else if (currentDataset === 'assertions') {
          renderAssertionCard(card, item);
        } else if (currentDataset === 'rules') {
          renderRuleCard(card, item);
        } else if (currentDataset === 'operands') {
          renderOperandCard(card, item);
        } else if (currentDataset === 'functions') {
          renderFunctionCard(card, item);
        } else {
          card.innerHTML = `
            <div class="card-header">
              <span class="card-id">${item.id || 'Tập tin'}</span>
            </div>
            <p style="color: var(--text-muted);">Tập tin này hiện chưa có dữ liệu dòng.</p>
          `;
        }

        container.appendChild(card);
      });
    }

        function formatParam(p) {
      if (!p) return '';
      const t = p.valueType || p.value_type || 'any';
      const card = p.cardinality && p.cardinality !== '(1..1)' ? p.cardinality : '';
      return `${p.name}: ${t}${card}`;
    }

    function formatParamList(params, emptyLabel) {
      if (!params) return emptyLabel;
      const list = Array.isArray(params) ? params : [params];
      if (!list.length) return emptyLabel;
      return list.map(p => `<code>${formatParam(p)}</code>`).join(', ');
    }

    function renderFunctionCard(card, item) {
      const inputs = formatParamList(item.input, 'None');
      const outStr = formatParamList(item.output, 'void');
      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge" style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;">Hàm</span>
            </div>
            <span class="card-subtitle">Mã định danh: <code>${item.id}</code></span>
          </div>
        </div>
        <div class="card-info-section">
          ${item.description ? `<div class="text-quote-box" style="margin-bottom: 0.75rem;"><b>Mô tả:</b> ${item.description}</div>` : ''}
          <div class="info-line">
            <span class="info-line-label">Đầu vào (Input):</span>
            <div class="info-line-value">${inputs}</div>
          </div>
          <div class="info-line">
            <span class="info-line-label">Đầu ra (Output):</span>
            <div class="info-line-value">${outStr}</div>
          </div>
        </div>
      `;
    }

    function renderOperandCard(card, item) {
      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.id}</span>
              <span class="badge" style="background: #fdf2f8; color: #db2777; border: 1px solid #fbcfe8;">Toán hạng (${(item.operandType || item.operand_type || 'operand')})</span>
            </div>
            <span class="card-subtitle">Biến đại diện: <code>${item.variable || ''}</code></span>
          </div>
        </div>
        <div class="card-info-section">
          <div class="info-line">
            <span class="info-line-label">Kiểu toán hạn:</span>
            <span class="info-line-value"><code>${item.operandType || item.operand_type || 'N/A'}</code></span>
          </div>
          <div class="info-line">
            <span class="info-line-label">Tên biến (Variable):</span>
            <span class="info-line-value"><b style="color: #2563eb;">${item.variable || 'N/A'}</b></span>
          </div>
          ${item.value ? `
          <div class="info-line">
            <span class="info-line-label">Giá trị liên kết (Value):</span>
            <span class="info-line-value"><code style="font-weight: 700; color: var(--concept-color);">${item.value}</code></span>
          </div>` : ''}
          ${item.alias ? `
          <div class="info-line">
            <span class="info-line-label">Bí danh (Alias):</span>
            <span class="info-line-value"><code>${item.alias}</code></span>
          </div>` : ''}
        </div>
      `;
    }

    function renderHierarchyCard(card, item) {
      const sub = item.subclass || item.subclassOf;
      const sup = item.superclass || item.parent;
      card.innerHTML = `
        <div class="card-header">
          <span class="card-id" style="color: var(--subclass-color);">${sub}</span>
          <span class="card-badge" style="background: var(--subclass-bg); color: var(--subclass-color); border: 1px solid var(--subclass-border);">subclassOf</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; margin: 1rem 0; background: var(--bg-subtle); padding: 0.85rem 1rem; border-radius: 8px;">
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 0.25rem;">Lớp con (Subclass)</div>
            <a href="#" onclick="filterConcept('${sub}'); return false;" style="font-weight: 700; color: var(--concept-color); text-decoration: none; font-size: 14px;">${sub} ↗</a>
          </div>
          <div style="color: var(--subclass-color); font-weight: 800; font-size: 16px;">➔</div>
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 0.25rem;">Lớp cha (Superclass)</div>
            <a href="#" onclick="filterConcept('${sup}'); return false;" style="font-weight: 700; color: var(--subclass-color); text-decoration: none; font-size: 14px;">${sup} ↗</a>
          </div>
        </div>
      `;
    }

    function renderConceptCard(card, item) {
      const subclassInfo = item.subclassOf 
        ? `<a href="#" onclick="filterConcept('${item.subclassOf}'); return false;" style="color: var(--subclass-color); font-weight: 700; text-decoration: none;">${item.subclassOf} ↗</a>`
        : '<span style="color: var(--text-muted); font-style: italic;">Lớp gốc (Không có lớp cha)</span>';

      let attrRowsHtml = '';
      if (Array.isArray(item.attributes) && item.attributes.length > 0) {
        attrRowsHtml = item.attributes.map(attr => {
          let constraintStr = '';
          if (attr.constraint && attr.constraint.length > 0) {
            constraintStr = ` <span style="font-size: 13px; color: var(--text-muted);">(Ràng buộc: ${JSON.stringify(attr.constraint)})</span>`;
          }
          const reqBadge = attr.required 
            ? `<span style="font-size: 12px; color: #ef4444; font-weight: 700; margin-left: 0.4rem;">*Bắt buộc</span>` 
            : `<span style="font-size: 12px; color: var(--text-muted); margin-left: 0.4rem;">(Tuỳ chọn)</span>`;
          return `
            <div class="attr-row">
              <span class="attr-name">${attr.name || 'attr'}${reqBadge}</span>
              <div class="attr-value">
                <span class="attr-type-pill">${attr.value_type || 'any'}</span>
                ${attr.default != null && attr.default !== '' ? `<span class="attr-type-pill">mặc định: ${attr.default}</span>` : ''}
                ${constraintStr}
              </div>
            </div>
          `;
        }).join('');
      }

      let opHtml = '<span style="color: var(--text-muted); font-style: italic;">Không có</span>';
      if (Array.isArray(item.operation) && item.operation.length > 0) {
        opHtml = `<div style="display: flex; flex-direction: column; gap: 0.35rem; margin-top: 0.35rem;">` + 
          item.operation.map(op => {
            if (typeof op === 'string') return `<div style="font-family: var(--font-mono); font-size: 13px; color: var(--concept-color);">• ${op}</div>`;
            const inputs = (op.input || []).map(p => formatParam(p)).join(', ');
            const out = op.output
              ? (Array.isArray(op.output) ? op.output.map(formatParam).join(', ') : formatParam(op.output))
              : 'void';
            return `<div style="font-family: var(--font-mono); font-size: 13px; color: var(--concept-color);">• <b>${op.name}</b>(${inputs}) ➔ ${out}${op.description ? ` <span style="color: var(--text-muted); font-family: var(--font-ui);">(${op.description})</span>` : ''}</div>`;
          }).join('') +
          `</div>`;
      }

      let invHtml = '<span style="color: var(--text-muted); font-style: italic;">Không có</span>';
      if (Array.isArray(item.invariant) && item.invariant.length > 0) {
        invHtml = `<div style="display: flex; flex-direction: column; gap: 0.35rem; margin-top: 0.35rem;">` +
          item.invariant.map(inv => {
            if (typeof inv === 'string') return `<div class="text-quote-box">${inv}</div>`;
            return `<div class="text-quote-box"><b>${inv.name}</b>: ${inv.description || ''} <code style="font-size: 13px;">[${inv.condition ? inv.condition.operator : ''}]</code></div>`;
          }).join('') +
          `</div>`;
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.id}</span>
              <span class="badge badge-concept">Khái niệm</span>
              ${item.domain ? `<span class="badge" style="background: var(--bg-subtle); color: var(--text-sub); border: 1px solid var(--border-color);">Miền: ${item.domain}</span>` : ''}
            </div>
            <span class="card-subtitle">${conceptLabel(item)}</span>
          </div>

          <button class="btn-3d-jump" onclick="jumpTo3D('${item.id}')">
            Xem 3D
          </button>
        </div>

        <div class="card-info-section">
          <div class="info-line">
            <span class="info-line-label">Kế thừa (subclassOf):</span>
            <div class="info-line-value">${subclassInfo}</div>
          </div>

          <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="info-line-label">Danh sách thuộc tính:</span>
              <span style="font-size: 13px; font-weight: 600; color: var(--text-muted);">${item.attributes ? item.attributes.length : 0} thuộc tính</span>
            </div>

            ${attrRowsHtml ? `
              <div class="attributes-box">
                <div class="attributes-header">
                  <span>Tên thuộc tính</span>
                  <span>Kiểu dữ liệu & Ràng buộc</span>
                </div>
                ${attrRowsHtml}
              </div>
            ` : '<div style="color: var(--text-muted); font-style: italic; padding: 0.25rem 0;">Khái niệm này không định nghĩa thêm thuộc tính.</div>'}
          </div>

          <div class="info-line">
            <span class="info-line-label">Ràng buộc bất biến:</span>
            <div class="info-line-value">${invHtml}</div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Thao tác / Hành vi:</span>
            <div class="info-line-value">${opHtml}</div>
          </div>
        </div>
      `;
    }

    function renderInstanceCard(card, item) {
      const instanceOfHtml = item.instanceOf 
        ? `<a href="#" onclick="switchConcept('${item.instanceOf}'); return false;" style="color: var(--concept-color); font-weight: 700; text-decoration: none;">${item.instanceOf} ↗</a>`
        : '<span style="color: var(--text-muted);">Không xác định</span>';

      let attrRowsHtml = '';
      if (Array.isArray(item.attributes) && item.attributes.length > 0) {
        attrRowsHtml = item.attributes.map(attr => {
          const isDesc = attr.name === 'description' || (typeof attr.value === 'string' && attr.value.length > 80);
          return `
            <div class="attr-row" style="${isDesc ? 'flex-direction: column; gap: 0.35rem;' : ''}">
              <span class="attr-name">${attr.name}:</span>
              <div class="attr-value">
                ${isDesc 
                  ? `<div class="text-quote-box">${attr.value}</div>` 
                  : `<b style="color: var(--text-heading); font-family: var(--font-mono); font-size: 13px;">${attr.value}</b>`
                }
              </div>
            </div>
          `;
        }).join('');
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.id}</span>
              <span class="badge badge-instance">Đối tượng</span>
            </div>
            <span class="card-subtitle">Thể hiện thực tế của mô hình dữ liệu</span>
          </div>

          <div style="display:flex;flex-direction:column;gap:0.35rem;align-items:flex-end;">
            <button class="btn-3d-jump" onclick="jumpTo3D('${item.id}')">
              Xem 3D
            </button>
            ${['O_C_QUESTION','O_C_EXPECTED_ANSWER','O_C_EXPECTED_RULE'].includes(item.instanceOf) ? `
            <button class="btn-3d-jump" onclick="openQuestionFromInstance('${item.id}')">
              Xem lời giải
            </button>` : ''}
          </div>
        </div>
            <div class="info-line-value">${instanceOfHtml}</div>
          </div>

          <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="info-line-label">Dữ liệu thuộc tính chi tiết:</span>
              <span style="font-size: 13px; font-weight: 600; color: var(--text-muted);">${item.attributes ? item.attributes.length : 0} trường</span>
            </div>

            ${attrRowsHtml ? `
              <div class="attributes-box">
                <div class="attributes-header">
                  <span>Trường thuộc tính</span>
                  <span>Giá trị ghi nhận</span>
                </div>
                ${attrRowsHtml}
              </div>
            ` : '<div style="color: var(--text-muted); font-style: italic; padding: 0.25rem 0;">Không có giá trị thuộc tính.</div>'}
          </div>
        </div>
      `;
    }

    function renderRelationCard(card, item) {
      let attrRowsHtml = '';
      if (Array.isArray(item.attributes) && item.attributes.length > 0) {
        attrRowsHtml = item.attributes.map(attr => `
          <div class="attr-row">
            <span class="attr-name">${attr.name}:</span>
            <div class="attr-value">
              <span class="attr-type-pill">${attr.value_type}</span>
              ${attr.constraint ? `<span style="font-size: 13px; color: var(--text-muted);">(Ràng buộc: ${JSON.stringify(attr.constraint)})</span>` : ''}
            </div>
          </div>
        `).join('');
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge badge-relation">Quan hệ</span>
            </div>
            <span class="card-subtitle">Mã định danh: <code>${item.id}</code></span>
          </div>
        </div>

        <div class="card-info-section">
          <div class="info-line">
            <span class="info-line-label">Khái niệm Nguồn (Source):</span>
            <div class="info-line-value">
              <b style="color: var(--concept-color);">${item.source}</b>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Khái niệm Đích (Target):</span>
            <div class="info-line-value">
              <b style="color: var(--concept-color);">${Array.isArray(item.target) ? item.target.join(', ') : item.target}</b>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Bản số (Cardinality):</span>
            <div class="info-line-value">
              <span class="badge" style="background: var(--bg-subtle); color: var(--text-heading); border: 1px solid var(--border-color);">${item.cardinality || 'Không xác định'}</span>
            </div>
          </div>

          ${attrRowsHtml ? `
            <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.4rem;">
              <span class="info-line-label">Thuộc tính bổ trợ của quan hệ:</span>
              <div class="attributes-box">
                ${attrRowsHtml}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }

    function renderAssertionCard(card, item) {
      let attrHtml = '';
      if (Array.isArray(item.attributes) && item.attributes.length > 0) {
        attrHtml = `
          <div class="info-line">
            <span class="info-line-label">Thuộc tính:</span>
            <div class="info-line-value">
              ${item.attributes.map(a => `<span class="attr-type-pill">${a.name}: ${a.value}</span>`).join(' ')}
            </div>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id" style="color: var(--primary-text);">${item.relation}</span>
              <span class="badge badge-assertion">Phán đoán</span>
            </div>
            <span class="card-subtitle">Mối liên kết thực tế giữa 2 đối tượng</span>
          </div>

          <div style="display: flex; gap: 0.5rem;">
            <button class="btn-3d-jump" onclick="jumpTo3D('${item.source}')">
              👁️ Nguồn (${item.source})
            </button>
            <button class="btn-3d-jump" onclick="jumpTo3D('${item.target}')">
              👁️ Đích (${item.target})
            </button>
          </div>
        </div>

        <div class="card-info-section">
          <div class="info-line">
            <span class="info-line-label">Chủ thể (Source / Subject):</span>
            <div class="info-line-value">
              <b style="color: var(--instance-color); font-family: var(--font-mono); font-size: 13px;">${item.source}</b>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Vị từ (Relation / Predicate):</span>
            <div class="info-line-value">
              <span class="badge badge-assertion">${item.relation}</span>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Đối tượng (Target / Object):</span>
            <div class="info-line-value">
              <b style="color: var(--instance-color); font-family: var(--font-mono); font-size: 13px;">${item.target}</b>
            </div>
          </div>

          ${attrHtml}
        </div>
      `;
    }

    function renderRuleCard(card, item) {
      let condListHtml = '';
      if (item.expression) {
        condListHtml = `
          <div style="background: var(--bg-card); padding: 0.6rem 0.85rem; border-radius: 6px; font-family: var(--font-mono); font-size: 14px; color: #2563eb; font-weight: 700; border: 1px solid #bfdbfe;">
            ${item.expression}
          </div>
        `;
      } else if (item.condition && item.condition.operands) {
        condListHtml = item.condition.operands.map((op, idx) => {
          const relVal = op.operands && op.operands[0] ? op.operands[0].value : (op.value || '');
          const instVal = op.operands && op.operands[1] ? op.operands[1].value : '';
          return `
            <div class="info-line" style="margin-bottom: 0.35rem; background: var(--bg-card);">
              <span style="font-weight: 700; color: var(--primary-text); min-width: 30px;">#${idx + 1}</span>
              <div style="flex: 1; font-size: 14px;">
                ${relVal} ${instVal ? `<b style="color: var(--instance-color);">${instVal}</b>` : ''}
              </div>
            </div>
          `;
        }).join('');
      }

      let conclListHtml = '';
      if (Array.isArray(item.conclusion)) {
        conclListHtml = item.conclusion.map(c => `
          <div class="text-quote-box" style="margin-top: 0.35rem;">
            (attribute) Gán <b>${c.target_instance}.${c.attribute_name}</b> = <span style="color: #059669; font-weight: 700;">${c.value}</span> (kiểu ${c.valueType})
          </div>
        `).join('');
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge" style="background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe;">Luật</span>
            </div>
            <span class="card-subtitle">Mã luật: <code>${item.id}</code></span>
          </div>
        </div>

        <div class="card-info-section">
          ${item.description ? `<div class="text-quote-box" style="margin-bottom: 0.6rem;"><b>Mô tả:</b> ${item.description}</div>` : ''}
          <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between;">
              <span class="info-line-label">Điều kiện tiên quyết (Preconditions):</span>
              <span class="badge" style="background: #fffbeb; color: #b45309; border: 1px solid #fde68a;">Phép toán: ${item.condition ? item.condition.operator : 'AND'}</span>
            </div>
            <div style="background: var(--bg-body); border-radius: 8px; padding: 0.5rem;">
              ${condListHtml || 'Không có điều kiện'}
            </div>
          </div>

          <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.5rem;">
            <span class="info-line-label">Hành động kết luận (Conclusion):</span>
            ${conclListHtml || 'Không có kết luận'}
          </div>
        </div>
      `;
    }

    function filterConcept(conceptId) {
      document.getElementById('searchInput').value = conceptId;
      applyFilters();
    }

    function switchConcept(conceptId) {
      selectDataset('concepts');
      document.getElementById('searchInput').value = conceptId;
      applyFilters();
    }

    // =========================================================================

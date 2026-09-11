import os

base_dir = os.path.dirname(os.path.abspath(__file__))

html_content = '''<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DSA Ontology & Knowledge Base Inspector (Real-time)</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Three.js and OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <style>
    :root {
      /* Configurable Theme Variables */
      --primary: #FF8787;
      --primary-hover: #ff6b6b;
      --primary-active: #fa5252;
      --primary-light: #fff0f0;
      --primary-border: #ffc9c9;
      --primary-text: #c92a2a;
      --primary-shadow: rgba(255, 135, 135, 0.25);

      /* Backgrounds */
      --bg-body: #f8fafc;
      --bg-card: #ffffff;
      --bg-subtle: #f1f5f9;
      --bg-input: #ffffff;
      
      /* Borders */
      --border-color: #e2e8f0;
      --border-hover: #cbd5e1;
      --border-focus: #FF8787;

      /* Typography */
      --text-main: #0f172a;       /* Slate 900 */
      --text-heading: #1e293b;    /* Slate 800 */
      --text-sub: #334155;        /* Slate 700 */
      --text-muted: #64748b;      /* Slate 500 */
      --text-light: #94a3b8;

      /* Semantic Badges */
      --concept-color: #2563eb;
      --concept-bg: #eff6ff;
      --concept-border: #bfdbfe;

      --instance-color: #059669;
      --instance-bg: #ecfdf5;
      --instance-border: #a7f3d0;

      --subclass-color: #d97706;
      --subclass-bg: #fffbeb;
      --subclass-border: #fde68a;

      --relation-color: #7c3aed;
      --relation-bg: #f5f3ff;
      --relation-border: #ddd6fe;

      --assertion-color: #FF8787;
      --assertion-bg: #fff0f0;
      --assertion-border: #ffc9c9;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-body);
      color: var(--text-main);
      overflow-x: hidden;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    /* Top Navigation Bar */
    header {
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 0.85rem 1.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.25rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
      transition: background 0.2s ease, border-color 0.2s ease;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-weight: 800;
      font-size: 1.2rem;
      color: var(--text-heading);
      text-decoration: none;
    }

    .brand-badge {
      background: var(--primary);
      color: #ffffff;
      padding: 0.35rem 0.65rem;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      box-shadow: 0 2px 6px var(--primary-shadow);
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      transition: background 0.2s ease;
    }

    .nav-tabs {
      display: flex;
      background: var(--bg-subtle);
      padding: 0.3rem;
      border-radius: 10px;
      border: 1px solid var(--border-color);
      gap: 0.35rem;
    }

    .nav-tab {
      padding: 0.55rem 1.25rem;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.2s ease;
      font-family: inherit;
    }

    .nav-tab:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.7);
    }

    .nav-tab.active {
      background: var(--primary);
      color: #ffffff;
      box-shadow: 0 2px 8px var(--primary-shadow);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    /* Live Sync Status Indicator */
    .live-status-pill {
      background: var(--bg-subtle);
      border: 1px solid var(--border-color);
      padding: 0.35rem 0.75rem;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      color: var(--text-sub);
      cursor: pointer;
      user-select: none;
      transition: all 0.15s ease;
    }

    .live-status-pill:hover {
      border-color: var(--border-hover);
      background: var(--bg-card);
    }

    .live-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
      animation: pulseGreen 2s infinite;
    }

    @keyframes pulseGreen {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .live-dot.paused {
      background: #94a3b8;
      animation: none;
    }

    .header-stats {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.82rem;
      color: var(--text-sub);
    }

    .stat-pill {
      background: var(--bg-card);
      padding: 0.3rem 0.65rem;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      font-weight: 500;
    }
    .stat-pill b {
      color: var(--text-heading);
      font-weight: 700;
    }

    .btn-theme {
      background: var(--primary-light);
      color: var(--primary-text);
      border: 1px solid var(--primary-border);
      font-size: 0.84rem;
      padding: 0.45rem 0.9rem;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      transition: all 0.2s ease;
      font-family: inherit;
    }

    .btn-theme:hover {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 2px 8px var(--primary-shadow);
    }

    /* View Switcher Containers */
    .view-container {
      flex: 1;
      display: none;
    }
    .view-container.active {
      display: flex;
    }

    /* ========================================= */
    /* VIEW 1: DATA INSPECTOR                    */
    /* ========================================= */
    #inspector-view {
      flex-direction: row;
      height: calc(100vh - 66px);
      overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
      width: 290px;
      min-width: 290px;
      background: var(--bg-card);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      transition: background 0.2s ease, border-color 0.2s ease;
    }

    .sidebar-header {
      padding: 1.1rem 1.25rem 0.75rem 1.25rem;
      border-bottom: 1px solid var(--border-color);
    }

    .sidebar-title {
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      font-weight: 800;
    }

    .dataset-list {
      list-style: none;
      overflow-y: auto;
      padding: 0.75rem 0.65rem;
      flex: 1;
    }

    .dataset-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 0.95rem;
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 0.35rem;
      color: var(--text-sub);
      font-size: 0.9rem;
      font-weight: 600;
      transition: all 0.15s ease;
      border: 1px solid transparent;
    }

    .dataset-item:hover {
      background: var(--bg-subtle);
      color: var(--text-heading);
    }

    .dataset-item.active {
      background: var(--primary-light);
      border-color: var(--primary-border);
      color: var(--primary-text);
      font-weight: 700;
    }

    .dataset-badge {
      background: var(--bg-subtle);
      padding: 0.2rem 0.55rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-muted);
    }

    .dataset-item.active .dataset-badge {
      background: var(--primary);
      color: #ffffff;
    }

    /* Main Inspector Area */
    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: var(--bg-body);
      overflow: hidden;
      transition: background 0.2s ease;
    }

    /* Filter & Search Toolbar */
    .filter-bar {
      padding: 1rem 1.75rem;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
      transition: background 0.2s ease, border-color 0.2s ease;
    }

    .filter-row-primary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .search-box {
      display: flex;
      align-items: center;
      background: var(--bg-body);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.55rem 0.9rem;
      flex: 1;
      min-width: 320px;
      gap: 0.6rem;
      transition: all 0.15s ease;
    }

    .search-box:focus-within {
      border-color: var(--border-focus);
      background: var(--bg-card);
      box-shadow: 0 0 0 3px var(--primary-light);
    }

    .search-box input {
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-main);
      font-size: 0.92rem;
      width: 100%;
      font-family: inherit;
    }

    .filter-row-secondary {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    .filter-group {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.84rem;
      color: var(--text-sub);
    }

    .filter-select {
      padding: 0.45rem 0.85rem;
      border-radius: 7px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      font-size: 0.84rem;
      font-weight: 500;
      font-family: inherit;
      outline: none;
      cursor: pointer;
    }

    .filter-select:focus {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px var(--primary-light);
    }

    .btn {
      padding: 0.45rem 0.95rem;
      border-radius: 7px;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .btn:hover {
      background: var(--bg-subtle);
      border-color: var(--border-hover);
    }

    .btn-primary {
      background: var(--primary);
      border-color: var(--primary);
      color: #ffffff;
      box-shadow: 0 2px 6px var(--primary-shadow);
    }

    .btn-primary:hover {
      background: var(--primary-hover);
      border-color: var(--primary-hover);
    }

    .count-indicator {
      margin-left: auto;
      font-size: 0.84rem;
      color: var(--text-muted);
      font-weight: 600;
    }

    /* 1-Column Full-Width Card List */
    .data-cards-container {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      width: 100%;
    }

    /* Card Item (100% full width, 1 column) */
    .data-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
    }

    .data-card:hover {
      border-color: var(--primary);
      box-shadow: 0 8px 20px var(--primary-shadow);
      transform: translateY(-1px);
    }

    .card-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.85rem;
    }

    .card-title-group {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .card-title-row {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      flex-wrap: wrap;
    }

    .card-id {
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text-heading);
    }

    .card-subtitle {
      font-size: 0.92rem;
      color: var(--text-muted);
      font-weight: 500;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 700;
      letter-spacing: 0.03em;
    }

    .badge-concept {
      background: var(--concept-bg);
      color: var(--concept-color);
      border: 1px solid var(--concept-border);
    }

    .badge-instance {
      background: var(--instance-bg);
      color: var(--instance-color);
      border: 1px solid var(--instance-border);
    }

    .badge-relation {
      background: var(--subclass-bg);
      color: var(--subclass-color);
      border: 1px solid var(--subclass-border);
    }

    .badge-assertion {
      background: var(--assertion-bg);
      color: var(--primary-text);
      border: 1px solid var(--assertion-border);
    }

    .btn-3d-jump {
      background: var(--primary-light);
      color: var(--primary-text);
      border: 1px solid var(--primary-border);
      font-size: 0.82rem;
      padding: 0.4rem 0.85rem;
      border-radius: 7px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-weight: 700;
      transition: all 0.15s ease;
      white-space: nowrap;
    }

    .btn-3d-jump:hover {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
      box-shadow: 0 2px 8px var(--primary-shadow);
    }

    /* Card Structured Information Rows */
    .card-info-section {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }

    .info-line {
      display: flex;
      align-items: baseline;
      gap: 0.75rem;
      padding: 0.55rem 0.85rem;
      background: var(--bg-body);
      border-radius: 6px;
      border: 1px solid var(--border-color);
      font-size: 0.88rem;
    }

    .info-line-label {
      font-weight: 700;
      color: var(--text-sub);
      min-width: 140px;
      flex-shrink: 0;
    }

    .info-line-value {
      color: var(--text-main);
      word-break: break-word;
      flex: 1;
    }

    /* Attributes Table inside Card */
    .attributes-box {
      border: 1px solid var(--border-color);
      border-radius: 8px;
      overflow: hidden;
      margin-top: 0.25rem;
    }

    .attributes-header {
      background: var(--bg-subtle);
      padding: 0.5rem 0.85rem;
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-sub);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
    }

    .attr-row {
      display: flex;
      align-items: flex-start;
      padding: 0.6rem 0.85rem;
      border-bottom: 1px solid var(--border-color);
      font-size: 0.88rem;
      background: var(--bg-card);
      gap: 1rem;
    }
    .attr-row:last-child {
      border-bottom: none;
    }
    .attr-row:nth-child(even) {
      background: var(--bg-subtle);
    }

    .attr-name {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: var(--primary-text);
      min-width: 150px;
      flex-shrink: 0;
    }

    .attr-type-pill {
      display: inline-block;
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      background: var(--border-color);
      color: var(--text-sub);
      margin-right: 0.5rem;
    }

    .attr-value {
      flex: 1;
      color: var(--text-main);
      line-height: 1.5;
    }

    .text-quote-box {
      background: var(--bg-body);
      border-left: 3px solid var(--primary);
      padding: 0.5rem 0.85rem;
      border-radius: 0 6px 6px 0;
      color: var(--text-sub);
      font-size: 0.88rem;
      line-height: 1.55;
      margin-top: 0.25rem;
    }

    /* ========================================= */
    /* THEME CUSTOMIZER MODAL                    */
    /* ========================================= */
    .theme-modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.4);
      backdrop-filter: blur(4px);
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      animation: fadeIn 0.15s ease-out;
    }

    .theme-modal {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 480px;
      max-width: 92vw;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      animation: scaleUp 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes scaleUp {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    .theme-modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.75rem;
    }

    .theme-modal-title {
      font-size: 1.15rem;
      font-weight: 800;
      color: var(--text-heading);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .color-grid {
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }

    .color-field {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.55rem 0.85rem;
      background: var(--bg-body);
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }

    .color-label-group {
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }

    .color-label {
      font-size: 0.88rem;
      font-weight: 700;
      color: var(--text-heading);
    }

    .color-desc {
      font-size: 0.76rem;
      color: var(--text-muted);
    }

    .color-input-wrapper {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .color-input-wrapper input[type="color"] {
      -webkit-appearance: none;
      border: 2px solid var(--border-color);
      border-radius: 8px;
      width: 42px;
      height: 34px;
      cursor: pointer;
      background: transparent;
      padding: 0;
    }

    .color-input-wrapper input[type="color"]::-webkit-color-swatch-wrapper {
      padding: 0;
    }
    .color-input-wrapper input[type="color"]::-webkit-color-swatch {
      border: none;
      border-radius: 6px;
    }

    .color-hex-text {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: var(--text-sub);
      width: 70px;
    }

    .preset-section {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .preset-title {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .preset-list {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.5rem;
    }

    .preset-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.55rem 0.85rem;
      border-radius: 8px;
      border: 1px solid var(--border-color);
      background: var(--bg-body);
      color: var(--text-heading);
      font-size: 0.84rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }

    .preset-btn:hover {
      border-color: var(--primary);
      background: var(--bg-card);
      transform: translateY(-1px);
    }

    .preset-dot {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 1px solid rgba(0,0,0,0.15);
      flex-shrink: 0;
    }

    .theme-modal-footer {
      display: flex;
      justify-content: space-between;
      border-top: 1px solid var(--border-color);
      padding-top: 0.85rem;
      margin-top: 0.25rem;
    }

    /* ========================================= */
    /* VIEW 2: 3D ONTOLOGY GRAPH                 */
    /* ========================================= */
    #graph-view {
      position: relative;
      width: 100%;
      height: calc(100vh - 66px);
      overflow: hidden;
      background: radial-gradient(circle at center, #ffffff 0%, #edf2f7 100%);
    }

    #canvas3d {
      width: 100%;
      height: 100%;
      display: block;
    }

    .hud-overlay {
      position: absolute;
      top: 1.25rem;
      left: 1.25rem;
      z-index: 10;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      max-width: 380px;
    }

    .hud-card {
      background: var(--bg-card);
      opacity: 0.96;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    .hud-card h3 {
      font-size: 0.95rem;
      margin-bottom: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      color: var(--text-heading);
      font-weight: 700;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.65rem;
      font-size: 0.84rem;
      margin-bottom: 0.45rem;
      color: var(--text-sub);
      font-weight: 500;
    }

    .legend-color {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      flex-shrink: 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    .legend-line {
      width: 20px;
      height: 3px;
      border-radius: 2px;
      flex-shrink: 0;
    }

    .hud-controls {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin-top: 0.75rem;
    }

    .drawer-3d {
      position: absolute;
      top: 1.25rem;
      right: 1.25rem;
      width: 380px;
      max-height: calc(100vh - 105px);
      background: var(--bg-card);
      opacity: 0.98;
      border: 1px solid var(--primary);
      border-radius: 14px;
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12), 0 0 16px var(--primary-shadow);
      padding: 1.35rem;
      z-index: 20;
      display: none;
      flex-direction: column;
      gap: 1rem;
      overflow-y: auto;
      animation: slideInRight 0.25s ease-out;
    }

    @keyframes slideInRight {
      from { transform: translateX(30px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    .drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 0.75rem;
    }

    .drawer-close {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 1.4rem;
      line-height: 1;
      padding: 0.2rem;
    }
    .drawer-close:hover {
      color: var(--text-heading);
    }

    .tooltip-3d {
      position: absolute;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid var(--primary);
      color: #ffffff;
      padding: 0.4rem 0.75rem;
      border-radius: 6px;
      font-size: 0.82rem;
      font-weight: 600;
      pointer-events: none;
      z-index: 50;
      display: none;
      white-space: nowrap;
      box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }

    .hint-bar {
      position: absolute;
      bottom: 1.25rem;
      left: 50%;
      transform: translateX(-50%);
      background: var(--bg-card);
      opacity: 0.95;
      border: 1px solid var(--border-color);
      border-radius: 30px;
      padding: 0.5rem 1.35rem;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-sub);
      display: flex;
      align-items: center;
      gap: 1.25rem;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
      pointer-events: none;
    }
  </style>
</head>
<body>

  <!-- Top Header Navigation -->
  <header>
    <a href="#" class="brand" onclick="switchView('inspector')">
      <span class="brand-badge" id="brandBadge">#FF8787</span>
      <span>DSA Knowledge Base</span>
    </a>

    <nav class="nav-tabs">
      <button id="tab-inspector" class="nav-tab active" onclick="switchView('inspector')">
        📋 Kiểm tra dữ liệu JSON
      </button>
      <button id="tab-graph" class="nav-tab" onclick="switchView('graph')">
        🌐 Mô hình Ontology 3D
      </button>
    </nav>

    <div class="header-actions">
      <!-- Live Sync Indicator -->
      <div class="live-status-pill" id="liveSyncToggle" onclick="toggleAutoSync()" title="Nhấp để Bật/Tắt tự động đồng bộ thời gian thực">
        <span class="live-dot" id="liveDot"></span>
        <span id="liveStatusText">Live Sync: 3s</span>
      </div>

      <!-- Manual Refresh Button -->
      <button class="btn" onclick="fetchKBData(true)" style="padding: 0.35rem 0.65rem;" title="Làm mới dữ liệu từ file JSON">
        🔄
      </button>

      <div class="header-stats">
        <div class="stat-pill">Khái niệm: <b id="stat-concepts">0</b></div>
        <div class="stat-pill">Kế thừa: <b id="stat-hierarchy">0</b></div>
        <div class="stat-pill">Đối tượng: <b id="stat-instances">0</b></div>
      </div>

      <!-- Color Customizer Button -->
      <button class="btn-theme" onclick="openThemeModal()">
        <span>🎨</span>
        <span>Tuỳ chỉnh màu sắc</span>
      </button>
    </div>
  </header>

  <!-- VIEW 1: DATA INSPECTOR (LIGHT THEME, 1 COLUMN FULL WIDTH) -->
  <div id="inspector-view" class="view-container active">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-title">Danh mục tập tin JSON</div>
      </div>
      <ul class="dataset-list">
        <li class="dataset-item active" onclick="selectDataset('concepts')">
          <span>📁 concepts.json</span>
          <span class="dataset-badge" id="badge-concepts">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('hierarchy')">
          <span>📁 hierarchy.json</span>
          <span class="dataset-badge" id="badge-hierarchy">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('instances')">
          <span>📁 instances.json (data/)</span>
          <span class="dataset-badge" id="badge-instances">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('relations')">
          <span>📁 relations.json</span>
          <span class="dataset-badge" id="badge-relations">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('assertions')">
          <span>📁 assertions.json (data/)</span>
          <span class="dataset-badge" id="badge-assertions">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('rules')">
          <span>📁 rules.json</span>
          <span class="dataset-badge" id="badge-rules">0</span>
        </li>
        <li class="dataset-item" onclick="selectDataset('functions')">
          <span>📁 functions.json</span>
          <span class="dataset-badge" id="badge-functions">0</span>
        </li>
      </ul>
    </aside>

    <!-- Main Inspector Area -->
    <main class="main-content">
      <!-- Search & Dynamic Filters Toolbar -->
      <div class="filter-bar">
        <!-- Row 1: Search -->
        <div class="filter-row-primary">
          <div class="search-box">
            <span style="font-size: 1rem; color: var(--text-muted);">🔍</span>
            <input type="text" id="searchInput" placeholder="Tìm kiếm theo ID, tên, thuộc tính, mô tả..." oninput="handleSearch()">
            <button class="btn" id="clearSearchBtn" style="display: none; padding: 0.2rem 0.5rem; font-size: 0.75rem;" onclick="clearSearch()">✕</button>
          </div>

          <div class="toolbar-actions" style="display: flex; gap: 0.5rem;">
            <button class="btn btn-primary" onclick="switchView('graph')">
              <span>🌐 Mở đồ thị 3D</span>
            </button>
          </div>
        </div>

        <!-- Row 2: Secondary Dynamic Filters -->
        <div class="filter-row-secondary">
          <div class="filter-group" id="filterCategoryGroup">
            <span>Bộ lọc:</span>
            <select class="filter-select" id="filterSelect" onchange="applyFilters()">
              <option value="all">Tất cả mục</option>
            </select>
          </div>

          <div class="filter-group">
            <span>Sắp xếp:</span>
            <select class="filter-select" id="sortSelect" onchange="applyFilters()">
              <option value="default">Mặc định</option>
              <option value="asc">Mã ID (A → Z)</option>
              <option value="desc">Mã ID (Z → A)</option>
            </select>
          </div>

          <button class="btn" onclick="resetFilters()">🔄 Đặt lại bộ lọc</button>

          <div class="count-indicator" id="resultCounter">
            Đang tải dữ liệu JSON...
          </div>
        </div>
      </div>

      <!-- Single Column Full Width Cards Container -->
      <div class="data-cards-container" id="cardsContainer">
        <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
          ⏳ Đang kết nối và tải dữ liệu từ các file JSON trực tiếp...
        </div>
      </div>
    </main>
  </div>

  <!-- VIEW 2: 3D ONTOLOGY GRAPH -->
  <div id="graph-view" class="view-container">
    <canvas id="canvas3d"></canvas>

    <div class="hud-overlay">
      <div class="hud-card">
        <h3><span style="color: var(--primary);">●</span> Chú thích Mô hình 3D Ontology</h3>
        
        <div class="legend-item">
          <span class="legend-color" style="background: var(--concept-color);"></span>
          <span><b>Khái niệm (Concepts)</b> (<span id="hud-count-concepts">0</span>)</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: var(--instance-color);"></span>
          <span><b>Đối tượng (Instances)</b> (<span id="hud-count-instances">0</span>)</span>
        </div>
        <div class="legend-item">
          <span class="legend-line" style="background: var(--subclass-color);"></span>
          <span><b>Kế thừa (subclassOf)</b></span>
        </div>
        <div class="legend-item">
          <span class="legend-line" style="background: var(--relation-color);"></span>
          <span><b>Thể hiện (instanceOf)</b></span>
        </div>
        <div class="legend-item">
          <span class="legend-line" id="legendAssertionLine" style="background: var(--primary); height: 4px;"></span>
          <span><b>Phán đoán thực tế (Assertions)</b></span>
        </div>

        <div class="hud-controls">
          <button class="btn" onclick="resetCamera()">🎯 Đặt lại góc nhìn</button>
          <button class="btn" id="autoRotateBtn" onclick="toggleAutoRotate()">🔄 Xoay tự động: Bật</button>
        </div>
      </div>
    </div>

    <div class="drawer-3d" id="drawer3d">
      <div class="drawer-header">
        <div>
          <span class="badge" id="drawerBadge">CONCEPT</span>
          <h2 class="card-id" id="drawerId" style="font-size: 1.15rem; margin-top: 0.35rem;">Id</h2>
        </div>
        <button class="drawer-close" onclick="closeDrawer()">&times;</button>
      </div>
      <div id="drawerBody" style="display: flex; flex-direction: column; gap: 0.75rem;">
      </div>
      <button class="btn btn-primary" id="drawerJumpBtn" style="margin-top: 0.5rem; justify-content: center;">
        📋 Xem trong Data Inspector
      </button>
    </div>

    <div class="tooltip-3d" id="tooltip3d">Tooltip</div>

    <div class="hint-bar">
      <span>🖱️ Chuột trái: Xoay 3D</span>
      <span>🖱️ Chuột phải: Di chuyển</span>
      <span>⚙️ Cuộn: Zoom</span>
      <span>👆 Nhấp vào Node: Xem thông tin chi tiết</span>
    </div>
  </div>

  <!-- THEME CUSTOMIZER MODAL -->
  <div class="theme-modal-backdrop" id="themeModalBackdrop" onclick="closeThemeModalOnBackdrop(event)">
    <div class="theme-modal">
      <div class="theme-modal-header">
        <div class="theme-modal-title">
          <span>🎨</span>
          <span>Tuỳ chỉnh màu sắc giao diện</span>
        </div>
        <button class="drawer-close" onclick="closeThemeModal()">&times;</button>
      </div>

      <div class="color-grid">
        <div class="color-field">
          <div class="color-label-group">
            <span class="color-label">Màu chủ đạo (Accent):</span>
            <span class="color-desc">Logo, nút chính, đường phán đoán 3D</span>
          </div>
          <div class="color-input-wrapper">
            <span class="color-hex-text" id="hex-primary">#FF8787</span>
            <input type="color" id="picker-primary" value="#FF8787" oninput="updateThemeColor('primary', this.value)">
          </div>
        </div>

        <div class="color-field">
          <div class="color-label-group">
            <span class="color-label">Màu nền trang (Background):</span>
            <span class="color-desc">Màu nền toàn trang và nội dung</span>
          </div>
          <div class="color-input-wrapper">
            <span class="color-hex-text" id="hex-bg-body">#f8fafc</span>
            <input type="color" id="picker-bg-body" value="#f8fafc" oninput="updateThemeColor('bgBody', this.value)">
          </div>
        </div>

        <div class="color-field">
          <div class="color-label-group">
            <span class="color-label">Màu nền khung / thẻ (Card Bg):</span>
            <span class="color-desc">Màu nền các thẻ dữ liệu, header, sidebar</span>
          </div>
          <div class="color-input-wrapper">
            <span class="color-hex-text" id="hex-bg-card">#ffffff</span>
            <input type="color" id="picker-bg-card" value="#ffffff" oninput="updateThemeColor('bgCard', this.value)">
          </div>
        </div>

        <div class="color-field">
          <div class="color-label-group">
            <span class="color-label">Màu chữ chính (Text Color):</span>
            <span class="color-desc">Màu chữ nội dung, tiêu đề, mã định danh</span>
          </div>
          <div class="color-input-wrapper">
            <span class="color-hex-text" id="hex-text-main">#0f172a</span>
            <input type="color" id="picker-text-main" value="#0f172a" oninput="updateThemeColor('textMain', this.value)">
          </div>
        </div>

        <div class="color-field">
          <div class="color-label-group">
            <span class="color-label">Màu đường viền (Border / Frame):</span>
            <span class="color-desc">Đường viền thẻ, khung bảng, thanh phân cách</span>
          </div>
          <div class="color-input-wrapper">
            <span class="color-hex-text" id="hex-border">#e2e8f0</span>
            <input type="color" id="picker-border" value="#e2e8f0" oninput="updateThemeColor('border', this.value)">
          </div>
        </div>
      </div>

      <div class="preset-section">
        <div class="preset-title">Giao diện mẫu có sẵn (Presets)</div>
        <div class="preset-list">
          <button class="preset-btn" onclick="applyPreset('default_light')">
            <span class="preset-dot" style="background: #FF8787;"></span>
            <span>Sáng San hô (#FF8787)</span>
          </button>
          <button class="preset-btn" onclick="applyPreset('dark_slate')">
            <span class="preset-dot" style="background: #38bdf8;"></span>
            <span>Tối Hiện đại (Dark Slate)</span>
          </button>
          <button class="preset-btn" onclick="applyPreset('ocean_blue')">
            <span class="preset-dot" style="background: #2563eb;"></span>
            <span>Đại dương Xanh (Ocean)</span>
          </button>
          <button class="preset-btn" onclick="applyPreset('warm_sepia')">
            <span class="preset-dot" style="background: #b45309;"></span>
            <span>Giấy ấm (Warm Sepia)</span>
          </button>
        </div>
      </div>

      <div class="theme-modal-footer">
        <button class="btn" onclick="resetThemeDefaults()">
          <span>🔄</span>
          <span>Khôi phục mặc định</span>
        </button>
        <button class="btn btn-primary" onclick="closeThemeModal()">
          <span>✓</span>
          <span>Hoàn tất & Đóng</span>
        </button>
      </div>
    </div>
  </div>

  <script>
    // =========================================================================
    // DYNAMIC & REAL-TIME KNOWLEDGE BASE DATA LOADING
    // =========================================================================
    let KB_DATA = {
      concepts: [],
      hierarchy: [],
      instances: [],
      relations: [],
      assertions: [],
      rules: [],
      operands: [],
      functions: []
    };

    let currentDataset = 'concepts';
    let lastDataFingerprint = '';
    let autoSyncEnabled = true;
    let autoSyncTimer = null;

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
      const [cData, iData, rData, aData, ruData, hData, fData] = await Promise.all([
        fetchJSONFile(`./ontology/concepts.json?_t=${t}`),
        fetchFirstAvailable([`./data/instances.json?_t=${t}`, `./ontology/instances.json?_t=${t}`]),
        fetchJSONFile(`./ontology/relations.json?_t=${t}`),
        fetchFirstAvailable([`./data/assertions.json?_t=${t}`, `./ontology/assertions.json?_t=${t}`]),
        fetchJSONFile(`./ontology/rules.json?_t=${t}`),
        fetchFirstAvailable([`./ontology/hierarchy.json?_t=${t}`, `./ontology/hierachy.json?_t=${t}`]),
        fetchJSONFile(`./ontology/functions.json?_t=${t}`)
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
      const instances = (iData && iData.instances) ? iData.instances : [];
      const relations = (rData && rData.relations) ? rData.relations : [];
      const assertions = (aData && aData.assertions) ? aData.assertions : [];
      const rules = (ruData && ruData.rules) ? ruData.rules : [];
      const functions = (fData && fData.functions) ? fData.functions : [];

      // Create fingerprint to detect changes
      const fingerprint = `${concepts.length}_${hierarchy.length}_${instances.length}_${relations.length}_${assertions.length}_${rules.length}_${functions.length}_${JSON.stringify(concepts).length}_${JSON.stringify(instances).length}`;

      if (fingerprint !== lastDataFingerprint || manualTrigger) {
        lastDataFingerprint = fingerprint;

        KB_DATA.concepts = concepts;
        KB_DATA.hierarchy = hierarchy;
        KB_DATA.instances = instances;
        KB_DATA.relations = relations;
        KB_DATA.assertions = assertions;
        KB_DATA.rules = rules;
        KB_DATA.functions = functions;

        // Update header & sidebar counters
        updateHeaderAndSidebarStats();

        // Refresh dropdown filter options and cards
        setupFilterDropdown();
        applyFilters();

        // If 3D graph is already active, refresh nodes
        if (graphInitialized) {
          refresh3DGraphData();
        }

        if (manualTrigger) {
          showLiveNotification('Đã tải lại dữ liệu mới nhất từ file JSON!');
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
      const bF = document.getElementById('badge-functions');
      const fLen = (KB_DATA.functions || []).length;
      if (bC) bC.innerText = cLen;
      if (bI) bI.innerText = iLen;
      if (bR) bR.innerText = rLen;
      if (bA) bA.innerText = aLen;
      if (bRu) bRu.innerText = ruLen;
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
        text.innerText = 'Live Sync: 3s';
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
        text.innerText = autoSyncEnabled ? 'Live Sync: 3s' : 'Live: Tạm dừng';
      }, 2000);
    }

    // =========================================================================
    // THEME CUSTOMIZER LOGIC
    // =========================================================================
    const DEFAULT_THEME = {
      primary: '#FF8787',
      bgBody: '#f8fafc',
      bgCard: '#ffffff',
      textMain: '#0f172a',
      border: '#e2e8f0'
    };

    const PRESETS = {
      default_light: {
        primary: '#FF8787',
        bgBody: '#f8fafc',
        bgCard: '#ffffff',
        textMain: '#0f172a',
        border: '#e2e8f0'
      },
      dark_slate: {
        primary: '#FF8787',
        bgBody: '#0f172a',
        bgCard: '#1e293b',
        textMain: '#f8fafc',
        border: '#334155'
      },
      ocean_blue: {
        primary: '#38bdf8',
        bgBody: '#f0f9ff',
        bgCard: '#ffffff',
        textMain: '#0c4a6e',
        border: '#bae6fd'
      },
      warm_sepia: {
        primary: '#d97706',
        bgBody: '#fefce8',
        bgCard: '#ffffff',
        textMain: '#451a03',
        border: '#fde68a'
      }
    };

    let currentTheme = Object.assign({}, DEFAULT_THEME);

    function loadSavedTheme() {
      try {
        const saved = localStorage.getItem('dsa_kb_custom_theme');
        if (saved) {
          currentTheme = Object.assign({}, DEFAULT_THEME, JSON.parse(saved));
        }
      } catch (e) {
        console.error('Could not load saved theme', e);
      }
      applyThemeToDOM();
    }

    function saveCurrentTheme() {
      try {
        localStorage.setItem('dsa_kb_custom_theme', JSON.stringify(currentTheme));
      } catch (e) {
        console.error('Could not save theme', e);
      }
    }

    function applyThemeToDOM() {
      const root = document.documentElement;

      root.style.setProperty('--primary', currentTheme.primary);
      root.style.setProperty('--primary-hover', adjustColorBrightness(currentTheme.primary, -15));
      root.style.setProperty('--primary-light', hexToRgba(currentTheme.primary, 0.12));
      root.style.setProperty('--primary-border', hexToRgba(currentTheme.primary, 0.35));
      root.style.setProperty('--primary-text', currentTheme.primary);
      root.style.setProperty('--primary-shadow', hexToRgba(currentTheme.primary, 0.25));

      root.style.setProperty('--bg-body', currentTheme.bgBody);
      root.style.setProperty('--bg-card', currentTheme.bgCard);
      root.style.setProperty('--bg-subtle', adjustColorBrightness(currentTheme.bgBody, -4));

      root.style.setProperty('--border-color', currentTheme.border);
      root.style.setProperty('--border-hover', adjustColorBrightness(currentTheme.border, -10));

      root.style.setProperty('--text-main', currentTheme.textMain);
      root.style.setProperty('--text-heading', currentTheme.textMain);
      root.style.setProperty('--text-sub', hexToRgba(currentTheme.textMain, 0.8));
      root.style.setProperty('--text-muted', hexToRgba(currentTheme.textMain, 0.6));

      const badge = document.getElementById('brandBadge');
      if (badge) badge.innerText = currentTheme.primary.toUpperCase();

      updatePickerValues();

      if (graphInitialized && assertionEdgeMaterial) {
        assertionEdgeMaterial.color.set(currentTheme.primary);
      }
    }

    function updatePickerValues() {
      const pPrimary = document.getElementById('picker-primary');
      const pBgBody = document.getElementById('picker-bg-body');
      const pBgCard = document.getElementById('picker-bg-card');
      const pTextMain = document.getElementById('picker-text-main');
      const pBorder = document.getElementById('picker-border');

      if (pPrimary) {
        pPrimary.value = currentTheme.primary;
        document.getElementById('hex-primary').innerText = currentTheme.primary;
      }
      if (pBgBody) {
        pBgBody.value = currentTheme.bgBody;
        document.getElementById('hex-bg-body').innerText = currentTheme.bgBody;
      }
      if (pBgCard) {
        pBgCard.value = currentTheme.bgCard;
        document.getElementById('hex-bg-card').innerText = currentTheme.bgCard;
      }
      if (pTextMain) {
        pTextMain.value = currentTheme.textMain;
        document.getElementById('hex-text-main').innerText = currentTheme.textMain;
      }
      if (pBorder) {
        pBorder.value = currentTheme.border;
        document.getElementById('hex-border').innerText = currentTheme.border;
      }
    }

    function updateThemeColor(prop, value) {
      currentTheme[prop] = value;
      applyThemeToDOM();
      saveCurrentTheme();
    }

    function applyPreset(presetKey) {
      const preset = PRESETS[presetKey];
      if (preset) {
        currentTheme = Object.assign({}, preset);
        applyThemeToDOM();
        saveCurrentTheme();
      }
    }

    function resetThemeDefaults() {
      currentTheme = Object.assign({}, DEFAULT_THEME);
      applyThemeToDOM();
      saveCurrentTheme();
    }

    function openThemeModal() {
      document.getElementById('themeModalBackdrop').style.display = 'flex';
      updatePickerValues();
    }

    function closeThemeModal() {
      document.getElementById('themeModalBackdrop').style.display = 'none';
    }

    function closeThemeModalOnBackdrop(e) {
      if (e.target.id === 'themeModalBackdrop') {
        closeThemeModal();
      }
    }

    function hexToRgba(hex, alpha = 1) {
      let c = hex.replace('#', '');
      if (c.length === 3) c = c.split('').map(x => x + x).join('');
      const num = parseInt(c, 16);
      return `rgba(${(num >> 16) & 255}, ${(num >> 8) & 255}, ${num & 255}, ${alpha})`;
    }

    function adjustColorBrightness(hex, percent) {
      let c = hex.replace('#', '');
      if (c.length === 3) c = c.split('').map(x => x + x).join('');
      const num = parseInt(c, 16);
      let r = (num >> 16) + percent;
      let g = ((num >> 8) & 0x00FF) + percent;
      let b = (num & 0x0000FF) + percent;
      r = Math.min(255, Math.max(0, r));
      g = Math.min(255, Math.max(0, g));
      b = Math.min(255, Math.max(0, b));
      return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    // =========================================================================
    // VIEW SWITCHER & DATASET
    // =========================================================================
    function switchView(viewName) {
      const inspectorView = document.getElementById('inspector-view');
      const graphView = document.getElementById('graph-view');
      const tabInspector = document.getElementById('tab-inspector');
      const tabGraph = document.getElementById('tab-graph');

      if (viewName === 'inspector') {
        inspectorView.classList.add('active');
        graphView.classList.remove('active');
        tabInspector.classList.add('active');
        tabGraph.classList.remove('active');
      } else {
        inspectorView.classList.remove('active');
        graphView.classList.add('active');
        tabInspector.classList.remove('active');
        tabGraph.classList.add('active');
        if (!graphInitialized) {
          init3DGraph();
        } else {
          onWindowResize();
          refresh3DGraphData();
        }
      }
    }

    function selectDataset(name) {
      currentDataset = name;
      document.querySelectorAll('.dataset-item').forEach(el => {
        el.classList.remove('active');
      });
      event.currentTarget.classList.add('active');
      
      setupFilterDropdown();
      document.getElementById('searchInput').value = '';
      document.getElementById('sortSelect').value = 'default';
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
        if (item.target && item.target.toLowerCase().includes(query)) return true;
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
            <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-heading);">Không tìm thấy dữ liệu phù hợp</div>
            <div style="font-size: 0.9rem; margin-top: 0.35rem; color: var(--text-muted);">Hãy thử nhập từ khoá khác hoặc bấm "Đặt lại bộ lọc" để xem toàn bộ danh sách.</div>
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

        function renderFunctionCard(card, item) {
      const inputs = (item.input || []).map(p => `<code>${p.name}: ${p.valueType || p.value_type}</code>`).join(', ') || 'None';
      let outStr = 'void';
      if (item.output) {
        if (Array.isArray(item.output)) {
          outStr = item.output.map(p => `<code>${p.name}: ${p.valueType || p.value_type}</code>`).join(', ');
        } else {
          outStr = `<code>${item.output.name}: ${item.output.valueType || item.output.value_type}</code>`;
        }
      }
      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge" style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;">HÀM (FUNCTION)</span>
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
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Lớp con (Subclass)</div>
            <a href="#" onclick="filterConcept('${sub}'); return false;" style="font-weight: 700; color: var(--concept-color); text-decoration: none; font-size: 0.95rem;">${sub} ↗</a>
          </div>
          <div style="color: var(--subclass-color); font-weight: 800; font-size: 1.2rem;">➔</div>
          <div style="flex: 1; text-align: center;">
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Lớp cha (Superclass)</div>
            <a href="#" onclick="filterConcept('${sup}'); return false;" style="font-weight: 700; color: var(--subclass-color); text-decoration: none; font-size: 0.95rem;">${sup} ↗</a>
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
            constraintStr = ` <span style="font-size: 0.78rem; color: var(--text-muted);">(Ràng buộc: ${JSON.stringify(attr.constraint)})</span>`;
          }
          const reqBadge = attr.required 
            ? `<span style="font-size: 0.72rem; color: #ef4444; font-weight: 700; margin-left: 0.4rem;">*Bắt buộc</span>` 
            : `<span style="font-size: 0.72rem; color: var(--text-muted); margin-left: 0.4rem;">(Tuỳ chọn)</span>`;
          return `
            <div class="attr-row">
              <span class="attr-name">${attr.name || 'attr'}${reqBadge}</span>
              <div class="attr-value">
                <span class="attr-type-pill">${attr.value_type || 'any'}</span>
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
            if (typeof op === 'string') return `<div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: var(--concept-color);">• ${op}</div>`;
            const inputs = (op.input || []).map(p => `${p.name}: ${p.valueType || p.value_type}`).join(', ');
            const out = op.output ? (op.output.name ? `${op.output.name}: ${op.output.valueType || op.output.value_type}` : JSON.stringify(op.output)) : 'void';
            return `<div style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: var(--concept-color);">• <b>${op.name}</b>(${inputs}) ➔ ${out}${op.description ? ` <span style="color: var(--text-muted); font-family: sans-serif;">(${op.description})</span>` : ''}</div>`;
          }).join('') +
          `</div>`;
      }

      let invHtml = '<span style="color: var(--text-muted); font-style: italic;">Không có</span>';
      if (Array.isArray(item.invariant) && item.invariant.length > 0) {
        invHtml = `<div style="display: flex; flex-direction: column; gap: 0.35rem; margin-top: 0.35rem;">` +
          item.invariant.map(inv => {
            if (typeof inv === 'string') return `<div class="text-quote-box">${inv}</div>`;
            return `<div class="text-quote-box"><b>${inv.name}</b>: ${inv.description || ''} <code style="font-size: 0.8rem;">[${inv.condition ? inv.condition.operator : ''}]</code></div>`;
          }).join('') +
          `</div>`;
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.id}</span>
              <span class="badge badge-concept">KHÁI NIỆM (CONCEPT)</span>
              ${item.domain ? `<span class="badge" style="background: var(--bg-subtle); color: var(--text-sub); border: 1px solid var(--border-color);">Miền: ${item.domain}</span>` : ''}
            </div>
            <span class="card-subtitle">${item.name || ''}</span>
          </div>

          <button class="btn-3d-jump" onclick="jumpTo3D('${item.id}')">
            👁️ Xem trên 3D
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
              <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">${item.attributes ? item.attributes.length : 0} thuộc tính</span>
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
                  : `<b style="color: var(--text-heading); font-family: 'JetBrains Mono'; font-size: 0.92rem;">${attr.value}</b>`
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
              <span class="badge badge-instance">ĐỐI TƯỢNG (INSTANCE)</span>
            </div>
            <span class="card-subtitle">Thể hiện thực tế của mô hình dữ liệu</span>
          </div>

          <button class="btn-3d-jump" onclick="jumpTo3D('${item.id}')">
            👁️ Xem trên 3D
          </button>
        </div>

        <div class="card-info-section">
          <div class="info-line">
            <span class="info-line-label">Thuộc khái niệm:</span>
            <div class="info-line-value">${instanceOfHtml}</div>
          </div>

          <div class="info-line" style="flex-direction: column; align-items: stretch; gap: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="info-line-label">Dữ liệu thuộc tính chi tiết:</span>
              <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">${item.attributes ? item.attributes.length : 0} trường</span>
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
              ${attr.constraint ? `<span style="font-size: 0.8rem; color: var(--text-muted);">(Ràng buộc: ${JSON.stringify(attr.constraint)})</span>` : ''}
            </div>
          </div>
        `).join('');
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge badge-relation">QUAN HỆ (RELATION)</span>
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
              <b style="color: var(--concept-color);">${item.target}</b>
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
              <span class="badge badge-assertion">PHÁN ĐOÁN (ASSERTION)</span>
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
              <b style="color: var(--instance-color); font-family: 'JetBrains Mono'; font-size: 0.95rem;">${item.source}</b>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Vị từ (Relation / Predicate):</span>
            <div class="info-line-value">
              <span class="badge badge-assertion" style="font-size: 0.84rem;">${item.relation}</span>
            </div>
          </div>

          <div class="info-line">
            <span class="info-line-label">Đối tượng (Target / Object):</span>
            <div class="info-line-value">
              <b style="color: var(--instance-color); font-family: 'JetBrains Mono'; font-size: 0.95rem;">${item.target}</b>
            </div>
          </div>

          ${attrHtml}
        </div>
      `;
    }

    function renderRuleCard(card, item) {
      let condListHtml = '';
      if (item.condition && item.condition.operands) {
        condListHtml = item.condition.operands.map((op, idx) => {
          const relVal = op.operands && op.operands[0] ? op.operands[0].value : '';
          const instVal = op.operands && op.operands[1] ? op.operands[1].value : '';
          return `
            <div class="info-line" style="margin-bottom: 0.35rem; background: var(--bg-card);">
              <span style="font-weight: 700; color: var(--primary-text); min-width: 30px;">#${idx + 1}</span>
              <div style="flex: 1; font-size: 0.88rem;">
                Tồn tại quan hệ <b style="color: var(--subclass-color);">${relVal}</b> với thực thể <b style="color: var(--instance-color);">${instVal}</b>
              </div>
            </div>
          `;
        }).join('');
      }

      let conclListHtml = '';
      if (Array.isArray(item.conclusion)) {
        conclListHtml = item.conclusion.map(c => `
          <div class="text-quote-box" style="margin-top: 0.35rem;">
            Gán thuộc tính <b>${c.attribute_name}</b> = <span style="color: #059669; font-weight: 700;">${c.value}</span> (kiểu ${c.valueType}) cho thực thể <b style="color: var(--instance-color);">${c.target_instance}</b>
          </div>
        `).join('');
      }

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-title-row">
              <span class="card-id">${item.name || item.id}</span>
              <span class="badge" style="background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe;">LUẬT SUY DIỄN (RULE)</span>
            </div>
            <span class="card-subtitle">Mã luật: <code>${item.id}</code></span>
          </div>
        </div>

        <div class="card-info-section">
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
    // 3D GRAPH VISUALIZATION (THREE.JS)
    // =========================================================================
    let graphInitialized = false;
    let scene, camera, renderer, controls;
    let nodeMeshes = [];
    let edgeLines = [];
    let labelSprites = [];
    let raycaster, mouse;
    let autoRotate = true;
    let hoveredNode = null;
    let nodesMap = {};
    let assertionEdgeMaterial = null;

    function init3DGraph() {
      const container = document.getElementById('graph-view');
      const canvas = document.getElementById('canvas3d');

      const width = container.clientWidth || window.innerWidth;
      const height = container.clientHeight || (window.innerHeight - 66);

      scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0xf1f5f9, 0.0016);

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

      const pointLight = new THREE.PointLight(0xFF8787, 1.8, 800);
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
          name: c.name || c.id,
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
        color: 0x2563eb,
        roughness: 0.25,
        metalness: 0.2
      });

      const instanceGeo = new THREE.OctahedronGeometry(3.4, 0);
      const instanceMat = new THREE.MeshStandardMaterial({
        color: 0x059669,
        roughness: 0.25,
        metalness: 0.2
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
          const sprite = createTextSprite(node.id, '#0f172a');
          sprite.position.set(node.x, node.y + 7.5, node.z);
          scene.add(sprite);
          labelSprites.push(sprite);
        }
      });

      // 1. subclassOf -> Amber
      const subclassMat = new THREE.LineBasicMaterial({
        color: 0xd97706,
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
        color: 0x7c3aed,
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
      ctx.font = 'bold 22px Plus Jakarta Sans, sans-serif';
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

      badge.innerText = node.type === 'concept' ? 'KHÁI NIỆM' : 'ĐỐI TƯỢNG';
      badge.className = 'badge ' + (node.type === 'concept' ? 'badge-concept' : 'badge-instance');
      idEl.innerText = node.id;

      let html = '';
      const data = node.data || {};

      if (node.type === 'concept') {
        html += `<div style="color: var(--text-muted); font-size: 0.88rem; font-weight: 600;">${data.name || ''}</div>`;
        if (data.domain) html += `<div class="info-line"><span class="info-line-label">Miền dữ liệu:</span><div class="info-line-value">${data.domain}</div></div>`;
        if (data.subclassOf) html += `<div class="info-line"><span class="info-line-label">Kế thừa:</span><div class="info-line-value"><b style="color: var(--subclass-color);">${data.subclassOf}</b></div></div>`;
        
        if (Array.isArray(data.attributes) && data.attributes.length > 0) {
          html += '<div style="margin-top: 0.35rem; font-weight: 700; font-size: 0.84rem; color: var(--text-sub);">Thuộc tính định nghĩa:</div>';
          html += '<div class="attributes-box">';
          data.attributes.forEach(attr => {
            html += `<div class="attr-row"><span class="attr-name">${attr.name}</span><span class="attr-type-pill">${attr.value_type}</span></div>`;
          });
          html += '</div>';
        }
      } else {
        html += `<div class="info-line"><span class="info-line-label">Thuộc khái niệm:</span><div class="info-line-value"><b style="color: var(--concept-color);">${data.instanceOf || 'N/A'}</b></div></div>`;
        if (Array.isArray(data.attributes) && data.attributes.length > 0) {
          html += '<div style="margin-top: 0.35rem; font-weight: 700; font-size: 0.84rem; color: var(--text-sub);">Giá trị thuộc tính:</div>';
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
      document.getElementById('autoRotateBtn').innerText = `🔄 Xoay tự động: ${autoRotate ? 'Bật' : 'Tắt'}`;
    }

    function animate() {
      requestAnimationFrame(animate);

      if (autoRotate && !hoveredNode) {
        scene.rotation.y += 0.0012;
      }

      controls.update();
      renderer.render(scene, camera);
    }

    // Window focus triggers immediate data check
    window.addEventListener('focus', () => {
      if (autoSyncEnabled) {
        fetchKBData(false);
      }
    });

    // Initial load
    document.addEventListener('DOMContentLoaded', () => {
      loadSavedTheme();
      fetchKBData(true);
      startAutoSync();
    });
  </script>
</body>
</html>
'''

dest_1 = os.path.join(base_dir, 'ontology_viewer.html')
dest_2 = os.path.join(base_dir, 'index.html')
kb_root = os.path.dirname(base_dir)
dest_3 = os.path.join(kb_root, 'index.html')

for dest in [dest_1, dest_2, dest_3]:
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated Dynamic Real-time UI at: {dest}")

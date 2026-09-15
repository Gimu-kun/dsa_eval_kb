    // THEME CUSTOMIZER LOGIC
    // =========================================================================
    var DEFAULT_THEME = {
      primary: '#6B7F6E',
      bgBody: '#F3EEE6',
      bgCard: '#FFFcf7',
      textMain: '#2A241C',
      border: '#E4D9C8'
    };

    var PRESETS = {
      default_light: {
        primary: '#6B7F6E',
        bgBody: '#F3EEE6',
        bgCard: '#FFFcf7',
        textMain: '#2A241C',
        border: '#E4D9C8'
      },
      porcelain: {
        primary: '#6A7C8C',
        bgBody: '#F4F1EC',
        bgCard: '#FFFEFB',
        textMain: '#2B3036',
        border: '#DDD6CC'
      },
      parchment: {
        primary: '#A07840',
        bgBody: '#F6F0E4',
        bgCard: '#FFFBF3',
        textMain: '#2C2418',
        border: '#E6D8BE'
      },
      dawn: {
        primary: '#B08986',
        bgBody: '#F7F1EE',
        bgCard: '#FFFBFA',
        textMain: '#2C2422',
        border: '#E8D9D4'
      }
    };

    var currentTheme = Object.assign({}, DEFAULT_THEME);

    function loadSavedTheme() {
      try {
        const saved = localStorage.getItem('dsa_kb_custom_theme_v2');
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
        localStorage.setItem('dsa_kb_custom_theme_v2', JSON.stringify(currentTheme));
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
      root.style.setProperty('--primary-text', adjustColorBrightness(currentTheme.primary, -28));
      root.style.setProperty('--primary-shadow', hexToRgba(currentTheme.primary, 0.16));
      root.style.setProperty('--bg-wash', hexToRgba(currentTheme.bgCard, 0.82));

      root.style.setProperty('--bg-body', currentTheme.bgBody);
      root.style.setProperty('--bg-card', currentTheme.bgCard);
      root.style.setProperty('--bg-subtle', adjustColorBrightness(currentTheme.bgBody, -4));

      root.style.setProperty('--border-color', currentTheme.border);
      root.style.setProperty('--border-hover', adjustColorBrightness(currentTheme.border, -10));
      root.style.setProperty('--border-focus', currentTheme.primary);

      root.style.setProperty('--text-main', currentTheme.textMain);
      root.style.setProperty('--text-heading', currentTheme.textMain);
      root.style.setProperty('--text-sub', hexToRgba(currentTheme.textMain, 0.72));
      root.style.setProperty('--text-muted', hexToRgba(currentTheme.textMain, 0.52));
      root.style.setProperty('--text-light', hexToRgba(currentTheme.textMain, 0.38));

      const badge = document.getElementById('brandBadge');
      if (badge) badge.style.background = currentTheme.primary;

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

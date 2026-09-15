    // VIEW SWITCHER & DATASET
    // =========================================================================
    function switchView(viewName) {
      const inspectorView = document.getElementById('inspector-view');
      const graphView = document.getElementById('graph-view');
      const questionsView = document.getElementById('questions-view');
      const dashboardView = document.getElementById('dashboard-view');
      const tabInspector = document.getElementById('tab-inspector');
      const tabGraph = document.getElementById('tab-graph');
      const tabQuestions = document.getElementById('tab-questions');
      const tabDashboard = document.getElementById('tab-dashboard');

      inspectorView.classList.remove('active');
      graphView.classList.remove('active');
      questionsView.classList.remove('active');
      if (dashboardView) dashboardView.classList.remove('active');
      tabInspector.classList.remove('active');
      tabGraph.classList.remove('active');
      tabQuestions.classList.remove('active');
      if (tabDashboard) tabDashboard.classList.remove('active');

      if (viewName === 'inspector') {
        inspectorView.classList.add('active');
        tabInspector.classList.add('active');
      } else if (viewName === 'questions') {
        questionsView.classList.add('active');
        tabQuestions.classList.add('active');
        renderQuestionExplorer();
      } else if (viewName === 'dashboard') {
        dashboardView.classList.add('active');
        tabDashboard.classList.add('active');
        renderDashboard();
      } else {
        graphView.classList.add('active');
        tabGraph.classList.add('active');
        if (!graphInitialized) {
          init3DGraph();
        } else {
          onWindowResize();
          refresh3DGraphData();
        }
      }
    }

    document.addEventListener('DOMContentLoaded', () => {
      loadSavedTheme();
      fetchKBData(true);
      startAutoSync();
    });

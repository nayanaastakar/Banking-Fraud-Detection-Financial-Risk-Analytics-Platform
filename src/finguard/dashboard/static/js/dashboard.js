/**
 * FinGuard Interactive Analytics Dashboard - Client Application Logic
 */

// Application State
const state = {
  theme: localStorage.getItem('finguard_theme') || 'dark',
  activeTab: 'overview',
  filters: {
    model: 'random_forest',
    time_band: '',
    amount_band: '',
    outcome: '',
    class_label: '',
    threshold: 0.70,
    search: '',
    page: 1,
    limit: 15,
    sort_by: 'transaction_id',
    sort_dir: 'asc'
  },
  charts: {},
  kpis: null,
  isLiveServer: true
};

// DOM Content Loaded Handler
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNavigation();
  initFilterListeners();
  initSimulatorListeners();
  initTableListeners();
  
  // Initial Fetch & Render
  loadAllDashboardData();
  
  // Set Last Updated Timestamp
  const tsEl = document.getElementById('lastUpdatedTimestamp');
  if (tsEl) {
    tsEl.textContent = new Date().toLocaleString();
  }
});

// 1. Theme Management
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  const themeToggle = document.getElementById('themeToggleBtn');
  if (themeToggle) {
    updateThemeIcon();
    themeToggle.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', state.theme);
      localStorage.setItem('finguard_theme', state.theme);
      updateThemeIcon();
      updateChartsTheme();
    });
  }
}

function updateThemeIcon() {
  const icon = document.getElementById('themeIcon');
  if (icon) {
    icon.innerHTML = state.theme === 'dark' 
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
}

function updateChartsTheme() {
  const isDark = state.theme === 'dark';
  const apexTheme = {
    mode: isDark ? 'dark' : 'light',
    palette: 'palette1'
  };
  Object.values(state.charts).forEach(chart => {
    if (chart && typeof chart.updateOptions === 'function') {
      chart.updateOptions({
        theme: apexTheme,
        grid: { borderColor: isDark ? '#243048' : '#e2e8f0' },
        chart: { background: 'transparent' }
      });
    }
  });
}

// 2. Navigation Tabs
function initNavigation() {
  const tabBtns = document.querySelectorAll('.nav-tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tabKey = btn.dataset.tab;
      switchTab(tabKey);
    });
  });
}

function switchTab(tabKey) {
  state.activeTab = tabKey;
  document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tabKey));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.toggle('active', c.id === `tab-${tabKey}`));
  
  // Trigger chart reflow on tab change
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  }, 100);
}

// 3. Filter Listeners
function initFilterListeners() {
  // Model selector radios
  document.querySelectorAll('.model-radio-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.model-radio-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      state.filters.model = card.dataset.model;
      state.filters.page = 1;
      loadAllDashboardData();
    });
  });

  // Time Band select
  const timeBandSelect = document.getElementById('filterTimeBand');
  if (timeBandSelect) {
    timeBandSelect.addEventListener('change', (e) => {
      state.filters.time_band = e.target.value;
      state.filters.page = 1;
      loadAllDashboardData();
    });
  }

  // Amount Band select
  const amountBandSelect = document.getElementById('filterAmountBand');
  if (amountBandSelect) {
    amountBandSelect.addEventListener('change', (e) => {
      state.filters.amount_band = e.target.value;
      state.filters.page = 1;
      loadAllDashboardData();
    });
  }

  // Outcome status select
  const outcomeSelect = document.getElementById('filterOutcome');
  if (outcomeSelect) {
    outcomeSelect.addEventListener('change', (e) => {
      state.filters.outcome = e.target.value;
      state.filters.page = 1;
      loadAllDashboardData();
    });
  }

  // Threshold slider (left sidebar)
  const threshSlider = document.getElementById('filterThresholdSlider');
  const threshValLabel = document.getElementById('filterThresholdVal');
  if (threshSlider && threshValLabel) {
    threshSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      threshValLabel.textContent = val.toFixed(2);
      state.filters.threshold = val;
    });
    threshSlider.addEventListener('change', () => {
      loadKpis();
      loadConfusionMatrix();
    });
  }

  // Reset filters button
  const resetBtn = document.getElementById('btnResetFilters');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      state.filters.time_band = '';
      state.filters.amount_band = '';
      state.filters.outcome = '';
      state.filters.class_label = '';
      state.filters.search = '';
      state.filters.threshold = 0.70;
      state.filters.page = 1;
      
      if (timeBandSelect) timeBandSelect.value = '';
      if (amountBandSelect) amountBandSelect.value = '';
      if (outcomeSelect) outcomeSelect.value = '';
      if (threshSlider) {
        threshSlider.value = 0.70;
        if (threshValLabel) threshValLabel.textContent = '0.70';
      }
      const searchInput = document.getElementById('tableSearchInput');
      if (searchInput) searchInput.value = '';
      
      loadAllDashboardData();
    });
  }
}

// 4. What-If Simulator Listeners
function initSimulatorListeners() {
  const simSlider = document.getElementById('simThresholdSlider');
  const simValLabel = document.getElementById('simThresholdVal');
  const simCostInput = document.getElementById('simAlertCostInput');

  if (simSlider && simValLabel) {
    simSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      simValLabel.textContent = val.toFixed(2);
      runSimulation(val, parseFloat(simCostInput ? simCostInput.value : 15.0));
    });
  }

  if (simCostInput) {
    simCostInput.addEventListener('input', (e) => {
      const cost = parseFloat(e.target.value) || 15.0;
      const thresh = parseFloat(simSlider ? simSlider.value : 0.70);
      runSimulation(thresh, cost);
    });
  }
}

// 5. Table Listeners & Actions
function initTableListeners() {
  const searchInput = document.getElementById('tableSearchInput');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        state.filters.search = e.target.value;
        state.filters.page = 1;
        loadTransactionsTable();
      }, 350);
    });
  }

  const exportBtn = document.getElementById('btnExportCsv');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      exportTransactionsCsv();
    });
  }

  const prevBtn = document.getElementById('btnPrevPage');
  const nextBtn = document.getElementById('btnNextPage');
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.filters.page > 1) {
        state.filters.page--;
        loadTransactionsTable();
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      state.filters.page++;
      loadTransactionsTable();
    });
  }
}

// 6. Data Loading Pipeline
async function loadAllDashboardData() {
  await Promise.all([
    loadKpis(),
    loadTimeTrendsChart(),
    loadAmountBandsChart(),
    loadConfusionMatrix(),
    loadThresholdTradeoffChart(),
    loadFeaturesChart(),
    loadTransactionsTable()
  ]);
  
  // Also run initial simulation with current threshold
  runSimulation(state.filters.threshold, 15.0);
}

// API Fetch Helper
async function fetchApi(endpoint) {
  try {
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`Fetch error for ${endpoint}:`, err);
    return null;
  }
}

// 7. Render KPI Cards
async function loadKpis() {
  const params = new URLSearchParams({
    model: state.filters.model,
    threshold: state.filters.threshold
  });
  if (state.filters.time_band) params.append('time_band', state.filters.time_band);
  if (state.filters.amount_band) params.append('amount_band', state.filters.amount_band);
  if (state.filters.outcome) params.append('outcome', state.filters.outcome);

  const data = await fetchApi(`/api/kpis?${params.toString()}`);
  if (!data) return;
  state.kpis = data;

  // Format Helper
  const fmtNum = (n) => Number(n).toLocaleString();
  const fmtCurrency = (n) => `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  // Update KPI Elements
  setElText('kpiTotalTx', fmtNum(data.total_transactions));
  setElText('kpiTotalAmount', fmtCurrency(data.total_amount));
  setElText('kpiAvgAmount', `Avg: ${fmtCurrency(data.avg_amount)}`);
  setElText('kpiFraudCount', fmtNum(data.fraud_count));
  setElText('kpiFraudRate', `${data.fraud_rate_pct.toFixed(4)}%`);
  setElText('kpiFraudAmount', fmtCurrency(data.fraud_amount));
  
  setElText('kpiPrecision', `${data.precision_pct.toFixed(2)}%`);
  setElText('kpiRecall', `${data.recall_pct.toFixed(2)}%`);
  setElText('kpiF1', data.f1_score.toFixed(4));
  setElText('kpiFlagged', fmtNum(data.flagged_count));
  setElText('kpiFlagRate', `${data.flag_rate_pct.toFixed(2)}%`);
  setElText('kpiPreventedAmount', fmtCurrency(data.prevented_fraud_amount));
  setElText('kpiMissedAmount', fmtCurrency(data.missed_fraud_amount));
}

function setElText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// 8. Render Time Band Trends Chart
async function loadTimeTrendsChart() {
  const data = await fetchApi('/api/charts/time_trends');
  if (!data) return;

  const categories = data.map(d => d.time_band);
  const txCounts = data.map(d => d.total_transactions);
  const fraudRates = data.map(d => d.fraud_rate);

  const options = {
    series: [
      { name: 'Total Transactions', type: 'column', data: txCounts },
      { name: 'Fraud Rate (%)', type: 'line', data: fraudRates }
    ],
    chart: {
      height: 290,
      type: 'line',
      toolbar: { show: false },
      background: 'transparent',
      foreColor: state.theme === 'dark' ? '#94a3b8' : '#475569'
    },
    stroke: { width: [0, 3], curve: 'smooth' },
    colors: ['#6366f1', '#f43f5e'],
    plotOptions: {
      bar: { columnWidth: '45%', borderRadius: 4 }
    },
    dataLabels: { enabled: false },
    xaxis: { categories: categories },
    yaxis: [
      {
        title: { text: 'Transactions' },
        labels: { formatter: (val) => val >= 1000 ? `${(val/1000).toFixed(0)}k` : val }
      },
      {
        opposite: true,
        title: { text: 'Fraud Rate (%)' },
        labels: { formatter: (val) => `${val.toFixed(2)}%` }
      }
    ],
    tooltip: {
      theme: state.theme === 'dark' ? 'dark' : 'light',
      y: {
        formatter: (val, opt) => opt.seriesIndex === 0 ? Number(val).toLocaleString() : `${val.toFixed(3)}%`
      }
    },
    grid: { borderColor: state.theme === 'dark' ? '#243048' : '#e2e8f0' }
  };

  renderApexChart('chartTimeTrends', options);
}

// 9. Render Amount Band Distribution Chart
async function loadAmountBandsChart() {
  const data = await fetchApi('/api/charts/amount_bands');
  if (!data) return;

  const categories = data.map(d => `$${d.amount_band}`);
  const fraudCounts = data.map(d => d.fraudulent_transactions);
  const fraudRates = data.map(d => d.fraud_rate);

  const options = {
    series: [
      { name: 'Fraud Cases', type: 'column', data: fraudCounts },
      { name: 'Fraud Rate (%)', type: 'line', data: fraudRates }
    ],
    chart: {
      height: 290,
      type: 'line',
      toolbar: { show: false },
      background: 'transparent',
      foreColor: state.theme === 'dark' ? '#94a3b8' : '#475569'
    },
    stroke: { width: [0, 3], curve: 'straight' },
    colors: ['#a855f7', '#f59e0b'],
    plotOptions: {
      bar: { columnWidth: '50%', borderRadius: 4 }
    },
    xaxis: { categories: categories },
    yaxis: [
      { title: { text: 'Fraud Cases' } },
      {
        opposite: true,
        title: { text: 'Risk Concentration (%)' },
        labels: { formatter: (val) => `${val.toFixed(2)}%` }
      }
    ],
    tooltip: {
      theme: state.theme === 'dark' ? 'dark' : 'light'
    },
    grid: { borderColor: state.theme === 'dark' ? '#243048' : '#e2e8f0' }
  };

  renderApexChart('chartAmountBands', options);
}

// 10. Render Confusion Matrix & Outcomes
async function loadConfusionMatrix() {
  const data = await fetchApi(`/api/charts/confusion_matrix?model=${state.filters.model}`);
  if (!data) return;

  const m = data.matrix;
  setElText('matTP', Number(m.tp).toLocaleString());
  setElText('matFP', Number(m.fp).toLocaleString());
  setElText('matFN', Number(m.fn).toLocaleString());
  setElText('matTN', Number(m.tn).toLocaleString());

  const options = {
    series: [m.tp, m.fp, m.fn, m.tn],
    labels: ['True Positives (Caught)', 'False Positives (Alarms)', 'False Negatives (Missed)', 'True Negatives (Cleared)'],
    chart: {
      type: 'donut',
      height: 280,
      background: 'transparent',
      foreColor: state.theme === 'dark' ? '#94a3b8' : '#475569'
    },
    colors: ['#10b981', '#f59e0b', '#f43f5e', '#0ea5e9'],
    legend: { position: 'bottom' },
    plotOptions: {
      pie: {
        donut: {
          size: '65%',
          labels: {
            show: true,
            total: {
              show: true,
              label: 'Total Scored',
              formatter: () => '283,726'
            }
          }
        }
      }
    },
    dataLabels: { enabled: false },
    tooltip: {
      theme: state.theme === 'dark' ? 'dark' : 'light'
    }
  };

  renderApexChart('chartConfusionDonut', options);
}

// 11. Render Threshold Trade-off Curve
async function loadThresholdTradeoffChart() {
  const data = await fetchApi(`/api/charts/threshold_curve?model=${state.filters.model}`);
  if (!data) return;

  const thresholds = data.map(d => d.threshold.toFixed(2));
  const precision = data.map(d => d.precision);
  const recall = data.map(d => d.recall);
  const f1 = data.map(d => (d.f1 * 100).toFixed(1));

  const options = {
    series: [
      { name: 'Precision (%)', data: precision },
      { name: 'Recall / Coverage (%)', data: recall },
      { name: 'F1 Score (x100)', data: f1 }
    ],
    chart: {
      height: 310,
      type: 'line',
      toolbar: { show: false },
      background: 'transparent',
      foreColor: state.theme === 'dark' ? '#94a3b8' : '#475569'
    },
    stroke: { width: 3, curve: 'smooth' },
    colors: ['#10b981', '#f43f5e', '#6366f1'],
    xaxis: {
      categories: thresholds,
      title: { text: 'Decision Threshold' }
    },
    yaxis: {
      min: 0,
      max: 100,
      title: { text: 'Percentage / Metric Score' }
    },
    grid: { borderColor: state.theme === 'dark' ? '#243048' : '#e2e8f0' },
    tooltip: {
      theme: state.theme === 'dark' ? 'dark' : 'light',
      y: { formatter: (val) => `${val}%` }
    }
  };

  renderApexChart('chartThresholdCurve', options);
}

// 12. Render Discriminative Features
async function loadFeaturesChart() {
  const data = await fetchApi('/api/charts/features');
  if (!data) return;

  const features = data.map(d => d.name);
  const gaps = data.map(d => d.gap);

  const options = {
    series: [{ name: 'Absolute Separation Gap', data: gaps }],
    chart: {
      type: 'bar',
      height: 300,
      toolbar: { show: false },
      background: 'transparent',
      foreColor: state.theme === 'dark' ? '#94a3b8' : '#475569'
    },
    plotOptions: {
      bar: { horizontal: true, borderRadius: 4, barHeight: '55%' }
    },
    colors: ['#6366f1'],
    dataLabels: { enabled: false },
    xaxis: {
      categories: features,
      title: { text: 'Mean Separation Magnitude' }
    },
    grid: { borderColor: state.theme === 'dark' ? '#243048' : '#e2e8f0' },
    tooltip: {
      theme: state.theme === 'dark' ? 'dark' : 'light'
    }
  };

  renderApexChart('chartFeatures', options);
}

// 13. Render & Populate Data Table
async function loadTransactionsTable() {
  const params = new URLSearchParams({
    page: state.filters.page,
    limit: state.filters.limit,
    model: state.filters.model,
    sort_by: state.filters.sort_by,
    sort_dir: state.filters.sort_dir
  });
  if (state.filters.search) params.append('search', state.filters.search);
  if (state.filters.outcome) params.append('outcome', state.filters.outcome);
  if (state.filters.class_label !== '') params.append('class_label', state.filters.class_label);

  const data = await fetchApi(`/api/transactions?${params.toString()}`);
  const tbody = document.getElementById('transactionsTableBody');
  if (!tbody || !data) return;

  tbody.innerHTML = '';
  const records = data.records || [];

  if (records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-muted);">No transactions match the selected filters.</td></tr>';
    return;
  }

  records.forEach(row => {
    const tr = document.createElement('tr');
    
    let outcomeClass = 'tn';
    if (row.outcome === 'True Positive') outcomeClass = 'tp';
    else if (row.outcome === 'False Positive') outcomeClass = 'fp';
    else if (row.outcome === 'False Negative') outcomeClass = 'fn';

    const isFraud = row.class_label === 1;
    const fraudBadge = isFraud 
      ? '<span class="outcome-pill fn">FRAUD (1)</span>' 
      : '<span style="color:var(--text-muted); font-size:0.75rem;">Legit (0)</span>';

    const probVal = (row.predicted_probability * 100).toFixed(1);
    const probColor = row.predicted_probability >= 0.70 ? 'var(--color-danger)' : (row.predicted_probability >= 0.30 ? 'var(--color-warning)' : 'var(--text-secondary)');

    tr.innerHTML = `
      <td><strong>#${row.transaction_id}</strong></td>
      <td>${row.time_hours}h</td>
      <td><strong>$${Number(row.transaction_amount).toFixed(2)}</strong></td>
      <td>${fraudBadge}</td>
      <td><span style="font-weight:700; color:${probColor}">${probVal}%</span></td>
      <td><span class="outcome-pill ${outcomeClass}">${row.outcome}</span></td>
      <td>
        <button class="pagination-btn" style="padding:0.2rem 0.5rem;" onclick="inspectTransaction(${row.transaction_id})">
          Inspect
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Update Pagination Controls
  const p = data.pagination || {};
  setElText('tablePaginationInfo', `Showing ${((p.page - 1) * p.limit) + 1} - ${Math.min(p.page * p.limit, p.total_records)} of ${Number(p.total_records).toLocaleString()} records`);
  
  const prevBtn = document.getElementById('btnPrevPage');
  const nextBtn = document.getElementById('btnNextPage');
  if (prevBtn) prevBtn.disabled = !p.has_prev;
  if (nextBtn) nextBtn.disabled = !p.has_next;
}

// 14. What-If Simulation Runner
async function runSimulation(threshold, costPerAlert) {
  const data = await fetchApi(`/api/simulate?model=${state.filters.model}&threshold=${threshold}&cost=${costPerAlert}`);
  if (!data) return;

  setElText('simTP', Number(data.true_positives).toLocaleString());
  setElText('simFP', Number(data.false_positives).toLocaleString());
  setElText('simFN', Number(data.false_negatives).toLocaleString());
  setElText('simAlerts', Number(data.flagged_alerts).toLocaleString());
  setElText('simPrecision', `${data.precision_pct.toFixed(2)}%`);
  setElText('simRecall', `${data.recall_pct.toFixed(2)}%`);
  setElText('simPreventedAmt', `$${Number(data.prevented_fraud_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}`);
  setElText('simInvestigationCost', `$${Number(data.alert_investigation_cost).toLocaleString(undefined, { minimumFractionDigits: 2 })}`);
  setElText('simNetBenefit', `$${Number(data.net_financial_benefit).toLocaleString(undefined, { minimumFractionDigits: 2 })}`);
}

// 15. Inspect Transaction Modal
async function inspectTransaction(txId) {
  const modal = document.getElementById('inspectModal');
  const body = document.getElementById('modalContent');
  if (!modal || !body) return;

  body.innerHTML = '<div style="text-align:center; padding:2rem;"><div class="pulse-dot" style="margin:0 auto 1rem;"></div>Loading transaction features...</div>';
  modal.classList.add('active');

  const data = await fetchApi(`/api/transaction/${txId}?model=${state.filters.model}`);
  if (!data || data.error) {
    body.innerHTML = '<p style="color:var(--color-danger);">Failed to load transaction details.</p>';
    return;
  }

  let signalsHtml = (data.top_signals || []).map(s => `
    <div style="display:flex; justify-content:space-between; padding:0.4rem 0; border-bottom:1px solid var(--border-subtle); font-size:0.8rem;">
      <strong>${s.feature}</strong>
      <span style="font-family:monospace; color:${s.value < 0 ? 'var(--color-danger)' : 'var(--color-info)'}">${s.value}</span>
    </div>
  `).join('');

  body.innerHTML = `
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem; margin-bottom:1rem;">
      <div style="background:var(--bg-primary); padding:0.85rem; border-radius:8px;">
        <div style="font-size:0.75rem; color:var(--text-muted);">Transaction ID</div>
        <div style="font-size:1.1rem; font-weight:700;">#${data.transaction_id}</div>
      </div>
      <div style="background:var(--bg-primary); padding:0.85rem; border-radius:8px;">
        <div style="font-size:0.75rem; color:var(--text-muted);">Amount</div>
        <div style="font-size:1.1rem; font-weight:700; color:var(--accent-primary);">$${Number(data.transaction_amount).toFixed(2)}</div>
      </div>
      <div style="background:var(--bg-primary); padding:0.85rem; border-radius:8px;">
        <div style="font-size:0.75rem; color:var(--text-muted);">Actual Ground Truth</div>
        <div style="font-size:1rem; font-weight:700;">${data.class_label === 1 ? '<span style="color:var(--color-danger);">Fraudulent (1)</span>' : '<span style="color:var(--color-success);">Legitimate (0)</span>'}</div>
      </div>
      <div style="background:var(--bg-primary); padding:0.85rem; border-radius:8px;">
        <div style="font-size:0.75rem; color:var(--text-muted);">Model Fraud Probability</div>
        <div style="font-size:1.1rem; font-weight:800; color:${data.predicted_probability >= 0.70 ? 'var(--color-danger)' : 'var(--color-success)'}">
          ${(data.predicted_probability * 100).toFixed(2)}%
        </div>
      </div>
    </div>
    
    <div>
      <h4 style="font-size:0.85rem; text-transform:uppercase; margin-bottom:0.6rem; color:var(--text-secondary);">Top Feature Anomaly Signals</h4>
      <div style="background:var(--bg-primary); padding:0.85rem; border-radius:8px;">
        ${signalsHtml}
      </div>
    </div>

    <div style="font-size:0.72rem; color:var(--text-muted); word-break:break-all;">
      <strong>SHA-256 Hash:</strong> ${data.transaction_hash}
    </div>
  `;
}

function closeModal() {
  const modal = document.getElementById('inspectModal');
  if (modal) modal.classList.remove('active');
}

// 16. CSV Export Trigger
function exportTransactionsCsv() {
  const params = new URLSearchParams({
    model: state.filters.model
  });
  if (state.filters.search) params.append('search', state.filters.search);
  if (state.filters.outcome) params.append('outcome', state.filters.outcome);
  if (state.filters.class_label !== '') params.append('class_label', state.filters.class_label);

  window.location.href = `/api/export?${params.toString()}`;
}

// ApexCharts Helper Wrapper
function renderApexChart(containerId, options) {
  const el = document.getElementById(containerId);
  if (!el || typeof ApexCharts === 'undefined') return;

  if (state.charts[containerId]) {
    state.charts[containerId].updateOptions(options);
  } else {
    state.charts[containerId] = new ApexCharts(el, options);
    state.charts[containerId].render();
  }
}

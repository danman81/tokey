(() => {
  const root = document.getElementById('tokey-cockpit');
  const el = id => root.querySelector('#tc-' + id);
  const post = (action, extra = {}) => {
    window.webkit?.messageHandlers?.tokey?.postMessage({action, ...extra});
  };
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function ownButton(id, handler) {
    const old = el(id), fresh = old.cloneNode(true);
    old.replaceWith(fresh);
    fresh.addEventListener('click', handler);
    return fresh;
  }

  const run = ownButton('run', () => post('toggle'));
  const save = ownButton('save', () => post('save', {format: el('format').value}));
  const copy = ownButton('copy', () => {});
  const copyCaption = ownButton('copy-caption', () => post('copy-caption', {text: el('caption').value}));
  const copyResults = ownButton('copy-results', () => post('copy-results', {format: el('format').value}));
  root.querySelectorAll('[data-device]').forEach(button => {
    const fresh = button.cloneNode(true); button.replaceWith(fresh);
    fresh.addEventListener('click', () => post('device', {device: fresh.dataset.device}));
  });
  root.querySelectorAll('[data-sort]').forEach(button => {
    const fresh = button.cloneNode(true); button.replaceWith(fresh);
    fresh.addEventListener('click', () => post('sort', {key: fresh.dataset.sort}));
  });
  el('format').value = 'PNG';
  [...el('format').options].forEach(option => option.disabled = option.value !== 'PNG');

  function iconState(state) {
    run.classList.toggle('tc-icon', state.running || state.complete);
    run.classList.toggle('tc-primary', !state.running && !state.complete);
    if (state.running) {
      run.innerHTML = state.paused
        ? '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.5v11l9-5.5z" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="2.5" width="3.5" height="11" rx="1" fill="currentColor"/><rect x="9.5" y="2.5" width="3.5" height="11" rx="1" fill="currentColor"/></svg>';
    } else if (state.complete) {
      run.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M13 5A5.5 5.5 0 1 0 13.2 10" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 2h3.5v3.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
    } else {
      run.textContent = 'Run Tokey!';
    }
    run.setAttribute('aria-label', state.running ? (state.paused ? 'Resume run' : 'Pause run') : state.complete ? 'Run again' : 'Run Tokey!');
  }

  function renderRows(state) {
    const body = el('models');
    body.innerHTML = '';
    for (const model of state.models || []) {
      const result = model.result || {};
      const generation = result.generation;
      const row = document.createElement('tr');
      row.dataset.active = String(Boolean(model.active));
      const generationWidth = generation ? Math.min(100, generation / Math.max(1, state.generationScale) * 100) : 0;
      const unavailable = '<span class="tc-number">—</span><div class="tc-track" aria-hidden="true"><span style="width:0"></span></div>';
      row.innerHTML = `<td><button type="button" class="tc-model" title="${esc(model.tooltip || model.name)}"><span class="tc-model-name">${esc(model.name)}</span><span class="tc-size">${esc(model.size || '')}</span></button></td>`+
        `<td data-key="speed"><div class="tc-metric"><span class="tc-number">${generation == null ? '—' : generation.toFixed(1)}</span><div class="tc-track" aria-hidden="true"><span style="width:${generationWidth}%"></span></div></div></td>`+
        `<td data-key="latency"><div class="tc-metric">${unavailable}</div></td>`+
        `<td data-key="memory"><div class="tc-metric">${unavailable}</div></td>`;
      body.append(row);
    }
  }

  window.TokeyProduction = {
    apply(state) {
      root.dataset.running = String(Boolean(state.running));
      root.dataset.paused = String(Boolean(state.paused));
      root.dataset.complete = String(Boolean(state.complete));
      root.dataset.production = 'true';
      iconState(state);
      el('hardware').textContent = state.running ? '' : (state.hardware || '');
      el('status').hidden = !state.status;
      el('stage').textContent = state.status || '';
      el('detail').textContent = '';
      el('detail-compact').textContent = '';
      const progress = Math.max(0, Math.min(100, Number(state.progress || 0)));
      el('progress').setAttribute('aria-valuenow', String(progress));
      el('progress').firstElementChild.style.width = progress + '%';
      root.querySelector('[data-device="CPU"]').hidden = false;
      root.querySelector('[data-device="CPU"]').setAttribute('aria-pressed', 'true');
      for (const device of ['GPU','NPU']) root.querySelector(`[data-device="${device}"]`).hidden = true;
      renderRows(state);
      const ready = Boolean(state.complete);
      el('format').disabled = !ready;
      save.disabled = !ready;
      copyResults.disabled = !ready;
      copyResults.textContent = 'Copy results · PNG';
      if (state.notice) el('caption-status').textContent = state.notice;
    }
  };
  save.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 2h10l2 2v10H2zM4 2v4h7V2M4 10h8v4H4z" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';
  copy.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="5" y="5" width="9" height="9" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M3 11H2V2h9v1" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';
  post('ready');
})();

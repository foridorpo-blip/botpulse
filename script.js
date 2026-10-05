// BotPulse — landing page interactivity

// Theme toggle
(function () {
  const toggle = document.querySelector('[data-theme-toggle]');
  const root = document.documentElement;
  let theme = matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light';
  root.setAttribute('data-theme', theme);

  function updateIcon() {
    toggle.innerHTML = theme === 'dark'
      ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    toggle.setAttribute('aria-label', theme === 'dark' ? 'Переключить на светлую тему' : 'Переключить на тёмную тему');
  }
  updateIcon();

  toggle.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', theme);
    updateIcon();
  });
})();

// Header scroll behavior
(function () {
  const header = document.getElementById('header');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const scroll = window.scrollY;
    if (scroll > 80) header.classList.add('header--scrolled');
    else header.classList.remove('header--scrolled');
    if (scroll > lastScroll && scroll > 200) header.classList.add('header--hidden');
    else header.classList.remove('header--hidden');
    lastScroll = scroll;
  }, { passive: true });
})();

// Mobile menu
(function () {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => nav.classList.toggle('nav--open'));
  nav.querySelectorAll('.nav__link').forEach(link =>
    link.addEventListener('click', () => nav.classList.remove('nav--open'))
  );
})();

// Install tabs
(function () {
  const tabs = document.querySelectorAll('.install__tab');
  const blocks = document.querySelectorAll('.install__block');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach(t => t.classList.remove('install__tab--active'));
      blocks.forEach(b => b.classList.remove('install__block--active'));
      tab.classList.add('install__tab--active');
      document.querySelector(`[data-block="${target}"]`).classList.add('install__block--active');
    });
  });
})();

// Copy buttons
(function () {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.dataset.copy;
      navigator.clipboard.writeText(text).then(() => {
        const original = btn.innerHTML;
        btn.classList.add('copy-btn--copied');
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg> Скопировано';
        setTimeout(() => {
          btn.classList.remove('copy-btn--copied');
          btn.innerHTML = original;
        }, 2000);
      });
    });
  });
})();

// Waveform canvas animation
(function () {
  const canvas = document.getElementById('waveform');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, time = 0;

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    w = canvas.width = rect.width * dpr;
    h = canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
  }
  resize();
  window.addEventListener('resize', resize);

  const isDark = () => document.documentElement.getAttribute('data-theme') === 'dark';
  const accentColor = () => isDark() ? 'rgba(0,217,255,0.15)' : 'rgba(0,102,204,0.12)';

  function draw() {
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    ctx.strokeStyle = accentColor();
    ctx.lineWidth = 2;
    ctx.beginPath();

    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const points = 60;

    for (let i = 0; i <= points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const wave = Math.sin(angle * 4 + time) * 8 + Math.sin(angle * 8 + time * 1.5) * 4;
      const radius = 160 + wave;
      const x = cx + Math.cos(angle) * radius;
      const y = cy + Math.sin(angle) * radius;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
    time += 0.02;
    requestAnimationFrame(draw);
  }
  draw();
})();

// Demo terminal
(function () {
  const body = document.getElementById('terminal-body');
  const form = document.getElementById('terminal-form');
  const input = document.getElementById('terminal-input');
  if (!body || !form || !input) return;

  const commands = {
    help: [
      { text: 'BotPulse v1.0.0 — команды:', class: 'terminal__line--accent' },
      { text: '  /start        — приветствие' },
      { text: '  /help         — эта справка' },
      { text: '  /checks       — список проверок' },
      { text: '  /check <name> — одна проверка' },
      { text: '  /check_all    — все проверки' },
      { text: '  /ai <вопрос>  — вопрос к AI' },
      { text: '  /status       — статус AI-модуля' },
    ],
    checks: [
      { text: 'Настроенные проверки:', class: 'terminal__line--accent' },
      { text: '1. OpenAI Balance (api_service)' },
      { text: '2. BTC Wallet (crypto)' },
      { text: '3. ETH Balance (crypto)' },
      { text: '4. VPN Panel (vpn)' },
      { text: '5. Custom API (universal)' },
    ],
    check_all: [
      { text: 'Запускаю 5 проверок...', class: 'terminal__line--muted' },
      { text: '' },
      { text: '[OK] OpenAI Balance: $12.50', class: 'terminal__line--ok' },
      { text: '[OK] BTC Wallet: 0.00245123 BTC', class: 'terminal__line--ok' },
      { text: '[OK] ETH Balance: 3.8421 ETH', class: 'terminal__line--ok' },
      { text: '[OK] VPN Panel: 18 дней осталось', class: 'terminal__line--ok' },
      { text: '[FAIL] Custom API: HTTP 503', class: 'terminal__line--err' },
      { text: '' },
      { text: 'Итого: 4/5 OK, 1 FAIL', class: 'terminal__line--accent' },
    ],
    status: [
      { text: 'Статус BotPulse:', class: 'terminal__line--accent' },
      { text: 'Проверок настроено: 5' },
      { text: 'AI-модуль: настроен' },
      { text: 'Провайдер: gemini' },
      { text: 'Модель: gemini-2.0-flash' },
      { text: 'Base URL: https://generativelanguage.googleapis.com/v1beta/openai' },
    ],
    ai: [
      { text: 'Вопрос: Какие сервисы требуют внимания?', class: 'terminal__line--ai' },
      { text: '' },
      { text: 'Анализирую результаты проверок...', class: 'terminal__line--muted' },
      { text: '' },
      { text: 'Custom API (api.example.com) вернул HTTP 503,', class: 'terminal__line--ai' },
      { text: 'что указывает на недоступность сервера.' },
      { text: 'Остальные 4 сервиса работают нормально.' },
      { text: 'Рекомендую проверить статус api.example.com' },
      { text: 'и повторить проверку через /check Custom API.' },
    ],
    start: [
      { text: 'BotPulse — бот для проверки балансов и статуса сервисов.', class: 'terminal__line--accent' },
      { text: 'Введите /help для списка команд.' },
    ],
  };

  function addLine(text, cls) {
    const div = document.createElement('div');
    div.className = 'terminal__line' + (cls ? ' ' + cls : '');
    div.textContent = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function addInputLine(cmd) {
    const div = document.createElement('div');
    div.className = 'terminal__line';
    div.innerHTML = '<span style="color:#00d9ff">botpulse</span><span style="color:#6b7c93">:~$</span> ' + cmd;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
  }

  function processCommand(cmd) {
    cmd = cmd.trim().toLowerCase();
    if (!cmd) return;
    addInputLine(cmd);

    // Remove leading /
    const key = cmd.replace(/^\//, '').split(' ')[0];

    if (commands[key]) {
      commands[key].forEach(line => {
        setTimeout(() => addLine(line.text, line.class), 50);
      });
    } else if (key === 'clear' || key === 'cls') {
      body.innerHTML = '';
    } else {
      addLine(`Команда не найдена: ${cmd}`, 'terminal__line--err');
      addLine('Введите help для списка команд.', 'terminal__line--muted');
    }
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    const cmd = input.value;
    input.value = '';
    processCommand(cmd);
  });

// Auto-focus
  body.addEventListener('click', () => input.focus());
})();

// AI Assistant Widget
(function () {
  const toggle = document.getElementById('ai-toggle');
  const panel = document.getElementById('ai-panel');
  const close = document.getElementById('ai-close');
  const form = document.getElementById('ai-form');
  const input = document.getElementById('ai-input');
  const messages = document.getElementById('ai-messages');
  const modelSelect = document.getElementById('ai-model-select');
  const statusText = document.getElementById('ai-status-text');
  const statusDot = document.getElementById('ai-status-dot');
  const actionBar = document.getElementById('ai-status-bar');
  const actionBtn = document.getElementById('ai-action-btn');
  const badge = document.getElementById('ai-badge');
  if (!toggle || !panel) return;

  // API base — __PORT_5000__ placeholder rewritten by deploy
  const API = '__PORT_5000__';

  // Toggle panel
  toggle.addEventListener('click', () => {
    panel.classList.toggle('ai-widget__panel--open');
    if (panel.classList.contains('ai-widget__panel--open')) input.focus();
  });
  close.addEventListener('click', () => panel.classList.remove('ai-widget__panel--open'));

  // License status
  let licenseStatus = 'inactive';

  async function checkStatus() {
    try {
      const r = await fetch(API + '/api/status');
      const data = await r.json();
      licenseStatus = data.status;
      statusText.textContent = data.message;

      statusDot.className = 'ai-widget__dot';
      if (data.status === 'active') {
        statusDot.classList.add('ai-widget__dot--active');
        badge.style.display = 'none';
        actionBtn.style.display = 'none';
      } else if (data.status === 'locked') {
        statusDot.classList.add('ai-widget__dot--locked');
        badge.textContent = '!';
        badge.style.background = 'var(--error)';
        actionBtn.style.display = 'none';
      } else if (data.status === 'expired') {
        statusDot.classList.add('ai-widget__dot--expired');
        badge.textContent = '!';
        badge.style.background = 'var(--warning)';
        actionBtn.textContent = 'Продлить';
        actionBtn.style.display = 'block';
      } else {
        // inactive
        badge.style.display = 'block';
        actionBtn.textContent = 'Активировать';
        actionBtn.style.display = 'block';
      }
    } catch (e) {
      statusText.textContent = 'Сервер недоступен';
      statusDot.className = 'ai-widget__dot';
    }
  }

  // Action button (activate / renew)
  actionBtn.addEventListener('click', async () => {
    actionBtn.disabled = true;
    actionBtn.textContent = '...';
    const endpoint = licenseStatus === 'expired' ? '/api/renew' : '/api/activate';
    try {
      const r = await fetch(API + endpoint, { method: 'POST' });
      const data = await r.json();
      if (r.ok) {
        await checkStatus();
      } else {
        statusText.textContent = data.error || 'Ошибка';
      }
    } catch (e) {
      statusText.textContent = 'Сервер недоступен';
    }
    actionBtn.disabled = false;
  });

  // Send message
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    if (licenseStatus !== 'active') {
      addMsg('API-ключ не активен. ' + statusText.textContent, 'error');
      return;
    }

    // Add user message
    addMsg(text, 'user');
    input.value = '';

    // Loading indicator
    const loading = addMsg('Думаю...', 'loading');

    // Send to API
    try {
      const r = await fetch(API + '/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: modelSelect.value,
          messages: buildMessages(text),
        }),
      });
      const data = await r.json();
      loading.remove();

      if (r.ok && data.response) {
        addMsg(data.response, 'bot');
      } else {
        addMsg(data.error || 'Ошибка при получении ответа', 'error');
      }
    } catch (e) {
      loading.remove();
      addMsg('Сервер недоступен. Попробуйте позже.', 'error');
    }
  });

  // Build message history (last 10 messages)
  const history = [];
  function buildMessages(text) {
    history.push({ role: 'user', content: text });
    if (history.length > 20) history.splice(0, history.length - 20);
    return [
      { role: 'system', content: 'Ты — ИИ-ассистент BotPulse. Помогаешь с вопросами о проверке балансов, VPN, криптовалютах, API-сервисах. Отвечай на русском языке, кратко и по делу.' },
      ...history,
    ];
  }

  function addMsg(text, type) {
    const div = document.createElement('div');
    div.className = 'ai-widget__msg ai-widget__msg--' + type;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  // Check status on load
  checkStatus();
  setInterval(checkStatus, 60000);
})();

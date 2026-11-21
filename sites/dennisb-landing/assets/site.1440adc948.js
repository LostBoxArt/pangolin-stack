(() => {
  const site = document.getElementById('site');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const chapters = [...document.querySelectorAll('.chapter')];
  const stories = [...document.querySelectorAll('.story')];
  const chapterStatus = document.getElementById('chapter-status');
  site.classList.add('has-js');

  function selectChapter(id, announce = false) {
    if (!stories.some(story => story.id === id)) return;
    site.dataset.chapter = id;
    stories.forEach(story => { story.hidden = story.id !== id; });
    chapters.forEach(link => {
      if (link.hash === '#' + id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (announce) chapterStatus.textContent = document.getElementById(id).querySelector('h2').textContent;
  }
  selectChapter(location.hash.slice(1) || 'home');
  if (!site.dataset.chapter) selectChapter('home');
  chapters.forEach(link => link.addEventListener('click', event => {
    // Preserve modifier-click and native open-in-new-tab behavior.
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    selectChapter(link.hash.slice(1), true);
    history.replaceState(null, '', link.hash);
  }));
  window.addEventListener('hashchange', () => selectChapter(location.hash.slice(1)));

  const video = document.getElementById('hero-film');
  const motionButton = document.getElementById('motion-control');
  const motionStatus = document.getElementById('motion-status');
  const connection = navigator.connection;
  let wantsMotion = !reducedMotion.matches && !connection?.saveData;
  let inView = false;
  let ready = document.readyState === 'complete';
  let mediaFailed = false;
  let playAttempt = 0;
  try { if (localStorage.getItem('dennisb-motion') === 'off') wantsMotion = false; } catch (_) { /* Storage is optional. */ }

  function updateMotion() {
    motionButton.textContent = wantsMotion ? 'Pause Motion Ⅱ' : 'Play Motion ↗';
    motionButton.setAttribute('aria-pressed', String(wantsMotion));
    if (!ready || mediaFailed) return;
    if (!wantsMotion || !inView || document.hidden) {
      playAttempt += 1;
      video.pause();
      return;
    }
    if (!video.src) video.src = video.dataset.src;
    const attempt = ++playAttempt;
    video.play().catch(error => {
      if (attempt !== playAttempt || error.name === 'AbortError') return;
      wantsMotion = false;
      updateMotion();
    });
  }
  video.addEventListener('playing', () => video.classList.add('is-playing'));
  video.addEventListener('error', () => {
    mediaFailed = true;
    video.classList.remove('is-playing');
    motionButton.hidden = true;
    motionStatus.textContent = 'Motion is unavailable. The illustration is still available.';
  });
  if (video.canPlayType('video/mp4')) {
    motionButton.addEventListener('click', () => {
      wantsMotion = !wantsMotion;
      try { localStorage.setItem('dennisb-motion', wantsMotion ? 'on' : 'off'); } catch (_) { /* Storage is optional. */ }
      updateMotion();
    });
    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      updateMotion();
    }, { threshold: .15 }).observe(document.querySelector('.hero'));
    const enableMotion = () => { ready = true; motionButton.hidden = mediaFailed; updateMotion(); };
    if (ready) enableMotion();
    else window.addEventListener('load', enableMotion, { once: true });
  }

  const demoButton = document.getElementById('demo-control');
  const demoStatus = document.getElementById('demo-status');
  const result = document.getElementById('trace-result');
  const steps = [...document.querySelectorAll('[data-step]')];
  const messages = [
    'Run the example to follow the scheduler checks.',
    'Reading the job’s pending reason.',
    'Comparing the request with available hosts.',
    'Checking the queue’s per-user policy.',
    'Replay complete. The per-user queue limit explains this example.'
  ];
  let step = 0;
  let timer = null;
  function renderReplay() {
    steps.forEach(line => {
      const number = Number(line.dataset.step);
      line.classList.toggle('is-pending', number > step);
      line.classList.toggle('trace-enter', number === step);
      if (number === step) line.setAttribute('aria-current', 'step');
      else line.removeAttribute('aria-current');
    });
    result.hidden = step < 4;
    demoStatus.textContent = messages[step];
    demoButton.textContent = timer !== null ? 'Pause Example Ⅱ' : step === 4 ? 'Replay the Example →' : step ? 'Continue the Example →' : 'Run the Example →';
  }
  function pauseReplay() {
    if (timer === null) return;
    clearTimeout(timer);
    timer = null;
    renderReplay();
  }
  function advanceReplay() {
    step += 1;
    timer = step < 4 ? setTimeout(advanceReplay, 1200) : null;
    renderReplay();
  }
  demoButton.hidden = false;
  demoButton.addEventListener('click', () => {
    if (timer !== null) { pauseReplay(); return; }
    if (step === 4) step = 0;
    if (reducedMotion.matches) step = 4;
    else timer = setTimeout(advanceReplay, 300);
    renderReplay();
  });
  renderReplay();
  document.addEventListener('visibilitychange', () => {
    updateMotion();
    if (document.hidden) pauseReplay();
  });
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) {
      wantsMotion = false;
      updateMotion();
      pauseReplay();
    }
  });
})();
